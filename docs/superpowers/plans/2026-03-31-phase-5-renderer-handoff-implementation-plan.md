# Phase 5 Renderer Handoff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local renderer handoff layer that turns completed job packages into stable renderer-ready payloads for After Effects first and Remotion second.

**Architecture:** Add typed renderer handoff models, real local adapter implementations, storage support for handoff payload files, API integration for successful handoff responses, and a small CLI wrapper that uses the same adapter contract.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, pathlib, json, pytest

---

## File Map

### New files

- `packages/layer_ai/renderers/models.py`
- `packages/layer_ai/renderers/after_effects.py`
- `packages/layer_ai/renderers/remotion.py`
- `apps/worker/run_renderer.py`
- `tests/renderers/test_after_effects.py`
- `tests/renderers/test_registry.py`

### Existing files to modify

- `packages/layer_ai/renderers/base.py`
- `packages/layer_ai/renderers/registry.py`
- `packages/layer_ai/storage/local.py`
- `packages/layer_ai/services/jobs.py`
- `packages/layer_ai/api/routes.py`
- `tests/api/test_renderers.py`
- `README.md`

## Task 1: Add Renderer Handoff Models

**Files:**
- Create: `packages/layer_ai/renderers/models.py`
- Modify: `packages/layer_ai/renderers/base.py`
- Test: `tests/renderers/test_registry.py`

- [ ] **Step 1: Write the failing model and contract test**

Add a test that requires renderer handoff models to support:
- job metadata
- ordered layer references
- output file path metadata

- [ ] **Step 2: Run the targeted test to verify it fails**

Run: `uv run pytest tests/renderers/test_registry.py -q`
Expected: FAIL because renderer models do not exist yet.

- [ ] **Step 3: Implement the minimal renderer handoff models**

Add typed models for:
- `RendererLayerRef`
- `RendererHandoff`
- `RendererHandoffResult`

Extend the base contract so adapters can accept:
- `job_id`
- `job_root`
- `manifest`

- [ ] **Step 4: Run the targeted test to verify it passes**

Run: `uv run pytest tests/renderers/test_registry.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/layer_ai/renderers/models.py packages/layer_ai/renderers/base.py tests/renderers/test_registry.py
git commit -m "feat: add renderer handoff models"
```

## Task 2: Implement the After Effects Adapter

**Files:**
- Create: `packages/layer_ai/renderers/after_effects.py`
- Modify: `packages/layer_ai/storage/local.py`
- Test: `tests/renderers/test_after_effects.py`

- [ ] **Step 1: Write the failing adapter tests**

Cover:
- adapter writes `renderers/after-effects/renderer_handoff.json`
- payload preserves manifest layer order
- payload includes background and text metadata

- [ ] **Step 2: Run the targeted test to verify it fails**

Run: `uv run pytest tests/renderers/test_after_effects.py -q`
Expected: FAIL because the adapter does not exist yet.

- [ ] **Step 3: Implement the minimal After Effects adapter**

The adapter should:
- validate the manifest
- build a handoff payload from manifest data
- write the payload under the job folder
- return a structured result with path metadata

Add storage helpers as needed to:
- resolve `job_root`
- resolve manifest asset paths relative to the job package
- create renderer output folders

- [ ] **Step 4: Run the targeted test to verify it passes**

Run: `uv run pytest tests/renderers/test_after_effects.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/layer_ai/renderers/after_effects.py packages/layer_ai/storage/local.py tests/renderers/test_after_effects.py
git commit -m "feat: add after effects handoff adapter"
```

## Task 3: Implement Registry and Remotion Contract Stub

**Files:**
- Create: `packages/layer_ai/renderers/remotion.py`
- Modify: `packages/layer_ai/renderers/registry.py`
- Test: `tests/renderers/test_registry.py`

- [ ] **Step 1: Write the failing registry tests**

Cover:
- registry returns a real After Effects adapter
- registry returns a contract-compatible Remotion adapter
- unknown renderer names fail cleanly

- [ ] **Step 2: Run the targeted tests to verify they fail**

Run: `uv run pytest tests/renderers/test_registry.py -q`
Expected: FAIL because the registry still returns stub adapters.

- [ ] **Step 3: Implement the registry and Remotion stub**

The Remotion adapter should:
- build the same style of handoff payload
- remain lightweight
- not claim real rendering behavior yet

- [ ] **Step 4: Run the targeted tests to verify they pass**

Run: `uv run pytest tests/renderers/test_registry.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/layer_ai/renderers/registry.py packages/layer_ai/renderers/remotion.py tests/renderers/test_registry.py
git commit -m "feat: add renderer adapter registry"
```

## Task 4: Integrate Renderer Handoff into the API

**Files:**
- Modify: `packages/layer_ai/services/jobs.py`
- Modify: `packages/layer_ai/api/routes.py`
- Modify: `tests/api/test_renderers.py`

- [ ] **Step 1: Write the failing API tests**

Extend renderer API tests to require:
- `after-effects` returns `200` for completed jobs
- `renderer_handoff.json` is written
- incomplete jobs are rejected with `409`
- unknown renderer names return `400`

- [ ] **Step 2: Run the targeted API tests to verify they fail**

Run: `uv run pytest tests/api/test_renderers.py -q`
Expected: FAIL because the API still returns `501`.

- [ ] **Step 3: Implement the minimal API integration**

Add job service support to:
- resolve the job root
- verify the job is renderer-eligible

Update routes to:
- return a real handoff result
- raise `409` for ineligible job states
- raise `400` for unsupported renderer names

- [ ] **Step 4: Run the targeted API tests to verify they pass**

Run: `uv run pytest tests/api/test_renderers.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/layer_ai/services/jobs.py packages/layer_ai/api/routes.py tests/api/test_renderers.py
git commit -m "feat: add renderer handoff api flow"
```

## Task 5: Add the CLI Wrapper

**Files:**
- Create: `apps/worker/run_renderer.py`
- Test: `tests/renderers/test_registry.py`

- [ ] **Step 1: Write the failing CLI behavior test**

Add coverage for:
- successful handoff generation from `job_id`
- non-zero failure for missing job

- [ ] **Step 2: Run the targeted test to verify it fails**

Run: `uv run pytest tests/renderers/test_registry.py -q`
Expected: FAIL because the CLI does not exist yet.

- [ ] **Step 3: Implement the minimal CLI wrapper**

The CLI should:
- accept `--job-id`
- accept `--renderer`
- load settings and the local job service dependencies
- generate the handoff using the same adapter flow
- print compact JSON output

- [ ] **Step 4: Run the targeted test to verify it passes**

Run: `uv run pytest tests/renderers/test_registry.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/worker/run_renderer.py tests/renderers/test_registry.py
git commit -m "feat: add renderer handoff cli"
```

## Task 6: Update README and Final QA

**Files:**
- Modify: `README.md`
- Test: `tests/renderers/test_after_effects.py`
- Test: `tests/renderers/test_registry.py`
- Test: `tests/api/test_renderers.py`

- [ ] **Step 1: Update README**

Document:
- renderer handoff endpoints
- renderer handoff output paths
- CLI usage example
- test commands for Phase 5

- [ ] **Step 2: Verify the README update**

Run: `Get-Content README.md`
Expected: includes Phase 5 renderer handoff notes.

- [ ] **Step 3: Run the full verification suite**

Run: `uv run pytest -q`
Expected: PASS

- [ ] **Step 4: Run compile verification**

Run: `uv run python -m compileall apps packages tests`
Expected: success

- [ ] **Step 5: Run one manual renderer smoke test**

Generate one completed job locally, then:
- call `POST /v1/jobs/{job_id}/render/after-effects`
- verify `renderer_handoff.json` exists
- verify ordered layers and warnings are preserved

- [ ] **Step 6: Commit**

```bash
git add README.md
git commit -m "docs: add phase 5 renderer handoff notes"
```

- [ ] **Step 7: Push**

```bash
git push origin main
```
