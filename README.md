# Layer AI

Contract-first implementation of a single-image layer extraction and motion-ready asset packaging system.

## Development

- Install base dependencies: `uv sync --dev`
- Install OCR runtime for Phase 2 text extraction: `uv sync --dev --extra ocr`

## Run

- Start API: `uv run uvicorn apps.api.main:app --reload`
- Open docs: `http://127.0.0.1:8000/docs`

## Phase 4A Quality Outputs

Each completed job package now includes deterministic Phase 4A quality signals:

- `manifest/manifest.json`
  - `reconstruction_score`
  - `preview_diff_ratio`
  - final `status`
  - job-level `warnings`
- `logs/confidence_report.json`
  - `global_confidence`
  - `reconstruction_score`
  - `preview_diff_ratio`
  - `changed_pixels`
  - layer confidence summary
- `logs/job_report.json`
  - final status and reconstruction summary

These values are intended to help local testing stay honest:

- `completed_high_confidence` means no current Phase 4A warnings were triggered
- `completed_with_warnings` means the package was produced but quality guardrails fired
- `completed_low_confidence` means the package is available, but the extraction quality is too weak for a trustworthy automated handoff

Current warning examples:

- `possible_duplicate_layers`
- `background_cleanup_approximate`
- `low_text_confidence`
- `low_visual_confidence`
- `reconstruction_mismatch`

## Phase 4A Test Commands

- Run the focused Phase 4A integration tests: `uv run pytest tests/api/test_jobs.py -q`
- Run the Phase 4A unit tests:
  - `uv run pytest tests/fusion/test_engine.py -q`
  - `uv run pytest tests/background/test_cleanup.py -q`
  - `uv run pytest tests/preview/test_scoring.py -q`
  - `uv run pytest tests/quality/test_evaluator.py -q`
- Run the full suite: `uv run pytest -q`
- Run compile verification: `uv run python -m compileall apps packages tests`

## Phase 5 Renderer Handoff

Completed jobs can now generate a local renderer handoff payload for downstream motion tools.

API endpoints:

- `POST /v1/jobs/{job_id}/render/after-effects`
- `POST /v1/jobs/{job_id}/render/remotion`
- `POST /v1/jobs/{job_id}/render/{renderer_name}`

Renderer output paths:

- `renderers/after-effects/renderer_handoff.json`
- `renderers/remotion/renderer_handoff.json`

Each handoff payload includes:

- job metadata
- ordered layer references
- resolved asset paths
- warnings and confidence
- background and text metadata

CLI usage:

```bash
uv run python apps/worker/run_renderer.py --job-id job_000001 --renderer after-effects --storage-root artifacts
```

Phase 5 test commands:

- `uv run pytest tests/api/test_renderers.py -q`
- `uv run pytest tests/renderers/test_after_effects.py -q`
- `uv run pytest tests/renderers/test_registry.py -q`
