# Phase 4A Fusion, Background, Preview, and Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build deterministic Phase 4A reliability improvements that fuse text and visual candidates, produce a cleaner background plate, score reconstruction quality, and emit honest warnings and status values without adding heavy model dependencies.

**Architecture:** Add focused modules for fusion, background cleanup, preview scoring, and quality evaluation, then connect them through a thin `packages/layer_ai/pipeline/phase4.py` orchestrator. Keep `packages/layer_ai/storage/local.py` responsible for package writing, while the new pipeline returns fused candidates, background artifacts, preview artifacts, confidence data, and warnings for export.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, Pillow, pytest, jsonschema

---

## File Map

### New files

- `packages/layer_ai/fusion/__init__.py`
- `packages/layer_ai/fusion/models.py`
- `packages/layer_ai/fusion/engine.py`
- `packages/layer_ai/background/__init__.py`
- `packages/layer_ai/background/cleanup.py`
- `packages/layer_ai/preview/__init__.py`
- `packages/layer_ai/preview/scoring.py`
- `packages/layer_ai/quality/__init__.py`
- `packages/layer_ai/quality/evaluator.py`
- `packages/layer_ai/pipeline/__init__.py`
- `packages/layer_ai/pipeline/phase4.py`
- `tests/fusion/test_engine.py`
- `tests/background/test_cleanup.py`
- `tests/preview/test_scoring.py`
- `tests/quality/test_evaluator.py`

### Existing files to modify

- `packages/layer_ai/contracts/models.py`
- `packages/layer_ai/contracts/examples.py`
- `packages/layer_ai/contracts/schemas/manifest.schema.json`
- `packages/layer_ai/storage/local.py`
- `tests/contracts/test_schemas.py`
- `tests/api/test_jobs.py`
- `README.md`

## Task 1: Extend Contracts for Phase 4A Quality Data

**Files:**
- Create: none
- Modify: `packages/layer_ai/contracts/models.py`
- Modify: `packages/layer_ai/contracts/examples.py`
- Modify: `packages/layer_ai/contracts/schemas/manifest.schema.json`
- Test: `tests/contracts/test_schemas.py`

- [ ] **Step 1: Write the failing contract tests**

Add tests that require the manifest example to support Phase 4A fields such as:
- `reconstruction_score`
- `preview_diff_ratio`
- richer warnings while preserving existing compatibility

- [ ] **Step 2: Run the contract test to verify it fails**

Run: `uv run pytest tests/contracts/test_schemas.py -q`
Expected: FAIL because the schema and examples do not yet include the new fields.

- [ ] **Step 3: Write the minimal contract changes**

Update the Pydantic models and schema so the manifest can safely carry:

```python
class SceneManifest(BaseModel):
    package_version: str
    schema_version: str
    job_id: str
    route: str
    status: str
    global_confidence: float
    reconstruction_score: float | None = None
    preview_diff_ratio: float | None = None
    warnings: list[str] = Field(default_factory=list)
    canvas: Canvas
    layers: list[LayerEntry]
```

- [ ] **Step 4: Run the contract test to verify it passes**

Run: `uv run pytest tests/contracts/test_schemas.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/layer_ai/contracts/models.py packages/layer_ai/contracts/examples.py packages/layer_ai/contracts/schemas/manifest.schema.json tests/contracts/test_schemas.py
git commit -m "feat: extend manifest contract for phase 4 quality data"
```

## Task 2: Add Fusion Engine

**Files:**
- Create: `packages/layer_ai/fusion/__init__.py`
- Create: `packages/layer_ai/fusion/models.py`
- Create: `packages/layer_ai/fusion/engine.py`
- Test: `tests/fusion/test_engine.py`

- [ ] **Step 1: Write the failing fusion tests**

Cover:
- text layers win over overlapping visual layers
- near-duplicate visual candidates are collapsed
- deterministic z-order is preserved

Example test shape:

```python
def test_fusion_prefers_text_over_overlapping_visual():
    fused = FusionEngine().fuse(text_layers=[text_layer], visual_layers=[visual_layer])
    assert [layer.kind for layer in fused.layers] == ["background", "text"]
    assert "possible_duplicate_layers" not in fused.warnings
```

- [ ] **Step 2: Run the fusion tests to verify they fail**

Run: `uv run pytest tests/fusion/test_engine.py -q`
Expected: FAIL because the fusion engine does not exist yet.

- [ ] **Step 3: Implement the minimal fusion engine**

Add small normalized models and a deterministic engine:

```python
class FusionResult(BaseModel):
    layers: list[dict]
    warnings: list[str] = Field(default_factory=list)


class FusionEngine:
    def fuse(self, text_layers: list[dict], visual_layers: list[dict]) -> FusionResult:
        # drop overlapping visuals when text owns the region
        # dedupe visuals by IoU and type
        # return stable layer ordering
```

- [ ] **Step 4: Run the fusion tests to verify they pass**

Run: `uv run pytest tests/fusion/test_engine.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/layer_ai/fusion tests/fusion/test_engine.py
git commit -m "feat: add deterministic fusion engine"
```

## Task 3: Add Background Cleanup Module

**Files:**
- Create: `packages/layer_ai/background/__init__.py`
- Create: `packages/layer_ai/background/cleanup.py`
- Test: `tests/background/test_cleanup.py`

- [ ] **Step 1: Write the failing background cleanup tests**

Cover:
- cleanup fills removed regions deterministically
- cleanup output keeps image size unchanged
- cleanup can flag approximate cleanup when many removed regions exist

Example:

```python
def test_cleanup_fills_removed_region_with_local_color():
    result = BackgroundCleaner().clean(image, removals=[bbox])
    assert result.image.size == image.size
    assert result.image.crop((x1, y1, x2, y2)).tobytes() != image.crop((x1, y1, x2, y2)).tobytes()
```

- [ ] **Step 2: Run the cleanup tests to verify they fail**

Run: `uv run pytest tests/background/test_cleanup.py -q`
Expected: FAIL because the background cleanup module does not exist yet.

- [ ] **Step 3: Implement the minimal background cleaner**

Add a deterministic cleaner:

```python
class BackgroundCleanupResult(BaseModel):
    image: Image.Image
    warnings: list[str] = Field(default_factory=list)


class BackgroundCleaner:
    def clean(self, image: Image.Image, removals: list[BoundingBox]) -> BackgroundCleanupResult:
        # fill with local edge color
        # optionally apply a tiny blur/smooth pass
        # emit background_cleanup_approximate when coverage is high
```

- [ ] **Step 4: Run the cleanup tests to verify they pass**

Run: `uv run pytest tests/background/test_cleanup.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/layer_ai/background tests/background/test_cleanup.py
git commit -m "feat: add deterministic background cleanup"
```

## Task 4: Add Preview Scoring Module

**Files:**
- Create: `packages/layer_ai/preview/__init__.py`
- Create: `packages/layer_ai/preview/scoring.py`
- Test: `tests/preview/test_scoring.py`

- [ ] **Step 1: Write the failing preview tests**

Cover:
- perfect reconstruction yields near-1 score
- obvious mismatch yields lower score
- diff ratio is exposed for later warning logic

Example:

```python
def test_preview_scoring_returns_perfect_score_for_identical_images():
    result = PreviewScorer().score(original, reconstructed)
    assert result.reconstruction_score == 1.0
    assert result.preview_diff_ratio == 0.0
```

- [ ] **Step 2: Run the preview tests to verify they fail**

Run: `uv run pytest tests/preview/test_scoring.py -q`
Expected: FAIL because the preview scorer does not exist yet.

- [ ] **Step 3: Implement the minimal preview scorer**

```python
class PreviewScore(BaseModel):
    reconstruction_score: float
    preview_diff_ratio: float
    changed_pixels: int


class PreviewScorer:
    def score(self, original: Image.Image, reconstructed: Image.Image) -> PreviewScore:
        # pixel diff ratio
        # normalized score = 1.0 - diff_ratio
```

- [ ] **Step 4: Run the preview tests to verify they pass**

Run: `uv run pytest tests/preview/test_scoring.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/layer_ai/preview tests/preview/test_scoring.py
git commit -m "feat: add reconstruction preview scoring"
```

## Task 5: Add Quality Evaluator

**Files:**
- Create: `packages/layer_ai/quality/__init__.py`
- Create: `packages/layer_ai/quality/evaluator.py`
- Test: `tests/quality/test_evaluator.py`

- [ ] **Step 1: Write the failing quality tests**

Cover:
- low text confidence produces warning
- low visual confidence produces warning
- poor reconstruction score downgrades final status
- duplicate warning penalizes global confidence

Example:

```python
def test_quality_marks_job_low_confidence_when_reconstruction_is_poor():
    result = QualityEvaluator().evaluate(layer_confidences=[0.95, 0.92], reconstruction_score=0.42, warnings=[])
    assert result.status == "completed_low_confidence"
    assert "reconstruction_mismatch" in result.warnings
```

- [ ] **Step 2: Run the quality tests to verify they fail**

Run: `uv run pytest tests/quality/test_evaluator.py -q`
Expected: FAIL because the quality evaluator does not exist yet.

- [ ] **Step 3: Implement the minimal quality evaluator**

```python
class QualityResult(BaseModel):
    status: str
    global_confidence: float
    warnings: list[str]


class QualityEvaluator:
    def evaluate(self, layer_confidences: list[float], reconstruction_score: float, warnings: list[str]) -> QualityResult:
        # start from minimum layer confidence
        # apply penalties
        # derive final warnings and status
```

- [ ] **Step 4: Run the quality tests to verify they pass**

Run: `uv run pytest tests/quality/test_evaluator.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/layer_ai/quality tests/quality/test_evaluator.py
git commit -m "feat: add phase 4 quality evaluator"
```

## Task 6: Add Phase 4 Orchestrator

**Files:**
- Create: `packages/layer_ai/pipeline/__init__.py`
- Create: `packages/layer_ai/pipeline/phase4.py`
- Modify: `packages/layer_ai/storage/local.py`
- Test: `tests/api/test_jobs.py`

- [ ] **Step 1: Write the failing integration tests**

Extend API tests to require:
- duplicate candidates collapse into one exported layer
- low reconstruction score produces `reconstruction_mismatch`
- manifest includes `reconstruction_score` and `preview_diff_ratio`
- logs expose the same quality metrics

- [ ] **Step 2: Run the targeted API tests to verify they fail**

Run: `uv run pytest tests/api/test_jobs.py -q`
Expected: FAIL because the Phase 4 orchestrator and new fields are not wired in.

- [ ] **Step 3: Implement the orchestrator and storage integration**

Use a thin pipeline object:

```python
class Phase4Pipeline:
    def run(self, image, text_candidates, visual_candidates):
        fused = self.fusion.fuse(...)
        background = self.background.clean(...)
        preview = self.preview.score(original=image, reconstructed=reconstructed)
        quality = self.quality.evaluate(...)
        return Phase4Artifacts(...)
```

Update `LocalArtifactStore.build_package(...)` so it:
- exports fused layers instead of raw extractor output
- writes cleaned background output
- saves preview metrics into the manifest and confidence log
- uses quality results for final status and warnings

- [ ] **Step 4: Run the targeted API tests to verify they pass**

Run: `uv run pytest tests/api/test_jobs.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/layer_ai/pipeline packages/layer_ai/storage/local.py tests/api/test_jobs.py
git commit -m "feat: integrate phase 4 fusion and quality pipeline"
```

## Task 7: Update README and Developer Notes

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write the failing docs expectation**

Add a short checklist to the current task notes or TODO list:
- Phase 4 preview metrics must be documented
- warnings and status behavior must be described for local testing

- [ ] **Step 2: Update README**

Document:
- that preview quality metrics now exist
- where to find `reconstruction_score` and `preview_diff_ratio`
- how to run the Phase 4A relevant tests

- [ ] **Step 3: Verify the README content**

Run: `Get-Content README.md`
Expected: includes Phase 4A notes and test commands.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: document phase 4 quality outputs"
```

## Task 8: Final QA Gate

**Files:**
- Modify: none unless a failing regression requires a fix
- Test: `tests/contracts/test_schemas.py`
- Test: `tests/api/test_health.py`
- Test: `tests/api/test_jobs.py`
- Test: `tests/api/test_renderers.py`
- Test: `tests/text/test_paddle.py`
- Test: `tests/visual/test_heuristic.py`
- Test: `tests/fusion/test_engine.py`
- Test: `tests/background/test_cleanup.py`
- Test: `tests/preview/test_scoring.py`
- Test: `tests/quality/test_evaluator.py`

- [ ] **Step 1: Run the full suite**

Run: `uv run pytest -q`
Expected: all tests pass

- [ ] **Step 2: Run compile verification**

Run: `uv run python -m compileall apps packages tests`
Expected: success with no failures

- [ ] **Step 3: Run one manual smoke test**

Use a synthetic image with:
- one text region
- one visual block
- one intentionally overlapping/duplicate candidate scenario

Verify:
- manifest warnings make sense
- status is honest
- preview metrics are emitted

- [ ] **Step 4: Review Git status**

Run: `git status --short`
Expected: only intended Phase 4A changes remain

- [ ] **Step 5: Create the final commit**

```bash
git add .
git commit -m "Complete Phase 4A fusion and quality checkpoint"
```

- [ ] **Step 6: Push**

```bash
git push origin main
```
