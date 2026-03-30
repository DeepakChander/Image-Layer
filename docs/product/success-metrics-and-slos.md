# Success Metrics and SLOs

Status: Draft  
Date: 2026-03-31  
Related docs: [PRD](./prd.md), [Evaluation and Acceptance Criteria](../quality/evaluation-and-acceptance-criteria.md)

## 1. Purpose

This document defines how the team will know whether the product is actually working, both as a user-facing workflow tool and as a service.

## 2. Product Success Metrics

### 2.1 Workflow Metrics

- average manual cleanup time after extraction
- percentage of jobs that are usable for animation without major rebuild
- percentage of layers that editors keep versus discard
- turnaround time from input image to renderer-ready package

### 2.2 Product Adoption Metrics

- jobs processed per active user
- repeat usage per editor or team
- pilot account retention
- percentage of customers using exported packages downstream

### 2.3 Output Quality Metrics

- layer recall on benchmark set
- layer precision on benchmark set
- OCR accuracy
- editable text acceptance rate
- reconstruction fidelity score

## 3. Business Metrics

- pilot-to-paid conversion rate
- average processing cost per job
- margin profile per plan or customer segment
- average support time per failed job

## 4. SLI Definitions

Service level indicators should include:

- job success rate
- median processing latency
- p95 processing latency
- artifact download success rate
- renderer handoff success rate

## 5. Initial SLO Targets

These are planning targets, not public commitments.

- job success rate for design-route images: 95 percent or higher
- artifact package generation success rate: 99 percent or higher
- p95 processing latency for normal design-route jobs: under 120 seconds
- manifest schema validation success rate: 100 percent

## 6. Quality Guardrail Metrics

- no release if missing-important-layer rate exceeds threshold
- no release if OCR parity regresses materially
- no release if reconstruction fidelity regresses beyond agreed tolerance

## 7. Reporting Cadence

- weekly internal quality review
- per-release benchmark review
- monthly pilot outcome review once external users begin

## 8. Ownership

- product owner: product adoption and workflow outcomes
- AI engineering: extraction quality metrics
- platform/backend: service health metrics

## 9. Rule for Metrics

Metrics should not reward false confidence. A lower-confidence but honest system is better than a high-volume system that silently outputs broken packages.
