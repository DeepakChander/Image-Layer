# Phase 4A Fusion, Background, Preview, and Quality Design

Status: Draft
Date: 2026-03-31
Related docs:
- `docs/architecture/2026-03-31-single-image-layer-extraction-architecture.md`
- `docs/contracts/output-package-spec.md`
- `docs/contracts/data-contracts-and-manifest-schema.md`

## 1. Purpose

This document defines the first deterministic Phase 4 checkpoint for Layer AI.

Phase 4A improves the current Phase 3 pipeline by adding:
- fusion of text and visual candidates
- stronger background plate cleanup
- reconstruction scoring
- honest guardrails for confidence, warnings, and final status

This phase must remain:
- local
- deterministic
- CPU-safe
- free of new heavy model dependencies

## 2. Problem Statement

After Phase 3, the system can:
- extract text layers
- extract simple visual layers
- export a valid package

But it still has major trust gaps:
- overlapping or duplicate candidates may survive into the manifest
- background cleanup is only a simple patching step
- preview reconstruction is written but not scored
- final status is still too coarse for production trust

Phase 4A exists to improve package honesty and package quality before deeper model upgrades or renderer automation.

## 3. Scope

### In Scope

- deterministic fusion of text and visual outputs
- duplicate and overlap guardrails
- deterministic background cleanup improvements
- reconstruction preview scoring
- warning generation from actual pipeline evidence
- job-level confidence that combines more than a single extractor score

### Out of Scope

- new inpainting or diffusion models
- deep occlusion recovery
- hidden-background hallucination
- GroundingDINO, SAM 2, or model-backed upgrades
- renderer integration changes
- cloud deployment changes

## 4. Goals

- reduce duplicated or conflicting layers
- improve background plate consistency after layer removal
- score reconstruction quality against the original input
- make final status and warnings evidence-based
- keep the pipeline modular and testable

## 5. Success Criteria

Phase 4A is successful when:
- fused layer output has fewer obvious duplicates
- reconstruction preview includes a measurable similarity score
- low-quality jobs downgrade honestly
- warnings explain why a job is not high confidence
- all existing Phase 2 and Phase 3 tests still pass

## 6. Proposed Architecture

Phase 4A introduces four new modules plus one thin orchestrator:

- `packages/layer_ai/fusion/`
- `packages/layer_ai/background/`
- `packages/layer_ai/preview/`
- `packages/layer_ai/quality/`
- `packages/layer_ai/pipeline/phase4.py`

### Design Principle

`LocalArtifactStore` should remain focused on package writing and file output.

The new reasoning should move into dedicated modules so that:
- each stage can be tested independently
- future model-backed upgrades can replace internals without breaking contracts
- Phase 5 and later phases do not turn storage code into a giant mixed-responsibility file

## 7. Data Flow

The intended Phase 4A pipeline is:

1. text extractor returns text candidates
2. visual extractor returns visual candidates
3. fusion module merges and normalizes candidates
4. background module creates the cleaned background plate
5. preview module reconstructs the scene and scores similarity
6. quality module calculates warnings, confidence, and final status
7. artifact store writes assets, manifest, scene graph, previews, and logs

## 8. Module Responsibilities

### 8.1 Fusion Module

Responsibilities:
- normalize text and visual candidates into one candidate set
- remove near-duplicate candidates
- resolve obvious text-versus-visual overlap conflicts
- preserve deterministic ordering and z-index rules

Expected rules:
- text candidates win against overlapping visual candidates in the same region
- visual candidates with very high intersection and similar geometry are treated as duplicates
- tiny noisy candidates are filtered before export

Output:
- fused layer candidates
- fusion warnings such as `possible_duplicate_layers`

### 8.2 Background Module

Responsibilities:
- generate a cleaner deterministic background plate
- fill removed regions with local color heuristics
- smooth obvious seams from removed text and visual regions

Constraints:
- must not require heavy dependencies
- must be deterministic and stable on CPU

Output:
- cleaned background image
- optional background cleanup warnings

### 8.3 Preview Module

Responsibilities:
- reconstruct the final image from background plus exported full-canvas layers
- compute simple image-similarity metrics against the original input
- produce debug artifacts for QA

Metrics for Phase 4A:
- pixel difference ratio
- changed pixel count
- normalized reconstruction score between `0.0` and `1.0`

Output:
- `preview/reconstructed.png`
- `preview/overlay_debug.png`
- reconstruction score data for logs and quality decisions

### 8.4 Quality Module

Responsibilities:
- aggregate text confidence
- aggregate visual confidence
- include reconstruction score in the final job confidence
- assign warnings and final status honestly

Expected warning set for Phase 4A:
- `low_text_confidence`
- `low_visual_confidence`
- `possible_duplicate_layers`
- `reconstruction_mismatch`
- `background_cleanup_approximate`

Expected status values:
- `completed_high_confidence`
- `completed_with_warnings`
- `completed_low_confidence`
- `failed_processing_error`

## 9. Confidence Model

Phase 4A confidence should be based on three evidence groups:

- text evidence
- visual evidence
- reconstruction evidence

### Recommended Initial Rules

- start from the minimum non-background layer confidence
- apply penalties for duplicate warnings
- apply penalties for poor reconstruction score
- downgrade to `completed_with_warnings` when warnings exist but confidence remains acceptable
- downgrade to `completed_low_confidence` when reconstruction or candidate confidence falls below the low-confidence threshold

This version should stay deterministic and explainable rather than statistically sophisticated.

## 10. Background Strategy

Phase 4A background cleanup should use deterministic local heuristics only:

- local average edge color
- simple region fill
- optional light smoothing to reduce visible seams

This is intentionally weaker than a model-based inpainting system, but it is much easier to validate and debug.

The product should be honest when cleanup is approximate. The system should warn instead of pretending the background is exact.

## 11. Output Contract Changes

Phase 4A should extend current package outputs without breaking existing paths.

### Manifest Additions

The manifest should expose stronger evidence fields through warnings and confidence.

Desired additions:
- reconstruction score
- quality warnings
- more honest status assignment

### Logs Additions

`logs/confidence_report.json` should include:
- text confidence summary
- visual confidence summary
- reconstruction score
- final confidence
- warnings used to derive status

## 12. Testing Strategy

### Unit Tests

- fusion duplicate detection
- fusion overlap resolution
- background deterministic cleanup
- preview score calculation
- quality aggregation and status rules

### Integration Tests

- text-only job
- visual-only job
- text-plus-visual job
- low-confidence job that must downgrade
- duplicate candidates producing warnings

### Package Tests

- manifest paths match actual assets
- scene graph remains aligned after fusion
- preview and logs are always emitted

### Regression Tests

- no duplicate text and visual layers in the same region
- no broken status transitions
- low reconstruction score produces `reconstruction_mismatch`

## 13. Rollout Plan

Phase 4A should be implemented in this order:

1. fusion module
2. background module
3. preview module
4. quality module
5. thin orchestrator
6. integration through package pipeline
7. final QA gate

This order minimizes risk because each step can be verified before the next one lands.

## 14. Acceptance Criteria

Do not call Phase 4A complete unless all of the following are true:

- full test suite passes
- new Phase 4A tests exist for fusion, preview, and quality
- manual smoke tests confirm warning and status behavior
- reconstruction score is present in outputs
- duplicate and overlap handling are visibly improved on representative synthetic cases

## 15. Recommendation

Proceed with Phase 4A as a focused local reliability milestone.

This is the right next step because it:
- strengthens trust in the package output
- improves QA visibility
- prepares the system for later renderer integration
- avoids destabilizing the pipeline with heavy new model dependencies too early
