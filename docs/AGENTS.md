# Agent Guidelines for Voice Transcriber

## Build/Lint/Test Commands
- **Test all**: `pytest`
- **Test single**: `pytest tests/test_file.py::TestClass::test_method -v`
- **Test with coverage**: `pytest --cov=src --cov-report=term-missing`
- **Test markers**: `pytest -m "unit"` or `pytest -m "integration"`
- **Lint**: `poetry run ruff check src/`
- **Format Python**: `poetry run black src/`
- **Format other**: `prettier --write "**/*.{md,yml,yaml,json,js,ts,html,css}"`
- **Build EXE**: `python tools/build.py`

## Code Style Guidelines
- **Python**: Black (100 chars), ruff linting, isort imports (profile=black)
- **Non-Python**: Prettier (80 chars, 2 spaces, double quotes, no semicolons, LF)
- **Imports**: stdlib → third-party → local; try/except for relative imports
- **Naming**: PascalCase classes, snake_case functions/variables/methods
- **Types**: Use typing module for hints; mypy for checking
- **Docstrings**: German for main modules explaining purpose
- **Error handling**: Use custom exceptions from `src/exceptions.py`
- **Security**: Never commit secrets; use python-dotenv for .env files</content>
<parameter name="filePath">/home/ladmin/Desktop/GIT/Speechering/AGENTS.md