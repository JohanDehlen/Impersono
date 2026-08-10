# Impersonic

**Professional Local AI Voice Creation**

> Your voices stay on your computer.

Impersonic is a local-first AI voice creation application designed for professional voice cloning, text-to-speech, and future voice production workflows.

The desktop application is intended to perform voice processing locally whenever the user's hardware allows it. Optional cloud processing may be offered later for users who need additional computing power or prefer to work through a web browser.

Impersonic is a completely separate project and product with its own architecture, user interface, branding, and development roadmap.

---

## Project Status

**Early development**

Current milestone:

**Milestone 0.1 — Project Foundation**

Impersonic is not yet ready for production use.

---

## Product Vision

Impersonic aims to become a professional AI voice creation platform that combines:

- High-quality voice cloning
- Natural text-to-speech
- Local inference
- Privacy-first processing
- Reusable voice libraries
- Professional project workflows
- Hardware-aware generation
- Optional cloud rendering
- A future browser-based experience
- A clean, polished desktop interface

The initial quality benchmark is VibeVoice-class speech generation.

Impersonic will not simply reproduce the VibeVoice demonstration interface. VibeVoice serves as an early technical reference and quality benchmark while Impersonic develops its own product architecture and user experience.

---

## Core Product Philosophy

### Local First

When using local generation, reference voices and generated audio remain on the user's computer.

### Cloud Optional

Users without suitable local hardware should eventually be able to choose secure cloud generation rather than being excluded from using Impersonic.

### Privacy by Design

Voice data must never be uploaded without an explicit user action that clearly indicates cloud processing will occur.

### Engine Independent

The application architecture should not permanently depend on a single AI model.

The Impersonic inference layer should eventually support multiple voice engines through a common interface.

### Professional Quality

Impersonic is intended to become commercial-quality software rather than a thin graphical wrapper around an AI research project.

---

## Planned Core Workflow

The initial desktop workflow will evolve toward:

```text
Import or create a voice
        ↓
Add text
        ↓
Choose generation settings
        ↓
Generate locally
        ↓
Preview audio
        ↓
Save or export