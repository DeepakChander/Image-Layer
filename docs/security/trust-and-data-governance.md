# Trust and Data Governance

Status: Draft  
Date: 2026-03-31  
Related docs: [Security Overview](./security-overview.md), [Risk Register](../governance/risk-register.md)

## 1. Purpose

This document defines how the product should treat customer data, generated artifacts, and trust-facing policies during the MVP and pilot stage.

## 2. Data Types in Scope

The system may handle:

- uploaded images
- extracted layer assets
- generated manifests
- job metadata
- logs
- debugging artifacts

## 3. Governance Principles

- collect only what is needed
- retain data only as long as necessary
- make deletion practical
- separate customer-visible artifacts from internal debug material
- be explicit about third-party dependencies

## 4. Recommended Data Lifecycle

### Input Data

- accept one image per job
- store original and normalized input versions only as needed

### Generated Assets

- store package artifacts for retrieval and evaluation
- define TTL-based cleanup once product behavior stabilizes

### Debug Artifacts

- restrict access tightly
- delete faster than customer-deliverable assets where practical

## 5. Retention Direction

Initial direction:

- raw uploads: short retention
- generated packages: moderate retention
- debug overlays and internal traces: shortest retention

Exact retention values should be set before external pilot onboarding.

## 6. Data Deletion Direction

The platform should be designed to support:

- job-level deletion
- artifact-level cleanup
- customer-requested deletion workflow later

## 7. Training and Model Use Policy Direction

The product should assume:

- customer uploads are not used for model training by default
- generated artifacts are not repurposed for unrelated model training without explicit policy

This is a major trust point for AI products and should be kept explicit.

## 8. Vendor and Subprocessor Direction

The team should maintain a clear internal list of:

- storage vendors
- compute vendors
- monitoring vendors
- model-hosting vendors if any are added

Even before a public subprocessor page exists, the internal record should be accurate.

## 9. Data Classification Direction

Treat uploaded imagery as potentially sensitive business material. Even if the image is only marketing creative, it may still contain:

- unreleased product visuals
- internal dashboards
- pricing details
- customer names

## 10. Trust FAQ Topics to Be Ready For

Pilot and enterprise-facing conversations will likely ask:

- where is data stored
- how long is data retained
- who can access it
- is data used for model training
- how is data deleted
- what third parties are involved

## 11. Documentation Rule

Public trust messaging should never promise more than the system can operationally support.
