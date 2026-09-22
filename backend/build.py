"""Vercel build step for the Tesseract DEMO (runs via ``[tool.vercel.scripts] build``).

This provisions the Tesseract candidate's runtime into the function bundle so the DEMO opt-in
(``DOCURA_OCR_ENGINE=tesseract``) can run real OCR on the serverless host. It does two things,
both DEMO-scoped and both kept OUT of ``pyproject.toml`` on purpose:

1. Installs the candidate's Python deps (pytesseract, Pillow, pypdfium2) into ``vendor/pydeps``.
   ``tests/test_extraction.py`` forbids declaring an OCR engine as a project dependency, so they
   are installed imperatively here and added to ``sys.path`` by ``ocr_candidates/__init__.py``.
2. Downloads a prebuilt Tesseract 5 runtime built FOR Amazon Linux 2023 x86_64 — the same OS
   family as the Vercel build image and Python runtime — and lays out ``vendor/tesseract/`` as
   ``bin/tesseract`` + ``lib/*.so*`` + ``tesseract/share/tessdata/eng.traineddata``. The adapter
   discovers these absolute paths at runtime (never PATH) and puts ``lib`` on LD_LIBRARY_PATH.

Nothing here selects Tesseract for production: the default engine stays unconfigured, and the
binary is inert unless ``DOCURA_OCR_ENGINE=tesseract`` is set. Fails loudly — a broken bundle
must fail the build, not silently degrade to "no OCR".
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

# Pinned AL2023 x86_64 Tesseract 5.4.0 layer (bin + shared libs + tessdata). Amazon Linux 2023
# matches Vercel's Python runtime, so this binary's glibc/ABI is compatible.
_TESSERACT_URL = (
    "https://github.com/bweigel/aws-lambda-tesseract-layer/releases/download/"
    "v5.4.0/tesseract-al2023-x86.zip"
)
_PYDEPS = ("pytesseract==0.3.13", "pillow==11.3.0", "pypdfium2==4.30.0")

_HERE = Path(__file__).resolve().parent
_VENDOR = _HERE / "vendor"
_TESS_DIR = _VENDOR / "tesseract"
_PYDEPS_DIR = _VENDOR / "pydeps"

# Only these members are needed for eng OCR of images and rasterized PDFs; osd/deu are dropped
# to keep the bundle lean. ``lib/`` (all shared objects) is taken wholesale.
_WANTED_PREFIXES = ("bin/tesseract", "lib/", "tesseract/share/tessdata/eng.traineddata")


def _install_pydeps() -> None:
    _PYDEPS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[build] installing OCR deps into {_PYDEPS_DIR}: {', '.join(_PYDEPS)}", flush=True)
    subprocess.run(  # noqa: S603 - fixed, trusted args
        [sys.executable, "-m", "pip", "install", "--target", str(_PYDEPS_DIR), *_PYDEPS],
        check=True,
    )


def _fetch_tesseract() -> None:
    binary = _TESS_DIR / "bin" / "tesseract"
    if binary.is_file():
        print("[build] tesseract runtime already present; skipping download", flush=True)
        return
    _TESS_DIR.mkdir(parents=True, exist_ok=True)
    archive = _VENDOR / "tesseract-al2023.zip"
    print(f"[build] downloading Tesseract runtime: {_TESSERACT_URL}", flush=True)
    urllib.request.urlretrieve(_TESSERACT_URL, archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    print(f"[build] downloaded {archive.stat().st_size} bytes sha256={digest}", flush=True)

    with zipfile.ZipFile(archive) as zf:
        for member in zf.namelist():
            if member.endswith("/"):
                continue
            if not member.startswith(_WANTED_PREFIXES):
                continue
            target = _TESS_DIR / member
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, open(target, "wb") as dst:
                dst.write(src.read())
    archive.unlink(missing_ok=True)

    if not binary.is_file():
        msg = "Tesseract binary missing after extraction — the DEMO bundle is broken."
        raise RuntimeError(msg)
    # The binary and shared objects must be executable/loadable at runtime.
    binary.chmod(0o755)
    for so in (_TESS_DIR / "lib").glob("*"):
        so.chmod(0o755)
    tessdata = _TESS_DIR / "tesseract" / "share" / "tessdata" / "eng.traineddata"
    if not tessdata.is_file():
        msg = "eng.traineddata missing after extraction — the DEMO bundle is broken."
        raise RuntimeError(msg)
    print(f"[build] tesseract runtime ready at {_TESS_DIR}", flush=True)


def main() -> None:
    _install_pydeps()
    _fetch_tesseract()
    print("[build] Tesseract DEMO bundle complete.", flush=True)


if __name__ == "__main__":
    main()
