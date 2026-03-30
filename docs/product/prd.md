# Product Requirements Document

Status: Draft  
Date: 2026-03-31  
Related docs: [Product Strategy](./product-strategy.md), [Architecture](../architecture/2026-03-31-single-image-layer-extraction-architecture.md), [Output Package Spec](../contracts/output-package-spec.md)

## 1. Product Name

Working name: `Layer AI`

## 2. Objective

Build a system that takes one image plus one instruction and returns a structured output package containing extracted layers and metadata that can drive motion workflows in After Effects MCP, Remotion, or similar renderers.

## 3. Problem Statement

Users currently spend too much time manually converting static visual references into animation-ready assets. The work is repetitive, slow, and difficult to scale.

## 4. Goals

- Extract meaningful visual elements from one image.
- Export motion-ready assets in deterministic structure.
- Preserve original position and size.
- Recover editable text when confidence is high.
- Provide a structured manifest for downstream rendering.
- Be honest about low-confidence outputs.

## 5. Non-Goals

- exact source file recovery from every image
- perfect editable text reconstruction for all fonts and effects
- best-in-class performance on arbitrary photos
- full enterprise compliance before product validation

## 6. Primary Users

- AI-assisted video editors
- motion designers
- creative operations managers
- SaaS marketing teams

## 7. Core User Stories

- As a video editor, I want to upload one image and receive separated assets so I can animate without manual cutting.
- As a creative ops lead, I want repeatable structured outputs so my team can move faster.
- As a marketer, I want a quick way to convert static creative into motion-ready content.
- As an integration workflow, I want a stable manifest so I can automate downstream composition.

## 8. Functional Requirements

### 8.1 Input

- The system must accept one image per job.
- The system must accept one instruction string per job.
- The system must validate file type, file size, and basic image quality.

### 8.2 Extraction

- The system must detect text layers.
- The system must detect non-text visual layers.
- The system must preserve original coordinates.
- The system must attempt background reconstruction when foreground layers are extracted.

### 8.3 Export

- The system must export tight crop PNGs.
- The system must export full-canvas transparent PNGs.
- The system must generate a manifest file.
- The system must generate a reconstructed preview.

### 8.4 Text Handling

- The system must recover text content where possible.
- The system must emit editable text only when confidence is high.
- The system must fall back to raster text when editability is unreliable.

### 8.5 Output Quality

- The system must attach confidence scores.
- The system must flag low-confidence layers.
- The system must avoid claiming exact extraction when confidence is low.

### 8.6 Integration

- The system must support downstream handoff to After Effects MCP.
- The system must support downstream handoff to Remotion.
- The system must remain renderer-neutral at the core data model level.

## 9. Non-Functional Requirements

- deterministic output structure
- testable manifest schema
- clear failure modes
- observable pipeline stages
- support for local development and cloud GPU testing

## 10. Key Decisions Already Locked

- Open-source-first extraction stack
- Canva is not the core dependency
- Best effort plus guardrail output policy
- Design-like image classes are the primary V1 target

## 11. Assumptions

- Users care more about motion-ready usefulness than exact source-file fidelity.
- Structured outputs matter as much as visual extraction.
- Early pilots will ask trust and security questions even before enterprise scale.

## 12. Constraints

- The input is a single flattened image.
- Source-layer truth is often unavailable.
- Some information loss is irreversible.
- AWS credits are limited, so cost-aware routing matters.

## 13. Success Criteria

- A user can take the output package and start animating without major manual reconstruction.
- Text is readable and correctly attributed in most design-oriented cases.
- The output manifest is stable enough for programmatic consumption.
- Pilot conversations can be supported with product, technical, and trust documentation.

## 14. Release Gates for V1

- architecture approved
- output package spec approved
- manifest schema approved
- benchmark dataset defined
- quality thresholds defined
- security and data-handling docs written

## 15. Open Questions Deferred

- pricing details
- exact UI form factor
- long-term multi-image batch workflows
- long-term compliance certifications

## 16. Delivery Principle

The V1 product should optimize for:

- trustworthiness
- motion usefulness
- predictable package structure

before optimizing for:

- extreme speed
- very broad input generalization
- aggressive enterprise packaging
