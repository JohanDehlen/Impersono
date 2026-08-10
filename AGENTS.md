# AGENTS.md — Impersono Development Guide

## Purpose

This file contains durable project-specific instructions for AI-assisted development of Impersono.

It supplements the user's general ChatGPT Workflow Principles. It is not a roadmap, changelog, or conversation history.

---

## Product Identity

**Product:** Impersono

**Positioning:** Professional Local AI Voice Creation

**Core privacy message:**

> Your voices stay on your computer.

Impersono is intended to become a commercial-quality, local-first AI voice creation platform.

It is not a renamed VibeVoice demo and must maintain its own architecture, UI, project model, voice management, hardware abstraction, branding, and product identity.

---

## Current Development Phase

Current milestone:

**Milestone 0.4 — First VibeVoice-Compatible Inference Prototype**

The current codebase is intentionally small.

Do not introduce AI inference frameworks, GUI frameworks, model downloads, cloud infrastructure, or other large dependencies until the relevant milestone requires them.

---

## Development Environment

Primary development environment:

- Windows 11
- Visual Studio Code
- Python 3.12
- Project virtual environment: `.venv`
- Git repository root: `C:\Projects\Impersono`

Current supported Python range is defined in `pyproject.toml`.

Do not casually upgrade Python or dependencies in a known-good environment.

---

## Core Commands

Activate the virtual environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project in editable mode:

```powershell
python -m pip install -e .
```

Run Impersono:

```powershell
python -m impersono
```

Run tests:

```powershell
python -m pytest -q
```

Before assuming GitHub matches the local machine, check:

```powershell
git status
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

## Architectural Boundaries

### UI and inference must remain separate

Do not put model-specific inference logic into the desktop UI.

Preferred direction:

```text
Desktop UI
    |
    v
Application Services
    |
    v
Impersono Core
    |
    v
Voice Engine Interface
    |
    v
Inference Backend
```

### Engine independence is mandatory

VibeVoice is an initial quality reference and likely early backend.

It must not define the entire application architecture.

Future engines may include other local TTS/voice-cloning systems.

The UI should depend on Impersono abstractions rather than directly on a specific model implementation.

### Hardware discovery is a core service

Hardware detection belongs under:

```text
src/impersono/core/hardware/
```

Raw detection data and user-facing presentation/recommendations should remain separable.

Do not build hardware detection around NVIDIA-only assumptions.

---

## VibeVoice Relationship

The known-good VibeVoice installation is separate from Impersono.

Primary working VibeVoice installation:

```text
C:\AI\VibeVoice
```

A sealed long-term VibeVoice Gold Master also exists outside this repository.

**Never modify the sealed Gold Master as part of Impersono development.**

Do not casually modify the known-good VibeVoice installation either.

When VibeVoice integration begins:

- inspect the known-good implementation first
- identify the minimum required inference path
- preserve output quality
- isolate VibeVoice-specific behavior behind an Impersono adapter/interface
- review third-party licenses and redistribution implications before commercial packaging

Do not depend on the VibeVoice Gradio interface.

---

## Privacy Requirements

Local-first processing is a product requirement, not merely marketing.

When Local Mode exists:

- reference voices remain local
- generated audio remains local
- project data remains local
- voice metadata remains local
- voice content must not be uploaded silently

Future Cloud Mode must be explicitly selected.

There must never be a silent local-to-cloud fallback.

Do not introduce telemetry that collects voice content.

---

## User Data and Generated Data

Directories such as `voices/` and `output/` represent local user/generated data and are intentionally excluded from Git except for placeholder files.

Do not commit:

- user voice recordings
- generated voice outputs
- model weights
- local caches
- secrets
- credentials
- personal user data

Do not casually change future persistent project/voice formats without considering backward compatibility.

---

## Model and Large-File Rules

Do not commit model weights to the source repository.

Examples include:

- `.safetensors`
- `.ckpt`
- `.pt`
- `.pth`
- large model `.bin` files

Model management will receive its own architecture later.

Model names, revisions, hashes, licenses, and runtime requirements should be recorded when models become part of a known-good configuration.

---

## Dependency Rules

Dependencies must be intentional.

Before adding or upgrading a significant dependency:

- explain why it is needed
- inspect current versions
- check Python compatibility
- consider Windows packaging impact
- consider security
- consider license/commercial-use implications
- consider whether a separate experimental environment is safer

Do not upgrade dependencies simply because newer versions exist.

---

## Commercial and Third-Party Code Rules

Impersono is intended for possible commercial distribution.

Before incorporating substantial third-party code, models, or research implementations, consider:

- license
- commercial-use rights
- redistribution rights
- attribution requirements
- provenance
- maintenance status
- production suitability
- security
- long-term availability

Research code does not automatically become production code.

Prefer adapters/interfaces over copying large third-party implementations into Impersono where practical.

---

## Development Workflow

The preferred project-specific loop is:

```text
UNDERSTAND
-> INSPECT CURRENT GITHUB SOURCE
-> PLAN
-> MAKE THE SMALLEST SAFE CHANGE
-> APPLY LOCALLY
-> REVIEW
-> USER TESTS LOCALLY
-> INVESTIGATE FAILURES
-> FIX
-> VERIFY
-> COMMIT/PUSH AT A USEFUL CHECKPOINT
-> INSPECT PUSHED RESULT
-> MERGE ONLY AFTER USER APPROVAL
```

ChatGPT can inspect GitHub but should not assume it can directly write to the user's Windows filesystem.

For meaningful multi-file changes, prefer a controlled local update script over repeated manual copy/paste. Prefer Python update scripts when file encoding or Unicode may matter on Windows.

Do not require a Git push after every individual file change.

---

## Branch Safety

`main` should represent the last known-good state whenever practical.

Use coherent branches such as:

```text
feature/...
fix/...
chore/...
refactor/...
docs/...
```

Do not force-push `main`.

Do not merge machine-dependent work merely because the source looks correct.

Wait for explicit local test confirmation and explicit user approval before merge.

---

## Local Testing Authority

The user's Windows PC is the authority for:

- GUI behavior
- audio playback
- microphones
- speakers
- FFmpeg
- model inference
- CPU/GPU behavior
- CUDA
- future ROCm/DirectML behavior
- VRAM reporting
- Windows filesystem behavior
- installers
- packaged executables
- environment variables
- machine-specific dependencies

Do not claim these are verified until the user has actually tested them or a suitable automated test genuinely proves the behavior.

---

## Scope Discipline

Do not opportunistically refactor unrelated working code.

Do not combine unrelated:

- feature work
- dependency upgrades
- formatting changes
- directory reorganizations
- architecture rewrites

without a compelling reason.

If unrelated technical debt is found, report it separately.

---

## Documentation

Keep these documents aligned with the product:

- `Readme.md`
- `docs/DESIGN_PRINCIPLES.md`
- `docs/ROADMAP.md`
- `CHANGELOG.md`
- `AGENTS.md`

Temporary debugging information should not be placed in `AGENTS.md`.

---

## Known Current Baseline

The current package identity is:

```text
Impersono 0.1.0-dev
```

Known-good baseline behavior:

```powershell
python -m impersono
```

prints the application identity and environment information.

Current automated baseline:

```powershell
python -m pytest -q
```

passes the package, hardware, compatibility, and CLI tests.

Hardware discovery commands:

```powershell
python -m impersono --hardware
python -m impersono --compatibility
```

Milestone 0.2 established the hardware discovery and compatibility layers without adding runtime dependencies.

Milestone 0.3 established the backend-independent voice engine contract, engine registry, common inference models and errors, progress/cancellation boundary, and standardized engine lifecycle status.

The current automated baseline is **24 passing tests** on the primary Windows development machine.

The next milestone is **Milestone 0.4 — First VibeVoice-Compatible Inference Prototype**. Preserve the engine boundary: inspect the known-good VibeVoice implementation first, isolate VibeVoice-specific behavior behind an Impersono engine implementation, and do not make the rest of the application depend directly on VibeVoice or its Gradio interface.

---

## Guiding Rule

When uncertain between a quick shortcut and a clean boundary, prefer the smallest design that preserves Impersono's long-term architecture without adding premature complexity.
