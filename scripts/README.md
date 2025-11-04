# Scripts für Voice Transcriber

Dieses Verzeichnis enthält Utility-Scripts für Entwicklung und Deployment.

## create_github_issues.py

Erstellt automatisch GitHub Issues aus `GITHUB_ISSUES.md`.

### Setup

1. **GitHub Personal Access Token erstellen:**
   - Gehe zu: https://github.com/settings/tokens/new
   - Scopes: `repo` (Full control of private repositories)
   - Kopiere Token

2. **Token setzen:**
   ```bash
   # Option A: Environment-Variable
   export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

   # Option B: .env Datei im Projekt-Root
   echo "GITHUB_TOKEN=ghp_xxxxxxxxxxxx" >> .env
   ```

### Verwendung

```bash
# Dry-Run (nur Preview, keine echten Issues)
python scripts/create_github_issues.py --dry-run

# Issues tatsächlich erstellen
python scripts/create_github_issues.py

# Mit custom Repository
python scripts/create_github_issues.py --repo username/repo

# Mit inline Token
python scripts/create_github_issues.py --token ghp_xxxx
```

### Features

- ✅ Parst automatisch alle Issues aus `GITHUB_ISSUES.md`
- ✅ Extrahiert Titel, Body und Labels
- ✅ Prüft auf bereits existierende Issues (überspring Duplikate)
- ✅ Rate Limiting (1 Sekunde zwischen Requests)
- ✅ Fehlerbehandlung und Retry-Logik
- ✅ Dry-Run-Modus für sichere Preview
- ✅ Detaillierter Progress-Output

### Ausgabe-Format

```
GitHub Issues Creator
============================================================
Repository: skquievreux/Speechering
Dry Run: False
============================================================

📖 Lese GITHUB_ISSUES.md...
📋 Gefunden: 38 Issues

[1/38] Issue #1: Versionsnummer inkonsistent zwischen version.py und README
  ⚠️  Übersprungen - existiert bereits als #42

[2/38] Issue #2: Code-Duplikate und fehlerhafte Log-Strings in main.py
  ✅ Erstellt als #43
  🔗 https://github.com/skquievreux/Speechering/issues/43

[3/38] Issue #3: Fehlende Error-Handling in _perform_recording()
  ✅ Erstellt als #44
  🔗 https://github.com/skquievreux/Speechering/issues/44

...

============================================================
✅ Erfolgreich erstellt: 35
⚠️  Übersprungen (existiert bereits): 3
✅ Fertig!
```

### Troubleshooting

**"GITHUB_TOKEN nicht gefunden"**
```bash
# Prüfe ob Token gesetzt ist:
echo $GITHUB_TOKEN

# Setze Token neu:
export GITHUB_TOKEN=ghp_xxxx
```

**"403 Forbidden"**
- Token hat nicht genug Rechte
- Erstelle neuen Token mit `repo` scope
- Prüfe ob Token nicht abgelaufen ist

**"Rate Limit Exceeded"**
- GitHub API-Limit erreicht (60 Requests/Stunde ohne Auth, 5000 mit Auth)
- Warte 1 Stunde oder verwende anderen Account

**"422 Validation Failed"**
- Issue-Body ist zu lang oder hat ungültiges Format
- Prüfe `GITHUB_ISSUES.md` auf Syntax-Fehler

### Sicherheit

⚠️ **WICHTIG:** GitHub Token ist sehr sensitive!

- ❌ **NIEMALS** Token in Git committen
- ❌ **NIEMALS** Token in öffentlichen Logs
- ✅ Verwende `.env` (ist in `.gitignore`)
- ✅ Verwende Environment-Variablen
- ✅ Token nach Verwendung löschen/deaktivieren

### Dependencies

```bash
# Erforderlich:
pip install requests python-dotenv

# Bereits in requirements.txt:
# - python-dotenv>=1.0.1
# - boto3>=1.34.0 (enthält requests als Dependency)
```

## Weitere Scripts (geplant)

- `update_version.py` - Automatisches Version-Bumping
- `generate_changelog.py` - Changelog aus Git-Commits
- `upload_to_r2.py` - Direkter Upload zu Cloudflare R2
- `create_release.py` - Automatischer GitHub Release
