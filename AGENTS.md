# Agent Guidelines for Voice Transcriber

## Build/Lint/Test Commands

### Testing
- Run all tests: `pytest`
- Run single test: `pytest tests/test_filename.py::TestClass::test_method`
- Run with coverage: `pytest --cov=src`
- Run specific test markers: `pytest -m "unit"` or `pytest -m "integration"`

### Linting & Formatting
- Lint code: `pylint src/`
- Format Python: `black src/`
- Format other files: `prettier --write "**/*.{md,yml,yaml,json,js,ts,html,css}"`

### Building
- Build EXE: `python build.py`
- Build with installer: `python build.py --installer`
- Build bootstrap installer: `python build.py --bootstrap`

## Code Style Guidelines

### Python Conventions
- **Formatting**: Use Black for consistent Python formatting
- **Imports**: Standard library → third-party → local imports
- **Relative imports**: Use try/except pattern for relative/local imports fallback
- **Naming**: PascalCase for classes, snake_case for functions/variables/methods
- **Type hints**: Use typing module for function signatures and variables
- **Docstrings**: German docstrings for main modules explaining purpose

### General Formatting
- **Prettier config**: No semicolons, double quotes, 2-space indentation, 80 char width, LF line endings
- **Line length**: 80 characters maximum
- **Tabs vs spaces**: Spaces only (2 spaces for non-Python files)

### Error Handling
- **Custom exceptions**: Use exceptions from `src/exceptions.py`
- **Comprehensive handling**: Catch and handle all foreseeable error conditions
- **Logging**: Use logging module with appropriate levels
- **User feedback**: Provide clear error messages for user-facing errors

### Security
- **Secrets**: Never commit API keys or sensitive data
- **Encryption**: Use secure_storage for sensitive user data
- **Environment variables**: Load from .env files with python-dotenv

### File Organization
- **Source code**: Place in `src/` directory
- **Tests**: Place in `tests/` directory matching source structure
- **Assets**: Place in `assets/` directory
- **Scripts**: Place in `scripts/` directory</content>
<parameter name="filePath">/home/ladmin/Desktop/GIT/Speechering/AGENTS.md