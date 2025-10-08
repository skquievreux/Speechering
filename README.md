# 🎤 Voice Transcriber

Eine Windows Desktop-Anwendung für Push-to-Talk Sprach-zu-Text Transkription mit KI-Unterstützung.

## ✨ Features

- 🎤 **Push-to-Talk Aufnahme**: Ctrl+Win halten = aufnehmen
- 🤖 **KI-Transkription**: OpenAI Whisper API
- ✨ **Text-Korrektur**: GPT-4 basierte Verbesserung
- ⌨️ **Auto-Einfügen**: Text direkt an Cursor-Position
- 🔔 **Akustisches Feedback**: Start/Stop Beeps
- 📍 **System Tray**: Unsichtbar im Hintergrund
- ⏱️ **30s Limit**: Automatischer Stop nach 30 Sekunden

## 🚀 Schnellstart

### 1. Repository klonen
```bash
git clone <repository-url>
cd voice-transcriber
```

### 2. Virtual Environment erstellen
```bash
# Windows CMD/PowerShell
python -m venv venv
venv\Scripts\activate

# Terminal zeigt jetzt: (venv) C:\...\voice-transcriber>
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. OpenAI API-Key konfigurieren
```bash
# .env Datei bearbeiten
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 5. Anwendung starten
```bash
python src/main.py
```

## 🎯 Verwendung

1. **Anwendung starten**: Tray-Icon erscheint
2. **Aufnehmen**: Strg + Windows-Taste gedrückt halten
3. **Sprechen**: Während Taste gehalten wird
4. **Loslassen**: Verarbeitung startet automatisch
5. **Text erscheint**: An aktueller Cursor-Position

## 🛠️ Entwicklung

### Projekt-Struktur
```
voice-transcriber/
├── src/                    # Quellcode
│   ├── main.py            # Hauptanwendung
│   ├── config.py          # Konfiguration
│   ├── hotkey_listener.py # Hotkey-Erkennung
│   ├── audio_recorder.py  # Audio-Aufnahme
│   ├── transcription.py   # Whisper API
│   ├── text_processor.py  # GPT Korrektur
│   └── clipboard_injector.py # Text-Einfügung
├── assets/                # Ressourcen
├── tests/                 # Unit Tests
├── .env                   # Umgebungsvariablen
├── requirements.txt       # Dependencies
├── build.py              # Build-Script
└── README.md
```

### Build für Distribution
```bash
# Virtual Environment muss aktiv sein!
python build.py
```

Das erstellt `dist/VoiceTranscriber.exe` - eine standalone Windows-Anwendung.

## ⚙️ Konfiguration

### .env Datei
```env
# OpenAI API
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx

# Recording
MAX_RECORDING_DURATION=30
SAMPLE_RATE=16000
CHANNELS=1

# Audio Feedback
BEEP_FREQUENCY_START=1000
BEEP_FREQUENCY_STOP=800
BEEP_DURATION=200

# Logging
LOG_LEVEL=INFO
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

- **Python**: 3.11+
- **Windows**: 10/11
- **Internet**: Erforderlich für OpenAI API
- **Mikrofon**: Standard-Audio-Gerät

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
pip install pyinstaller
```

### "OpenAI API Fehler"
- API-Key in .env prüfen
- Internetverbindung prüfen
- API-Limits/Kosten prüfen

### Mikrofon funktioniert nicht
- Standard-Mikrofon in Windows-Einstellungen prüfen
- Audio-Geräte neu starten

## 📈 Performance

- **Transkription**: < 10 Sekunden für 30s Audio
- **Hotkey-Reaktion**: < 100ms
- **CPU im Idle**: < 1%

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