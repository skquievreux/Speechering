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
