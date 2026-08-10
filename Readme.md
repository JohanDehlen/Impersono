# Impersono

**Professional Local AI Voice Creation**

> Your voices stay on your computer.

Impersono is a local-first AI voice creation application designed for professional voice cloning, text-to-speech, and future voice production workflows.

The desktop application is intended to perform voice processing locally whenever the user's hardware allows it. Optional cloud processing may be offered later for users who need additional computing power or prefer to work through a web browser.

Impersono is a completely separate project and product with its own architecture, user interface, branding, and development roadmap.

---

## Project Status

**Early development**

Current milestone:

**Milestone 0.4 — First VibeVoice-Compatible Inference Prototype**

Impersono is not yet ready for production use.

---

## Product Vision

Impersono aims to become a professional AI voice creation platform that combines:

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

Impersono will not simply reproduce the VibeVoice demonstration interface. VibeVoice serves as an early technical reference and quality benchmark while Impersono develops its own product architecture and user experience.

---

## Core Product Philosophy

### Local First

When using local generation, reference voices and generated audio remain on the user's computer.

### Cloud Optional

Users without suitable local hardware should eventually be able to choose secure cloud generation rather than being excluded from using Impersono.

### Privacy by Design

Voice data must never be uploaded without an explicit user action that clearly indicates cloud processing will occur.

### Engine Independent

The application architecture should not permanently depend on a single AI model.

The Impersono inference layer should eventually support multiple voice engines through a common interface.

### Professional Quality

Impersono is intended to become commercial-quality software rather than a thin graphical wrapper around an AI research project.

---

## Planned Core Workflow

The initial desktop workflow will evolve toward:

```text
Import or create a voice
        |
        v
Add text
        |
        v
Choose generation settings
        |
        v
Generate locally
        |
        v
Preview audio
        |
        v
Save or export
```

If local hardware is unsuitable:

```text
Generate
   |
   v
Local hardware check
   |
   v
Local generation available?
   |-- Yes -> Generate privately on this computer
   `-- No  -> Offer optional cloud generation
```

---

## Planned Architecture

```text
Impersono
|
+-- Desktop Application
|       |
|       v
+-- Impersono Core
|   +-- Inference
|   +-- Audio
|   +-- Hardware Detection
|   +-- Voice Management
|   `-- Project Management
|
+-- Voice Engine Interface
|   +-- VibeVoice-compatible backend
|   `-- Future voice engines
|
`-- Optional Future Services
    +-- Impersono Cloud
    +-- Web Application
    `-- API
```

The desktop user interface must remain separate from the inference engine so that the same core technology can later support desktop, cloud, and web environments.

---

## Planned Development Stages

### Foundation

- Project structure
- Design principles
- Roadmap
- Development standards
- Basic application entry point

### Hardware Discovery

- Detect the local computer
- Detect CPU, RAM, GPU and VRAM where practical
- Detect supported acceleration
- Translate technical information into practical model guidance

### Inference Prototype

- Load a supported local voice model
- Load a reference voice
- Accept text input
- Generate audio
- Save WAV output
- Establish repeatable quality benchmarks

### Desktop Application

- Professional Windows interface
- Voice selector
- Text editor
- Generation controls
- Audio preview
- Export workflow

### Voice Library

- Import reference recordings
- Name and organize voices
- Store voice metadata
- Preview saved voices

### Privacy and Execution Modes

- Local generation
- Clear local privacy status
- Optional cloud generation
- Explicit cloud-processing disclosure

### Future Platform

- Cloud rendering
- Web application
- Accounts and licensing
- Usage-based cloud credits
- Commercial deployment
- Optional API

---

## Development Principles

- Build one reliable milestone at a time.
- Do not modify the sealed VibeVoice Gold Master.
- Do not depend on the existing VibeVoice Gradio interface.
- Keep inference logic independent from UI code.
- Prefer clear architecture over quick hacks.
- Keep dependencies intentional and documented.
- Test features before expanding them.
- Treat privacy as a product feature, not a marketing afterthought.
- Maintain a clean and meaningful Git history.
- Commit and push at meaningful checkpoints rather than after every minor edit.
- Inspect the actual repository before changing existing implementation.
- Prefer controlled local update scripts over repeated manual copy/paste for meaningful multi-file changes.

---

## Development Environment

Initial development environment:

- Windows 11
- Python 3.12
- Visual Studio Code
- Git
- Local virtual environment

Project directory:

```text
C:\Projects\Impersono
```

Run the package:

```powershell
python -m impersono
```

Run tests:

```powershell
python -m pytest -q
```

---

## Repository Structure

```text
Impersono/
+-- assets/
+-- docs/
|   +-- DESIGN_PRINCIPLES.md
|   `-- ROADMAP.md
+-- output/
+-- src/
|   `-- impersono/
|       +-- core/
|       |   +-- audio/
|       |   +-- hardware/
|       |   `-- inference/
|       +-- projects/
|       +-- ui/
|       `-- voices/
+-- tests/
+-- voices/
+-- .gitignore
+-- AGENTS.md
+-- CHANGELOG.md
+-- pyproject.toml
`-- Readme.md
```

---

## Privacy Positioning

The core privacy message of Impersono is:

> **Your voices stay on your computer.**

When local mode is used, reference recordings, generated speech, and project data should remain local.

If optional cloud processing is introduced, the application must clearly distinguish between:

**Local Mode**

Voice processing remains on the user's computer.

and:

**Cloud Mode**

Selected voice data and generation requests are intentionally sent for remote processing.

---

## Name and Brand

**Impersono**

**Professional Local AI Voice Creation**

Impersono is being developed as an independent software product and brand.
