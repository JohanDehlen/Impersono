# Impersonic Changelog

All significant changes to Impersonic will be documented in this file.

Impersonic uses milestone-based development during the pre-release phase. Version numbers will be introduced as the application approaches public testing and release.

---

## Unreleased

### Development Workflow

- Added project-specific `AGENTS.md`.
- Established GitHub as the shared inspection/history source for pushed code.
- Established the local Windows working tree as the runtime source for unpushed changes.
- Adopted controlled local update scripts for meaningful multi-file guided changes where they reduce manual copy/paste.
- Confirmed that commits and pushes should occur at useful checkpoints rather than after every file modification.
- Established explicit local testing and user approval before merging machine-dependent changes.

### Milestone 0.2 — Hardware Discovery

#### Added

- Added a structured hardware discovery subsystem under `src/impersonic/core/hardware/`.
- Added operating-system, architecture, Python, CPU-model, logical-core, and system-RAM detection.
- Added Windows GPU discovery with GPU name, vendor, and dedicated VRAM where available.
- Added conservative NVIDIA driver/CUDA-tool detection without assuming that CUDA inference is automatically usable.
- Added generic hardware capability assessment separate from raw detection.
- Added a VibeVoice 1.5B compatibility profile separate from generic hardware facts.
- Added explicit compatibility states for known paths, candidates, unconfirmed paths, and unavailable paths.
- Added user-facing hardware and model-compatibility report formatting.
- Added `python -m impersonic --hardware`.
- Added `python -m impersonic --compatibility`.
- Added automated hardware, compatibility, and CLI tests.

#### Design Decisions

- Kept hardware detection independent from the future desktop UI.
- Kept model-specific compatibility separate from raw hardware discovery.
- Avoided hard-coding Impersonic as an NVIDIA-only application.
- Avoided claiming that a detected AMD or other non-NVIDIA GPU is supported before runtime verification.
- Kept model file size separate from RAM/VRAM requirements.
- Deferred model-fit thresholds until actual runtime memory behavior is measured.
- Added no new runtime Python dependencies for this milestone.

#### Local Validation

The primary Windows development machine successfully reported:

- Windows 11 / AMD64
- Intel Xeon E3-1230 v3 CPU
- 8 logical CPU cores
- approximately 15.9 GB system RAM
- AMD Radeon HD 7000 series GPU
- approximately 1.0 GB dedicated VRAM
- no NVIDIA driver/CUDA tooling detected

The VibeVoice 1.5B compatibility report correctly kept the CPU route as a known path and the detected AMD GPU route as unconfirmed.

---

### Milestone 0.1 — Project Foundation

#### Added

- Created the Impersonic project.
- Established Python 3.12 as the initial development baseline.
- Created an isolated Python virtual environment.
- Created the initial project directory structure.
- Added Git ignore rules for:
  - Python temporary files
  - virtual environments
  - development tools
  - generated audio
  - local voice data
  - AI model files
  - Hugging Face caches
  - logs
  - secrets
  - temporary files
- Added placeholder files to preserve empty output and voice directories.
- Added project README.
- Added design principles.
- Added development roadmap.
- Added initial Python package and executable module entry point.
- Added initial package identity test.
- Verified `python -m impersonic`.
- Verified the initial automated test suite.
- Created and pushed the first known-good Git milestone.

#### Architecture

Established the initial planned separation between:

- desktop user interface
- application services
- Impersonic core
- hardware detection
- audio processing
- voice management
- project management
- inference engines

Established engine independence as a core architectural requirement.

VibeVoice will initially serve as an inference reference and quality benchmark rather than defining the Impersonic application architecture.

#### Privacy

Established local-first processing as a core product principle.

Primary privacy message:

> Your voices stay on your computer.

Established that future cloud processing must:

- remain optional
- be explicitly selected by the user
- clearly disclose when voice data leaves the local computer
- never silently replace local processing

#### Development Process

Established the following development rules:

- Work in small, testable milestones.
- Inspect existing implementation before modifying it.
- Complete and test a milestone before significantly expanding scope.
- Keep UI code separate from inference logic.
- Avoid unnecessary dependencies.
- Preserve known-good working states.
- Document important architectural decisions.
- Prefer controlled local update scripts over repeated manual copy/paste for meaningful multi-file changes.
- Commit and push to GitHub at meaningful checkpoints rather than after every individual file change.
- Review pushed results when exact shared state matters.
- Require local testing and explicit approval before merging machine-dependent changes.

---

## Project Beginning

Impersonic was started as an independent local-first AI voice creation project.

Initial product positioning:

**Impersonic**

**Professional Local AI Voice Creation**

Initial objective:

Build a professional desktop application capable of high-quality local AI voice cloning and text-to-speech while preserving user privacy and maintaining the ability to support multiple inference engines over time.
