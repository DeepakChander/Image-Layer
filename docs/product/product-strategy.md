# Product Strategy

Status: Draft  
Date: 2026-03-31  
Related docs: [Architecture](../architecture/2026-03-31-single-image-layer-extraction-architecture.md), [PRD](./prd.md), [Roadmap](./roadmap.md)

## 1. Purpose

This document defines why this product should exist, who it is for, where it wins in the market, and what strategic boundaries should shape the project before implementation begins.

## 2. Product Summary

The product takes one flattened image plus one instruction and returns a motion-ready output package containing extracted visual layers, transparent assets, metadata, and renderer-ready structure for tools such as After Effects MCP and Remotion.

The product is not positioned as a magical "recover the exact source file from any image" system. It is positioned as an AI system that reconstructs useful layered assets from design-oriented images with confidence-aware outputs.

## 3. Core Problem

Creative teams regularly work from:

- static reference images
- screenshots
- social ad mockups
- landing page hero visuals
- marketing compositions made in multiple tools

When those assets need to become motion graphics, editors must manually:

- separate text
- isolate logos and icons
- cut screenshots out of cards
- remove backgrounds
- reconstruct layers
- rebuild scene structure

This is repetitive, slow, and expensive. It also breaks creative velocity when teams need multiple variants.

## 4. Target User Segments

### 4.1 Primary Users

- AI-assisted video editors
- motion designers
- creative operations teams
- growth design teams creating ad variants

### 4.2 Secondary Users

- SaaS founders and marketers creating social videos
- agencies producing quick design-to-video transformations
- internal content teams working across many campaigns

### 4.3 Early Enterprise Buyers

- teams that care about speed, repeatability, and integration
- teams that need trust, data handling clarity, and predictable outputs

## 5. Value Proposition

### 5.1 Functional Value

- Convert one image into motion-ready layers faster than manual editing.
- Reduce repetitive extraction work before animation begins.
- Standardize the handoff into downstream rendering systems.

### 5.2 Strategic Value

- Shortens time from concept to animated asset.
- Enables creative teams to scale content generation.
- Makes design-to-motion workflows more automatable.

### 5.3 Trust Value

- Confidence-aware output is more credible than pretending every image is fully recoverable.
- Structured package outputs make enterprise and integration conversations easier.

## 6. Positioning

This product should be positioned as:

- an AI layer reconstruction and motion-prep engine
- built for design-oriented images
- optimized for animation workflows
- honest about confidence and failure cases

It should not be positioned as:

- a full Canva replacement
- a guaranteed PSD recovery system
- a universal photo decomposition tool

## 7. Market Positioning Thesis

The strongest initial wedge is not generic image editing. It is the gap between:

- static design tools
- and motion production tools

That gap is painful because editors often receive only flattened references, while animation tools work best with structured layers.

This project wins when it becomes the fastest route from:

- static creative
- to motion-ready package

## 8. Strategic Differentiators

The project should differentiate on:

- motion-readiness, not only visual extraction
- structured output package, not only loose assets
- editable text when confidence is high
- renderer-neutral architecture
- open-source-first extraction core
- explicit confidence and trust signals

## 9. Business and Product Boundaries

The project should prioritize:

- SaaS marketing creatives
- landing page hero sections
- social media ads
- dashboard and product showcase visuals
- poster-like design layouts with text, icons, cards, and screenshots

The project should deprioritize in V1:

- arbitrary photography
- painterly images
- dense collage art
- highly distorted typography
- exact source recreation claims

## 10. Commercial Readiness View

For pilot customers and early enterprise buyers, the product needs more than a strong demo. It needs a coherent story across:

- product strategy
- technical architecture
- trust and security posture
- predictable integration contracts
- quality expectations

That is why this documentation set is intentionally broader than a normal hackathon project.

## 11. Pricing and Packaging Direction

Pricing is not finalized, but the product should be compatible with:

- usage-based pricing per processed image
- plan-based pricing by monthly jobs
- enterprise pricing for integration-heavy teams

The architecture and docs should avoid assumptions that make only one commercial model possible.

## 12. Competitive Frame

The primary competition is not one product. It is a workflow stack:

- manual Canva and design editing
- manual Photoshop or After Effects preparation
- generic background removal tools
- generic OCR tools
- ad hoc automation scripts

The product wins when it feels like a workflow system, not a single-feature utility.

## 13. Strategic Success Conditions

The strategy is working if:

- editors trust the package enough to animate from it
- teams save meaningful preparation time
- early pilot customers can understand the product in one meeting
- investors and hires can see a real market wedge
- the team can clearly explain what the product does and does not promise

## 14. Strategic Failure Modes

The strategy fails if:

- the product is positioned as exact source recovery
- the pipeline is optimized for all images instead of the right image classes
- the docs overstate enterprise maturity before the product is stable
- the team builds around third-party product dependencies it cannot control

## 15. References

- Atlassian guidance on PRDs and roadmaps influenced the structure of the product and planning docs.
- Public trust and security materials from Atlassian, GitLab, and GitHub influenced the trust-ready positioning.
- AWS, NIST, CSA, and Google SRE references influenced the trust and reliability document set.
