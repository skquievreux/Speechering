## [2.0.4](https://github.com/skquievreux/Speechering/compare/v2.0.3...v2.0.4) (2026-02-02)


### Bug Fixes

* **transcription:** prevent silent fallback to API when torch missing ([fc56990](https://github.com/skquievreux/Speechering/commit/fc5699071606e9c98e7a6cace01a78619db59afd))

## [2.0.3](https://github.com/skquievreux/Speechering/compare/v2.0.2...v2.0.3) (2026-02-01)


### Bug Fixes

* **build:** resolve remaining NameError bugs ([bd06e9b](https://github.com/skquievreux/Speechering/commit/bd06e9bed2853ce44f1e262f3e222e0736bb664e))

## [2.0.2](https://github.com/skquievreux/Speechering/compare/v2.0.1...v2.0.2) (2026-02-01)


### Bug Fixes

* **build:** resolve sys NameError and NSIS encoding issues ([59e9d49](https://github.com/skquievreux/Speechering/commit/59e9d49957b4e517524db8c4f1066eac0c2240c5))

## [2.0.1](https://github.com/skquievreux/Speechering/compare/v2.0.0...v2.0.1) (2026-02-01)


### Bug Fixes

* **transcription:** clarify paths and icons in frozen build ([14b8002](https://github.com/skquievreux/Speechering/commit/14b8002cd8f14b50a4ef1c44200ed7d58caac660))

# [2.0.0](https://github.com/skquievreux/Speechering/compare/v1.9.6...v2.0.0) (2026-02-01)


### Bug Fixes

* **core:** stability improvements and bug fixes ([a533084](https://github.com/skquievreux/Speechering/commit/a533084e558c0699506ddd505a46658a82a8cb90))
* **merge:** resolve conflicts in main.py and settings_gui.py ([d0098e1](https://github.com/skquievreux/Speechering/commit/d0098e123e3b57458cc9f34ba963ac4957ebcdf5))
* restore AI modules (torch) and set version to 1.9.4 for functional release ([914976d](https://github.com/skquievreux/Speechering/commit/914976d1cea4fb0a39ba5f0031e040afd7411dab))


### Features

* implement transcription history log and fix debug logging ([4977d07](https://github.com/skquievreux/Speechering/commit/4977d0789e213291e05e370fd5b335b1050ad87d))


### BREAKING CHANGES

* Debug logs now reside in %APPDATA%/VoiceTranscriber/

## [1.9.6](https://github.com/skquievreux/Speechering/compare/v1.9.5...v1.9.6) (2026-01-24)


### Bug Fixes

* restore AI modules (torch) and set version to 1.9.4 for functional release ([#40](https://github.com/skquievreux/Speechering/issues/40)) ([1407c71](https://github.com/skquievreux/Speechering/commit/1407c71f1829bdf17dce01976d53150735e51053))

## [1.9.5](https://github.com/skquievreux/Speechering/compare/v1.9.4...v1.9.5) (2026-01-24)


### Bug Fixes

* resolve syntax errors and add build system learnings ([#38](https://github.com/skquievreux/Speechering/issues/38)) ([6a37544](https://github.com/skquievreux/Speechering/commit/6a37544d62641f961a2a6b9beb35c5669509c356))

## [1.9.4](https://github.com/skquievreux/Speechering/compare/v1.9.3...v1.9.4) (2026-01-24)


### Bug Fixes

* fix versioning and restore local model download ([#37](https://github.com/skquievreux/Speechering/issues/37)) ([3d9d9c0](https://github.com/skquievreux/Speechering/commit/3d9d9c006de9574ae26878cc7ba328dbabbbcece))

## [1.9.3](https://github.com/skquievreux/Speechering/compare/v1.9.2...v1.9.3) (2026-01-24)


### Bug Fixes

* **windows:** resolve DLL loading error and missing Start Menu entries ([#19](https://github.com/skquievreux/Speechering/issues/19)) ([3928aee](https://github.com/skquievreux/Speechering/commit/3928aeef4a5d3b137f1d6677bdb6d419b81aeb4f)), closes [hi#DPI](https://github.com/hi/issues/DPI) [Hi#DPI](https://github.com/Hi/issues/DPI)

## [1.9.2](https://github.com/skquievreux/Speechering/compare/v1.9.1...v1.9.2) (2026-01-24)


### Bug Fixes

* handle encoding errors in build script subprocess ([#18](https://github.com/skquievreux/Speechering/issues/18)) ([769b87c](https://github.com/skquievreux/Speechering/commit/769b87c27b66e4eeb75934e1498df64d62d26e3f))

## [1.9.1](https://github.com/skquievreux/Speechering/compare/v1.9.0...v1.9.1) (2026-01-24)


### Bug Fixes

* explicit disable of upx by removing it from ci environment ([d949fe6](https://github.com/skquievreux/Speechering/commit/d949fe67f509f198bfab53dd56f0923501913121))

# [1.9.0](https://github.com/skquievreux/Speechering/compare/v1.8.3...v1.9.0) (2026-01-23)


### Bug Fixes

* revert invalid action versions to stable releases ([4b8d320](https://github.com/skquievreux/Speechering/commit/4b8d3202a96c49b80425352b4a89fb778f93a520))


### Features

* professionalize installer with nsis, autostart, and clean build flow ([603cdd5](https://github.com/skquievreux/Speechering/commit/603cdd5f90bc2181b6415059fdacf9fbf8c4d8ba))

## [1.8.3](https://github.com/skquievreux/Speechering/compare/v1.8.2...v1.8.3) (2026-01-23)


### Bug Fixes

* **build:** disable UPX compression to resolve 'Failed to load Python DLL' error ([4f228a6](https://github.com/skquievreux/Speechering/commit/4f228a6a4ccd9b8827721720230c045a1e5975ba))

## [1.8.2](https://github.com/skquievreux/Speechering/compare/v1.8.1...v1.8.2) (2026-01-23)


### Bug Fixes

* **deploy:** correctly detect 'dist' directory for artifacts upload ([879e4b2](https://github.com/skquievreux/Speechering/commit/879e4b2c1cf1e84d615ba414ae882415028acc98))

## [1.8.1](https://github.com/skquievreux/Speechering/compare/v1.8.0...v1.8.1) (2026-01-23)


### Bug Fixes

* **config:** aggressively auto-repair corrupt R2 URL in user config ([592c368](https://github.com/skquievreux/Speechering/commit/592c36885d6b4ce2bd842f6efeea3185099f6c39))

# [1.8.0](https://github.com/skquievreux/Speechering/compare/v1.7.0...v1.8.0) (2026-01-23)


### Features

* **bootstrap:** add comprehensive diagnostics and detailed error reporting ([#16](https://github.com/skquievreux/Speechering/issues/16)) ([7c73928](https://github.com/skquievreux/Speechering/commit/7c7392857bb770876f1206c12ac5a90cfed101d9))

# [1.7.0](https://github.com/skquievreux/Speechering/compare/v1.6.0...v1.7.0) (2026-01-23)


### Bug Fixes

* **build:** correct NSIS script paths to tools/ directory ([f64995e](https://github.com/skquievreux/Speechering/commit/f64995edf679fa7a740e8fb395112be26d4914e3))
* **build:** correct README.md path in NSIS scripts ([5917392](https://github.com/skquievreux/Speechering/commit/59173920228a373337d521e47e1e1b2d6d37bb87))
* **build:** correct relative paths in NSIS scripts for CI ([7f0e19b](https://github.com/skquievreux/Speechering/commit/7f0e19bd6a115fbc27852f16a6e07d11aab1bb26))
* **ci:** comprehensive workflow fixes ([e016163](https://github.com/skquievreux/Speechering/commit/e0161638820e89979a3d341ccf03a487865d51b5))
* **ci:** correct all bootstrap_tools references to tools/bootstrap_installer.nsi ([6843ada](https://github.com/skquievreux/Speechering/commit/6843ada0dff8aa50d5838784e730160f6508467e))
* **ci:** correct NSIS file paths to tools/ directory ([aa7ce2a](https://github.com/skquievreux/Speechering/commit/aa7ce2a5265f9f29a23603567eefe3c5b9cedbb3))
* **ci:** remove poetry cache to fix installation ([6129faf](https://github.com/skquievreux/Speechering/commit/6129faf0d9a3c4efad7abe7905b42805ee2591c5))
* **ci:** use poetry version instead of non-existent script ([a60be8b](https://github.com/skquievreux/Speechering/commit/a60be8b8f3838e85186833dadb64a8b437b0d267))
* resolve build failures and optimize startup performance ([0587fe8](https://github.com/skquievreux/Speechering/commit/0587fe8d9342a1575ed1c94c59d3b5c47f6ebc7d))


### Features

* add scrollable tabs to Settings GUI ([0c45be3](https://github.com/skquievreux/Speechering/commit/0c45be3ce9a0bd99f4ffc42e8a0f13cba67451ce))
* **gui:** improve scrollbars, add vocabulary tab and fix shutdown/Python 3.13 issues ([2c87cd5](https://github.com/skquievreux/Speechering/commit/2c87cd5e6466caf33586765ec1ee9dd3745b73e4))

# [1.6.0](https://github.com/skquievreux/Speechering/compare/v1.5.3...v1.6.0) (2026-01-17)


### Features

* optimize dependencies, UX, and logging ([5249dac](https://github.com/skquievreux/Speechering/commit/5249dac696dab13d5624bd7a8d965db261467bb0))

## [1.5.3](https://github.com/skquievreux/Speechering/compare/v1.5.2...v1.5.3) (2026-01-17)


### Bug Fixes

* **ci:** add Poetry installation to release workflow ([8372d94](https://github.com/skquievreux/Speechering/commit/8372d948869f2dfc56e2f0afde89a352070d5e90))
* **ci:** disable npm cache and ecosystem-guard for Python project ([e35227d](https://github.com/skquievreux/Speechering/commit/e35227d2699b4390e2b6a6916522705ed15f9b4c))
* **ci:** remove Node.js setup from Python workflow ([47a6669](https://github.com/skquievreux/Speechering/commit/47a6669be76085dbdca73002fe3a6c0c3f7ea7c7))
* **release:** add package.json for semantic-release compatibility ([9744475](https://github.com/skquievreux/Speechering/commit/97444751dcdf641e12312eee4d7f7110ac8c2b34))
