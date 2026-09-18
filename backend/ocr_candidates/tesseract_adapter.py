"""Tesseract candidate adapter (M20) — technical smoke testing only, NOT production.

Tesseract is candidate #1 in the M14 list (``app.evaluation.engines.CANDIDATE_ENGINES``):
self-hosted, offline, Apache-2.0, word-level boxes + confidence — the lightest engine
that satisfies the seam's needs. **This adapter selects nothing.** Production still runs
the unconfigured extractor; engine selection stays blocked on the S-6 held-out evaluation
(D-02 / AR-AST-008 / M14). See ``backend/docs/SPRINT_4_M20_OCR_CANDIDATE_ADAPTER.md``.

Design:

* The only place ``pytesseract``/``Pillow`` are imported is :func:`_read_words_with_tesseract`,
  and the import is lazy so a missing dependency becomes an honest extraction failure rather
  than an import-time crash. No engine knowledge leaks anywhere else.
* :func:`result_from_words` is a PURE mapping (engine word boxes → the seam's
  ``ExtractionResult``) with no OCR dependency, so the contract is testable without the
  binary installed.
* The engine runs locally as a subprocess of Tesseract. It makes no network calls, and no
  document text is logged.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, BinaryIO, NamedTuple

from app.core.errors import DocumentExtractionError
from app.services.extraction import (
    ExtractedPage,
    ExtractionResult,
    TextBlock,
    TextRegion,
)

if TYPE_CHECKING:
    from app.core.config import Settings

# Content types Tesseract can read directly. PDF is deliberately excluded: Tesseract does
# not rasterize PDFs, so supporting them would mean pulling in poppler/pdf2image — another
# system dependency and out of scope for a smoke adapter (M20 §4). A PDF is an honest
# extraction failure here, not a silently empty result.
_SUPPORTED_CONTENT_TYPES = frozenset({"image/png", "image/jpeg", "image/jpg", "image/tiff"})

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


# A reader turns a document stream into words + image size. The real one shells out to
# Tesseract; tests inject a deterministic fake so the adapter is exercisable without the
# binary. This is a narrow test/rasterizer seam, not a second extraction abstraction.
WordReader = Callable[[BinaryIO, str], ImageWords]


def _fraction(value: int, extent: int) -> float:
    """Pixel coordinate → page-relative fraction, clamped into [0, 1]."""
    if extent <= 0:
        return 0.0
    return min(max(value / extent, 0.0), 1.0)


def result_from_words(
    read: ImageWords,
    *,
    engine_version: str,
    page_number: int = 1,
) -> ExtractionResult:
    """Map engine word boxes to the seam's ``ExtractionResult`` (pure, no OCR dependency).

    Words with empty text or a negative confidence (Tesseract's marker for a non-word
    region) are dropped. Boxes are converted from pixels to page-relative fractions so no
    engine's pixel units leak past the boundary (see ``TextRegion``).
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

    page = ExtractedPage(number=page_number, text=" ".join(texts), blocks=tuple(blocks))
    return ExtractionResult(
        pages=(page,),
        engine=_ENGINE_NAME,
        engine_version=engine_version,
        metadata={"word_count": str(len(blocks))},
    )


def _read_words_with_tesseract(
    source: BinaryIO,
    content_type: str,
    *,
    cmd: str | None,
    languages: str,
) -> ImageWords:
    """Run Tesseract locally on one image. The ONLY place pytesseract/Pillow is imported.

    Any missing dependency, unreadable image, or engine error is converted to
    :class:`DocumentExtractionError` — the seam's honest-failure contract (FR-OCR-009,
    BR-016). It never returns an empty-but-successful result.
    """
    try:
        import pytesseract
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:  # dependency not installed — honest failure
        raise DocumentExtractionError(
            detail="The Tesseract candidate adapter is not installed.",
            remediation="Install 'pytesseract' and 'Pillow' and the Tesseract binary to "
            "run this candidate. Your file is unchanged.",
        ) from exc

    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd

    try:
        image = Image.open(source)
        image.load()
        width, height = image.size
        data = pytesseract.image_to_data(
            image, lang=languages, output_type=pytesseract.Output.DICT
        )
    except UnidentifiedImageError as exc:
        raise DocumentExtractionError(
            detail="Tesseract could not read this file as an image.",
            remediation="Upload a valid PNG or JPEG. Your file is unchanged.",
        ) from exc
    except Exception as exc:  # pytesseract raises many engine-specific errors; treat as one
        # No document content or engine internals are put in the message (NFR-ERR-004).
        raise DocumentExtractionError from exc

    words = _words_from_tsv_dict(data)
    return ImageWords(words=words, image_width=width, image_height=height)


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
        word_reader: WordReader | None = None,
    ) -> None:
        # ``word_reader`` overrides the real Tesseract call; the harness/tests inject a
        # deterministic reader so the adapter runs without the binary installed.
        self._cmd = tesseract_cmd
        self._languages = languages
        self._reader = word_reader

    @property
    def version(self) -> str:
        if self._reader is not None:
            return "stub"
        try:
            import pytesseract

            return str(pytesseract.get_tesseract_version())
        except Exception:  # not installed / binary missing — the version is simply unknown
            return "unknown"

    def is_available(self) -> bool:
        if self._reader is not None:
            return True
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
        except Exception:
            return False
        return True

    def extract(self, source: BinaryIO, *, content_type: str) -> ExtractionResult:
        if content_type not in _SUPPORTED_CONTENT_TYPES:
            raise DocumentExtractionError(
                detail="The Tesseract candidate adapter reads images only.",
                remediation="Provide a PNG or JPEG image. PDF is not supported by this "
                "candidate. Your file is unchanged.",
            )
        reader = self._reader or self._default_reader
        read = reader(source, content_type)
        return result_from_words(read, engine_version=self.version)

    def _default_reader(self, source: BinaryIO, content_type: str) -> ImageWords:
        return _read_words_with_tesseract(
            source, content_type, cmd=self._cmd, languages=self._languages
        )


def build_tesseract_extractor(settings: Settings) -> TesseractExtractor:
    """Construct the Tesseract candidate adapter for evaluation/dev use.

    ``settings`` is accepted to match the engine-builder shape (and to allow future
    engine configuration to be read from it); it selects nothing in production.
    """
    _ = settings
    return TesseractExtractor()
