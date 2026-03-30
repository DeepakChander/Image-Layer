# Personas and Use Cases

Status: Draft  
Date: 2026-03-31  
Related docs: [PRD](./prd.md), [Product Strategy](./product-strategy.md)

## 1. Purpose

This document defines the human and workflow context for the project so feature decisions stay grounded in real users rather than abstract capabilities.

## 2. Persona 1: AI Video Editor

### Profile

- edits short-form motion content
- works fast and under deadline pressure
- receives static reference images from a senior or client

### Main Pain

- spends too much time manually isolating text, cards, screenshots, logos, and backgrounds before animation work can even begin

### Desired Outcome

- upload one image
- receive animation-ready assets
- move directly into After Effects or Remotion

## 3. Persona 2: Creative Operations Lead

### Profile

- manages throughput
- cares about consistency, repeatability, and turnaround time
- may manage multiple editors and campaigns

### Main Pain

- repeated manual extraction work wastes time and creates inconsistent layer structures across projects

### Desired Outcome

- standard package outputs
- predictable naming
- metadata-rich assets for automation

## 4. Persona 3: Founder or Growth Marketer

### Profile

- needs more creative output with less production time
- may not be an advanced editor
- values speed over perfect source fidelity

### Main Pain

- static design assets are easier to get than motion assets

### Desired Outcome

- use one existing creative asset to produce motion variants faster

## 5. Primary Use Cases

### 5.1 Design to Motion Conversion

A user uploads a SaaS promo image and asks the system to extract layers for motion use.

Success means:

- major elements are separated
- text is recoverable
- output is usable without heavy manual cleanup

### 5.2 Hero Section Reconstruction

A user uploads a landing page hero screenshot and wants motion-ready layers for a promo video.

Success means:

- navbar, headline, CTA, product screenshot, and supporting visuals are separable
- original structure is preserved

### 5.3 Social Ad Variation Pipeline

A team uploads multiple ad-style visuals one by one and uses the extracted packages in templated animation workflows.

Success means:

- package structure is consistent across jobs
- naming conventions and manifests are reliable

## 6. Secondary Use Cases

- agency workflow acceleration
- reusable creative component extraction
- AI-assisted content localization preparation
- internal benchmark generation for motion templates

## 7. Use Cases to Avoid in V1 Positioning

- exact PSD recovery claims
- general photo decomposition claims
- highly artistic collage reconstruction claims
- low-resolution noisy screenshot promises without caveats

## 8. What Matters Most to Users

- usable output
- speed to animation
- confidence they can trust
- clean packaging
- fewer manual steps

## 9. What Users Will Not Forgive

- missing obvious layers
- unreadable text extraction
- broken coordinates
- inconsistent file naming
- false claims of editability

## 10. User Experience Principle

The system should behave like a reliable prep artist, not like a vague AI toy. Users should feel that the output package is structured, inspectable, and ready for real work.
