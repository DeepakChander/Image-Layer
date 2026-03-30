# Output Package Specification

Status: Draft  
Date: 2026-03-31  
Related docs: [Architecture](../architecture/2026-03-31-single-image-layer-extraction-architecture.md), [API and Integration Contract](./api-and-integration-contract.md), [Data Contracts and Manifest Schema](./data-contracts-and-manifest-schema.md)

## 1. Purpose

This document defines the exact package that the system must return for every successful job. It is one of the core contracts of the product.

## 2. Package Goal

The package must be:

- machine-readable
- human-inspectable
- deterministic
- renderer-ready

## 3. Mandatory Package Contents

Each job output package must contain:

- original normalized input image
- cropped transparent PNGs for each extracted layer
- full-canvas transparent PNGs for each extracted layer
- mask files for each extracted layer
- manifest file
- scene graph file
- preview reconstruction
- debug overlay
- job report

## 4. Canonical Folder Layout

```text
job_output/
  input/
    original.png
    normalized.png
  layers/
    cropped/
    full_canvas/
    masks/
  manifest/
    manifest.json
    scene_graph.json
  preview/
    reconstructed.png
    overlay_debug.png
  logs/
    job_report.json
    confidence_report.json
```

## 5. Layer Asset Requirements

For every emitted layer:

- `cropped` version must be tightly bounded around the element
- `full_canvas` version must preserve original element position on a transparent canvas matching input dimensions
- `mask` version must align with the element geometry

## 6. File Naming Rules

- use lowercase slugs
- use deterministic numeric ordering
- avoid spaces
- include semantic hint when possible

Example:

- `layer_001_navbar_bg.png`
- `layer_002_logo.png`
- `layer_003_pricing_text.png`

## 7. Package Invariants

The package is valid only if:

- every manifest asset path resolves to a real file
- full-canvas assets share the original canvas size
- cropped assets match the declared crop bounds
- manifest layer count matches asset count
- preview reconstruction exists

## 8. Allowed Output Statuses

- `completed_high_confidence`
- `completed_with_warnings`
- `completed_low_confidence`

If the system cannot produce a credible package, it should fail rather than emit a misleading partial success.

## 9. Layer Types

Allowed layer types in V1:

- `text`
- `shape`
- `image`
- `icon`
- `logo`
- `button`
- `screenshot`
- `illustration`
- `background`
- `group`

## 10. Minimum Layer Metadata

Every layer entry must include:

- id
- name
- type
- bbox
- z-index
- asset paths
- confidence
- warnings

## 11. Preview Assets

The preview folder must include:

- `reconstructed.png` to show package fidelity
- `overlay_debug.png` to visualize detected boxes, labels, or masks

## 12. Package Versioning

Every package must declare:

- package version
- manifest schema version
- job id
- pipeline version

## 13. Future Extensions

Future package outputs may include:

- PSD-like package
- PPTX export
- HTML animation bundle
- renderer-specific import bundle
