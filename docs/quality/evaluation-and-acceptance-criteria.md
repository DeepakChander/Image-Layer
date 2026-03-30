# Evaluation and Acceptance Criteria

Status: Draft  
Date: 2026-03-31  
Related docs: [Success Metrics and SLOs](../product/success-metrics-and-slos.md), [Risk Register](../governance/risk-register.md), [Architecture](../architecture/2026-03-31-single-image-layer-extraction-architecture.md)

## 1. Purpose

This document defines how the system will be evaluated and what quality bars must be met before claiming that the product is working.

## 2. Evaluation Principle

AI extraction quality should not be judged by demos alone. The system must be tested against a defined dataset and stable acceptance criteria.

## 3. Benchmark Dataset Categories

The evaluation set should include:

- SaaS hero sections
- dashboard promo graphics
- social ad creatives
- poster-like text-heavy layouts
- mixed screenshot and decorative layouts
- hard arbitrary images for stress testing

## 4. Ground Truth Strategy

For each benchmark sample, capture:

- expected meaningful layers
- expected key text content
- approximate z-order
- whether editable text is realistically acceptable
- whether the image belongs to supported or hard-route input class

## 5. Core Metrics

- layer recall
- layer precision
- OCR text accuracy
- editable text acceptance quality
- reconstruction fidelity
- missing-important-layer rate
- duplicate-layer rate

## 6. Acceptance Gates for V1

The system should not be considered V1-ready unless:

- package schema is stable
- output folder contract is stable
- common design-route jobs produce usable packages
- confidence and warning behavior is consistent
- low-confidence jobs are clearly marked

## 7. Suggested Release Gates

- no critical schema break without version bump
- no unexplained regression on benchmark reconstruction fidelity
- no major drop in OCR accuracy
- no rise in missing-important-layer rate beyond agreed tolerance

## 8. Manual Review Criteria

Human reviewers should assess:

- whether the output package is usable for animation
- whether obvious elements are missing
- whether text is acceptable
- whether the full-canvas assets preserve position correctly
- whether the preview reconstruction resembles the source sufficiently

## 9. Confidence Policy

Quality evaluation must check not only output quality but also confidence honesty. A system that emits a warning for a weak extraction is behaving better than a system that emits false certainty.

## 10. Evaluation Cadence

- before the first internal demo
- before the first pilot customer
- before each major model swap
- before each external-facing release

## 11. Artifact Requirements for Evaluation Runs

Every evaluation run should store:

- model versions
- route decisions
- generated package
- preview images
- benchmark metrics
- reviewer notes

## 12. Acceptance Rule

The product is acceptable only when the emitted package is both:

- technically valid
- practically useful for downstream motion work
