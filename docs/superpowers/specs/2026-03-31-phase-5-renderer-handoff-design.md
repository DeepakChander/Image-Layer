# Phase 5 Renderer Handoff Design

**Goal**

Add a local renderer handoff layer that converts a completed Layer AI job package into a renderer-ready payload for downstream motion tooling, starting with `after-effects` and a contract-compatible `remotion` path.

**Why this phase exists**

The project already produces a motion-ready package, but there is still a gap between `package generated` and `renderer can consume it`. Phase 5 closes that gap without depending on a live After Effects MCP runtime yet. This gives the system a stable, testable renderer contract before real tool integration.

## Scope

This checkpoint will:

- add typed renderer handoff models
- implement a real local `after-effects` adapter
- keep `remotion` available as a light contract-compatible adapter
- write `renderer_handoff.json` into the job folder
- return real API success responses for renderer handoff
- add a small CLI wrapper for local renderer handoff generation
- reject handoff for jobs that are not in a completed state

This checkpoint will not:

- call the real After Effects MCP
- render a comp or video
- modify the core extraction pipeline
- implement a full Remotion renderer

## Architecture

Phase 5 adds a small renderer orchestration layer on top of the existing package contract.

The flow is:

1. API or CLI receives a request for a renderer handoff.
2. The job manifest is loaded.
3. The system verifies the job exists and is in a completed state.
4. The selected renderer adapter builds a normalized handoff payload.
5. The handoff payload is written to the job folder.
6. The API or CLI returns metadata about the generated handoff file.

This keeps the handoff deterministic and local while preserving the same core package format created by earlier phases.

## Contract

The canonical output for this phase is `renderer_handoff.json`.

Recommended path:

```text
<job_root>/
  renderers/
    after-effects/
      renderer_handoff.json
    remotion/
      renderer_handoff.json
```

The handoff payload should contain:

- `job_id`
- `renderer`
- `created_at`
- `manifest_path`
- `original_image_path`
- `background_asset_path`
- `global_confidence`
- `reconstruction_score`
- `warnings`
- `layers`

Each layer entry should contain:

- `id`
- `name`
- `type`
- `z_index`
- `bbox`
- `cropped_asset`
- `full_canvas_asset`
- `mask_asset`
- `confidence`
- `warnings`
- `text_content`
- `text_confidence`
- `editable_text`

The payload should preserve manifest ordering so a downstream renderer can rebuild the scene consistently.

## Components

### Renderer Models

`packages/layer_ai/renderers/models.py`

Contains typed models for:

- renderer handoff payload
- handoff layer references
- adapter response metadata

### After Effects Adapter

`packages/layer_ai/renderers/after_effects.py`

Responsibilities:

- validate the manifest is renderer-eligible
- build the `after-effects` handoff payload
- write the payload to disk
- return a structured handoff response

### Remotion Adapter

`packages/layer_ai/renderers/remotion.py`

Responsibilities:

- keep the same contract shape
- emit a valid local handoff payload
- remain lightweight until the real Remotion phase

### Registry

`packages/layer_ai/renderers/registry.py`

Responsibilities:

- select the correct adapter by name
- provide a single adapter lookup surface for API and CLI code

### Storage Support

`packages/layer_ai/storage/local.py`

Responsibilities:

- resolve job root paths
- resolve manifest-relative asset paths to job-relative renderer paths
- write renderer payload files into predictable folders

### CLI Wrapper

`apps/worker/run_renderer.py`

Responsibilities:

- accept a `job_id` and `renderer` name
- run the same handoff path as the API
- print a small success payload
- fail clearly for missing or invalid jobs

## Error Handling

The renderer handoff path should fail with explicit reasons:

- unknown job -> `404`
- missing manifest -> `404`
- incomplete or failed job -> `409`
- unsupported renderer -> `400`
- invalid manifest data -> `500`

This phase should stop pretending success when the renderer contract cannot be produced.

## Testing

Phase 5 should add:

- adapter unit tests
- registry tests
- API tests for successful handoff and failed eligibility
- CLI tests or command-level smoke coverage

Most important assertions:

- handoff file is written to the expected directory
- payload contains ordered layers and background
- warnings and confidence are preserved
- text metadata survives
- incomplete jobs are rejected

## Success Criteria

Phase 5 is complete when:

- `POST /v1/jobs/{job_id}/render/after-effects` returns a real handoff result
- `renderer_handoff.json` is created for completed jobs
- the CLI can generate the same output
- remotion remains contract-compatible
- all renderer tests pass locally
