# Changelog

Alle wichtigen Änderungen an Voice Transcriber werden hier dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
und dieses Projekt hält sich an
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-10-08

### 🐛 Fixed - Behoben

#### Hotkey-System korrigiert
- **Problem:** Windows-Hotkey-Kombinationen (`ctrl+alt+s`, `ctrl+shift+f12`) wurden nicht erkannt
- **Lösung:** F12 als garantierte Standard-Hotkey mit Fallback-Kette
- **Status:** Hotkey funktioniert zuverlässig

#### Debug-Logging implementiert
- **Problem:** Keine sichtbaren Logs für MP3-Komprimierung
- **Lösung:** Detaillierte Logs für Komprimierungs-Status und Datengrößen
- **Status:** Zeigt Komprimierungs-Details in Echtzeit

#### PyInstaller-Import-Fehler behoben
- **Problem:** Relative Imports in EXE funktionierten nicht
- **Lösung:** `--paths=src` für korrekte Modul-Auflösung
- **Status:** EXE startet ohne Import-Fehler

### 🔧 Changed - Geändert

- **Hotkey-Standard:** F12 (vorher problematische Kombinationen)
- **Build-System:** Verbesserte PyInstaller-Konfiguration
- **Logging:** Erweiterte Debug-Informationen

## [1.2.0] - 2025-10-08

### 🎉 Added - Erstmals hinzugefügt

#### Audio-Optimierung & Performance

- **Audio-Komprimierung**: Automatische MP3-Komprimierung mit 75% Datenreduktion
  - Reduziert Upload-Zeit von ~800ms auf ~200ms
  - Verringert Gesamtlatenz von ~2.5s auf ~1.2s
  - Konfigurierbare Bitrate (64k Standard, 128k/256k verfügbar)
  - Graceful Fallback auf WAV bei fehlenden Dependencies
- **Erweiterte Test-Infrastruktur**: 17 umfassende Unit- und Integration-Tests
  - Automatische Test-Audio-Datei-Generierung
  - Komprimierungs-Performance-Tests
  - Memory-Effizienz-Validierung

#### Hotkey-Verbesserungen

- **Neues Standard-Hotkey**: Strg + Windows-Taste (links/rechts)
  - Intuitive Bedienung für Windows-Benutzer
  - Automatische Fallback-Kette bei Konflikten
  - Verbesserte Hotkey-Erkennung und -Stabilität

#### Build-System & Deployment

- **Robustes Build-System**: Automatische Dependency-Erkennung
  - Verhindert Import-Fehler bei EXE-Builds
  - Automatische Hidden-Import-Generierung
  - Separates main_exe.py für PyInstaller-Kompatibilität
- **65.4 MB Standalone-EXE**: Vollständig gebündelt mit allen Dependencies

#### Technische Verbesserungen

- **Verbesserte Fehlerbehandlung**: Robuste Fallback-Mechanismen
- **Performance-Monitoring**: Detaillierte Logging für Komprimierungsraten
- **Memory-Management**: Optimierte Audio-Verarbeitung
- **Thread-Sicherheit**: Verbesserte Koordination bei Komprimierung

### 🔧 Changed - Geändert

- **Hotkey-System**: Strg + Windows als neuer Standard (vorher F12)
- **Build-Prozess**: Automatische src-Module-Erkennung für PyInstaller
- **Audio-Workflow**: Automatische Komprimierung im Standard-Workflow
- **Dokumentation**: Aktualisierte Audio-Optimierung-Dokumentation

### 🐛 Fixed - Behoben

- **Import-Fehler**: Robuste Build-System verhindert PyInstaller-Probleme
- **Hotkey-Konflikte**: Verbesserte Fallback-Logik bei belegten Hotkeys
- **Memory-Leaks**: Besseres Cleanup komprimierter Audio-Daten
- **Performance**: Optimierte Komprimierungs-Algorithmen

### 📊 Performance-Verbesserungen

- **75% Datenreduktion**: WAV → MP3 64k Komprimierung
- **52% schnellere Transkription**: 2.5s → 1.2s Gesamtlatenz
- **Verbesserte Zuverlässigkeit**: Robuste Fallback-Mechanismen
- **Kleinere EXE-Größe**: Optimierte Bundle-Strategie

## [1.1.0] - 2025-10-08

### 🎉 Added - Erstmals hinzugefügt

#### Benutzeroberfläche & Bedienbarkeit

- **Einstellungs-GUI**: Vollständige tkinter-basierte GUI für alle
  Anwendungseinstellungen
- **Tray-Menü Integration**: Rechtsklick-Menü mit direkten Zugriff auf
  Einstellungen
- **Hotkey-Auswahl**: GUI zur Auswahl und Testen verschiedener Hotkey-Kombinationen
- **Status-Anzeige**: Live-Status der Anwendung im Tray-Icon und GUI
- **Audio-Device Auswahl**: Dropdown-Menü zur Auswahl des Mikrofons

#### Entwicklung & Qualitätssicherung

- **Vollständige Dokumentation**: Umfassende API-Dokumentation für alle
  Bibliotheken (PyAudio, PyStray, OpenAI)
- **Markdown-Linter Integration**: Automatische Formatierung mit Prettier
- **Code-Qualität**: Behobene Linter-Probleme in allen Python-Modulen
- **Konfigurations-Management**: Verbesserte .env-Handhabung und Validierung

#### Technische Verbesserungen

- **Fallback-Mechanismen**: Verbesserte Fehlerbehandlung bei API-Ausfällen
- **Logging-Verbesserungen**: Strukturiertes Logging für bessere Debugging
- **Resource-Management**: Besseres Cleanup temporärer Dateien
- **Thread-Sicherheit**: Verbesserte Thread-Koordination

### 🔧 Changed - Geändert

- **Hotkey-System**: Erweiterte Hotkey-Optionen (F12, F11, F10, Strg+Shift+S, etc.)
- **Dokumentation**: Vollständig überarbeitete und linter-konforme Markdown-Dateien
- **Code-Struktur**: Bereinigte Imports und verbesserte Typisierung

### 🐛 Fixed - Behoben

- **Import-Probleme**: Korrekte relative Imports in allen Modulen
- **Type Hints**: Vollständige Typisierung für bessere IDE-Unterstützung
- **Markdown-Formatierung**: Alle Linter-Probleme in Dokumentation behoben
- **Code-Style**: PEP8-konforme Formatierung

## [1.0.0] - 2025-10-08

### 🎉 Added - Erstmals hinzugefügt

#### Kernfunktionalität

- **Push-to-Talk Sprachaufnahme**: Ctrl+Win Hotkey für intuitive Bedienung
- **KI-Transkription**: OpenAI Whisper API Integration für präzise
  Sprach-zu-Text Konvertierung
- **Text-Korrektur**: GPT-4 basierte Verbesserung von Grammatik und
  Interpunktion
- **Automatische Text-Einfügung**: Nahtlose Integration in beliebige Anwendungen
- **System Tray Integration**: Unsichtbarer Betrieb mit Tray-Icon

#### Technische Architektur

- **Modulare Architektur**: 7 unabhängige Module für Wartbarkeit
  - `main.py`: Orchestrator und System Tray Management
  - `hotkey_listener.py`: Globale Tastenkombination-Erkennung
  - `audio_recorder.py`: Mikrofon-Aufnahme mit WAV-Speicherung
  - `transcription.py`: Whisper API Client mit Retry-Logik
  - `text_processor.py`: GPT-4 Text-Korrektur Service
  - `clipboard_injector.py`: Automatische Text-Einfügung
  - `config.py`: Zentrale Konfigurationsverwaltung
- **Virtual Environment Support**: Vollständige venv-Integration
- **Standalone Deployment**: PyInstaller Build für EXE-Erstellung
- **Umfassende Fehlerbehandlung**: Graceful Degradation bei API-Fehlern

#### Qualitätssicherung

- **Unit Tests**: pytest-Testframework mit 6 Testfällen
- **Type Hints**: Vollständige Typisierung für bessere IDE-Unterstützung
- **Logging**: Strukturiertes Logging für Debugging und Monitoring
- **Konfiguration**: .env basierte Konfiguration ohne Hardcoding

#### Benutzerfreundlichkeit

- **Akustisches Feedback**: Start/Stop Beep-Sounds
- **Automatische Limits**: 30-Sekunden Aufnahmebegrenzung
- **Fallback-Mechanismen**: Clipboard-Nutzung bei Einfüge-Fehlern
- **Intuitive Bedienung**: Push-to-Talk ohne GUI-Interaktion

#### Entwicklungsumgebung

- **VS Code Integration**: Vollständige IDE-Konfiguration
- **Build-Automatisierung**: build.py Script mit venv-Prüfung
- **Dependency Management**: requirements.txt mit Versions-Pinning
- **Dokumentation**: Umfassende README und API-Dokumentation

### 🔧 Changed - Geändert

- Initiale Version - keine vorherigen Änderungen

### 🐛 Fixed - Behoben

- Initiale Version - keine vorherigen Fehler

### 🔒 Security - Sicherheit

- API-Keys werden nur lokal in .env gespeichert
- Keine persistenten Audio-Aufnahmen
- Temporäre Dateien werden automatisch gelöscht
- Validierung aller Benutzereingaben

### 📦 Build - Build-System

- PyInstaller Integration für Windows EXE-Erstellung
- Automatische Icon-Generierung
- venv-Prüfung vor Build-Prozess
- Optimierte Bundle-Größe durch selektive Paket-Inkludierung

---

## Versionierung

Dieses Projekt verwendet [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking Changes
- **MINOR**: Neue Features (abwärtskompatibel)
- **PATCH**: Bugfixes (abwärtskompatibel)

## Beitragende

- **Entwicklung**: Voice Transcriber Team
- **Architektur**: Modulare Python-Architektur
- **Testing**: pytest-Framework
- **Deployment**: PyInstaller für Windows

---

## Nächste Versionen (Roadmap)

### [1.1.0] - Geplant

- Mehrsprachige Unterstützung
- Anpassbare Hotkeys
- Audio-Qualitäts-Optimierungen

### [1.2.0] - Geplant

- GUI für erweiterte Einstellungen
- Makro-Unterstützung
- Cloud-Synchronisation

### [2.0.0] - Geplant

- Multi-Plattform Support (macOS, Linux)
- Offline-Modi mit lokalen Modellen
- Erweiterte KI-Integrationen
