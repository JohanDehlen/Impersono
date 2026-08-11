# Impersono Roadmap

## Product

**Impersono**

**Professional Local AI Voice Creation**

Core privacy message:

> Your voices stay on your computer.

---

## Development Approach

Impersono will be developed in small, testable milestones.

A milestone should not be considered complete until its main functionality is:

- working
- tested
- cleaned up
- documented
- reviewed

GitHub commits and pushes should occur at meaningful checkpoints rather than after every minor file change.

---

# Milestone 0.1 — Project Foundation

## Status

**Complete**

## Goal

Establish a clean, professional foundation before introducing AI inference code.

## Scope

- [x] Create local project directory
- [x] Create Python 3.12 virtual environment
- [x] Create clean repository structure
- [x] Create `.gitignore`
- [x] Create placeholder folders for output and voices
- [x] Create `Readme.md`
- [x] Create `docs/DESIGN_PRINCIPLES.md`
- [x] Create `docs/ROADMAP.md`
- [x] Create `CHANGELOG.md`
- [x] Create initial Python package
- [x] Create application entry point
- [x] Confirm `python -m impersono` runs
- [x] Add basic automated test
- [x] Review project structure
- [x] Make first milestone Git commit
- [x] Push milestone to GitHub
- [x] Establish repository-guided development workflow
- [x] Add project-specific `AGENTS.md`

## Completion Standard

The project has a clean repository, documentation, a runnable Python package, and a basic test suite without yet depending on VibeVoice or any large AI framework.

---

# Milestone 0.2 — Hardware Discovery

## Status

**Complete**

## Goal

Allow Impersono to understand the computer it is running on before attempting model installation or inference.

## Completed Scope

- [x] Detect operating system
- [x] Detect Python environment
- [x] Detect CPU model and logical CPU count
- [x] Detect system RAM
- [x] Detect available GPU devices on Windows
- [x] Detect GPU vendor
- [x] Detect dedicated VRAM where Windows exposes it
- [x] Detect NVIDIA driver/CUDA tooling availability conservatively
- [x] Design extensible acceleration capability reporting
- [x] Preserve future AMD and other acceleration options without hard-coding the product to NVIDIA
- [x] Produce a user-friendly hardware summary
- [x] Separate raw hardware data from presentation and compatibility assessment
- [x] Add automated tests
- [x] Add VibeVoice 1.5B compatibility guidance without inventing RAM/VRAM thresholds
- [x] Add `python -m impersono --hardware`
- [x] Add `python -m impersono --compatibility`
- [x] Validate hardware discovery on the primary Windows development machine

## Completion Notes

Milestone 0.2 intentionally does not claim that every detected GPU is usable for AI inference.

Raw hardware detection, generic capability assessment, and model-specific compatibility guidance remain separate layers.

The current VibeVoice 1.5B compatibility profile treats:

- the established CPU route as a known execution path
- NVIDIA plus working driver tooling as a candidate requiring runtime verification
- other detected GPUs as unconfirmed until the relevant runtime is actually proven
- model file size as separate from runtime RAM/VRAM requirements

Detailed model-fit thresholds should be based on measured runtime behavior rather than guessed values.

## Desired User Experience

Example:

```text
Hardware Status

CPU:
AMD Ryzen 9

RAM:
32 GB

GPU:
NVIDIA RTX 4070

VRAM:
12 GB

Local AI capability:
Good

Recommended model tier:
Medium
```

The user should not need to understand CUDA, ROCm, DirectML, or model internals.

---

# Milestone 0.3 — Voice Engine Interface

## Status

**Complete**

## Goal

Create the abstraction that allows Impersono to support multiple AI voice engines.

## Completed Scope

- [x] Define stable engine identity metadata
- [x] Define engine capability discovery
- [x] Define engine-independent model metadata
- [x] Define model loading and unloading operations
- [x] Define engine-independent generation requests and results
- [x] Support reference-voice conditioning through the common request boundary
- [x] Define normalized progress callbacks
- [x] Define cancellation through the common engine contract
- [x] Define common inference error types
- [x] Add an engine registry for discovery and selection by stable engine ID
- [x] Define standardized engine lifecycle states
- [x] Expose engine status, loaded-model identity, and optional status messages
- [x] Keep framework-specific objects out of the public engine contract
- [x] Add automated tests for the interface, registry, and lifecycle state

## Completion Notes

The interface is intentionally backend-independent. It does not expose PyTorch,
VibeVoice, ONNX, subprocess, or GUI-specific objects.

Engine-specific generation controls can remain in a generic options mapping until
a control proves stable enough to become part of the Impersono-level abstraction.

The lifecycle model exposes high-level states such as unloaded, loading, ready,
generating, cancelling, and error without prescribing how a backend implements
those transitions.

Possible future engines:

```text
Impersono Voice Engine Interface
        |
        +-- VibeVoice Backend
        +-- Qwen TTS Backend
        +-- Other Local Engine
        `-- Future Impersono Engine
```

## Completion Standard

**Met.** The application now has a backend-independent boundary through which
voice engines can be added or replaced without requiring the future desktop UI
to depend directly on a specific inference implementation.

---

# Milestone 0.4 — First VibeVoice-Compatible Inference Prototype

## Status

**Complete**

## Goal

Generate speech from Impersono without using the VibeVoice Gradio interface.

## Completed Scope

- [x] Study the known-good VibeVoice inference path
- [x] Identify the processor/model components required for VibeVoice 1.5B inference
- [x] Create a concrete `VibeVoiceEngine` behind the engine-independent Impersono interface
- [x] Keep VibeVoice, PyTorch, and model objects isolated behind an optional runtime boundary
- [x] Add lazy optional-runtime dependency detection
- [x] Implement the native VibeVoice processor/model loader
- [x] Validate the CPU `float32` + SDPA model-loading path on the primary Windows development machine
- [x] Preserve a CUDA BF16/Flash-Attention-first path with SDPA fallback for future compatible machines
- [x] Implement real single-speaker text generation without the VibeVoice Gradio interface
- [x] Support optional reference-voice conditioning through `GenerationRequest.voice_reference`
- [x] Save generated WAV output through the VibeVoice processor
- [x] Report generated-audio duration
- [x] Add Impersono-owned fixed-level WAV normalization
- [x] Add automated tests for backend behavior, runtime loading, generation, and WAV normalization
- [x] Validate real VibeVoice 1.5B model loading from the existing local model cache
- [x] Validate real CPU speech generation
- [x] Validate real reference-voice conditioning by local listening comparison
- [x] Validate final normalized output by side-by-side listening comparison with the reference voice

## Validated Prototype Configuration

Primary locally validated configuration:

```text
Model: VibeVoice 1.5B
Device: CPU
Precision: float32
Attention: SDPA
DDPM inference steps: 10
CFG scale: 1.3
Reference handling: original reference file passed directly to VibeVoiceProcessor
Output: 24 kHz WAV
Output normalization: -16 dBFS RMS target, -1 dBFS peak ceiling
```

The direct original reference file produced substantially better voice fidelity than an externally resampled/mono 24 kHz copy during local comparison. Impersono therefore leaves reference-audio preprocessing to the VibeVoice processor for this prototype.

The first unnormalized conditioned output measured about 8.57 dB lower in RMS level than the comparison reference. Impersono now applies a fixed, configurable output-level normalization step rather than matching every generation to the loudness of its reference recording.

## Validation Notes

The real VibeVoice 1.5B model successfully loaded through the Impersono runtime adapter on the primary Windows development machine.

Real speech generation and reference-voice conditioning both succeeded. Local listening confirmed that the final level-normalized conditioned output compared very well with the source reference voice.

The automated suite passes with **49 tests**.

Runtime memory usage was not formally benchmarked in this milestone. Repeatable quality, speed, and memory measurement belongs in Milestone 0.5 and later performance work rather than being guessed from a single prototype run.

## Initial Quality Requirement

**Met for the prototype.** The result was not accepted merely because it produced audio; the locally generated conditioned speech was reviewed for voice similarity and output level, and the final result compared very well with the reference voice.

This is a prototype-quality validation, not yet a formal benchmark suite.

---

# Milestone 0.5 — Quality Benchmark Suite

## Goal

Create repeatable tests so future engine or dependency changes do not silently reduce voice quality.

## Planned Benchmark Areas

- voice similarity
- intelligibility
- pronunciation
- pacing
- prosody
- emotional consistency
- long-form consistency
- generation time
- RAM use
- VRAM use
- output stability

## Benchmark Assets

Create a controlled test library containing:

- approved reference voice samples
- fixed scripts
- short-form tests
- long-form tests
- difficult names and pronunciation tests
- punctuation tests
- number/date tests

Benchmark material must use voices for which appropriate permission exists.

---

# Milestone 0.6 — Basic Desktop Shell

## Goal

Create the first real Impersono desktop interface.

## Initial UI

The first version should be deliberately simple.

```text
Impersono

Voice:
[ Select Voice ]

Text:
+--------------------------------------+
| Enter text here...                   |
|                                      |
+--------------------------------------+

[ Generate ]

Output:
[ Play ] [ Save ]
```

## Planned Scope

- Application window
- Impersono branding
- Text input
- Voice selector
- Generate button
- Progress state
- Audio playback
- Save/export
- User-friendly error messages
- Background generation so UI remains responsive

No advanced model controls should dominate the primary workflow.

---

# Milestone 0.7 — Voice Import and Cloning Workflow

## Goal

Allow a user to create a reusable Impersono voice from a reference recording.

## Planned Workflow

```text
Create Voice
    |
    +-- Record microphone
    |
    `-- Import audio file
            |
            v
       Analyze sample
            |
            v
       Create voice
            |
            v
       Preview
            |
            v
       Save to Voice Library
```

## Planned Scope

- WAV import
- additional audio formats where appropriate
- microphone recording
- sample validation
- silence detection
- duration checks
- sample quality guidance
- voice naming
- preview generation
- voice metadata
- consent confirmation

---

# Milestone 0.8 — Voice Library

## Goal

Make voices first-class reusable assets.

## Planned Scope

Each voice may contain:

- name
- source reference
- creation date
- language
- tags
- notes
- engine compatibility
- preview audio
- consent information
- optional avatar
- engine-specific conditioning assets

## User Features

- create
- rename
- duplicate
- delete
- search
- filter
- preview
- export
- import

The library should remain portable where practical.

---

# Milestone 0.9 — Generation Controls

## Goal

Provide useful control without exposing unnecessary research-model complexity.

## Candidate Controls

- speaking speed
- generation seed
- expressiveness
- temperature where meaningful
- inference steps where meaningful
- voice strength where meaningful
- output format
- sample rate

Controls must be exposed only when they provide reliable value.

Engine-specific controls should live behind advanced settings rather than polluting the main interface.

---

# Milestone 0.10 — Project System

## Goal

Allow users to save complete Impersono work sessions.

## Possible Project Data

- script text
- selected voice
- selected engine
- generation settings
- output references
- project notes
- project metadata
- version information

## Requirements

- readable/documented format where practical
- backward compatibility
- safe recovery
- recent-project list
- autosave/recovery strategy

---

# Milestone 0.11 — Local Privacy Experience

## Goal

Make Impersono's local-first privacy promise visible in the product.

## Planned UI

Example:

```text
LOCAL MODE

This generation stays on your computer.
```

The application should clearly indicate:

- where inference is happening
- whether network access is required
- whether voice data is leaving the machine

No silent fallback from local to cloud is allowed.

---

# Milestone 0.12 — Model Management

## Goal

Make local AI model installation manageable for non-technical users.

## Planned Scope

- available model list
- model size
- disk requirement
- RAM/VRAM requirement
- download progress
- model version
- integrity verification
- uninstall model
- repair model
- offline model import
- model storage location

Users should not need to manually navigate Hugging Face cache folders.

---

# Milestone 0.13 — Performance and Hardware Profiles

## Goal

Automatically recommend suitable models and settings.

## Possible Profiles

```text
CPU Only
Entry GPU
Mid-range GPU
High-end GPU
Workstation
```

The application should favor reliable recommendations over aggressive settings.

---

# Milestone 0.14 — Long-Form Generation

## Goal

Support professional narration and long scripts reliably.

## Planned Scope

- long script processing
- chunking
- sentence/paragraph boundaries
- continuity between chunks
- progress tracking
- cancellation
- recovery after interruption
- output assembly
- long-form benchmark testing

This milestone is especially important for:

- YouTube narration
- audiobooks
- podcasts
- educational content

---

# Milestone 0.15 — Multi-Speaker Generation

## Goal

Support conversations and multi-speaker content.

## Planned Scope

- multiple voices per project
- speaker labels
- dialogue parsing
- speaker assignment
- consistent voice identity
- export of combined audio
- optional separated speaker tracks

---

# Milestone 0.16 — Voice Design

## Goal

Investigate creation of voices without requiring an existing reference speaker.

Possible workflow:

```text
Describe a voice
        |
        v
Generate candidate
        |
        v
Preview
        |
        v
Refine
        |
        v
Save Voice
```

This milestone depends on available model capabilities and licensing.

---

# Milestone 0.17 — Voice Conversion

## Goal

Evaluate speech-to-speech voice conversion.

Potential uses:

- preserve timing while changing voice
- dubbing workflows
- performance transfer
- correction of existing narration

This feature should be implemented only if quality reaches the Impersono product standard.

---

# Milestone 0.18 — Scriptolator Integration

## Goal

Allow Scriptolator to use Impersono as an optional narration engine while keeping both projects completely separate.

Possible future integration:

```text
Scriptolator
    |
    +-- Microsoft Edge
    +-- Microsoft Azure
    +-- Impersono Local
    `-- Impersono Cloud
```

Integration should use a documented interface rather than sharing internal code between the projects.

---

# Milestone 0.19 — Optional Impersono Cloud

## Goal

Provide access to powerful inference for users without suitable local hardware.

## Principles

Cloud is optional.

Local remains the default philosophy.

Cloud use must be explicit.

## Planned Scope

- secure upload
- encrypted transport
- temporary processing
- clear retention policy
- generation queue
- GPU workers
- credit accounting
- job status
- downloadable results
- automatic deletion policy

Possible user experience:

```text
Your computer cannot run this model efficiently.

Choose:

[ Use Smaller Local Model ]

[ Generate in Impersono Cloud ]
```

---

# Milestone 0.20 — Web Application

## Goal

Allow users to use Impersono without installing the desktop application.

## Planned Workflow

```text
Sign in
   |
Upload or select voice
   |
Enter text
   |
Generate
   |
Preview
   |
Download
```

The web product should clearly disclose that uploaded voice data is processed remotely.

---

# Milestone 0.21 — Accounts and Licensing

## Goal

Introduce commercial product infrastructure.

Possible capabilities:

- account creation
- desktop license
- license activation
- offline-friendly licensing strategy
- purchased cloud credits
- billing history
- subscription options if appropriate
- enterprise licensing

The application should not become unusable merely because a licensing server is temporarily unavailable.

---

# Milestone 0.22 — Cloud Credits

## Goal

Provide sustainable GPU monetization.

Initial preference:

Usage-based credits rather than unlimited inference.

Possible billing units may consider:

- generated audio duration
- model tier
- GPU time
- generation complexity

Pricing should remain understandable to users.

---

# Milestone 0.23 — Website and Commercial Launch Infrastructure

## Planned Scope

- impersono.com
- product pages
- documentation
- account portal
- downloads
- pricing
- privacy policy
- terms
- responsible-use policy
- support
- update distribution

---

# Milestone 0.24 — Installer and Update System

## Goal

Create a polished Windows installation experience.

## Planned Scope

- signed installer
- installation directory
- shortcuts
- model storage choices
- FFmpeg/runtime requirements
- clean uninstall
- update checking
- controlled application updates
- model updates separate from application updates where practical

---

# Milestone 0.25 — Security and Privacy Review

## Planned Areas

- secret handling
- filesystem permissions
- cloud authentication
- API security
- voice upload handling
- temporary-file deletion
- log sanitization
- dependency vulnerabilities
- update integrity
- model integrity
- privacy review

---

# Milestone 0.26 — Accessibility and UX Review

## Planned Areas

- keyboard navigation
- high-DPI support
- readable contrast
- screen-reader considerations
- clear focus states
- scalable UI
- understandable errors
- loading/progress feedback

---

# Milestone 0.27 — Beta

## Goal

Test Impersono outside the development environment.

## Beta Requirements

- stable installer
- tested inference
- working voice library
- hardware detection
- local privacy mode
- usable documentation
- crash/error reporting strategy
- known-issues list
- clean upgrade path

---

# Milestone 1.0 — First Commercial Release

## Product Standard

Version 1.0 should feel like a finished application, not a research preview.

Minimum expectations:

- professional Windows UI
- reliable local generation
- excellent voice quality
- voice cloning
- reusable voice library
- hardware detection
- model management
- strong privacy messaging
- export workflow
- project stability
- documentation
- installer
- licensing
- reproducible builds
- third-party notices
- tested upgrade process

Optional cloud capabilities do not have to block the desktop 1.0 release if the local product is commercially strong without them.

---

# Post-1.0 Possibilities

Future development may include:

- additional voice engines
- macOS support
- Linux support
- advanced dubbing
- translation
- pronunciation dictionaries
- timeline editing
- batch generation
- audiobook workflows
- collaborative projects
- enterprise deployment
- API
- marketplace
- user-created voice packs
- approved commercial voice marketplace
- Impersono-native models

These ideas are not commitments.

Quality and product focus take priority over feature count.

---

# Guiding Principle

Every milestone should move Impersono toward one goal:

> Build the best professional local-first AI voice creation platform we can.
