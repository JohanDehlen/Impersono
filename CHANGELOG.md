# Impersonic Changelog

All significant changes to Impersonic will be documented in this file.

Impersonic uses milestone-based development during the pre-release phase. Version numbers will be introduced as the application approaches public testing and release.

---

## Unreleased

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
- Complete and test a milestone before significantly expanding scope.
- Keep UI code separate from inference logic.
- Avoid unnecessary dependencies.
- Preserve known-good working states.
- Document important architectural decisions.
- Provide complete replacement files during guided development rather than partial line edits.
- Commit and push to GitHub at meaningful milestones rather than after every individual file change.

---

## Project Beginning

Impersonic was started as an independent local-first AI voice creation project.

Initial product positioning:

**Impersonic**

**Professional Local AI Voice Creation**

Initial objective:

Build a professional desktop application capable of high-quality local AI voice cloning and text-to-speech while preserving user privacy and maintaining the ability to support multiple inference engines over time.