# Data Contracts and Manifest Schema

Status: Draft  
Date: 2026-03-31  
Related docs: [Output Package Specification](./output-package-spec.md), [Architecture](../architecture/2026-03-31-single-image-layer-extraction-architecture.md)

## 1. Purpose

This document defines the canonical data model that all pipeline stages, exports, and integrations must agree on.

## 2. Core Principle

The system should have one canonical scene representation. Model outputs may differ, but the exported manifest and scene graph must be normalized into one stable schema.

## 3. Core Documents

The data contract is expressed through:

- `manifest.json`
- `scene_graph.json`
- per-layer asset files

## 4. Top-Level Manifest Structure

```json
{
  "package_version": "1.0.0",
  "schema_version": "1.0.0",
  "job_id": "job_20260331_001",
  "route": "design_route",
  "canvas": {
    "width": 1440,
    "height": 900
  },
  "status": "completed_with_warnings",
  "global_confidence": 0.86,
  "warnings": [],
  "layers": []
}
```

## 5. Layer Schema

Every layer object should contain:

```json
{
  "id": "layer_003_pricing_text",
  "name": "pricing text",
  "type": "text",
  "bbox": {
    "x": 842,
    "y": 31,
    "width": 62,
    "height": 22
  },
  "z_index": 6,
  "parent_id": "group_navbar",
  "cropped_asset": "layers/cropped/layer_003_pricing_text.png",
  "full_canvas_asset": "layers/full_canvas/layer_003_pricing_text.png",
  "mask_asset": "layers/masks/layer_003_pricing_text.png",
  "confidence": 0.79,
  "warnings": [],
  "editable_text": null
}
```

## 6. Editable Text Object Schema

When text editability is available, the layer should include:

```json
{
  "text": "Pricing",
  "font_family_guess": "Inter",
  "font_weight": 600,
  "font_size_px": 18,
  "fill": "#101828",
  "alignment": "left",
  "confidence": 0.71
}
```

## 7. Scene Graph Requirements

The scene graph should represent:

- hierarchy
- grouping
- z-order
- parent-child relationships
- semantic grouping metadata

## 8. Allowed Status Values

- `queued`
- `preprocessing`
- `routing`
- `decomposing`
- `extracting_text`
- `extracting_visuals`
- `reconstructing_background`
- `building_scene_graph`
- `exporting_assets`
- `verifying_output`
- `completed_high_confidence`
- `completed_with_warnings`
- `completed_low_confidence`
- `failed_unsupported`
- `failed_processing_error`

## 9. Allowed Route Values

- `design_route`
- `mixed_route`
- `general_route`

## 10. Allowed Warning Types

- `font_approximation`
- `low_text_confidence`
- `possible_missing_layers`
- `background_reconstruction_approximate`
- `overlap_ambiguity`
- `unsupported_stylization`

## 11. Coordinate Rules

- coordinates are pixel-based
- origin is top-left
- full-canvas assets use original image dimensions
- cropped assets use local element dimensions

## 12. Versioning Rules

- schema changes must be versioned
- breaking changes require schema version bump
- integrations must validate schema version before processing

## 13. Validation Rules

The manifest is invalid if:

- required fields are missing
- layer ids are duplicated
- asset paths are missing
- bbox values are negative
- z-index order is inconsistent

## 14. Ownership Rule

No integration should invent new required manifest fields without updating this document first.
