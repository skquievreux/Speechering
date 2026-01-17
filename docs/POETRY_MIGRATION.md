# Poetry Migration Guide - Speechering

## 📋 Übersicht

Dieses Projekt wurde von `requirements.txt` auf **Poetry** migriert, um moderne Python-Dependency-Management-Praktiken zu nutzen.

---

## 🚀 Schnellstart (für Entwickler)

### 1. Poetry installieren

```bash
# Windows (PowerShell als Admin)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Alternative: Via pipx (empfohlen)
pip install pipx
pipx install poetry
```

### 2. Dependencies installieren

```bash
cd c:\CODE\GIT\Speechering
poetry install
```

**Das war's!** Poetry erstellt automatisch ein Virtual Environment und installiert alle Dependencies.

### 3. Virtual Environment aktivieren

```bash
# Option A: Poetry shell (empfohlen)
poetry shell

# Option B: Direkt Befehle ausführen
poetry run python src/main.py
```

---

## 📦 Häufige Befehle

```bash
# Dependencies installieren
poetry install

# Neue Dependency hinzufügen
poetry add requests

# Dev-Dependency hinzufügen
poetry add --group dev pytest

# Dependencies aktualisieren
poetry update

# Virtual Environment anzeigen
poetry env info

# Tests ausführen
poetry run pytest

# Code formatieren
poetry run black src/

# Linting
poetry run ruff check src/

# Build erstellen
poetry run python tools/build.py
```

---

## 🔄 Migration von requirements.txt

`requirements.txt` ist jetzt **deprecated** und wird in einer zukünftigen Version entfernt.

### Warum Poetry?

| Feature               | requirements.txt | Poetry             |
| --------------------- | ---------------- | ------------------ |
| Lock-File             | ❌ Nein           | ✅ `poetry.lock`    |
| Dependency Resolution | ⚠️ Manuell        | ✅ Automatisch      |
| Virtual Env           | ⚠️ Manuell        | ✅ Automatisch      |
| Build-System          | ❌ Separate Tools | ✅ Integriert       |
| Publishing            | ❌ Komplex        | ✅ `poetry publish` |

### Alte Workflow (requirements.txt)

```bash
# ❌ Alt - Nicht mehr verwenden
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python tools/build.py
```

### Neuer Workflow (Poetry)

```bash
# ✅ Neu - Empfohlen
poetry install
poetry run python tools/build.py
```

---

## 🐛 Troubleshooting

### Problem: "poetry: command not found"

**Lösung:**

```bash
# Poetry-Pfad zur PATH-Variable hinzufügen
# Standardpfad: %APPDATA%\Python\Scripts
```

### Problem: "Python version not found"

**Lösung:**

```bash
# Poetry auf Python 3.8+ umstellen
poetry env use python3.11
```

### Problem: Virtual Environment wird nicht gefunden

**Lösung:**

```bash
# Env neu erstellen
poetry env remove python
poetry install
```

### Problem: PyInstaller findet Modules nicht

**Lösung:**

```bash
# Poetry-Environment für PyInstaller verwenden
poetry run pyinstaller build.spec
```

---

## 🆕 Neue Features

### Pre-commit Hooks

```bash
# Aktivieren
poetry run pre-commit install

# Manuell ausführen
poetry run pre-commit run --all-files
```

**Verfügbare Hooks:**
- `black` - Code-Formatierung
- `ruff` - Linting
- `isort` - Import-Sortierung
- `mypy` - Type-Checking

### Dependency Groups

```toml
# pyproject.toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^23.0.0"

[tool.poetry.group.build.dependencies]
pyinstaller = "^6.0.0"
```

```bash
# Nur Production-Dependencies
poetry install --only main

# Ohne Dev-Dependencies
poetry install --without dev
```

---

## ✅ Verifikation

### Checkliste: Migration erfolgreich

```bash
# 1. Poetry installiert
poetry --version
# ✅ Erwartet: Poetry (version 1.7.0)

# 2. Dependencies installiert
poetry install
# ✅ Erwartet: Installing dependencies from lock file

# 3. Tests laufen
poetry run pytest
# ✅ Erwartet: All tests passed

# 4. Build funktioniert
poetry run python tools/build.py
# ✅ Erwartet: dist/VoiceTranscriber.exe erstellt
```

---

## 📚 Weitere Ressourcen

- [Poetry Dokumentation](https://python-poetry.org/docs/)
- [Python Governance Framework (Abschnitt 13)](../../GEMINI.md)
- [pyproject.toml Referenz](https://python-poetry.org/docs/pyproject/)

---

**Migration abgeschlossen am:** 2026-01-17  
**Poetry Version:** 1.7+  
**Python Version:** 3.8 - 3.11
