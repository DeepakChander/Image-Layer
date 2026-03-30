# Risk Register

Status: Draft  
Date: 2026-03-31  
Related docs: [Architecture](../architecture/2026-03-31-single-image-layer-extraction-architecture.md), [Security Overview](../security/security-overview.md), [Evaluation and Acceptance Criteria](../quality/evaluation-and-acceptance-criteria.md)

## 1. Purpose

This document tracks the major risks that could affect delivery, trust, usability, cost, or commercial viability.

## 2. Risk Scale

- Impact: Low, Medium, High
- Likelihood: Low, Medium, High

## 3. Core Risks

| ID | Risk | Impact | Likelihood | Mitigation Direction |
| --- | --- | --- | --- | --- |
| R1 | The system misses important visual layers on common design inputs | High | High | benchmark recall carefully, use multi-stage extraction, set confidence guardrails |
| R2 | Editable text appears plausible but is wrong | High | High | emit editable text only above strict similarity thresholds, raster fallback otherwise |
| R3 | Arbitrary image requests create false market expectations | High | High | position V1 around design-like inputs and explicit unsupported cases |
| R4 | Heavy model cost exceeds budget during experimentation | High | Medium | route jobs, cap resolutions, benchmark early, avoid wasteful multi-model runs |
| R5 | Third-party model or dependency license issues block shipping | High | Medium | track model provenance and license posture before adoption |
| R6 | Trust documentation overstates actual controls | High | Medium | keep docs honest and tied to implemented operations |
| R7 | Integration contract changes frequently and breaks downstream automation | High | Medium | version schemas and freeze contracts before external pilots |
| R8 | Background reconstruction quality is not good enough for motion | Medium | Medium | gate quality with reconstruction metrics and preview review |
| R9 | Team spends too much time on enterprise theater before product proof | Medium | Medium | keep trust docs lean and phase-based |
| R10 | Product fails to create enough time savings over manual editing | High | Medium | measure workflow impact and prioritize motion-ready usefulness |

## 4. Risk Review Cadence

- review at the end of each major milestone
- review before any external pilot
- update after major incidents or discovery changes

## 5. Ownership Rule

Each high-impact risk should eventually have:

- named owner
- current status
- next mitigation action

## 6. Decision Rule

If a risk threatens the truthfulness of the product promise, that risk must be addressed before adding surface-level polish.
