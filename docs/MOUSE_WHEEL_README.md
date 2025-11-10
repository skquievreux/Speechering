# Mittleres Mausrad für Voice Transcriber

## Übersicht

Die neue Version des Voice Transcribers unterstützt das mittlere Mausrad als
Alternative zu Hotkeys für die Aufnahmesteuerung. Dies löst Probleme mit
Hotkey-Konflikten in Browsern und anderen Anwendungen.

## Neue Features

### 1. Benutzerspezifische Konfiguration

- Einstellungen werden jetzt in `%APPDATA%/VoiceTranscriber/config.json`
  gespeichert
- Persistente Hotkey-Konfiguration
- Individuelle Einstellungen pro Benutzer

### 2. Konfigurierbare Hotkeys

- Hotkeys können über die GUI angepasst werden
- Mehrere Fallback-Optionen
- Automatische Konflikterkennung

### 3. Mittleres Mausrad Unterstützung

- Toggle-Modus: Ein Klick startet/stoppt die Aufnahme
- Funktioniert in allen Anwendungen (Browser, Editoren, etc.)
- Keine Konflikte mit bestehenden Hotkeys

## Installation

### 1. AutoHotkey installieren (für mittleres Mausrad)

1. Besuche [https://www.autohotkey.com/](https://www.autohotkey.com/)
2. Lade die neueste Version herunter
3. Installiere AutoHotkey

### 2. Voice Transcriber aktualisieren

Die neuen Features sind bereits in der aktuellen Version integriert. Bei der
ersten Ausführung wird automatisch:

- Das AppData-Verzeichnis erstellt: `%APPDATA%/VoiceTranscriber/`
- Eine Standardkonfiguration angelegt: `config.json`
- Bestehende .env-Einstellungen migriert

## Konfiguration

### Mittleres Mausrad aktivieren

```python
from src.config import config

# Mittleres Mausrad aktivieren
config.enable_mouse_wheel(True)

# Prüfen ob aktiviert
if config.is_mouse_wheel_enabled():
    print("Mittleres Mausrad ist aktiviert")
```

### Hotkeys konfigurieren

```python
# Hotkey setzen
config.set_user_hotkey('primary', 'f11')
config.set_user_hotkey('secondary', 'ctrl+f12')

# Hotkey abrufen
primary = config.get_user_hotkey('primary')
```

## Verwendung

### Mit Hotkeys (Standard)

- Drücke den konfigurierten Hotkey zum Starten der Aufnahme
- Lass den Hotkey los zum Stoppen
- Piepton signalisiert Start/Stopp

### Mit mittlerem Mausrad (Alternative)

1. Stelle sicher, dass AutoHotkey installiert ist
2. Aktiviere mittleres Mausrad in den Einstellungen
3. Starte die Anwendung neu
4. Klicke mit dem mittleren Mausrad zum Starten/Stoppen der Aufnahme

## Technische Details

### AHK-Skript

Das AutoHotkey-Skript (`scripts/mouse_toggle.ahk`) erkennt mittlere
Mausrad-Klicks und simuliert F12-Tastenanschläge an die Voice Transcriber
Anwendung.

### Konfigurationsdatei

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

### API

#### UserConfig

```python
from src.user_config import user_config

# Konfiguration laden/speichern
user_config.load()
user_config.save()

# Hotkeys verwalten
user_config.set_hotkey('primary', 'f11')
hotkey = user_config.get_hotkey('primary')

# Mittleres Mausrad
user_config.enable_mouse_wheel(True)
enabled = user_config.is_mouse_wheel_enabled()
```

#### MouseWheelIntegration

```python
from src.mouse_integration import MouseWheelIntegration

integration = MouseWheelIntegration()

# AHK-Verfügbarkeit prüfen
if integration.is_ahk_available():
    # Skript starten/stoppen
    integration.start()
    integration.stop()
```

## Problembehandlung

### Mittleres Mausrad funktioniert nicht

1. **AutoHotkey nicht installiert**
   - Installiere AutoHotkey von der offiziellen Website
   - Starte die Anwendung neu

2. **AHK-Skript läuft nicht**
   - Prüfe Task-Manager nach "AutoHotkey.exe"
   - Starte die Voice Transcriber Anwendung neu

3. **Konfiguration nicht gespeichert**
   - Prüfe Schreibrechte für `%APPDATA%/VoiceTranscriber/`
   - Lösche `config.json` und starte neu (wird neu erstellt)

### Hotkey-Konflikte

1. **F12 funktioniert nicht im Browser**
   - Verwende mittleres Mausrad als Alternative
   - Oder konfiguriere andere Hotkeys: `f11`, `ctrl+f12`, etc.

2. **Strg+Win belegt**
   - Windows-Systemverknüpfungen können deaktiviert werden:
     - Win+R → `shell:windows#general`
     - "Windows-Taste-Verknüpfungen" deaktivieren

## Migration von alten Versionen

Bei der ersten Ausführung der neuen Version:

1. **AppData-Verzeichnis erstellen**: `%APPDATA%/VoiceTranscriber/`
2. **Konfiguration migrieren**: Relevante .env-Werte werden übernommen
3. **Standardwerte setzen**: Fehlende Einstellungen bekommen Defaults

Die alte .env-Datei bleibt unverändert als Fallback erhalten.

## Roadmap

- **GUI für Einstellungen**: Benutzerfreundliche Konfiguration über Tray-Menü
- **Mehr Eingabemethoden**: Touchpad-Gesten, Sprachbefehle
- **Profil-Unterstützung**: Verschiedene Konfigurationen für verschiedene
  Anwendungsfälle
