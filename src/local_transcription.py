"""
Lokale Transkriptionsservice - Faster-Whisper Integration
Transkribiert Audio-Dateien lokal mittels faster-whisper Modell.
"""

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Optional

# Lazy imports - nur laden wenn tatsächlich verwendet
if TYPE_CHECKING:
    from faster_whisper import WhisperModel

from src.config import config

logger = logging.getLogger(__name__)

# Globales Singleton für das lokale Transkriptionsservice
_instance: Optional["LocalTranscriptionService"] = None
_instance_model_size: str | None = None


class LocalTranscriptionService:
    """Service für lokale Audio-zu-Text Transkription mit faster-whisper"""

    def __new__(cls):
        """Singleton-Pattern: Stelle sicher, dass nur eine Instanz existiert"""
        global _instance, _instance_model_size

        current_model_size = config.WHISPER_MODEL_SIZE

        # Prüfe ob Modellgröße sich geändert hat
        if _instance is not None and _instance_model_size != current_model_size:
            logger.info(
                f"Modellgröße geändert von {_instance_model_size} zu {current_model_size} - Service neu initialisieren"
            )
            _instance = None

        if _instance is None:
            _instance = super().__new__(cls)
            _instance_model_size = current_model_size
            logger.info(
                f"Neue LocalTranscriptionService Instanz erstellt (Modell: {current_model_size})"
            )

        return _instance

    def __init__(self):
        # __init__ wird bei jedem Aufruf von __new__ aufgerufen, aber wir wollen nur einmal initialisieren
        if hasattr(self, "_initialized"):
            return

        self.model: WhisperModel | None = None
        self.model_size = config.WHISPER_MODEL_SIZE
        self._initialized = True
        self._load_model()

    def _load_model(self):
        """Lädt das Whisper-Modell"""
        try:
            # Frühe Dependency-Prüfung
            try:
                import torch
            except ImportError as e:
                logger.error("PyTorch nicht installiert - lokale Transkription nicht verfügbar")
                raise RuntimeError(
                    "Lokale Transkription erfordert PyTorch. "
                    "Installieren Sie es mit: poetry install --extras ai"
                ) from e

            try:
                from faster_whisper import WhisperModel
            except ImportError as e:
                logger.error("faster-whisper nicht installiert")
                raise RuntimeError(
                    "Lokale Transkription erfordert faster-whisper. "
                    "Installieren Sie es mit: poetry install --extras ai"
                ) from e

            from src.model_manager import get_model_path

            logger.info(f"Prüfe lokales Whisper-Modell: '{self.model_size}'")

            # Prüfe ob Modell vorhanden ist
            model_path = get_model_path(self.model_size)
            if not model_path:
                logger.warning(
                    f"Whisper-Modell '{self.model_size}' nicht lokal gefunden. Muss heruntergeladen werden."
                )
                raise RuntimeError(
                    f"Whisper-Modell '{self.model_size}' nicht gefunden. "
                    "Bitte laden Sie es über die Einstellungen herunter."
                )

            # Prüfe GPU-Verfügbarkeit
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"

            logger.info(
                f"Verwende Device: {device}, Compute Type: {compute_type} (Pfad: {model_path})"
            )

            # Unterdrücke huggingface_hub Warnungen über fehlende hf_xet
            import warnings

            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", message=".*Xet Storage is enabled.*", category=UserWarning
                )

                # Nutze den Pfad vom Model-Manager
                self.model = WhisperModel(
                    str(model_path),  # Expliziter Pfad zum lokalen Modell
                    device=device,
                    compute_type=compute_type,
                    local_files_only=True,  # Erzwinge lokale Dateien
                )

            logger.info(
                f"✓ Whisper-Modell '{self.model_size}' erfolgreich geladen (Device: {device}, App v{config.APP_VERSION})"
            )

        except RuntimeError:
            # RuntimeError direkt durchreichen (unsere eigenen Fehler)
            self.model = None
            raise
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Laden des Whisper-Modells: {e}")
            self.model = None
            raise RuntimeError(f"Whisper-Modell konnte nicht geladen werden: {e}") from e

    def transcribe(self, audio_path: str) -> str | None:
        """Transkribiert Audio-Datei zu Text"""
        if not self._validate_audio_file(audio_path):
            return None

        if not self.model:
            logger.info("Modell nicht geladen - versuche Re-Inizialisierung...")
            self._load_model()

            if not self.model:
                logger.error("Lokale Transkription nicht möglich: Whisper-Modell nicht geladen.")
                from src.notification import notification_service

                notification_service.show_notification(
                    "Lokale Transkription",
                    f"Das Modell '{self.model_size}' muss erst heruntergeladen werden.",
                    duration=5,
                )
                return None

        try:
            logger.info(f"Starte lokale Transkription mit Modell '{self.model_size}'")
            logger.debug(f"Audio-Pfad: {Path(audio_path).absolute()}")

            if not Path(audio_path).exists():
                raise FileNotFoundError(f"Audio-Datei nicht gefunden: {audio_path}") from None

            start_time = time.time()

            # Vokabular (Prompt) laden
            vocabulary = config.get_vocabulary()

            # Transkription durchführen
            # segments ist ein Iterator, die actual work passiert beim Iterieren
            segments, info = self.model.transcribe(
                audio_path,
                language="de",  # Deutsche Sprache priorisieren
                beam_size=5,
                patience=1.0,
                initial_prompt=vocabulary if vocabulary else None,
                vad_filter=True,  # Voice Activity Detection
                vad_parameters={"threshold": 0.5, "min_speech_duration_ms": 250},
            )

            # Segmente zu Text kombinieren (hier passiert die Transkription)
            segment_list = list(segments)
            transcript = " ".join([segment.text for segment in segment_list])

            duration = time.time() - start_time
            logger.info(
                f"Transkription abgeschlossen in {duration:.2f}s ({len(segment_list)} Segmente)"
            )

            # Validiere Ergebnis
            if self._validate_transcript(transcript):
                return transcript.strip()
            else:
                logger.warning("Transkript ist leer oder ungültig (mögliche Stille)")
                return None

        except Exception as e:
            logger.error(f"Fehler bei lokaler Transkription: {e}", exc_info=True)
            from src.exceptions import TranscriptionError

            raise TranscriptionError(f"Lokale Transkription fehlgeschlagen: {e}") from e

    def transcribe_audio_data(self, audio_data: bytes, filename: str = "audio.mp3") -> str | None:
        """Transkribiert komprimierte Audio-Daten zu Text"""
        import tempfile

        try:
            # Temporäre Datei erstellen
            with tempfile.NamedTemporaryFile(
                suffix=Path(filename).suffix, delete=False
            ) as temp_file:
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
            if path.suffix.lower() not in [".wav", ".mp3", ".m4a", ".flac", ".ogg"]:
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
        return ["wav", "mp3", "m4a", "flac", "ogg"]

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
            "compute_type": compute_type,
        }
