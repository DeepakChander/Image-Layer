# API and Integration Contract

Status: Draft  
Date: 2026-03-31  
Related docs: [Output Package Specification](./output-package-spec.md), [Data Contracts and Manifest Schema](./data-contracts-and-manifest-schema.md), [Architecture](../architecture/2026-03-31-single-image-layer-extraction-architecture.md)

## 1. Purpose

This document defines the service-facing contract for job submission, status retrieval, artifact retrieval, and renderer handoff.

## 2. API Style

Recommended V1 style:

- REST over HTTPS
- JSON request and response bodies
- multipart upload for image submission
- stable versioned endpoints under `/v1`

## 3. Core Endpoints

### 3.1 Create Job

- Method: `POST`
- Path: `/v1/jobs`
- Purpose: create a new extraction job

Required inputs:

- image file
- instruction string

Optional inputs:

- target renderer
- priority
- output mode

### 3.2 Get Job Status

- Method: `GET`
- Path: `/v1/jobs/{job_id}`
- Purpose: retrieve lifecycle state, warnings, and confidence

### 3.3 Get Manifest

- Method: `GET`
- Path: `/v1/jobs/{job_id}/manifest`
- Purpose: return manifest metadata

### 3.4 Download Assets

- Method: `GET`
- Path: `/v1/jobs/{job_id}/assets`
- Purpose: return package download location or archive

### 3.5 Renderer Handoff

- Method: `POST`
- Path: `/v1/jobs/{job_id}/render/after-effects`
- Purpose: trigger After Effects MCP handoff

- Method: `POST`
- Path: `/v1/jobs/{job_id}/render/remotion`
- Purpose: trigger Remotion handoff

## 4. Sample Create Job Request

```json
{
  "instruction": "Extract layers and prepare motion-ready assets",
  "target_renderer": "after_effects",
  "output_mode": "package"
}
```

## 5. Sample Status Response

```json
{
  "job_id": "job_20260331_001",
  "status": "extracting_visuals",
  "route": "design_route",
  "global_confidence": null,
  "warnings": [],
  "created_at": "2026-03-31T00:00:00Z"
}
```

## 6. Authentication Direction

V1 internal development may use simple service auth, but the contract should be designed to support:

- API keys
- workspace-based auth
- future role-based permissions

## 7. Error Contract

Every API error should include:

- machine-readable error code
- human-readable message
- job id when applicable
- retryability flag when applicable

Suggested error categories:

- `validation_error`
- `unsupported_input`
- `processing_error`
- `artifact_not_ready`
- `renderer_handoff_error`

## 8. Integration Rules

Integrations must treat the package as the source of truth. No downstream system should infer hidden behavior that is not documented in the manifest or package spec.

## 9. Renderer Adapter Contract

Renderer adapters must accept:

- canvas size
- scene graph
- layer assets
- text metadata
- group structure

Renderer adapters must not require:

- original source design files
- hidden proprietary intermediate formats

## 10. OpenAPI Direction

When implementation begins, this contract should become:

- a formal OpenAPI document
- versioned alongside the service
- validated in CI
