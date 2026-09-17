"""S-6 OCR corpus and evaluation infrastructure (M19).

This package is EVALUATION infrastructure, not production runtime. It is never imported by
``app.main`` and it changes no production behaviour: production extraction stays on the
unconfigured extractor (the plug point in ``app.services.extraction``) until an approved S-6
corpus exists, the evaluation is run, an engine is selected on evidence, and governance permits
implementation (D-02 / M14 / G-02).

It reuses the existing extractor seam (``app.services.extraction``) and the D-02/M14
methodology and terminology. It selects NO OCR engine, installs none, and fabricates no
evaluation evidence. See ``backend/docs/SPRINT_4_M19_S6_CORPUS_AND_EVALUATION.md``.
"""
