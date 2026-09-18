"""Tesseract candidate adapter (M20/M21) — technical candidate path only, NOT production.

Tesseract is candidate #1 in the M14 list (``app.evaluation.engines.CANDIDATE_ENGINES``):
self-hosted, offline, Apache-2.0, word-level boxes + confidence — the lightest engine
that satisfies the seam's needs. **This adapter selects nothing.** Production still runs
the unconfigured extractor; engine selection stays blocked on the S-6 held-out evaluation
(D-02 / AR-AST-008 / M14). See ``SPRINT_4_M20_OCR_CANDIDATE_ADAPTER.md`` and
``SPRINT_4_M21_PDF_RASTERIZATION.md``.

Input handling:

* **image/png, image/jpeg, image/tiff** → Tesseract directly (one page).
* **application/pdf** → rasterized locally to one image per page (``pdf_rasterizer``) → Tesseract
  per page → one ``ExtractedPage`` per PDF page, in order (M21).

Design:

* ``pytesseract``/``Pillow`` are imported lazily and only in the reader helpers, so a missing
  dependency becomes an honest extraction failure rather than an import-time crash. The PDF
  renderer is isolated in :mod:`ocr_candidates.pdf_rasterizer`. No engine knowledge leaks
  outside this package.
* :func:`result_from_words` / :func:`result_from_pages` are PURE mappings (engine word boxes →
  the seam's ``ExtractionResult``) with no OCR dependency, so the contract is testable without
  the binary or renderer installed.
* Everything runs locally. No network calls; no document text or page image is logged.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, BinaryIO, NamedTuple

from app.core.errors import DocumentExtractionError
from app.services.extraction import (
    ExtractedPage,
    ExtractionResult,
    TextBlock,
    TextRegion,
)
from ocr_candidates.pdf_rasterizer import DEFAULT_SCALE, rasterize_pdf

if TYPE_CHECKING:
    from app.core.config import Settings

_IMAGE_CONTENT_TYPES = frozenset({"image/png", "image/jpeg", "image/jpg", "image/tiff"})
_PDF_CONTENT_TYPE = "application/pdf"

_ENGINE_NAME = "tesseract"


class Word(NamedTuple):
    """One recognised word: text, confidence (0..100, engine scale), pixel box."""

    text: str
    conf: float
    left: int
    top: int
    width: int
    height: int


class ImageWords(NamedTuple):
    """A page's words plus the pixel size they were measured against."""

    words: list[Word]
    image_width: int
    image_height: int


# A word reader turns one image stream into words + size; a page reader turns a PDF stream into
# one ``ImageWords`` per page. The real ones call Tesseract (and the rasterizer); tests inject
# deterministic fakes so the adapter is exercisable without the binary/renderer. These are narrow
# test/rasterizer seams, not a second extraction abstraction.
WordReader = Callable[[BinaryIO, str], ImageWords]
PageReader = Callable[[BinaryIO], list[ImageWords]]


def _fraction(value: int, extent: int) -> float:
    """Pixel coordinate → page-relative fraction, clamped into [0, 1]."""
    if extent <= 0:
        return 0.0
    return min(max(value / extent, 0.0), 1.0)


def _page_from_words(read: ImageWords, page_number: int) -> ExtractedPage:
    """Build one ``ExtractedPage`` from engine word boxes (pure, no OCR dependency).

    Words with empty text or a negative confidence (Tesseract's marker for a non-word region)
    are dropped. Boxes are converted from pixels to page-relative fractions so no engine's pixel
    units leak past the boundary (see ``TextRegion``).
    """
    blocks: list[TextBlock] = []
    texts: list[str] = []
    for word in read.words:
        text = word.text.strip()
        if not text or word.conf < 0:
            continue
        x = _fraction(word.left, read.image_width)
        y = _fraction(word.top, read.image_height)
        w = _fraction(word.width, read.image_width)
        h = _fraction(word.height, read.image_height)
        # Clamp so float rounding cannot push the box past the page edge (TextRegion rejects
        # that), and skip a box that has collapsed to zero area after clamping.
        w = min(w, 1.0 - x)
        h = min(h, 1.0 - y)
        region: TextRegion | None = None
        if w > 0 and h > 0:
            region = TextRegion(page=page_number, x=x, y=y, width=w, height=h)
        blocks.append(
            TextBlock(text=text, region=region, confidence=min(word.conf / 100.0, 1.0))
        )
        texts.append(text)
    return ExtractedPage(number=page_number, text=" ".join(texts), blocks=tuple(blocks))


def result_from_words(
    read: ImageWords,
    *,
    engine_version: str,
    page_number: int = 1,
) -> ExtractionResult:
    """Single-page ``ExtractionResult`` (image input). Pure, no OCR dependency."""
    page = _page_from_words(read, page_number)
    return ExtractionResult(
        pages=(page,),
        engine=_ENGINE_NAME,
        engine_version=engine_version,
        metadata={"word_count": str(len(page.blocks)), "page_count": "1"},
    )


def result_from_pages(
    reads: Sequence[ImageWords],
    *,
    engine_version: str,
) -> ExtractionResult:
    """Multi-page ``ExtractionResult`` (PDF input): one ``ExtractedPage`` per page, in order."""
    pages = tuple(_page_from_words(read, i) for i, read in enumerate(reads, start=1))
    word_count = sum(len(page.blocks) for page in pages)
    return ExtractionResult(
        pages=pages,
        engine=_ENGINE_NAME,
        engine_version=engine_version,
        metadata={"word_count": str(word_count), "page_count": str(len(pages))},
    )


def _run_tesseract_on_image(image: object, *, cmd: str | None, languages: str) -> ImageWords:
    """Run Tesseract on an already-open PIL image. The only place ``pytesseract`` is imported."""
    try:
        import pytesseract
    except ImportError as exc:
        raise DocumentExtractionError(
            detail="The Tesseract candidate adapter is not installed.",
            remediation="Install 'pytesseract' and the Tesseract binary to run this candidate. "
            "Your file is unchanged.",
        ) from exc

    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd

    try:
        width, height = image.size  # type: ignore[attr-defined]
        data = pytesseract.image_to_data(
            image, lang=languages, output_type=pytesseract.Output.DICT
        )
    except Exception as exc:  # pytesseract raises many engine-specific errors; treat as one
        # No document content or engine internals are put in the message (NFR-ERR-004).
        raise DocumentExtractionError from exc

    # Blocks are line-level (one "Word" per Tesseract line), not per-word: a value like a
    # full name or a table-row date lives on one line, so a line block gives it a single
    # region and a single provenance handle — which is what a downstream field extractor and
    # the AttributeObservation model (one source block per value) need.
    return ImageWords(words=_lines_from_tsv_dict(data), image_width=width, image_height=height)


def _read_words_with_tesseract(
    source: BinaryIO,
    content_type: str,
    *,
    cmd: str | None,
    languages: str,
) -> ImageWords:
    """Open one image and OCR it. Honest failure on a missing dep or an unreadable image."""
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        raise DocumentExtractionError(
            detail="The Tesseract candidate adapter is not installed.",
            remediation="Install 'Pillow' and 'pytesseract' to run this candidate. Your file "
            "is unchanged.",
        ) from exc

    try:
        image = Image.open(source)
        image.load()
    except UnidentifiedImageError as exc:
        raise DocumentExtractionError(
            detail="Tesseract could not read this file as an image.",
            remediation="Upload a valid PNG or JPEG. Your file is unchanged.",
        ) from exc

    try:
        return _run_tesseract_on_image(image, cmd=cmd, languages=languages)
    finally:
        image.close()


def _read_pages_with_tesseract(
    source: BinaryIO,
    *,
    cmd: str | None,
    languages: str,
    scale: float,
) -> list[ImageWords]:
    """Rasterize a PDF locally, then OCR each page. Page images are closed deterministically."""
    images = rasterize_pdf(source, scale=scale)
    try:
        return [
            _run_tesseract_on_image(image, cmd=cmd, languages=languages) for image in images
        ]
    finally:
        for image in images:
            image.close()


def _lines_from_tsv_dict(data: dict[str, list[object]]) -> list[Word]:
    """Aggregate pytesseract word rows into one :class:`Word` per line (text unit = a line).

    Words are grouped by Tesseract's (block, paragraph, line) numbering, in row order; each
    line's text is the space-joined words, its box is the union of the word boxes, and its
    confidence is the mean of the words' confidences (a measured OCR value — never invented).
    Falls back to per-word blocks if the grouping columns are absent.
    """
    group_keys = ("block_num", "par_num", "line_num")
    if not all(key in data for key in group_keys):
        return _words_from_tsv_dict(data)

    words = _words_from_tsv_dict(data)
    rows = len(data["text"])
    lines: dict[tuple[int, int, int], list[Word]] = {}
    order: list[tuple[int, int, int]] = []
    for i in range(rows):
        word = words[i]
        if not word.text.strip() or word.conf < 0:
            continue  # skip non-words / empty cells, as the per-word mapping does
        try:
            key = (
                int(float(str(data["block_num"][i]))),
                int(float(str(data["par_num"][i]))),
                int(float(str(data["line_num"][i]))),
            )
        except (TypeError, ValueError) as exc:
            raise DocumentExtractionError(
                detail="Tesseract returned a malformed row.",
                remediation="This is an engine error; your file is unchanged. Try again.",
            ) from exc
        if key not in lines:
            lines[key] = []
            order.append(key)
        lines[key].append(word)

    result: list[Word] = []
    for key in order:
        members = lines[key]
        text = " ".join(w.text.strip() for w in members)
        left = min(w.left for w in members)
        top = min(w.top for w in members)
        right = max(w.left + w.width for w in members)
        bottom = max(w.top + w.height for w in members)
        mean_conf = sum(w.conf for w in members) / len(members)
        result.append(
            Word(text=text, conf=mean_conf, left=left, top=top,
                 width=right - left, height=bottom - top)
        )
    return result


def _words_from_tsv_dict(data: dict[str, list[object]]) -> list[Word]:
    """Convert pytesseract's ``image_to_data`` DICT into :class:`Word` rows.

    Kept separate (and free of any OCR import) so the parsing of Tesseract's tabular output
    is unit-testable with a hand-built dict.
    """
    required = ("text", "conf", "left", "top", "width", "height")
    if not all(key in data for key in required):
        raise DocumentExtractionError(
            detail="Tesseract returned an unexpected result shape.",
            remediation="This is an engine error; your file is unchanged. Try again.",
        )
    rows = len(data["text"])
    words: list[Word] = []
    for i in range(rows):
        try:
            words.append(
                Word(
                    text=str(data["text"][i]),
                    conf=float(str(data["conf"][i])),
                    left=int(float(str(data["left"][i]))),
                    top=int(float(str(data["top"][i]))),
                    width=int(float(str(data["width"][i]))),
                    height=int(float(str(data["height"][i]))),
                )
            )
        except (TypeError, ValueError) as exc:
            raise DocumentExtractionError(
                detail="Tesseract returned a malformed row.",
                remediation="This is an engine error; your file is unchanged. Try again.",
            ) from exc
    return words


class TesseractExtractor:
    """A ``DocumentExtractor`` (see the Protocol in ``app.services.extraction``) backed by
    Tesseract. Candidate for S-6 smoke testing only — not the selected production engine.
    """

    name = _ENGINE_NAME

    def __init__(
        self,
        *,
        tesseract_cmd: str | None = None,
        languages: str = "eng",
        pdf_scale: float = DEFAULT_SCALE,
        word_reader: WordReader | None = None,
        page_reader: PageReader | None = None,
    ) -> None:
        # ``word_reader`` / ``page_reader`` override the real Tesseract (and rasterizer) calls;
        # the harness/tests inject deterministic readers so the adapter runs without the
        # binary/renderer installed. An injected reader also marks the adapter "available".
        self._cmd = tesseract_cmd
        self._languages = languages
        self._pdf_scale = pdf_scale
        self._word_reader = word_reader
        self._page_reader = page_reader

    @property
    def version(self) -> str:
        if self._word_reader is not None or self._page_reader is not None:
            return "stub"
        try:
            import pytesseract

            return str(pytesseract.get_tesseract_version())
        except Exception:  # not installed / binary missing — the version is simply unknown
            return "unknown"

    def is_available(self) -> bool:
        if self._word_reader is not None or self._page_reader is not None:
            return True
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
        except Exception:
            return False
        return True

    def extract(self, source: BinaryIO, *, content_type: str) -> ExtractionResult:
        if content_type in _IMAGE_CONTENT_TYPES:
            read_image = self._word_reader or self._default_image_reader
            return result_from_words(
                read_image(source, content_type), engine_version=self.version
            )
        if content_type == _PDF_CONTENT_TYPE:
            read_pages = self._page_reader or self._default_pdf_reader
            return result_from_pages(read_pages(source), engine_version=self.version)
        raise DocumentExtractionError(
            detail="The Tesseract candidate adapter accepts images and PDFs only.",
            remediation="Provide a PNG, JPEG, TIFF, or PDF. Your file is unchanged.",
        )

    def _default_image_reader(self, source: BinaryIO, content_type: str) -> ImageWords:
        return _read_words_with_tesseract(
            source, content_type, cmd=self._cmd, languages=self._languages
        )

    def _default_pdf_reader(self, source: BinaryIO) -> list[ImageWords]:
        return _read_pages_with_tesseract(
            source, cmd=self._cmd, languages=self._languages, scale=self._pdf_scale
        )


def build_tesseract_extractor(settings: Settings) -> TesseractExtractor:
    """Construct the Tesseract candidate adapter for evaluation/dev use.

    ``settings`` is accepted to match the engine-builder shape (and to allow future
    engine configuration to be read from it); it selects nothing in production.
    """
    _ = settings
    return TesseractExtractor()
