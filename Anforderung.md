# Voice Transcriber - Architektur-Dokument

## Projekt-Übersicht

### Kurzbeschreibung
**Voice Transcriber** ist eine Windows Desktop-Anwendung, die gesprochene Sprache über ein Mikrofon aufnimmt, mittels KI transkribiert, den Text automatisch korrigiert und direkt an der aktuellen Cursor-Position einfügt. Die Anwendung läuft unsichtbar im System Tray und wird per Hotkey (Ctrl+Win) gesteuert.

### Hauptfunktionen
- 🎤 **Push-to-Talk Aufnahme**: Ctrl+Win halten = aufnehmen
- 🤖 **KI-Transkription**: Whisper API von OpenAI
- ✨ **Text-Korrektur**: GPT-basierte Kontextverbesserung
- ⌨️ **Auto-Einfügen**: Text wird direkt eingefügt wo Cursor ist
- 🔔 **Akustisches Feedback**: Beep-Sounds für Start/Stop
- 📍 **System Tray Integration**: Icon mit Kontextmenü
- ⏱️ **30 Sekunden Maximum**: Automatischer Stop nach 30s

### Zielplattform
- **Betriebssystem**: Windows 10/11
- **Distribution**: Standalone .exe (keine Installation nötig)
- **Architektur**: x64

---

## Anforderungen

### Funktionale Anforderungen

#### FR-01: Hotkey-Steuerung
- **Beschreibung**: Ctrl+Win gedrückt halten startet Aufnahme
- **Details**:
  - Hotkey: Strg + Windows-Taste
  - Push-to-Talk: Halten = Aufnahme läuft
  - Loslassen = Stopp + Verarbeitung
  - Global: Funktioniert in allen Anwendungen

#### FR-02: Audio-Aufnahme
- **Beschreibung**: Mikrofon-Audio aufnehmen
- **Details**:
  - Quelle: Standard-Mikrofon des Systems
  - Format: WAV, 16-bit, 16kHz
  - Maximale Dauer: 30 Sekunden
  - Automatischer Stop nach 30s

#### FR-03: Transkription
- **Beschreibung**: Audio zu Text konvertieren
- **Details**:
  - Engine: OpenAI Whisper API
  - Sprache: Automatische Erkennung (primär Deutsch)
  - Online-Verarbeitung (Internet erforderlich)

#### FR-04: Text-Korrektur
- **Beschreibung**: Transkribierten Text verbessern
- **Details**:
  - Engine: OpenAI GPT-4
  - Korrekturen: Grammatik, Interpunktion, Kontext
  - Stil: Natürlicher, fließender Text

#### FR-05: Text-Einfügen
- **Beschreibung**: Text an Cursor-Position einfügen
- **Details**:
  - Primär: Direktes Einfügen via Tastatur-Simulation
  - Fallback: Zwischenablage (wenn kein Eingabefeld aktiv)
  - Keine manuelle Paste-Aktion nötig

#### FR-06: Akustisches Feedback
- **Beschreibung**: Sound-Signale für Benutzer-Feedback
- **Details**:
  - Start-Beep: Bei Beginn der Aufnahme
  - Stop-Beep: Bei Ende der Aufnahme
  - Kein Sound beim Einfügen

#### FR-07: System Tray Integration
- **Beschreibung**: Icon im System Tray
- **Details**:
  - Always-on: Läuft im Hintergrund
  - Icon: Mikrofon-Symbol
  - Kontextmenü: Status, Einstellungen, Beenden
  - Hover-Text: Status-Anzeige

### Nicht-funktionale Anforderungen

#### NFR-01: Performance
- Transkription: < 10 Sekunden für 30s Audio
- Hotkey-Reaktion: < 100ms
- CPU-Last im Idle: < 1%

#### NFR-02: Usability
- Keine sichtbaren Fenster während Betrieb
- Intuitive Bedienung (Push-to-Talk)
- Klare Status-Anzeigen

#### NFR-03: Sicherheit
- API-Keys verschlüsselt in .env
- Keine Audio-Aufnahmen persistent gespeichert
- Temporäre Dateien werden gelöscht

#### NFR-04: Zuverlässigkeit
- Fehlerbehandlung bei Netzwerkproblemen
- Graceful Degradation (Fallback auf Clipboard)
- Kein Crash bei fehlendem Mikrofon

#### NFR-05: Wartbarkeit
- Modulare Architektur
- Klare Trennung der Komponenten
- Logging für Debugging

---

## Technologie-Stack

### Programmiersprache
- **Python 3.11+**

### Kernbibliotheken

| Bibliothek | Version | Zweck |
|------------|---------|-------|
| `pystray` | 0.19.5 | System Tray Icon |
| `pillow` | 10.0.0 | Icon-Bildverarbeitung |
| `keyboard` | 0.13.5 | Globale Hotkey-Erkennung |
| `pyaudio` | 0.2.13 | Mikrofon-Aufnahme |
| `openai` | 1.3.0 | Whisper + GPT API |
| `pyperclip` | 1.8.2 | Zwischenablage-Zugriff |
| `pyautogui` | 0.9.54 | Tastatur-Simulation |
| `python-dotenv` | 1.0.0 | Umgebungsvariablen |
| `pyinstaller` | 6.3.0 | EXE-Erstellung |

### Standard-Bibliotheken
- `wave`: WAV-Datei Handling
- `winsound`: Beep-Sounds (Windows)
- `threading`: Multi-Threading
- `logging`: Logging-Framework

### Entwicklungs-Tools
- **IDE**: Visual Studio Code
- **Versionskontrolle**: Git
- **Dependency Management**: pip + requirements.txt
- **Build-Tool**: PyInstaller
- **Testing**: pytest

---

## Architektur

### Systemarchitektur

```
┌─────────────────────────────────────────────────────────┐
│                    Windows Desktop                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Voice Transcriber (main.py)             │   │
│  │                                                  │   │
│  │  ┌──────────────┐  ┌─────────────────────────┐ │   │
│  │  │ System Tray  │  │   Hotkey Listener       │ │   │
│  │  │   (pystray)  │  │    (keyboard)           │ │   │
│  │  └──────┬───────┘  └───────┬─────────────────┘ │   │
│  │         │                   │                    │   │
│  │         │    ┌──────────────▼─────────────┐     │   │
│  │         │    │   Orchestrator             │     │   │
│  │         └────►   (Workflow Control)       │     │   │
│  │              └──────────┬─────────────────┘     │   │
│  │                         │                        │   │
│  │         ┌───────────────┼───────────────┐       │   │
│  │         │               │               │       │   │
│  │    ┌────▼────┐   ┌─────▼─────┐  ┌─────▼────┐  │   │
│  │    │ Audio   │   │Transcribe │  │Clipboard │  │   │
│  │    │Recorder │   │Processor  │  │Injector  │  │   │
│  │    │(pyaudio)│   │(OpenAI)   │  │(pyautogui│  │   │
│  │    └─────────┘   └───────────┘  └──────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                              │
└──────────────────────────┼──────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  OpenAI API │
                    │  (Internet) │
                    └─────────────┘
```

### Komponentenarchitektur

```
src/
├── main.py                 # Entry Point + Orchestration
├── hotkey_listener.py      # Hotkey Detection
├── audio_recorder.py       # Microphone Recording
├── transcription.py        # Whisper API Integration
├── text_processor.py       # GPT Text Correction
├── clipboard_injector.py   # Text Injection
└── config.py              # Configuration Management
```

---

## Komponenten-Details

### 1. main.py (Orchestrator)

**Verantwortlichkeiten:**
- System Tray Icon initialisieren
- Alle Module koordinieren
- Event Loop verwalten
- Graceful Shutdown

**Schnittstellen:**
```python
def main():
    """Startet die Anwendung"""
    
def setup_tray_icon():
    """Erstellt System Tray Icon"""
    
def on_exit():
    """Cleanup beim Beenden"""
```

**Threading:**
- Main Thread: System Tray (pystray)
- Worker Thread: Hotkey Listener
- Worker Thread: Audio Processing

---

### 2. hotkey_listener.py

**Verantwortlichkeiten:**
- Globale Hotkey-Registrierung
- Drücken/Halten/Loslassen erkennen
- Callbacks triggern

**Schnittstellen:**
```python
def register_hotkey(on_press_callback, on_release_callback):
    """Registriert Ctrl+Win Hotkey"""
    
def on_hotkey_press():
    """Callback bei Hotkey-Drücken"""
    
def on_hotkey_release():
    """Callback bei Hotkey-Loslassen"""
```

**Implementation:**
```python
import keyboard

def register_hotkey(on_press, on_release):
    keyboard.on_press_key('ctrl+left windows', on_press)
    keyboard.on_release_key('ctrl+left windows', on_release)
```

---

### 3. audio_recorder.py

**Verantwortlichkeiten:**
- Mikrofon-Zugriff
- Audio-Stream aufnehmen
- WAV-Datei speichern
- 30s Timer verwalten

**Schnittstellen:**
```python
def start_recording():
    """Startet Aufnahme"""
    
def stop_recording() -> str:
    """Stoppt Aufnahme, gibt WAV-Pfad zurück"""
    
def play_beep(frequency: int):
    """Spielt Beep-Sound"""
```

**Technische Details:**
- Sample Rate: 16000 Hz
- Channels: 1 (Mono)
- Sample Width: 2 Bytes (16-bit)
- Format: WAV
- Temporärer Speicher: `temp/recording.wav`

---

### 4. transcription.py

**Verantwortlichkeiten:**
- Whisper API aufrufen
- Audio-Datei senden
- Text-Antwort empfangen
- Fehlerbehandlung

**Schnittstellen:**
```python
def transcribe_audio(audio_path: str) -> str:
    """Transkribiert Audio zu Text"""
    
def _retry_on_failure(func, max_retries=3):
    """Retry-Logik für API-Aufrufe"""
```

**API-Aufruf:**
```python
import openai

def transcribe_audio(audio_path: str) -> str:
    with open(audio_path, 'rb') as audio_file:
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            language="de"  # Optional: Auto-detect
        )
    return transcript.text
```

---

### 5. text_processor.py

**Verantwortlichkeiten:**
- GPT-4 für Text-Korrektur nutzen
- Kontext-basierte Verbesserungen
- Grammatik & Interpunktion

**Schnittstellen:**
```python
def process_text(raw_text: str) -> str:
    """Korrigiert und verbessert Text"""
    
def _create_correction_prompt(text: str) -> str:
    """Erstellt GPT-Prompt"""
```

**GPT-Prompt:**
```python
def process_text(raw_text: str) -> str:
    prompt = f"""
    Korrigiere folgenden transkribierten Text:
    - Verbessere Grammatik und Interpunktion
    - Behalte den originalen Sinn bei
    - Mache den Text flüssig lesbar
    - Keine zusätzlichen Kommentare
    
    Text: {raw_text}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

---

### 6. clipboard_injector.py

**Verantwortlichkeiten:**
- Text direkt einfügen (primär)
- Zwischenablage nutzen (fallback)
- Tastatur-Simulation

**Schnittstellen:**
```python
def inject_text(text: str):
    """Fügt Text an Cursor-Position ein"""
    
def _paste_via_keyboard(text: str):
    """Simuliert Ctrl+V"""
    
def _copy_to_clipboard(text: str):
    """Fallback: Nur in Clipboard"""
```

**Implementation:**
```python
import pyautogui
import pyperclip

def inject_text(text: str):
    try:
        # Primär: Direkt einfügen
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
    except Exception as e:
        # Fallback: Nur Clipboard
        pyperclip.copy(text)
        logging.warning(f"Direct injection failed: {e}")
```

---

### 7. config.py

**Verantwortlichkeiten:**
- Umgebungsvariablen laden
- Konfigurationswerte bereitstellen
- API-Keys verwalten

**Schnittstellen:**
```python
def load_config():
    """Lädt Konfiguration aus .env"""
    
def get_api_key() -> str:
    """Gibt OpenAI API-Key zurück"""
    
class Config:
    OPENAI_API_KEY: str
    MAX_RECORDING_DURATION: int
    BEEP_FREQUENCY_START: int
    BEEP_FREQUENCY_STOP: int
```

**.env Format:**
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
MAX_RECORDING_DURATION=30
BEEP_FREQUENCY_START=1000
BEEP_FREQUENCY_STOP=800
```

---

## Workflow / Ablauf

### Normaler Workflow

```
1. App Start
   └─> System Tray Icon erscheint
   └─> Hotkey Listener aktiv
   └─> Warte auf User-Input

2. User drückt Ctrl+Win
   └─> START-BEEP 🔔
   └─> Audio Recording startet
   └─> Timer: 30s Countdown
   
3. User spricht (hält Taste)
   └─> Audio wird aufgenommen
   └─> Visuelles Feedback (Tray Icon blinkt optional)
   
4. User lässt Taste los ODER 30s erreicht
   └─> STOP-BEEP 🔔
   └─> Audio Recording stoppt
   └─> Temporäre WAV-Datei erstellt
   
5. Verarbeitung (asynchron)
   └─> Upload zu Whisper API
   └─> Transkription empfangen
   └─> Text an GPT-4 zur Korrektur
   └─> Korrigierter Text empfangen
   
6. Text-Einfügen
   └─> Text in Zwischenablage
   └─> Ctrl+V simulieren
   └─> Text erscheint an Cursor-Position
   
7. Cleanup
   └─> Temporäre Audio-Datei löschen
   └─> Zurück zu Schritt 1
```

### Fehlerbehandlung

**Kein Mikrofon verfügbar:**
```
└─> Zeige Notification
└─> Log Error
└─> Deaktiviere Hotkey (optional)
```

**API-Fehler (Netzwerk):**
```
└─> Retry 3x mit Exponential Backoff
└─> Falls weiterhin Fehler:
    └─> Zeige Notification "Netzwerkproblem"
    └─> Audio-Datei behalten (optional)
```

**Kein Eingabefeld aktiv:**
```
└─> Text nur in Zwischenablage
└─> Zeige Notification "Text in Zwischenablage"
```

---

## Projekt-Struktur

```
voice-transcriber/
│
├── .vscode/                    # VS Code Konfiguration
│   ├── settings.json          # Editor-Einstellungen
│   ├── launch.json            # Debug-Konfiguration
│   └── tasks.json             # Build-Tasks
│
├── assets/                     # Ressourcen
│   ├── icon.ico               # Tray Icon (256x256)
│   ├── start_beep.wav         # Start-Sound
│   └── stop_beep.wav          # Stop-Sound
│
├── src/                        # Quellcode
│   ├── __init__.py
│   ├── main.py                # Entry Point
│   ├── hotkey_listener.py     # Hotkey-Modul
│   ├── audio_recorder.py      # Audio-Modul
│   ├── transcription.py       # Whisper-Modul
│   ├── text_processor.py      # GPT-Modul
│   ├── clipboard_injector.py  # Injection-Modul
│   └── config.py              # Konfiguration
│
├── tests/                      # Unit Tests
│   ├── __init__.py
│   ├── test_audio.py
│   ├── test_transcription.py
│   └── test_injection.py
│
├── temp/                       # Temporäre Dateien (gitignore)
│   └── recording.wav          # Audio-Aufnahmen
│
├── venv/                       # Virtual Environment (gitignore)
│
├── .env                        # API-Keys (gitignore)
├── .gitignore                 # Git Ignore Rules
├── requirements.txt           # Python Dependencies
├── build.py                   # Build-Script
├── README.md                  # Projekt-Dokumentation
└── ARCHITECTURE.md            # Dieses Dokument
```

---

## Build & Deployment

### Development Setup

```bash
# 1. Repository klonen
git clone <repository-url>
cd voice-transcriber

# 2. Virtual Environment erstellen
python -m venv venv

# 3. Virtual Environment aktivieren
venv\Scripts\activate

# 4. Dependencies installieren
pip install -r requirements.txt

# 5. .env Datei erstellen
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 6. App starten
python src/main.py
```

### Build Process

```bash
# Development: Direkt ausführen
python src/main.py

# Production: EXE erstellen
python build.py

# Output: dist/VoiceTranscriber.exe
```

### PyInstaller Konfiguration

```bash
pyinstaller \
  --onefile \
  --windowed \
  --icon=assets/icon.ico \
  --name=VoiceTranscriber \
  --add-data="assets;assets" \
  --hidden-import=pyaudio \
  --hidden-import=keyboard \
  src/main.py
```

### Distribution

**Finale .exe:**
- Größe: ~60-100 MB
- Keine Installation nötig
- Portable: USB-Stick fähig
- Keine Admin-Rechte erforderlich

---

## Sicherheit & Datenschutz

### API-Key Management
- ✅ Keys in `.env` (nicht in Git)
- ✅ `.env` im `.gitignore`
- ✅ Keine Hardcoded Keys
- ✅ User muss eigenen Key bereitstellen

### Datenverarbeitung
- ✅ Audio nur temporär gespeichert
- ✅ Automatische Löschung nach Verarbeitung
- ✅ Keine Logs von Audio/Text-Inhalten
- ✅ Keine Telemetrie

### Netzwerk
- ✅ Nur HTTPS zu OpenAI API
- ✅ Keine anderen externen Verbindungen
- ✅ Keine Analytics/Tracking

---

## Testing-Strategie

### Unit Tests

**test_audio.py:**
```python
def test_microphone_available()
def test_recording_creates_wav()
def test_30s_timeout()
```

**test_transcription.py:**
```python
def test_whisper_api_call()
def test_retry_on_failure()
def test_german_language_detection()
```

**test_injection.py:**
```python
def test_clipboard_copy()
def test_keyboard_simulation()
def test_fallback_behavior()
```

### Integration Tests

1. **End-to-End Test:**
   - Hotkey drücken → Audio → Transkription → Einfügen

2. **Error Cases:**
   - Kein Internet
   - Ungültiger API-Key
   - Kein Mikrofon

### Manual Testing Checklist

- [ ] Tray Icon erscheint
- [ ] Hotkey funktioniert global
- [ ] Start-Beep hörbar
- [ ] Aufnahme läuft 30s
- [ ] Stop-Beep hörbar
- [ ] Text wird korrekt eingefügt
- [ ] Funktioniert in verschiedenen Apps (Notepad, Word, Browser)
- [ ] Fehlerbehandlung bei Netzwerkausfall

---

## Performance-Metriken

### Zielwerte

| Metrik | Zielwert | Kritisch bei |
|--------|----------|--------------|
| Hotkey Latenz | < 100ms | > 500ms |
| Start Recording | < 200ms | > 1s |
| API Response (30s Audio) | < 10s | > 30s |
| Text Injection | < 100ms | > 500ms |
| RAM im Idle | < 100 MB | > 500 MB |
| CPU im Idle | < 1% | > 5% |

### Optimierungen

- Asynchrone API-Calls
- Audio-Compression vor Upload
- Caching von häufigen Korrekturen (optional)
- Lazy Loading von Modulen

---

## Erweiterungsmöglichkeiten

### Phase 2 (Optional)

1. **Einstellungen-GUI:**
   - Hotkey anpassbar
   - Sprache wählen
   - Maximale Aufnahmedauer
   - Beep-Sounds an/aus

2. **Lokales Whisper:**
   - Offline-Modus
   - Keine API-Kosten
   - Langsamere Verarbeitung

3. **Text-Historie:**
   - Letzte 10 Transkriptionen speichern
   - Erneut einfügen

4. **Mehrere Hotkeys:**
   - Verschiedene Sprachen
   - Verschiedene Korrektur-Stile

5. **Statistiken:**
   - Anzahl Transkriptionen
   - Gesamt-Audiozeit
   - API-Kosten

---

## Anhang

### requirements.txt

```txt
# Core Dependencies
pystray==0.19.5
pillow==10.0.0
keyboard==0.13.5
pyaudio==0.2.13
openai==1.3.0
pyperclip==1.8.2
pyautogui==0.9.54
python-dotenv==1.0.0

# Development
black==23.12.0
pylint==3.0.3
pytest==7.4.3
watchdog==3.0.0

# Building
pyinstaller==6.3.0
```

### .gitignore

```gitignore
# Virtual Environment
venv/
env/
ENV/
.venv/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Distribution
build/
dist/
*.egg-info/
*.spec

# IDE
.vscode/*.log
.idea/

# Secrets & Config
.env
*.key

# Temporary Files
temp/
*.wav
*.mp3

# OS
.DS_Store
Thumbs.db
desktop.ini
```

### Lizenz-Hinweise

**Projekt-Lizenz:** MIT (oder nach Wahl)

**Verwendete Libraries:**
- OpenAI API: [Terms of Service](https://openai.com/policies/terms-of-use)
- pystray: LGPL-3.0
- keyboard: MIT
- PyAudio: MIT

---

## Kontakt & Support

**Entwickler:** [Name]  
**Projekt-Repository:** [GitHub URL]  
**Issue Tracker:** [GitHub Issues]  
**Dokumentation:** [Docs URL]

---

**Version:** 1.0.0  
**Erstellt:** 2025-10-08  
**Letztes Update:** 2025-10-08