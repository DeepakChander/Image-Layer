# Layer AI

Contract-first implementation of a single-image layer extraction and motion-ready asset packaging system.

## Development

- Install base dependencies: `uv sync --dev`
- Install OCR runtime for Phase 2 text extraction: `uv sync --dev --extra ocr`

## Run

- Start API: `uv run uvicorn apps.api.main:app --reload`
- Open docs: `http://127.0.0.1:8000/docs`
