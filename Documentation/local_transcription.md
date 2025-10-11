# Lokale Sprach-zu-Text-Transkription mit Faster-Whisper

## Übersicht

Die lokale Transkriptionsfunktion ermöglicht offline-fähige Sprach-zu-Text-Umwandlung unter Verwendung der `faster-whisper` Bibliothek. Dies eliminiert die Abhängigkeit von der OpenAI Whisper API und bietet Offline-Nutzung, Kosteneinsparungen und verbesserte Privatsphäre.

## Installation

```bash
pip install faster-whisper
```

## Grundlegende Verwendung

### Lokale Transkription initialisieren

```python
from src.local_transcription import LocalTranscriptionService

# Service initialisieren (lädt Modell automatisch)
service = LocalTranscriptionService()

# Prüfen ob verfügbar
if service.is_available():
    print("Lokale Transkription bereit")
else:
    print("Lokale Transkription nicht verfügbar")
```

### Audio-Datei transkribieren

```python
# Audio-Datei transkribieren
result = service.transcribe("audio.wav")

if result:
    print(f"Transkript: {result}")
else:
    print("Transkription fehlgeschlagen")
```

### Audio-Daten transkribieren

```python
# Komprimierte Audio-Daten transkribieren
with open("audio.mp3", "rb") as f:
    audio_data = f.read()

result = service.transcribe_audio_data(audio_data, "audio.mp3")
print(f"Transkript: {result}")
```

## Konfiguration

### Umgebungsvariablen

```bash
# Lokale Transkription aktivieren/deaktivieren
USE_LOCAL_TRANSCRIPTION=true

# Modellgröße wählen (tiny, base, small, medium, large)
WHISPER_MODEL_SIZE=small
```

### Modellgrößen und Ressourcen

| Modell | Größe | RAM | Geschwindigkeit | Genauigkeit |
|--------|-------|-----|----------------|-------------|
| tiny   | 39 MB | ~1 GB | Sehr schnell | Grundlegend |
| base   | 74 MB | ~1 GB | Schnell | Gut |
| small  | 244 MB | ~2 GB | Mittel | Sehr gut |
| medium | 769 MB | ~5 GB | Langsam | Ausgezeichnet |
| large  | 1550 MB | ~10 GB | Sehr langsam | Hervorragend |

## Hardware-Anforderungen

### Minimale Anforderungen
- **CPU**: Intel i5 oder equivalent
- **RAM**: 4 GB (small Modell)
- **Speicher**: 500 MB freier Speicherplatz

### Empfohlene Anforderungen
- **CPU**: Intel i7 oder equivalent
- **RAM**: 8 GB
- **GPU**: NVIDIA mit CUDA (optional, beschleunigt Transkription)

### Automatische Hardware-Erkennung

```python
# Modell-Informationen abrufen
info = service.get_model_info()

print(f"Modell: {info['model_size']}")
print(f"Device: {info['device']}")  # 'cuda' oder 'cpu'
print(f"Compute Type: {info['compute_type']}")  # 'float16' oder 'int8'
```

## Integration in Voice Transcriber

### Automatische Umschaltung

```python
from src.transcription import TranscriptionService

# Service verwendet automatisch lokale Transkription falls aktiviert
transcription_service = TranscriptionService()

# Transkribiert mit lokalem Modell oder fällt auf API zurück
result = transcription_service.transcribe("audio.wav")
```

### Fallback-Mechanismus

1. **Lokale Transkription versuchen** (falls `USE_LOCAL_TRANSCRIPTION=true`)
2. **Bei Fehler**: Automatisch auf OpenAI API zurückfallen
3. **Bei API-Fehler**: Fehler zurückgeben

## Performance-Optimierung

### GPU-Beschleunigung

```python
# Automatisch erkannt - keine manuelle Konfiguration nötig
# CUDA wird verwendet falls verfügbar, sonst CPU mit INT8
```

### VAD-Filterung (Voice Activity Detection)

```python
# Automatisch aktiviert für bessere Performance
# Entfernt Stille und verbessert Genauigkeit
segments, info = model.transcribe(
    audio_path,
    vad_filter=True,
    vad_parameters=dict(threshold=0.5, min_speech_duration_ms=250)
)
```

### Mehrsprachige Unterstützung

```python
# Automatisch Deutsch priorisiert
segments, info = model.transcribe(audio_path, language="de")
```

## Fehlerbehandlung

### Modell-Initialisierung

```python
try:
    service = LocalTranscriptionService()
except RuntimeError as e:
    print(f"Modell konnte nicht geladen werden: {e}")
    # Fallback auf API-Modus
```

### Transkriptionsfehler

```python
result = service.transcribe("audio.wav")

if result is None:
    print("Transkription fehlgeschlagen")
    # Automatischer Fallback zur API erfolgt in TranscriptionService
```

### Hardware-Probleme

```python
# Service prüft automatisch Hardware-Verfügbarkeit
if not service.is_available():
    print("Lokale Transkription nicht verfügbar - verwende API")
```

## Testen und Validierung

### Unit-Tests ausführen

```bash
# Tests für lokale Transkription
pytest tests/test_local_transcription.py -v

# Coverage-Bericht
pytest tests/test_local_transcription.py --cov=src.local_transcription --cov-report=html
```

### Integrationstests

```bash
# Vollständige Integration testen
pytest tests/test_integration.py::TestAudioToTextWorkflow::test_full_compression_workflow -v
```

## Sicherheit und Datenschutz

### Lokale Verarbeitung
- **Audio-Daten**: Bleiben lokal auf dem Gerät
- **Keine Übertragung**: Daten werden nicht an externe Server gesendet
- **Temporäre Dateien**: Werden nach Verarbeitung automatisch gelöscht

### Modell-Speicherung
- **Lokaler Cache**: Modelle werden in `temp/whisper_models/` gespeichert
- **Keine externen Abhängigkeiten**: Nach Download sind Modelle offline verfügbar

## Troubleshooting

### Häufige Probleme

**"Modell konnte nicht geladen werden"**

- Überprüfen Sie verfügbaren RAM (mind. 4 GB für small)
- Prüfen Sie Speicherplatz (mind. 500 MB)
- Versuchen Sie ein kleineres Modell (`WHISPER_MODEL_SIZE=base`)

**"CUDA nicht verfügbar"**

- Installieren Sie CUDA-Treiber (NVIDIA GPUs)
- Fallback auf CPU erfolgt automatisch
- CPU-Modus verwendet INT8 für bessere Performance

**"Transkription zu langsam"**

- Verwenden Sie GPU falls verfügbar
- Wählen Sie kleineres Modell (tiny/base)
- Aktivieren Sie VAD-Filterung (standardmäßig aktiv)

**"Schlechte Transkriptionsqualität"**

- Verwenden Sie höherwertiges Modell (small/medium)
- Stellen Sie sicher, dass Audio klar und laut genug ist
- Verwenden Sie unterstützte Formate (WAV, MP3, etc.)

### Debug-Informationen

```python
# Detaillierte Modell-Informationen
info = service.get_model_info()
print(f"Modell-Status: {info}")

# Logging aktivieren
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Vergleich: Lokal vs. API

| Aspekt | Lokale Transkription | OpenAI API |
|--------|---------------------|------------|
| **Kosten** | Kostenlos | $0.006/minute |
| **Offline** | ✅ Ja | ❌ Nein |
| **Privatsphäre** | ✅ Hoch | ⚠️ Daten an OpenAI |
| **Latenz** | < 5 Sekunden* | 2-10 Sekunden |
| **Setup** | Modell-Download | API-Key |
| **Hardware** | CPU/GPU benötigt | Nur Internet |

*Abhängig von Hardware und Modellgröße

## Erweiterte Konfiguration

### Benutzerdefinierte Modell-Pfade

```python
# Standard: temp/whisper_models/
# Kann überschrieben werden
model = WhisperModel(
    "small",
    download_root="/custom/path/to/models"
)
```

### Erweiterte Transkriptions-Optionen

```python
segments, info = model.transcribe(
    audio_path,
    language="de",
    beam_size=5,              # Höhere Werte = bessere Genauigkeit
    patience=1.0,             # Beam search patience
    vad_filter=True,          # Voice Activity Detection
    vad_parameters=dict(
        threshold=0.5,
        min_speech_duration_ms=250
    )
)
```

## Zukunftsaussichten

### Geplante Erweiterungen
- **Modell-Updates**: Automatische Aktualisierung von Whisper-Modellen
- **Caching**: Intelligentes Caching für häufig verwendete Modelle
- **Batch-Verarbeitung**: Mehrere Dateien gleichzeitig transkribieren
- **Streaming**: Echtzeit-Transkription während der Aufnahme

### Performance-Verbesserungen
- **Quantisierung**: Weitere Optimierungen für CPU-Performance
- **Modell-Komprimierung**: Kleinere Modelle mit gleicher Genauigkeit
- **Hardware-Beschleunigung**: Optimierungen für verschiedene GPU-Typen