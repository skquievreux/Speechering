# Build System Learnings: Versioning & Dependency Synchronization

## Overview
This document summarizes the technical challenges and solutions implementation (Jan 2026) regarding the Voice Transcriber build system, specifically focusing on cross-component version synchronization and PyInstaller stability.

## 1. The "Single Source of Truth" Versioning Issue

### The Problem
Versions were hardcoded in multiple locations:
- `pyproject.toml` (Poetry/Dev)
- `src/config.py` (Runtime)
- `tools/installer.nsi` (Full Installer metadata)
- `tools/bootstrap_installer.nsi` (Bootstrap metadata)

This led to "Versionschaos" where the app reported 1.9.3 while the installer was tagged as 1.5.0, confusing both users and CI build logic.

### The Solution: Dynamic Injection
We implemented a build pipeline in `tools/build.py` that:
1.  **Extracts** the version from `pyproject.toml` at the start of the build.
2.  **Generates** a transient module `src/_version.py` containing `__version__ = "X.Y.Z"`.
3.  **Imports** this version in `src/config.py` at runtime.
4.  **Injects** the version into NSIS scripts using the `/DVERSION=true` command-line flag during compilation.

**Developer Note**: Do *not* manually update `src/_version.py`. Always update `pyproject.toml`.

## 2. PyInstaller & AI Module Exclusions

### The Conflict: Size vs. Functionality
To minimize EXE size (~50MB), we previously excluded:
- `numpy`, `faster_whisper`, `ctranslate2`, `tokenizers`, `huggingface_hub`.

### The Learning
While this reduces size, it BREAKS the "Local Model" feature at runtime. The user would see `DistributionNotFound` or `ModuleNotFoundError` when trying to use local transcription.

### The Solution: Hybrid Packaging
- **Onedir Mode**: Always preferred for the full installer to prevent DLL corruption.
- **Hidden Imports**: Explicitly add AI modules back into `tools/build.py` hidden imports.
- **Removed Exclusions**: We stopped excluding these crates to ensure that the "Local Model" download logic actually has the engines needed to run the downloaded files.

## 3. The Jaraco/pkg_resources Dilemma

### The Challenge
Nested dependencies like `jaraco.text` or `jaraco.functools` are often used by namespace-package based libraries. PyInstaller's hooks often fail to collect them, leading to runtime failures.

### Failed Attempt: `--copy-metadata`
We tried using `--copy-metadata=jaraco.*`, but this caused issues in CI environments where the build environment might differ from the runtime environment.

### Final Solution: Explicit Strict Imports
In `tools/build.py`, we use:
```python
"--hidden-import=jaraco",
"--hidden-import=jaraco.text",
"--hidden-import=jaraco.classes",
"--hidden-import=jaraco.context",
"--hidden-import=jaraco.functools",
```
This is the most robust way to ensure PyInstaller bundles the necessary paths without relying on fragile auto-hooks.

## 4. GitHub Actions Synchronization

### Rebase Workflow
When working on build system changes in a branch:
- **Frequent Rebasing**: Essential because `tools/build.py` and workflows change often in `main`.
- **MSYS Path Conversion**: When running `makensis` or other EXE tools in Git Bash (default shell for some GA steps), use `MSYS_NO_PATHCONV=1` to prevent Windows paths (starting with `/`) from being converted to Linux-style paths unnecessarily.

## Summary for Developers
- **Single Source of Truth**: `pyproject.toml`.
- **Build Mode**: Use `poetry run python tools/build.py --installer`.
- **Verification**: Check artifact size. If it's < 60MB, AI modules might be missing.
