# Impersonic Design Principles

## Purpose

This document defines the architectural, privacy, quality, and product principles that guide development of Impersonic.

These principles are intended to remain stable even as implementation details, supported models, frameworks, and hardware change.

---

## 1. Impersonic Is Its Own Product

Impersonic is not a renamed VibeVoice interface.

VibeVoice may be used as an early inference reference and quality benchmark, but Impersonic must develop:

- its own architecture
- its own user interface
- its own voice management system
- its own project format
- its own hardware abstraction
- its own cloud architecture
- its own branding
- its own product identity

Model engines are replaceable components.

Impersonic is the product.

---

## 2. Local First

Local execution is the preferred default.

When local generation is selected:

- reference voices remain on the user's computer
- generated audio remains on the user's computer
- project data remains on the user's computer
- voice metadata remains on the user's computer
- no voice data is uploaded automatically

The product should make local processing obvious and understandable.

Primary privacy message:

> Your voices stay on your computer.

---

## 3. Cloud Optional

Cloud processing may be offered when:

- local hardware is unsuitable
- the user prefers faster generation
- a model requires more memory than the local machine provides
- batch or long-form workloads benefit from remote compute

Cloud processing must always require an explicit user choice.

The UI must clearly distinguish:

### Local Mode

Processing occurs on the user's computer.

### Cloud Mode

Selected voice and generation data is intentionally transmitted for remote processing.

Cloud mode must never be silently activated.

---

## 4. Engine Independent

Impersonic must not permanently depend on one speech model.

All inference engines should eventually implement a common interface.

Conceptually:

```text
Impersonic
    |
    +-- Voice Engine Interface
            |
            +-- VibeVoice Backend
            +-- Qwen TTS Backend
            +-- Future Engine
            +-- Future Impersonic Engine