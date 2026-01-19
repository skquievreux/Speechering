"""
Lokale Transkriptionsservice - Faster-Whisper Integration
Transkribiert Audio-Dateien lokal mittels faster-whisper Modell.
"""

import logging
import time
from pathlib import Path
from typing import Optional, TYPE_CHECKING

# Lazy imports - nur laden wenn tatsächlich verwendet
if TYPE_CHECKING:
    import torch
    from faster_whisper import WhisperModel

from src.config import config

logger = logging.getLogger(__name__)

# Globales Singleton für das lokale Transkriptionsservice
_instance: Optional['LocalTranscriptionService'] = None
_instance_model_size: Optional[str] = None

class LocalTranscriptionService:
    """Service für lokale Audio-zu-Text Transkription mit faster-whisper"""

    def __new__(cls):
        """Singleton-Pattern: Stelle sicher, dass nur eine Instanz existiert"""
        global _instance, _instance_model_size

        current_model_size = config.WHISPER_MODEL_SIZE

        # Prüfe ob Modellgröße sich geändert hat
        if (_instance is not None and
            _instance_model_size != current_model_size):
            logger.info(f"Modellgröße geändert von {_instance_model_size} zu {current_model_size} - Service neu initialisieren")
            _instance = None

        if _instance is None:
            _instance = super().__new__(cls)
            _instance_model_size = current_model_size
            logger.info(f"Neue LocalTranscriptionService Instanz erstellt (Modell: {current_model_size})")

        return _instance

    def __init__(self):
        # __init__ wird bei jedem Aufruf von __new__ aufgerufen, aber wir wollen nur einmal initialisieren
        if hasattr(self, '_initialized'):
            return

        self.model: Optional[WhisperModel] = None
        self.model_size = config.WHISPER_MODEL_SIZE
        self._initialized = True
        self._load_model()

    def _load_model(self):
        """Lädt das Whisper-Modell"""
        try:
            # Lazy imports - nur hier laden wenn tatsächlich benötigt
            import torch
            from faster_whisper import WhisperModel
            
            logger.info(f"Lade lokales Whisper-Modell: '{self.model_size}'")

            # Prüfe GPU-Verfügbarkeit
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"

            logger.info(f"Verwende Device: {device}, Compute Type: {compute_type}")

            # Unterdrücke huggingface_hub Warnungen über fehlende hf_xet
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message=".*Xet Storage is enabled.*", category=UserWarning)

                self.model = WhisperModel(
                    self.model_size,
                    device=device,
                    compute_type=compute_type,
                    download_root=str(config.get_temp_dir() / "whisper_models")
                )

            logger.info(f"✓ Whisper-Modell '{self.model_size}' erfolgreich geladen (Device: {device}, App v{config.APP_VERSION})")

        except Exception as e:
            logger.error(f"Fehler beim Laden des Whisper-Modells: {e}")
            self.model = None
            raise RuntimeError(f"Whisper-Modell konnte nicht geladen werden: {e}")

    def transcribe(self, audio_path: str) -> Optional[str]:
        """Transkribiert Audio-Datei zu Text"""
        if not self._validate_audio_file(audio_path):
            return None

        if not self.model:
            logger.error("Whisper-Modell ist nicht verfügbar")
            return None

        try:
            logger.info(f"Starte lokale Transkription mit Modell '{self.model_size}'")

            start_time = time.time()

            # Transkription durchführen
            segments, info = self.model.transcribe(
                audio_path,
                language="de",  # Deutsche Sprache priorisieren
                beam_size=5,
                patience=1.0,
                vad_filter=True,  # Voice Activity Detection
                vad_parameters=dict(threshold=0.5, min_speech_duration_ms=250)
            )

            # Segmente zu Text kombinieren
            transcript = " ".join([segment.text for segment in segments])

            duration = time.time() - start_time
            logger.info(f"Transkription abgeschlossen in {duration:.2f}s")

            # Validiere Ergebnis
            if self._validate_transcript(transcript):
                return transcript.strip()
            else:
                logger.warning("Transkript ist leer oder ungültig")
                return None

        except Exception as e:
            logger.error(f"Fehler bei lokaler Transkription: {e}")
            return None

    def transcribe_audio_data(self, audio_data: bytes, filename: str = "audio.mp3") -> Optional[str]:
        """Transkribiert komprimierte Audio-Daten zu Text"""
        import io
        import tempfile

        try:
            # Temporäre Datei erstellen
            with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            try:
                # Transkribiere temporäre Datei
                result = self.transcribe(temp_path)
                return result
            finally:
                # Temporäre Datei löschen
                Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Fehler bei Transkription von Audio-Daten: {e}")
            return None

    def _validate_audio_file(self, audio_path: str) -> bool:
        """Validiert die Audio-Datei"""
        try:
            path = Path(audio_path)

            if not path.exists():
                logger.error(f"Audio-Datei existiert nicht: {audio_path}")
                return False

            if not path.is_file():
                logger.error(f"Pfad ist keine Datei: {audio_path}")
                return False

            # Prüfe Dateigröße (max 25MB wie bei API)
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > 25:
                logger.error(f"Audio-Datei zu groß: {size_mb:.1f}MB (max 25MB)")
                return False

            # Prüfe Dateiendung
            if path.suffix.lower() not in ['.wav', '.mp3', '.m4a', '.flac', '.ogg']:
                logger.warning(f"Ungewöhnliche Dateiendung: {path.suffix}")

            logger.info(f"Audio-Datei validiert: {path.name} ({size_mb:.1f}MB)")
            return True

        except Exception as e:
            logger.error(f"Fehler bei Audio-Datei-Validierung: {e}")
            return False

    def _validate_transcript(self, transcript: str) -> bool:
        """Validiert das Transkriptionsergebnis"""
        if not transcript:
            return False

        # Entferne Leerzeichen und prüfe Länge
        cleaned = transcript.strip()
        return len(cleaned) > 0

    def get_supported_formats(self) -> list:
        """Gibt unterstützte Audio-Formate zurück"""
        return ['wav', 'mp3', 'm4a', 'flac', 'ogg']

    def is_available(self) -> bool:
        """Prüft, ob der lokale Service verfügbar ist"""
        return self.model is not None

    def get_model_info(self) -> dict:
        """Gibt Informationen über das geladene Modell zurück"""
        if not self.model:
            return {"available": False}

        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
        except ImportError:
            device = "unknown"
            compute_type = "unknown"

        return {
            "available": True,
            "model_size": self.model_size,
            "device": device,
            "compute_type": compute_type
        }