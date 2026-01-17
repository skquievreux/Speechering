# 🎤 Voice Transcriber v1.5.1

Eine professionelle Windows Desktop-Anwendung für Push-to-Talk Sprach-zu-Text
Transkription mit KI-Unterstützung, optimierter Audio-Verarbeitung und flexiblem
Eingabesystem.

**🐛 Bugfix-Release**: Repository-Struktur bereinigt und Pfade aktualisiert.
Verbesserte Organisation und Maintenance.

## ✨ Features

### 🎯 Kernfunktionalität

- 🎤 **Push-to-Talk Aufnahme**: Mehrere Hotkey-Optionen (F12, F11, F10, etc.)
- 🖱️ **Mittleres Mausrad**: Systemweite Alternative (funktioniert in allen
  Anwendungen!)
- 🔊 **Audio-Komprimierung**: Automatische MP3-Komprimierung (75%
  Datenreduktion)
- ⚡ **Schnelle Transkription**: < 1.2s Gesamtlatenz (vorher ~2.5s)
- 🤖 **KI-Transkription**: OpenAI Whisper API + Offline-Modi
- ✨ **Text-Korrektur**: GPT-4 basierte Verbesserung (ohne Anführungszeichen)
- ⌨️ **Auto-Einfügen**: Text direkt an Cursor-Position

### 💼 Professionelle Features

- 📦 **Windows-Installer**: Vollständige Installation mit Deinstaller
- ⚙️ **Benutzerspezifische Konfiguration**: Persistente Einstellungen im AppData
- 🔧 **Konfigurierbare Hotkeys**: Individuelle Tastenkombinationen
- 🛡️ **Single-Instance-Schutz**: Verhindert Mehrfachausführung
- 📍 **System Tray**: Unsichtbar im Hintergrund mit erweitertem Menü

### 🎨 Benutzerfreundlichkeit

- 🔔 **Akustisches Feedback**: Start/Stop Beeps
- ⏱️ **30s Limit**: Automatischer Stop nach 30 Sekunden
- 🌐 **Mehrsprachig**: Deutsch/Englisch (Installer & App)
- 🧪 **Umfassende Tests**: 17+ Unit- und Integration-Tests
- 📚 **Vollständige Dokumentation**: Mehrere Sprachen & Formate

## 🚀 Schnellstart

### Option A: Bootstrap-Installer (Empfohlen - nur 15 MB!)

1. **Download**: `VoiceTranscriber_Bootstrap_Installer_v1.5.0.exe` herunterladen
2. **Installieren**: Doppelklick → Installer lädt **vollautomatisch** die App (220 MB) von Cloudflare R2 herunter
3. **Fertig**: Desktop-Verknüpfung "Voice Transcriber" klicken und loslegen!

**Vorteile**:
- ⚡ Schneller Download (nur 15 MB initial)
- 🤖 Vollautomatische Installation (kein zweiter Klick nötig!)
- ☁️ Cloudflare R2 Storage (weltweite schnelle Downloads)
- 🔄 Basis für zukünftige Auto-Updates

### Option B: Vollständiger Installer (220 MB)

1. **Download**: `VoiceTranscriber_Installer_v1.5.0.exe` herunterladen
2. **Installieren**: Doppelklick und Anweisungen folgen
3. **Fertig**: Anwendung ist installiert und bereit!

**Vorteile**: Alles in einem Paket, Offline-Installation möglich

## Option B: Manuelle Installation (für Entwickler)

#### 1. Repository klonen

```bash
git clone <repository-url>
cd Speechering
```

#### 2. Poetry installieren

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Alternative: Via pipx
pip install pipx
pipx install poetry
```

#### 3. Dependencies installieren

```bash
poetry install
```

**Poetry erstellt automatisch ein Virtual Environment!**

#### 4. OpenAI API-Key konfigurieren

```bash
# .env Datei bearbeiten
OPENAI_API_KEY=sk-your-openai-api-key-here
```

#### 5. Anwendung starten

```bash
# Option A: Poetry shell (empfohlen)
poetry shell
python src/main.py

# Option B: Direkt mit poetry run
poetry run python src/main.py
```

#### 6. Standalone-EXE erstellen (optional)

```bash
# Nur EXE erstellen
poetry run python tools/build.py

# Bootstrap-Installer erstellen (empfohlen für Distribution)
poetry run python tools/build.py --bootstrap

# Vollständigen Installer erstellen
poetry run python tools/build.py --installer

# Hilfe anzeigen
poetry run python tools/build.py --help
```

## 🎯 Verwendung

### Nach Installation:

1. **Anwendung starten**: Über Desktop-Verknüpfung oder Startmenü
2. **Tray-Icon erscheint**: Anwendung läuft im Hintergrund
3. **Aufnehmen**: Wähle eine Eingabemethode:

### 🎤 Eingabemethoden

#### Option A: Hotkeys (traditionell)

- **F12 gedrückt halten** → Aufnahme startet
- **F12 loslassen** → Verarbeitung beginnt
- **Text erscheint** automatisch an Cursor-Position

**Hotkey-Optionen** (automatische Fallback-Reihenfolge):

- **F12** (Standard, funktioniert garantiert)
- **F11, F10** (Fallbacks)
- **Strg+F12, Alt+F12** (erweiterte Optionen)

#### Option B: Mittleres Mausrad (empfohlen!)

- **Mittlere Maustaste klicken** → Aufnahme startet/stoppt (Toggle-Modus)
- **Funktioniert überall**: Browser, Editoren, alle Anwendungen!
- **Keine Konflikte**: Umgehung von Browser-Hotkey-Blockaden

### ⚙️ Einstellungen

- **Rechtsklick auf Tray-Icon** → "Einstellungen"
- **Konfigurierbare Hotkeys** (zukünftig über GUI)
- **Audio-Geräte Auswahl**
- **Transkriptions-Modi** (Online/Offline)

## 🛠️ Entwicklung

### Projekt-Struktur

```
voice-transcriber/
├── src/                    # Quellcode
│   ├── __init__.py        # Package-Definition
│   ├── main.py            # Hauptanwendung + Tray-Icon
│   ├── config.py          # Konfiguration + Logging
│   ├── user_config.py     # Benutzerspezifische Einstellungen (NEU)
│   ├── hotkey_listener.py # Hotkey-Erkennung (erweitert)
│   ├── mouse_integration.py # AHK-Integration (NEU)
│   ├── audio_recorder.py  # Mikrofon-Aufnahme
│   ├── transcription.py   # OpenAI Whisper API + Offline
│   ├── text_processor.py  # GPT-4 Korrektur
│   ├── clipboard_injector.py # Text-Einfügung
│   └── settings_gui.py    # Einstellungs-GUI
├── scripts/               # AHK-Skripte (NEU)
│   └── mouse_toggle.ahk   # Mittleres Mausrad-Skript
├── assets/                # Ressourcen
│   ├── icon.ico          # Tray-Icon
│   └── icon_generator.py # Icon-Erstellung
├── tests/                 # Unit Tests (erweitert)
│   ├── test_config.py    # Konfigurationstests
│   └── test_mouse_integration.py # Neue Tests (NEU)
├── Documentation/         # Bibliotheks-Dokumentation
├── release/               # Release-Artefakte (NEU)
├── installer.nsi          # NSIS-Installer-Skript (NEU)
├── .env                   # Umgebungsvariablen
├── .gitignore            # Git-Ignorierungen (erweitert)
├── requirements.txt       # Dependencies
├── tools/build.py        # PyInstaller Build-Script (erweitert)
├── MOUSE_WHEEL_README.md  # Neue Dokumentation (NEU)
└── README.md
```

### Build für Distribution

```bash
# Virtual Environment muss aktiv sein!

# Option 1: Nur EXE erstellen (für Tests)
python tools/build.py

# Option 2: Bootstrap-Installer (empfohlen für Releases)
python tools/build.py --bootstrap

# Option 3: Vollständiger Installer (traditionell)
python tools/build.py --installer

# Option 4: Alle Varianten erstellen
python tools/build.py --bootstrap --installer
```

**Build-Artefakte:**
- `dist/VoiceTranscriber.exe` - Standalone Windows-Anwendung (221 MB)
- `VoiceTranscriber_Bootstrap_Installer.exe` - Kleiner Downloader (15 MB)
- `VoiceTranscriber_Installer.exe` - Vollständiger Installer (220 MB)

## ⚙️ Konfiguration

### .env Datei (Systemweite Einstellungen)

```env
# OpenAI API (bleibt in .env für Sicherheit)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx

# Systemeinstellungen
MAX_RECORDING_DURATION=30
SAMPLE_RATE=16000
CHANNELS=1

# Audio-Komprimierung
AUDIO_COMPRESSION_ENABLED=true
AUDIO_COMPRESSION_FORMAT=mp3
AUDIO_COMPRESSION_BITRATE=64k

# Audio Feedback
BEEP_FREQUENCY_START=1000
BEEP_FREQUENCY_STOP=800
BEEP_DURATION=200

# Logging
LOG_LEVEL=INFO
```

### Benutzerspezifische Konfiguration (ab v1.4.0)

Automatisch erstellt in: `%APPDATA%/VoiceTranscriber/config.json`

```json
{
  "version": "1.0",
  "hotkeys": {
    "primary": "f12",
    "secondary": "f11",
    "tertiary": "f10"
  },
  "input_method": "mouse_wheel",
  "mouse_wheel_enabled": true,
  "audio": {
    "compression_enabled": true,
    "device_index": -1
  }
}
```

**Konfiguration über Code:**

```python
from src.config import config

# Hotkeys konfigurieren
config.set_user_hotkey('primary', 'f11')

# Mittleres Mausrad aktivieren
config.enable_mouse_wheel(True)

# Eingabemethode prüfen
method = config.get_input_method()  # "hotkey" oder "mouse_wheel"
```

### VS Code Setup

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true
}
```

## 🧪 Tests

```bash
# Tests ausführen
pytest tests/

# Mit Coverage
pytest --cov=src tests/
```

## 📋 Anforderungen

### Systemanforderungen

- **Betriebssystem**: Windows 10/11 (64-Bit)
- **Prozessor**: 1 GHz oder schneller
- **RAM**: 4 GB minimum, 8 GB empfohlen
- **Festplatte**: 500 MB freier Speicher
- **Mikrofon**: Standard-Audio-Gerät

### Software-Abhängigkeiten

- **AutoHotkey**: Wird automatisch installiert (für mittleres Mausrad)
- **Python**: 3.8+ (nur für manuelle Installation)
- **Internet**: Erforderlich für OpenAI API (Offline-Modi verfügbar)

### Optionale Features

- **CUDA-GPU**: Für schnellere Offline-Transkription
- ** Mehrere Mikrofone**: Für erweiterte Audio-Konfiguration

## 🔒 Sicherheit

- API-Keys werden nur lokal gespeichert
- Audio-Dateien werden nach Verarbeitung gelöscht
- Keine persistenten Audio-Aufnahmen

## 🐛 Fehlerbehebung

### "python nicht gefunden"

```bash
# Virtual Environment aktivieren
venv\Scripts\activate
```

### "PyInstaller nicht gefunden"

```bash
poetry install
```

### "OpenAI API Fehler"

- API-Key in .env prüfen
- Internetverbindung prüfen
- API-Limits/Kosten prüfen

### Mikrofon funktioniert nicht

- Standard-Mikrofon in Windows-Einstellungen prüfen
- Audio-Geräte neu starten

## 📈 Performance

### Audio-Verarbeitung

- **Audio-Komprimierung**: 75% Datenreduktion (WAV → MP3)
- **Upload-Zeit**: 800ms → 200ms (75% schneller)
- **Gesamtlatenz**: 2.5s → 1.2s (52% schneller)
- **Transkription**: < 1.2 Sekunden für 30s Audio
- **Offline-Modi**: 0$ Kosten, lokale Verarbeitung

### System-Performance

- **Hotkey-Reaktion**: < 100ms
- **Mausrad-Reaktion**: < 50ms (systemweit)
- **CPU im Idle**: < 1%
- **Memory-Verbrauch**: ~50 MB RAM
- **EXE-Größe**: 221.8 MB (Standalone mit allen Features)
- **Bootstrap-Installer**: 14.9 MB (kleiner Downloader)
- **Vollständiger Installer**: 220.3 MB (komprimiert)
- **Download-Ersparnis**: 93% weniger initialer Download (220 MB → 15 MB)

### Neue Deployment-Features

- **Bootstrap-Installer**: Automatisches Nachladen von Cloudflare R2
- **Versionsverwaltung**: Automatische Update-Prüfung
- **Retry-Mechanismus**: Robuste Downloads mit Fehlerbehandlung
- **CDN-Integration**: Weltweite schnelle Downloads via Cloudflare

### Neue Features Performance

- **Konfiguration**: < 10ms Laden/Speichern
- **AHK-Integration**: Automatische Verfügbarkeitsprüfung
- **Registry-Operationen**: Sichere Windows-Integration
- **Mehrfachinstanz-Schutz**: < 100ms Prüfung

## 🤝 Beitragen

1. Fork das Projekt
2. Feature-Branch erstellen
3. Tests schreiben
4. Pull Request erstellen

## 📄 Lizenz

[License-Informationen hier einfügen]

## 🙏 Danksagungen

- OpenAI für Whisper und GPT APIs
- Python-Community für exzellente Libraries
- Cloudflare für R2 Storage und CDN-Infrastruktur
- GitHub für Actions und Artifact-Management
