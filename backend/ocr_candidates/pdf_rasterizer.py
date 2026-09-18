"""Local PDF → page-image rasterization for the OCR candidate path (M21).

Tesseract reads images, not PDFs. To let the M20 candidate adapter process a PDF through the
SAME ``DocumentExtractor`` seam, this module renders each PDF page to an in-memory image. It is
strictly a rasterizer: it does NO OCR, no field interpretation, no record access, no DOM writes,
and no network I/O. It lives outside ``app`` (with the rest of the candidate code) and is
imported lazily, so a missing dependency is an honest extraction failure, not an import crash.

Renderer: **pypdfium2** (bundles Google's PDFium) — a self-contained pip wheel with no system
binary and a permissive licence. It is a candidate/evaluation dependency, installed out-of-band
and never declared in the production manifest (see ``SPRINT_4_M21_PDF_RASTERIZATION.md`` §
"Dependency decision"). Rendering is fully local.

Cleanup is deterministic: the PDFium document and every page handle are closed in ``finally``
blocks even when a page fails to render. Rendered images are returned in memory (nothing is
written to disk), so there are no temporary files to leak; the caller owns and closes the images.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO

from app.core.errors import DocumentExtractionError

if TYPE_CHECKING:
    from PIL.Image import Image

# Rendering scale (PDF points → pixels). ~2.0 gives roughly 144 DPI, enough for OCR of rendered
# text without huge bitmaps. It is a knob, not a requirement value.
DEFAULT_SCALE = 2.0


def rasterize_pdf(source: BinaryIO, *, scale: float = DEFAULT_SCALE) -> list[Image]:
    """Render every page of a PDF to an in-memory RGB image, in page order.

    The original bytes are only read, never modified. On any failure — missing renderer,
    empty/malformed/encrypted PDF, or a page that will not render — this raises
    :class:`DocumentExtractionError`; it never returns a partial or empty-but-"successful"
    result. No PDF content is placed in the error message (NFR-ERR-004).
    """
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise DocumentExtractionError(
            detail="The PDF rasterizer for the OCR candidate is not installed.",
            remediation="Install 'pypdfium2' to process PDFs with this candidate. Your file "
            "is unchanged.",
        ) from exc

    data = source.read()
    if not data:
        raise DocumentExtractionError(
            detail="The PDF is empty.",
            remediation="Provide a PDF with at least one page. Your file is unchanged.",
        )

    try:
        document = pdfium.PdfDocument(data)
    except Exception as exc:  # malformed, encrypted, or unsupported — one honest failure
        raise DocumentExtractionError(
            detail="The PDF could not be opened for rasterization.",
            remediation="It may be corrupt, encrypted, or an unsupported PDF. Your file is "
            "unchanged.",
        ) from exc

    images: list[Image] = []
    try:
        page_count = len(document)
        if page_count == 0:
            raise DocumentExtractionError(
                detail="The PDF has no pages.",
                remediation="Provide a PDF with at least one page. Your file is unchanged.",
            )
        for index in range(page_count):
            page = document[index]
            try:
                images.append(page.render(scale=scale).to_pil().convert("RGB"))
            finally:
                page.close()
    except DocumentExtractionError:
        for image in images:
            image.close()
        raise
    except Exception as exc:  # a page that will not render — do not proceed on partial output
        for image in images:
            image.close()
        raise DocumentExtractionError(
            detail="A PDF page could not be rasterized.",
            remediation="The PDF may use unsupported features. Your file is unchanged.",
        ) from exc
    finally:
        document.close()

    return images
