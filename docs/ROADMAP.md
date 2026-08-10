# Impersonic Roadmap

## Product

**Impersonic**

**Professional Local AI Voice Creation**

Core privacy message:

> Your voices stay on your computer.

---

## Development Approach

Impersonic will be developed in small, testable milestones.

A milestone should not be considered complete until its main functionality is:

- working
- tested
- cleaned up
- documented
- reviewed

GitHub commits and pushes should occur at meaningful milestones rather than after every minor file change.

---

# Milestone 0.1 — Project Foundation

## Goal

Establish a clean, professional foundation before introducing AI inference code.

## Scope

- [x] Create local project directory
- [x] Create Python 3.12 virtual environment
- [x] Create clean repository structure
- [x] Create `.gitignore`
- [x] Create placeholder folders for output and voices
- [x] Create `README.md`
- [x] Create `docs/DESIGN_PRINCIPLES.md`
- [ ] Create `docs/ROADMAP.md`
- [ ] Create `CHANGELOG.md`
- [ ] Create initial Python package
- [ ] Create application entry point
- [ ] Confirm `python -m impersonic` runs
- [ ] Add basic automated test
- [ ] Review project structure
- [ ] Make first milestone Git commit
- [ ] Push milestone to GitHub

## Completion Standard

The project should have a clean repository, documentation, a runnable Python package, and a basic test suite without yet depending on VibeVoice or any large AI framework.

---

# Milestone 0.2 — Hardware Discovery

## Goal

Allow Impersonic to understand the computer it is running on before attempting model installation or inference.

## Planned Scope

- Detect operating system
- Detect Python environment
- Detect CPU
- Detect system RAM
- Detect available GPU devices
- Detect GPU vendor
- Detect VRAM where available
- Detect CUDA availability
- Evaluate future AMD acceleration options
- Produce a user-friendly hardware summary
- Separate raw hardware data from UI presentation
- Add automated tests where practical

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