# Deployment-Prozess für Voice Transcriber

## Übersicht

Der Voice Transcriber verwendet einen automatisierten CI/CD-Prozess mit GitHub Actions, der folgende Schritte umfasst:

1. **Build**: Kompilierung der Anwendung und Erstellung der Installer
2. **Test**: Automatisierte Tests der Anwendungslogik
3. **Deploy**: Hochladen der Build-Artefakte zu Cloudflare R2 Storage

## GitHub Actions Workflow

Der Workflow wird automatisch ausgelöst durch:
- Push auf `main` oder `master` Branch
- Erstellung eines Tags mit `v*` Präfix (z.B. `v1.5.0`)
- Pull Requests auf `main` oder `master`
- Manuelle Auslösung über die GitHub UI

### Build-Job

1. **Versionierung**:
   - Verwendet entweder:
     - Manuell angegebene Version (bei Workflow-Dispatch)
     - Git-Tag (bei Tag-Push)
     - Automatische Versionsinkrementierung via `scripts/version_manager.py`
   
2. **Kompilierung**:
   - Erstellt die Standalone-EXE (`VoiceTranscriber.exe`)
   - Erstellt den Bootstrap-Installer (`VoiceTranscriber_Bootstrap_Installer_v*.exe`)
   - Erstellt den vollständigen NSIS-Installer (`VoiceTranscriber_Installer_v*.exe`)

3. **Artefakte**:
   - Alle Build-Artefakte werden als GitHub Actions Artifacts gespeichert
   - Enthält zusätzlich eine `build_info.txt` mit Metadaten

### Deploy-Job

Der Deploy-Job wird nur ausgeführt, wenn:
- Der Build erfolgreich war
- Der Push auf `main`/`master` erfolgte oder ein Tag erstellt wurde

#### Cloudflare R2 Deployment

Das Deployment zu Cloudflare R2 Storage erfolgt über das Skript `scripts/deploy_to_r2.py`, welches:

1. Die Build-Artefakte aus dem vorherigen Job herunterlädt
2. Eine Verbindung zu Cloudflare R2 Storage herstellt (über boto3/S3-kompatible API)
3. Folgende Dateien hochlädt:
   - `VoiceTranscriber.exe` (als aktuelle Version)
   - `VoiceTranscriber.exe` (in versioniertem Pfad)
   - Bootstrap-Installer
   - Vollständiger Installer
   - Build-Informationen
   - Versions-Metadaten als JSON

#### Erforderliche Secrets

Für das Deployment werden folgende GitHub Secrets benötigt:
- `R2_ACCESS_KEY_ID`: Zugriffsschlüssel für Cloudflare R2
- `R2_SECRET_ACCESS_KEY`: Geheimer Schlüssel für Cloudflare R2
- `R2_ACCOUNT_ID`: Cloudflare Account-ID
- `R2_BUCKET_NAME`: Name des R2 Storage Buckets

## Lokales Deployment für Tests

Um Builds lokal zu testen, ohne sie auf Cloudflare R2 hochzuladen, gibt es mehrere Optionen:

### Option 1: Lokaler Build ohne Deployment

```bash
# Nur EXE erstellen
python build.py

# Bootstrap-Installer erstellen
python build.py --bootstrap

# Vollständigen Installer erstellen
python build.py --installer
```

Die erstellten Dateien befinden sich im `dist/`-Verzeichnis und können direkt getestet werden.

### Option 2: Manuelles Deployment zu Cloudflare R2

Für ein manuelles Deployment zu Cloudflare R2 müssen die R2-Zugangsdaten in der Umgebung verfügbar sein:

```bash
# Umgebungsvariablen setzen
export R2_ACCESS_KEY_ID="dein_access_key"
export R2_SECRET_ACCESS_KEY="dein_secret_key"
export R2_ACCOUNT_ID="deine_account_id"
export R2_BUCKET_NAME="dein_bucket_name"

# Deployment-Skript ausführen
python scripts/deploy_to_r2.py
```

### Option 3: Lokaler Test des Bootstrap-Installers

Der Bootstrap-Installer lädt die Hauptanwendung von Cloudflare R2 herunter. Um ihn lokal zu testen:

1. Stelle sicher, dass die neueste Version auf Cloudflare R2 verfügbar ist
2. Führe den Bootstrap-Installer aus: `dist/BootstrapInstaller.exe`

## Fehlerbehebung

### Fehlende Cloudflare R2 Credentials

Wenn die Cloudflare R2 Credentials nicht verfügbar sind, kann der Deployment-Schritt nicht ausgeführt werden. In diesem Fall:

1. Kontaktiere den Projektadministrator für Zugriff auf die R2 Credentials
2. Oder verwende die lokal erstellten Dateien für Tests

### Fehler beim Hochladen zu Cloudflare R2

Bei Fehlern während des Uploads:

1. Überprüfe die Netzwerkverbindung
2. Stelle sicher, dass die R2 Credentials korrekt sind
3. Überprüfe die Berechtigungen des R2 Buckets
4. Prüfe die Logs des Deployment-Skripts auf spezifische Fehlermeldungen

## Zusammenfassung

Der Deployment-Prozess ist vollständig automatisiert und wird durch GitHub Actions gesteuert. Für lokale Tests können die Build-Artefakte direkt verwendet werden, ohne sie auf Cloudflare R2 hochzuladen.

Die aktuelle Version 1.5.0 wurde lokal gebaut, aber nicht auf Cloudflare R2 hochgeladen. Für einen vollständigen Release-Prozess müsste entweder:

1. Ein Push auf den `main`/`master` Branch erfolgen
2. Ein Tag mit `v1.5.0` erstellt werden
3. Oder das Deployment manuell mit den entsprechenden R2 Credentials durchgeführt werden