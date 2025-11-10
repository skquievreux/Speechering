# Changelog

Alle wichtigen Änderungen an Voice Transcriber werden hier dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
und dieses Projekt hält sich an
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.2] - 2025-11-10

### 🐛 Fixed - Behoben

#### Settings-GUI Verbesserungen
- **Mikrofon-Auswahl repariert**: Auswahl wird jetzt korrekt gespeichert und wieder geladen
- **Mikrofon-Liste bereinigt**: Duplikate entfernt, alphabetische Sortierung
- **Tab-Beschriftungen**: Fett gedruckte Überschriften für bessere UX
- **Debug-Datei Funktion**: Mehrere Pfade, automatische Beispiel-Erstellung
- **Datenfluss konsistent**: GUI verwendet jetzt user_config statt config für Einstellungen

#### Build-Optimierungen
- **Performance-Flags**: `--optimize=1 --strip --noupx` für schnellere Builds
- **Modul-Excludes**: Nicht benötigte Module entfernt für kleinere EXE
- **Cross-Platform**: Korrekte Pfad-Syntax für Linux/Windows

### 🔧 Changed - Geändert

#### Code-Qualität
- **Variable Redefinition behoben**: Einmalige Definition aller GUI-Variablen
- **Exception Handling verbessert**: Bessere Fehlerbehandlung in Debug-Funktionen
- **Import-Konsistenz**: Korrekte user_config Integration

## [1.5.0] - 2025-11-09

### 🎉 Added - Erstmals hinzugefügt

#### Bootstrap-Installer & Cloudflare R2 Deployment
- **Kleiner Bootstrap-Installer**: Nur 14.9 MB Downloader lädt automatisch 221.8 MB App nach
  - 93% weniger initialer Download (220 MB → 15 MB)
  - Automatisches Nachladen von Cloudflare R2 Storage
  - Versionsverwaltung und Update-Prüfung
  - Robuste Download-Fehlerbehandlung mit Retry-Mechanismus
- **Cloudflare R2 Storage Integration**: Weltweite schnelle Downloads
  - CDN-Integration für optimale Performance
  - Sichere API-basierte Uploads via boto3
  - Versionsgesteuerte Artefakt-Verwaltung
  - Automatische GitHub Actions CI/CD Pipeline
- **Verbesserte Deployment-Architektur**: Mehrere Installer-Optionen
  - Bootstrap-Installer (15 MB) für schnelle Downloads
  - Vollständiger Installer (220 MB) für Offline-Installation
  - Standalone-EXE (221.8 MB) für direkte Ausführung
  - Automatische Versionssynchronisation

#### Fehlerbehebungen und Verbesserungen
- **Lokale Transkription optimiert**: Verbesserte Stabilität und Performance
  - `hf_xet` Paket für bessere HuggingFace-Downloads hinzugefügt
  - Warnungen über fehlende Xet Storage werden unterdrückt
  - Automatischer Fallback bei lokalen Transkriptionsfehlern

- **Audio-Geräte-Anzeige korrigiert**: Mikrofonnamen werden korrekt dargestellt
  - Unicode-Normalisierung für deutsche Sonderzeichen
  - Bereinigung fehlerhafter UTF-8-Kodierung
  - Sichere Fallback-Namen bei Kodierungsfehlern

- **Verbesserte Fehlerbehandlung**: Robuste Fallback-Mechanismen
  - Lokale Transkription deaktiviert sich automatisch bei Fehlern
  - Klare Logging-Nachrichten für Debugging
  - Verbesserte Transkriptions-Validierung

### 🔧 Changed - Geändert
- **Dependencies aktualisiert**: `huggingface-hub` auf Version 0.36.0
- **Audio-Geräte-Verarbeitung**: Unicode-sichere Namen-Bereinigung
- **Transkriptions-Architektur**: Verbesserte Fehlerbehandlung und Logging

### 🐛 Fixed - Behoben
- **Mikrofon-Auswahl**: Problem mit der Speicherung und Wiederherstellung von Mikrofon-Einstellungen behoben
- **Sonderzeichen in Mikrofonnamen**: Deutsche Umlaute werden korrekt angezeigt
- **HuggingFace-Warnungen**: Störende Xet Storage-Warnungen eliminiert
- **Transkriptions-Fallback**: Automatische API-Nutzung bei lokalen Fehlern
- **Einrückungsfehler**: Syntaxfehler in main.py behoben
- **Versionierung**: Vereinheitlichung der Versionsnummern in allen Projektteilen

## [1.4.1] - 2025-10-26

### 🐛 Fixed - Behoben

#### EXE-Kompatibilität verbessert
- **Temp-Verzeichnis-Problem**: Zugriff verweigert bei relativen temp/ Pfaden in
  EXE
  - Temp-Dateien werden jetzt in `%APPDATA%/VoiceTranscriber/temp/` erstellt
  - Verhindert Zugriffsfehler bei Standalone-EXE-Ausführung
- **Hotkey-Fehler behoben**:
  `ValueError("Key name 'alt+f12' is not mapped to any known key.")`
  - Problemhaften Hotkey `'alt+f12'` aus Fallback-Liste entfernt
  - Zuverlässige Hotkey-Registrierung ohne ValueError

#### Versionsverwaltung implementiert
- **Zentrales Versionsmanagement**: Automatische Synchronisation aller
  Versionseinträge
  - `version.py` Tool für Versionsverwaltung (`patch`, `minor`, `major`)
  - Automatische Aktualisierung von `src/config.py`, `installer.nsi`, `build.py`
  - Kommandozeilen-Tool: `python version.py [get|set|patch|minor|major|info]`

## [1.3.0] - 2025-10-25

### 🎉 Added - Erstmals hinzugefügt

#### Zuverlässigkeits-Verbesserungen
- **Hotkey-Debouncing**: Verhindert doppelte Aufnahmen durch zu schnelle
  Hotkey-Presses
  - Mindestens 0.5 Sekunden Abstand zwischen Aufnahmen
  - Automatische Erkennung von Hotkey-Spamming
- **Mindestaufnahmedauer**: Erzwingt 0.5 Sekunden Mindestdauer für zuverlässige
  Transkription
  - Verhindert extrem kurze Aufnahmen (1-8 Frames)
  - Verbessert Transkriptionsqualität und -genauigkeit
- **Singleton-Pattern für TranscriptionService**: Lokales Whisper-Modell wird
  nur einmal geladen
  - Kein Neuladen bei jeder Transkription
  - Reduzierte Startzeit und Memory-Verbrauch
- **Verbessertes Logging und Debugging**: Separate Debug-Datei für
  Transkriptionsergebnisse
  - Detaillierte Logs für bessere Fehlerdiagnose
  - Automatische Debug-Datei-Erstellung im User-Verzeichnis

#### Timing-Optimierungen
- **Thread-Synchronisation**: Verbesserte Koordination zwischen Aufnahme- und
  Stopp-Threads
- **Timing-Korrekturen**: Zusätzliche Pausen für zuverlässiges Audio-Stoppen
- **Korrekte Fehlerbehandlung**: Null-Checks für Service-Instanzen

#### Benutzeroberfläche
- **Persistente Einstellungen**: Settings-GUI speichert Einstellungen korrekt in
  config.json
- **Erweiterte Hotkey-Optionen**: Zusätzliche Kombinationen für
  Browser-Kompatibilität
- **Warnung für Windows-Taste**: Klare Hinweise zu blockierten OS-Hotkeys

### 🔧 Changed - Geändert
- **Hotkey-System**: Verbesserte Debouncing-Logik und Timing-Kontrolle
- **TranscriptionService**: Singleton-Implementierung für bessere Performance
- **Settings-GUI**: Persistente Speicherung aller Einstellungen
- **Logging**: Unterdrückung störender pkg_resources Warnungen

### 🐛 Fixed - Behoben
- **Doppelte Aufnahmen**: Hotkey-Debouncing verhindert Mehrfachauslösungen
- **Zu kurze Aufnahmen**: Mindestdauer von 0.5 Sekunden erzwungen
- **Modell-Neuladung**: Singleton verhindert wiederholtes Laden
- **Einstellungen-Speicherung**: Korrekte Persistierung in config.json
- **Timing-Probleme**: Verbesserte Thread-Synchronisation

### 📊 Performance-Verbesserungen
- **Schnellere Transkription**: Kein Modell-Neuladen bei jeder Aufnahme
- **Zuverlässigere Aufnahmen**: Debouncing und Mindestdauer-Prüfungen
- **Bessere Stabilität**: Verbesserte Fehlerbehandlung und Thread-Sicherheit

## [1.4.0] - 2025-10-12

### 🎉 Added - Erstmals hinzugefügt

#### Windows Installer & Professional Deployment
- **Professioneller NSIS-Installer**: Vollständiger Windows-Installer mit Modern
  UI
  - Automatische Installation aller Komponenten
  - Deutsche und englische Sprachunterstützung
  - Fortschrittsanzeige und benutzerfreundliche Oberfläche
  - Automatische Desktop- und Startmenü-Verknüpfungen
- **Automatische AutoHotkey-Installation**: AHK wird bei Bedarf automatisch
  heruntergeladen und installiert
  - Nahtlose Integration ohne manuelle Schritte
  - Versionsprüfung und Update-Mechanismus
  - Fallback bei Download-Fehlern
- **Vollständiger Deinstaller**: Professionelle Deinstallation über
  Windows-Systemsteuerung
  - Komplette Entfernung aller installierten Dateien
  - Registry-Bereinigung
  - Optionale Beibehaltung von Benutzerdaten

#### Benutzerspezifisches Konfigurationssystem
- **AppData-Integration**: Persistente Einstellungen im Windows
  AppData-Verzeichnis
  - `%APPDATA%/VoiceTranscriber/config.json` für benutzerspezifische Daten
  - Automatische Migration von .env-Einstellungen
  - Sichere Speicherung ohne Projektabhängigkeit
- **Konfigurierbare Hotkeys**: Benutzer können Hotkeys individuell anpassen
  - Mehrere Hotkey-Ebenen (primary, secondary, tertiary)
  - Automatische Konflikterkennung und Fallback
  - Persistente Speicherung von Hotkey-Präferenzen

#### Mittleres Mausrad als Eingabemethode
- **Systemweite Mauserkennung**: Mittleres Mausrad funktioniert in allen
  Anwendungen
  - Keine Konflikte mit Browser-Hotkeys (F12, etc.)
  - Toggle-Modus für intuitive Bedienung
  - Automatischer AHK-Skript-Start mit der Anwendung
- **Alternative Eingabemethoden**: Wahl zwischen Hotkeys und Mausrad
  - Konfigurierbare Eingabemethode pro Benutzer
  - Nahtlose Umschaltung ohne Neustart
  - Visuelles Feedback bei Aktivierung

### 🔧 Changed - Geändert

#### Architektur-Verbesserungen
- **Modulare Konfiguration**: Trennung zwischen System- und
  Benutzereinstellungen
  - `.env` für globale/systemweite Einstellungen (API-Keys, etc.)
  - `config.json` für benutzerspezifische Präferenzen
  - Automatische Synchronisation und Migration
- **Erweiterte Build-System**: Vollständige NSIS-Integration
  - Automatischer Installer-Build mit `python build.py --installer`
  - Mehrsprachige Installer-Unterstützung
  - Professionelle Registry-Integration

#### Technische Verbesserungen
- **AHK-Integration**: Nahtlose AutoHotkey-Verwaltung
  - Automatische Versionserkennung
  - Sichere Prozessverwaltung und Cleanup
  - Fehlerbehandlung bei AHK-Problemen
- **Konfigurations-API**: Neue Methoden für benutzerspezifische Einstellungen
  - `config.get_user_hotkey()`, `config.set_user_hotkey()`
  - `config.is_mouse_wheel_enabled()`, `config.enable_mouse_wheel()`
  - `config.get_input_method()`

### 📊 Performance-Verbesserungen
- **Schnellere Installation**: Optimierter Installer mit minimaler Größe
  - Komprimierte Distribution (214.8 MB Installer)
  - Parallele Download- und Installationsprozesse
  - Reduzierte Installationszeit durch optimierte Skripte
- **Verbesserte Stabilität**: Robuste Fehlerbehandlung
  - Automatische Fallback-Mechanismen
  - Detaillierte Fehlermeldungen
  - Sichere Deinstallation bei Fehlern

### 🛡️ Security - Sicherheit
- **Lokale Konfiguration**: Benutzereinstellungen bleiben lokal
  - Keine Übertragung sensibler Daten
  - Sichere Dateiberechtigungen
  - Backup/Restore-Funktionalität
- **Installer-Sicherheit**: Verifizierte Downloads und Installation
  - Digitale Signatur-Bereitschaft
  - Sichere AHK-Download-URLs
  - Registry-Schutz vor unbefugtem Zugriff

### 📦 Build - Build-System
- **Professioneller Release-Build**: Vollständige CI/CD-Bereitschaft
  - Automatischer Multi-Format-Build (EXE + Installer)
  - Versionsnummerierung und Tagging
  - Release-Artifact-Generierung
- **Erweiterte PyInstaller-Konfiguration**: Optimierte Standalone-EXE
  - Neue Module: `user_config`, `mouse_integration`
  - Zusätzliche Daten: AHK-Skript, Dokumentation
  - Verbesserte Kompatibilität und Größe

## [1.3.0] - 2025-10-11

### 🎉 Added - Erstmals hinzugefügt

#### Lokale Sprach-zu-Text Transkription
- **Offline-Transkription**: Integration von `faster-whisper` für lokale
  Verarbeitung
  - Keine Abhängigkeit von OpenAI API für Offline-Nutzung
  - Reduzierte Kosten und verbesserte Privatsphäre
  - Automatische GPU-Erkennung (CUDA) mit CPU-Fallback
  - Konfigurierbare Modellgrößen (tiny, base, small, medium, large)
- **Dual-Mode Architektur**: Nahtlose Umschaltung zwischen lokal und
  API-Transkription
  - Automatischer Fallback bei lokalen Fehlern
  - Konfiguration via `.env` (USE_LOCAL_TRANSCRIPTION, WHISPER_MODEL_SIZE)
  - GUI-Integration für Benutzereinstellungen

#### Single-Instance-Schutz
- **Anwendungs-Sperre**: Verhindert mehrfache Instanzen der Anwendung
  - Lock-Datei-Mechanismus im Benutzerverzeichnis
  - Benutzerfreundliche Warnmeldung bei Doppelstart
  - Automatisches Cleanup beim Beenden

#### Erweiterte Konfiguration
- **Lokale Transkriptions-Einstellungen**: Neue GUI-Tab für
  Transkriptionsoptionen
- **Modell-Auswahl**: Dropdown für Whisper-Modellgrößen
- **Status-Anzeige**: Live-Informationen über aktiven Transkriptionsmodus

### 🔧 Changed - Geändert
- **Transkriptions-Architektur**: Erweiterte `TranscriptionService` mit lokaler
  Unterstützung
- **Konfigurationssystem**: Neue Parameter für lokale Transkription
- **GUI-Struktur**: Neuer "Transkription"-Tab in Einstellungen
- **Build-System**: Zusätzliche Dependencies (faster-whisper, torch)

### 📊 Performance-Verbesserungen
- **Offline-Betrieb**: Keine Netzwerk-Latenz bei lokaler Transkription
- **Kosteneinsparung**: 0$ für lokale Transkription vs. $0.006/min bei API
- **Privatsphäre**: Audio-Daten bleiben lokal und werden nicht übertragen
- **Hardware-Optimierung**: GPU-Beschleunigung für schnellere Verarbeitung

### 🛡️ Security - Sicherheit
- **Lokale Datenverarbeitung**: Audio-Dateien werden nur lokal verarbeitet
- **Keine externen API-Calls**: Optionale Offline-Nutzung ohne Internet
- **Single-Instance-Schutz**: Verhindert Ressourcen-Konflikte

## [1.2.1] - 2025-10-08

### 🐛 Fixed - Behoben

#### Hotkey-System korrigiert
- **Problem:** Windows-Hotkey-Kombinationen (`ctrl+alt+s`, `ctrl+shift+f12`)
  wurden nicht erkannt
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
- **Hotkey-Auswahl**: GUI zur Auswahl und Testen verschiedener
  Hotkey-Kombinationen
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
- **Hotkey-System**: Erweiterte Hotkey-Optionen (F12, F11, F10, Strg+Shift+S,
  etc.)
- **Dokumentation**: Vollständig überarbeitete und linter-konforme
  Markdown-Dateien
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
