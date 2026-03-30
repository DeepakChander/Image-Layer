# Roadmap

Status: Draft  
Date: 2026-03-31  
Related docs: [PRD](./prd.md), [Success Metrics and SLOs](./success-metrics-and-slos.md), [Architecture](../architecture/2026-03-31-single-image-layer-extraction-architecture.md)

## 1. Roadmap Principle

This roadmap is phase-based rather than date-committed. The goal is to keep the sequence realistic while the project is still in definition mode.

## 2. Phase 0: Definition and Benchmark Foundation

Deliverables:

- product strategy
- PRD
- architecture
- output package contract
- manifest schema
- benchmark plan
- risk register

Exit criteria:

- documentation approved
- benchmark categories defined
- V1 scope locked

## 3. Phase 1: Motion-Ready Raster Extraction

Deliverables:

- image intake pipeline
- text detection
- non-text detection
- segmentation
- cropped PNG export
- full-canvas PNG export
- scene manifest
- preview reconstruction

Exit criteria:

- package output is usable for design-like images
- major layer classes are consistently extracted

## 4. Phase 2: Editable Text and Better Structure

Deliverables:

- OCR-backed text objects
- style inference
- font approximation
- higher-quality scene graph grouping

Exit criteria:

- editable text is emitted only when quality thresholds are met
- fallback logic is stable

## 5. Phase 3: Renderer Integration

Deliverables:

- After Effects MCP adapter
- Remotion adapter
- prompt-to-render handoff contract

Exit criteria:

- downstream renderer can consume emitted package with low manual cleanup

## 6. Phase 4: Pilot Readiness

Deliverables:

- trust and security docs refined
- incident readiness doc refined
- evaluation and acceptance gates formalized
- pilot demo flows prepared

Exit criteria:

- early external conversations can be supported with confidence

## 7. Phase 5: Hard-Input Improvements

Deliverables:

- better routing
- harder image handling
- more robust background reconstruction
- broader input-class support

Exit criteria:

- confidence system is robust enough for more varied imagery

## 8. Deferred Until Later

- formal enterprise compliance programs
- batch project workflows
- multi-image scene assembly
- deep pricing and billing design

## 9. Roadmap Rule

No phase should be considered complete only because the code exists. Each phase must satisfy documentation, quality, and usability gates.
