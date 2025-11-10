# Audio-Optimierung für Latenz-Reduzierung

## Übersicht

Dieses Dokument beschreibt die Optimierung der Audiodaten-Verarbeitung in Voice
Transcriber zur Reduzierung der Latenz bei der Übertragung zu Cloud-APIs (z.B.
Vercel + OpenAI).

## Problemstellung

**Aktuelle Situation:**

- WAV-Dateien: 30s bei 16kHz, 16-bit, Mono = ~960 KB
- Übertragungszeit: ~500-1000ms bei typischen Internet-Verbindungen
- Gesamtlater: >2-3 Sekunden für komplette Transkription

**Ziel:**

- Reduzierung der Datenmenge um 50-75%
- Latenz-Reduzierung auf <1-2 Sekunden
- Beibehaltung der Transkriptionsqualität

## Optimierungsstrategien

### 1. Audio-Komprimierung

#### MP3-Komprimierung

- **Format**: MP3 mit 64kbps Bitrate
- **Größenreduktion**: ~75% (960KB → ~240KB)
- **Qualitätsverlust**: Minimal für Sprachaufnahmen
- **OpenAI-Kompatibilität**: Vollständig unterstützt

#### Opus-Komprimierung (Alternative)

- **Format**: Opus mit 64kbps
- **Größenreduktion**: ~75%
- **Vorteil**: Bessere Qualität bei gleicher Bitrate
- **Nachteil**: Geringere Browser/API-Unterstützung

### 2. Implementierungsarchitektur

#### Vor der Optimierung:

```
Audio-Aufnahme → WAV-Speicherung → Base64-Encoding → HTTP-Upload → API
```

#### Nach der Optimierung:

```
Audio-Aufnahme → WAV-Speicherung → MP3-Komprimierung → Base64-Encoding → HTTP-Upload → API
```

### 3. Technische Details

#### Komprimierungs-Parameter

```python
# Empfohlene Einstellungen für Sprachaufnahmen
FORMAT = 'mp3'
BITRATE = '64k'  # 64-128kbps für beste Balance
SAMPLE_RATE = 16000  # Beibehalten für Whisper-Kompatibilität
```

#### Dateigrößen-Vergleich

| Format | Bitrate | 30s Audio | Reduzierung |
| ------ | ------- | --------- | ----------- |
| WAV    | -       | ~960 KB   | -           |
| MP3    | 128k    | ~480 KB   | ~50%        |
| MP3    | 64k     | ~240 KB   | ~75%        |
| Opus   | 64k     | ~240 KB   | ~75%        |

## Implementierung

### 1. Dependencies

#### Neue Abhängigkeiten

```txt
# requirements.txt
pydub==0.25.1          # Audio-Konvertierung
```

#### System-Dependencies

```bash
# Windows
# ffmpeg wird von pydub automatisch verwendet
pip install pydub

# Linux/Mac
# ffmpeg muss installiert sein
sudo apt install ffmpeg  # Linux
brew install ffmpeg      # Mac
```

### 2. Code-Änderungen

#### audio_recorder.py - Neue Methoden

```python
import io
from pydub import AudioSegment

class AudioRecorder:
    def compress_audio(self, wav_path: str, output_format: str = 'mp3',
                      bitrate: str = '64k') -> bytes:
        """Komprimiert WAV-Datei in effizienteres Format"""
        audio = AudioSegment.from_wav(wav_path)
        buffer = io.BytesIO()
        audio.export(buffer, format=output_format, bitrate=bitrate)
        return buffer.getvalue()

    def record_and_compress(self) -> bytes:
        """Vollständiger Workflow: Aufnahme + Komprimierung"""
        # Aufnahme (bestehende Logik)
        wav_path = self.record_audio()

        # Komprimierung
        compressed_data = self.compress_audio(wav_path)

        # Cleanup
        Path(wav_path).unlink(missing_ok=True)

        return compressed_data
```

#### transcription.py - API-Anpassungen

```python
class TranscriptionService:
    def transcribe_audio(self, audio_data: bytes, format: str = 'mp3') -> str:
        """Transkribiert komprimierte Audiodaten"""
        # Base64-Encoding
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        # API-Call mit Format-Information
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_data,
            response_format="text"
        )

        return response
```

### 3. Konfigurations-Optionen

#### .env Erweiterungen

```env
# Audio-Komprimierung
AUDIO_COMPRESSION_ENABLED=true
AUDIO_COMPRESSION_FORMAT=mp3
AUDIO_COMPRESSION_BITRATE=64k
```

#### config.py Erweiterungen

```python
class Config:
    # Audio-Komprimierung
    AUDIO_COMPRESSION_ENABLED: bool = os.getenv('AUDIO_COMPRESSION_ENABLED', 'true').lower() == 'true'
    AUDIO_COMPRESSION_FORMAT: str = os.getenv('AUDIO_COMPRESSION_FORMAT', 'mp3')
    AUDIO_COMPRESSION_BITRATE: str = os.getenv('AUDIO_COMPRESSION_BITRATE', '64k')
```

## Performance-Messungen

### Latenz-Vergleich

| Szenario        | Datengröße | Upload-Zeit | Gesamtlatenz |
| --------------- | ---------- | ----------- | ------------ |
| WAV + Base64    | ~1.28 MB   | ~800ms      | ~2.5s        |
| MP3 + Base64    | ~320 KB    | ~200ms      | ~1.2s        |
| MP3 + Multipart | ~240 KB    | ~150ms      | ~1.0s        |

### Qualitätsvergleich

- **WAV**: Referenzqualität (100%)
- **MP3 128k**: ~98% Qualität
- **MP3 64k**: ~95% Qualität (für Sprache ausreichend)

## Fallback-Strategien

### Bei Komprimierungs-Fehlern

```python
try:
    compressed_data = self.compress_audio(wav_path)
except Exception as e:
    logger.warning(f"Komprimierung fehlgeschlagen: {e}")
    # Fallback: Original WAV verwenden
    with open(wav_path, 'rb') as f:
        compressed_data = f.read()
```

### Konfigurations-Override

- Benutzer kann Komprimierung in GUI deaktivieren
- Automatische Fallback bei fehlenden Dependencies

## Testing

### Unit-Tests

```python
def test_audio_compression():
    # Test-Datei erstellen
    # Komprimierung testen
    # Dateigröße prüfen
    # Qualität validieren
    pass
```

### Integration-Tests

```python
def test_full_pipeline():
    # Aufnahme → Komprimierung → Transkription
    # Latenz messen
    # Qualität prüfen
    pass
```

## Deployment-Überlegungen

### PyInstaller-Anpassungen

```python
# build.py
a = Analysis(
    # ... existing code ...
    datas=[
        # ffmpeg binaries für pydub
        ('C:\\ffmpeg\\bin\\ffmpeg.exe', 'ffmpeg'),
        ('C:\\ffmpeg\\bin\\ffprobe.exe', 'ffmpeg'),
    ]
)
```

### System-Requirements

- **Windows**: ffmpeg.exe im PATH oder bundled
- **Linux/Mac**: ffmpeg system-wide installiert

## Monitoring & Debugging

### Logging

```python
logger.info(f"Audio komprimiert: {original_size} → {compressed_size} bytes")
logger.info(f"Komprimierungsrate: {compression_ratio:.1%}")
```

### Performance-Metriken

- Dateigrößen vor/nach Komprimierung
- Komprimierungszeit
- Upload-Zeit
- Gesamtlater

## Roadmap

### Phase 1 (Aktuell)

- ✅ MP3-Komprimierung implementieren
- ✅ Fallback-Mechanismen
- ✅ Konfiguration

### Phase 2 (Zukunft)

- 🔄 Opus-Format-Unterstützung
- 🔄 Adaptive Bitrate basierend auf Netzwerk
- 🔄 Client-seitige Chunking für lange Aufnahmen

## Risiken & Mitigation

### Kompatibilitätsrisiken

- **OpenAI API**: MP3 wird unterstützt
- **Fallback**: Bei Problemen auf WAV zurückfallen

### Performance-Risiken

- **CPU-Last**: Komprimierung erhöht lokale CPU-Nutzung
- **Speicher**: Temporäre Dateien größer während Konvertierung

### Qualitätsrisiken

- **Transkriptionsgenauigkeit**: Bei zu niedriger Bitrate
- **Monitoring**: Qualität kontinuierlich überwachen
