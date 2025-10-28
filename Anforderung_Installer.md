# Anforderungsdokumentation: Voice Transcriber v1.4.0 - Windows Installer Release

## 📋 Dokumenteninformationen

- **Version:** 1.4.0
- **Status:** In Entwicklung
- **Autor:** AI Assistant
- **Datum:** 12.10.2025
- **Priorität:** Hoch

## 🎯 Überblick

Diese Version führt einen professionellen Windows-Installer ein, der die
Anwendung benutzerfreundlich installierbar macht und alle erforderlichen
Komponenten automatisch bereitstellt.

## 🚀 Neue Features

### 1. Windows Installer (NSIS)

**Beschreibung:** Vollständiger Windows-Installer mit Deinstaller-Funktionalität

**Anforderungen:**

- [ ] Automatische Installation der VoiceTranscriber.exe
- [ ] Integration des AutoHotkey-Skripts für mittleres Mausrad
- [ ] Automatische AutoHotkey-Installation (falls nicht vorhanden)
- [ ] Desktop-Verknüpfung erstellen
- [ ] Startmenü-Eintrag hinzufügen
- [ ] Registry-Einträge für Windows-Programme

### 2. Deinstaller

**Beschreibung:** Vollständige Deinstallation über Windows-Systemsteuerung

**Anforderungen:**

- [ ] Komplette Entfernung aller installierten Dateien
- [ ] Registry-Bereinigung
- [ ] Verknüpfungen entfernen
- [ ] Optionale Beibehaltung von Benutzerdaten

### 3. Benutzerspezifische Konfiguration

**Beschreibung:** Persistente Einstellungen im AppData-Verzeichnis

**Anforderungen:**

- [ ] Automatische Migration von .env zu user config
- [ ] Sichere Speicherung sensibler Daten
- [ ] Backup/Restore-Funktionalität

### 4. Mittleres Mausrad Integration

**Beschreibung:** Systemweite Mauserkennung als Hotkey-Alternative

**Anforderungen:**

- [ ] Toggle-Modus für Aufnahme Start/Stopp
- [ ] Automatischer AHK-Skript-Start mit Anwendung
- [ ] Konfliktfreie Koexistenz mit Hotkeys
- [ ] Visuelles Feedback bei Aktivierung

## 🏗️ Technische Architektur

### Build-System

```
build.py (erweitert)
├── PyInstaller-Build
├── NSIS-Installer-Generierung
└── Automatische Tests
```

### Installationsstruktur

```
%PROGRAMFILES%/Voice Transcriber/
├── VoiceTranscriber.exe
├── mouse_toggle.ahk
├── uninstall.exe
├── README.md
└── config/
    └── default_settings.json
```

### Registry-Einträge

```
HKLM\Software\VoiceTranscriber\
├── InstallPath = "C:\Program Files\Voice Transcriber"
├── Version = "1.4.0"
└── AutoStart = 0/1

HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\VoiceTranscriber\
├── DisplayName = "Voice Transcriber"
├── UninstallString = "...\uninstall.exe"
├── Publisher = "Voice Transcriber Team"
├── Version = "1.4.0"
└── EstimatedSize = XXXX
```

## 📦 Abhängigkeiten

### Erforderliche Tools

- **Python 3.8+** mit PyInstaller
- **NSIS 3.0+** mit Modern UI
- **AutoHotkey** (wird automatisch installiert)

### Python-Packages (neu)

- `user_config.py` - Benutzerspezifische Konfiguration
- `mouse_integration.py` - AHK-Integration

## 🔧 Implementierungsdetails

### 1. PyInstaller-Updates

**Datei:** `build.py`

**Änderungen:**

```python
# Neue Hidden Imports
hidden_imports.extend([
    "--hidden-import=user_config",
    "--hidden-import=mouse_integration",
])

# Zusätzliche Daten
pyinstaller_cmd.extend([
    "--add-data=scripts;scripts",
    "--add-data=MOUSE_WHEEL_README.md;.",
])
```

### 2. NSIS-Skript

**Datei:** `installer.nsi`

**Features:**

- Mehrsprachige Unterstützung (Deutsch/Englisch)
- Fortschrittsanzeige
- Fehlerbehandlung
- Automatische AHK-Installation
- Desktop/Startmenü-Verknüpfungen

### 3. AHK-Integration

**Datei:** `scripts/mouse_toggle.ahk`

**Features:**

- Systemweite Mauserkennung
- Toggle-Logik
- Visuelles Feedback
- Sichere Beendigung

## ✅ Akzeptanzkriterien

### Installation

- [ ] Installer startet ohne Fehler
- [ ] Alle Dateien werden korrekt installiert
- [ ] AHK wird automatisch installiert (falls fehlend)
- [ ] Verknüpfungen funktionieren
- [ ] Anwendung startet nach Installation

### Deinstallation

- [ ] Komplette Entfernung über Systemsteuerung
- [ ] Keine Datei- oder Registry-Reste
- [ ] Optionale Datenbeibehaltung funktioniert

### Funktionalität

- [ ] Mittleres Mausrad funktioniert systemweit
- [ ] Hotkeys funktionieren weiterhin
- [ ] Benutzereinstellungen werden gespeichert
- [ ] Mehrere Instanzen werden verhindert

## 🧪 Testfälle

### Installationstests

1. **Saubere Installation** - Auf neuem System
2. **Update-Installation** - Über bestehender Version
3. **AHK-Installation** - Automatische AHK-Installation
4. **Berechtigungstest** - Installation ohne Admin-Rechte

### Funktionstests

1. **Hotkey-Funktionalität** - F12 und konfigurierbare Hotkeys
2. **Mausrad-Funktionalität** - Toggle-Modus systemweit
3. **Konfiguration** - Einstellungen werden gespeichert/geladen
4. **Mehrfachinstanzen** - Single-Instance-Schutz

### Deinstallationstests

1. **Vollständige Deinstallation** - Alle Dateien entfernt
2. **Registry-Bereinigung** - Keine Reste in Registry
3. **Neuinstallation** - Nach Deinstallation möglich

## 📈 Roadmap: Nächste Stufen

### Phase 2: GUI-Verbesserungen (v1.5.0)

- Benutzerfreundliche Einstellungs-GUI
- Hotkey-Konfiguration über GUI
- Tray-Menü erweitern
- Dark/Light Theme

### Phase 3: Erweiterte Features (v1.6.0)

- Lokale Transkription (Whisper)
- Mehrere Audio-Geräte-Unterstützung
- Makro-Unterstützung
- Cloud-Synchronisation

### Phase 4: Professional (v2.0.0)

- Multi-Plattform (macOS, Linux)
- Plugin-System
- Team-Funktionen
- Enterprise-Features

## 🎯 Meilensteine

### Woche 1: Grundlagen

- [ ] PyInstaller-Skript aktualisieren
- [ ] NSIS-Skript erstellen
- [ ] Grundinstallation testen

### Woche 2: Erweiterungen

- [ ] AHK-Autoinstallation implementieren
- [ ] Deinstaller fertigstellen
- [ ] Registry-Integration

### Woche 3: Tests & Polish

- [ ] Vollständige Testsuite
- [ ] Fehlerbehebung
- [ ] Dokumentation aktualisieren

### Woche 4: Release

- [ ] Finaler Build
- [ ] Release-Notes schreiben
- [ ] Distribution vorbereiten

## 📋 Risiken & Mitigation

### Technische Risiken

1. **NSIS-Kompatibilität** - Verschiedene Windows-Versionen testen
2. **AHK-Abhängigkeit** - Fallback ohne AHK implementieren
3. **Registry-Berechtigungen** - Admin-Rechte prüfen

### Geschäftsrisiken

1. **Installation-Fehler** - Detaillierte Fehlermeldungen
2. **Deinstallation-Probleme** - Sichere Deinstallationsroutine
3. **Benutzerdaten-Verlust** - Backup vor Update

## 📞 Support & Wartung

### Support-Modell

- GitHub Issues für Bug-Reports
- Dokumentation für Selbsthilfe
- Community-Support

### Wartungsplan

- Sicherheitsupdates alle 3 Monate
- Feature-Releases alle 6-8 Wochen
- LTS-Version für Stabilität

---

**Genehmigt für Entwicklung:** ✅ **Geplante Release-Datum:** 31.10.2025
