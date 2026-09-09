"""Sprint 4 D-01 — the extraction boundary, before any engine exists behind it.

These tests are about *substitutability*, not about OCR. Nothing here asserts that
a document was read correctly, because no engine is configured and AR-AST-008
requires an evaluation against a held-out corpus before any claim of that kind can
be made. What is tested is the part that must be right before an engine is chosen:
that the interface can be injected, that the placeholder refuses honestly instead of
returning something plausible, that the result type is engine-neutral, and that no
concrete OCR provider has crept into the application.
"""

from __future__ import annotations

import io
import re
import tomllib
from pathlib import Path
from typing import Any, BinaryIO, cast

import pytest

from app.api.deps import get_document_extractor
from app.core.config import Settings
from app.core.errors import DocumentExtractionError, ExtractionNotConfiguredError
from app.services.extraction import (
    DocumentExtractor,
    ExtractedPage,
    ExtractionResult,
    TextBlock,
    TextRegion,
    UnconfiguredExtractor,
    build_document_extractor,
)

BACKEND_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = BACKEND_ROOT / "app"


class ExplodingStream(io.RawIOBase):
    """A stream that fails if anything reads it.

    The placeholder must not touch document bytes: it has nothing to do with them,
    and a component that reads a file it cannot process is one that could log or
    leak its contents.
    """

    def readable(self) -> bool:
        return True

    def readinto(self, _buffer: Any) -> int:
        raise AssertionError("the unconfigured extractor must not read document bytes")

    def read(self, _size: int = -1) -> bytes:
        raise AssertionError("the unconfigured extractor must not read document bytes")


class RecordingExtractor:
    """A stand-in engine, used only to prove the boundary is substitutable.

    It returns a fixed, obviously synthetic result. That is a statement about wiring
    and nothing else — it is not evidence about extraction quality, and no test here
    treats it as such.
    """

    name = "recording-test-double"
    version = "0"

    def __init__(self) -> None:
        self.calls: list[str] = []

    def is_available(self) -> bool:
        return True

    def extract(self, source: Any, *, content_type: str) -> ExtractionResult:
        self.calls.append(content_type)
        return ExtractionResult(
            pages=(ExtractedPage(number=1, text="test double"),),
            engine=self.name,
            engine_version=self.version,
        )


class TestResultStructure:
    """The result type is engine-neutral: text, pages, regions, confidence, metadata."""

    def test_a_result_carries_text_pages_and_the_engine_that_produced_it(self) -> None:
        result = ExtractionResult(
            pages=(
                ExtractedPage(number=1, text="first"),
                ExtractedPage(number=2, text="second"),
            ),
            engine="stub",
            engine_version="1.2.3",
        )

        assert result.page_count == 2
        assert result.text == "first\nsecond"
        assert result.engine == "stub"
        assert result.engine_version == "1.2.3"
        assert result.metadata == {}

    def test_a_result_must_name_its_engine(self) -> None:
        """AR-AST-008 evidence is about a specific component, so results say which."""
        with pytest.raises(ValueError, match="name the engine"):
            ExtractionResult(pages=(), engine="", engine_version="1")

    def test_pages_must_be_ordered(self) -> None:
        """FR-OCR-008: a multi-page document is one document, in page order."""
        with pytest.raises(ValueError, match="strictly increasing"):
            ExtractionResult(
                pages=(
                    ExtractedPage(number=2, text="second"),
                    ExtractedPage(number=1, text="first"),
                ),
                engine="stub",
                engine_version="1",
            )

    def test_page_numbers_are_one_based(self) -> None:
        with pytest.raises(ValueError, match="1-based"):
            ExtractedPage(number=0, text="")

    def test_a_block_carries_its_region_and_confidence(self) -> None:
        """FR-OCR-007 and FR-OCR-005: provenance and confidence survive the boundary."""
        block = TextBlock(
            text="12/03/2004",
            region=TextRegion(page=1, x=0.1, y=0.2, width=0.3, height=0.05),
            confidence=0.87,
        )

        assert block.region is not None
        assert block.region.page == 1
        assert block.confidence == 0.87

    def test_a_missing_confidence_is_none_and_not_a_number(self) -> None:
        """None means "the engine reported none" — a different fact from a low value."""
        assert TextBlock(text="unmeasured").confidence is None

    @pytest.mark.parametrize("confidence", [-0.1, 1.1])
    def test_a_confidence_outside_zero_to_one_is_rejected(self, confidence: float) -> None:
        with pytest.raises(ValueError, match="confidence"):
            TextBlock(text="x", confidence=confidence)

    @pytest.mark.parametrize(
        ("kwargs", "message"),
        [
            ({"page": 0, "x": 0.0, "y": 0.0, "width": 0.5, "height": 0.5}, "1-based"),
            ({"page": 1, "x": -0.1, "y": 0.0, "width": 0.5, "height": 0.5}, "fraction"),
            ({"page": 1, "x": 0.0, "y": 0.0, "width": 0.0, "height": 0.5}, "width"),
            ({"page": 1, "x": 0.0, "y": 0.0, "width": 0.5, "height": 0.0}, "height"),
            ({"page": 1, "x": 0.8, "y": 0.0, "width": 0.5, "height": 0.5}, "right edge"),
            ({"page": 1, "x": 0.0, "y": 0.8, "width": 0.5, "height": 0.5}, "bottom edge"),
        ],
    )
    def test_an_impossible_region_is_rejected(self, kwargs: dict[str, Any], message: str) -> None:
        """Regions are page-relative fractions, so an engine's pixels cannot leak in."""
        with pytest.raises(ValueError, match=message):
            TextRegion(**kwargs)

    def test_a_block_may_not_claim_a_region_on_another_page(self) -> None:
        with pytest.raises(ValueError, match="names page"):
            ExtractedPage(
                number=1,
                text="x",
                blocks=(
                    TextBlock(
                        text="x",
                        region=TextRegion(page=2, x=0.0, y=0.0, width=0.1, height=0.1),
                    ),
                ),
            )

    def test_results_are_immutable(self) -> None:
        """A later component may not edit an extraction after the fact (AR-AST-007)."""
        result = ExtractionResult(pages=(), engine="stub", engine_version="1")

        with pytest.raises(AttributeError):
            result.engine = "something-else"  # type: ignore[misc]


class TestUnconfiguredExtractor:
    """The placeholder says the engine is missing. It never pretends otherwise."""

    def test_it_reports_that_it_cannot_work(self) -> None:
        assert UnconfiguredExtractor().is_available() is False

    def test_extraction_fails_with_a_reason_naming_the_missing_engine(self) -> None:
        with pytest.raises(ExtractionNotConfiguredError) as raised:
            UnconfiguredExtractor().extract(io.BytesIO(b"%PDF-1.7"), content_type="application/pdf")

        assert "no extraction engine is configured" in raised.value.detail.lower()
        # NFR-ERR-001: an error says what the user can do next, and here that
        # includes the assurance FR-OCR-009 requires — the original is untouched.
        assert raised.value.remediation

    def test_the_failure_is_an_extraction_failure(self) -> None:
        """So the eventual pipeline can catch one class for every FR-OCR-009 path."""
        assert issubclass(ExtractionNotConfiguredError, DocumentExtractionError)

    def test_it_returns_no_result_at_all(self) -> None:
        """Empty text would be indistinguishable from an unreadable document."""
        with pytest.raises(ExtractionNotConfiguredError):
            UnconfiguredExtractor().extract(io.BytesIO(b""), content_type="image/png")

    def test_it_does_not_read_the_document(self) -> None:
        with pytest.raises(ExtractionNotConfiguredError):
            UnconfiguredExtractor().extract(
                cast(BinaryIO, ExplodingStream()), content_type="application/pdf"
            )


class TestTheBoundaryIsInjectable:
    def test_the_builder_returns_something_satisfying_the_interface(
        self, settings: Settings
    ) -> None:
        extractor = build_document_extractor(settings)

        assert isinstance(extractor, DocumentExtractor)
        assert extractor.is_available() is False

    def test_the_application_installs_an_extractor_on_its_state(self, settings: Settings) -> None:
        from app.main import create_app

        app = create_app(settings)

        assert isinstance(app.state.document_extractor, DocumentExtractor)

    async def test_the_dependency_resolves_the_installed_extractor(
        self, settings: Settings
    ) -> None:
        from app.main import create_app

        app = create_app(settings)
        request = type("_Request", (), {"app": app})()

        resolved = await get_document_extractor(request)

        assert resolved is app.state.document_extractor

    async def test_a_substitute_engine_can_be_installed_without_touching_callers(
        self, settings: Settings
    ) -> None:
        """The point of D-01: the engine is replaced here and nowhere else."""
        from app.main import create_app

        app = create_app(settings)
        double = RecordingExtractor()
        app.state.document_extractor = double
        request = type("_Request", (), {"app": app})()

        resolved = await get_document_extractor(request)
        result = resolved.extract(io.BytesIO(b"%PDF-1.7"), content_type="application/pdf")

        assert resolved is double
        assert double.calls == ["application/pdf"]
        assert result.engine == "recording-test-double"


class TestNoConcreteOcrProvider:
    """D-01 chose an architecture, not an engine. Nothing may have chosen one for us."""

    # Engines and hosted providers that would make the choice for us if imported.
    FORBIDDEN = (
        "pytesseract",
        "tesserocr",
        "paddleocr",
        "paddle",
        "easyocr",
        "doctr",
        "rapidocr",
        "surya",
        "kraken",
        "ocrmypdf",
        "openai",
        "anthropic",
        "boto3",
        "botocore",
        "azure",
        "transformers",
        "torch",
    )

    def test_no_ocr_engine_is_declared_as_a_dependency(self) -> None:
        content = (BACKEND_ROOT / "pyproject.toml").read_bytes()
        project = tomllib.loads(content.decode("utf-8"))["project"]

        declared = list(project["dependencies"])
        for extras in project.get("optional-dependencies", {}).values():
            declared.extend(extras)

        names = {re.split(r"[<>=!\[; ]", item, maxsplit=1)[0].strip().lower() for item in declared}
        assert names.isdisjoint(self.FORBIDDEN)
        # google-cloud-vision and friends are not caught by an exact match.
        assert not [name for name in names if name.startswith(("google-", "google."))]

    def test_no_module_in_the_application_imports_an_ocr_provider(self) -> None:
        pattern = re.compile(
            r"^\s*(?:from|import)\s+(" + "|".join(self.FORBIDDEN) + r"|google\.\w+)\b",
            re.MULTILINE,
        )

        offenders = [
            path.relative_to(BACKEND_ROOT).as_posix()
            for path in APP_ROOT.rglob("*.py")
            if pattern.search(path.read_text(encoding="utf-8"))
        ]

        assert offenders == []

    def test_only_the_extraction_module_may_know_about_engines(self) -> None:
        """Every other module depends on the interface, never on an implementation."""
        importers = [
            path.relative_to(BACKEND_ROOT).as_posix()
            for path in APP_ROOT.rglob("*.py")
            if "UnconfiguredExtractor" in path.read_text(encoding="utf-8")
        ]

        assert importers == ["app/services/extraction.py"]
