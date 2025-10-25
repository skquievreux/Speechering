"""
Transcription Service - OpenAI Whisper Integration
Transkribiert Audio-Dateien zu Text mittels OpenAI Whisper API.
"""

import logging
import time
from pathlib import Path
from typing import Optional

from openai import OpenAI

from src.config import config
from src.local_transcription import LocalTranscriptionService

logger = logging.getLogger(__name__)

# Globales Singleton für lokalen Transkriptionsservice
_global_local_service: Optional[LocalTranscriptionService] = None
_global_local_service_model_size: Optional[str] = None

class TranscriptionService:
    """Service für Audio-zu-Text Transkription"""

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.max_retries = 3
        self.retry_delay = 1.0  # Sekunden

    def _get_local_transcription_service(self) -> Optional[LocalTranscriptionService]:
        """Lokalen Transkriptionsservice abrufen (Singleton)"""
        global _global_local_service, _global_local_service_model_size

        current_model_size = config.WHISPER_MODEL_SIZE

        # Prüfe ob Modellgröße sich geändert hat
        if (_global_local_service is not None and
            _global_local_service_model_size != current_model_size):
            logger.info(f"Modellgröße geändert von {_global_local_service_model_size} zu {current_model_size} - Service neu initialisieren")
            _global_local_service = None

        if _global_local_service is None and config.USE_LOCAL_TRANSCRIPTION:
            try:
                _global_local_service = LocalTranscriptionService()
                _global_local_service_model_size = current_model_size
                logger.info(f"Lokaler Transkriptionsservice initialisiert (Modell: {current_model_size})")
            except Exception as e:
                logger.error(f"Fehler beim Initialisieren des lokalen Services: {e}")
                _global_local_service = None
                _global_local_service_model_size = None

        return _global_local_service

    def transcribe(self, audio_path: str) -> Optional[str]:
        """Transkribiert Audio-Datei zu Text"""
        if not self._validate_audio_file(audio_path):
            return None

        # Versuche lokale Transkription zuerst, falls aktiviert
        if config.USE_LOCAL_TRANSCRIPTION:
            local_service = self._get_local_transcription_service()
            if local_service and local_service.is_available():
                logger.info("Verwende lokale Transkription")
                result = local_service.transcribe(audio_path)
                if result:
                    return result
                else:
                    logger.warning("Lokale Transkription fehlgeschlagen, wechsle zu API")

        # Fallback auf API-Transkription
        return self._transcribe_with_api(audio_path)

    def _transcribe_with_api(self, audio_path: str) -> Optional[str]:
        """Transkribiert Audio-Datei mit OpenAI API"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Starte API-Transkription (Versuch {attempt + 1}/{self.max_retries})")

                start_time = time.time()

                with open(audio_path, 'rb') as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="de",  # Deutsche Sprache priorisieren
                        response_format="text"
                    )

                duration = time.time() - start_time
                logger.info(".2f")

                # Validiere Ergebnis
                if self._validate_transcript(transcript):
                    return transcript.strip()
                else:
                    logger.warning("Transkript ist leer oder ungültig")
                    return None

            except Exception as e:
                logger.error(f"Fehler bei API-Transkription (Versuch {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error("Maximale Anzahl von Versuchen erreicht")
                    return None

        return None

    def transcribe_audio_data(self, audio_data: bytes, filename: str = "audio.mp3") -> Optional[str]:
        """Transkribiert komprimierte Audio-Daten zu Text"""
        # Versuche lokale Transkription zuerst, falls aktiviert
        if config.USE_LOCAL_TRANSCRIPTION:
            local_service = self._get_local_transcription_service()
            if local_service and local_service.is_available():
                logger.info("Verwende lokale Transkription für Audio-Daten")
                result = local_service.transcribe_audio_data(audio_data, filename)
                if result:
                    return result
                else:
                    logger.warning("Lokale Transkription von Audio-Daten fehlgeschlagen, wechsle zu API")

        # Fallback auf API-Transkription
        return self._transcribe_audio_data_with_api(audio_data, filename)

    def _transcribe_audio_data_with_api(self, audio_data: bytes, filename: str = "audio.mp3") -> Optional[str]:
        """Transkribiert Audio-Daten mit OpenAI API"""
        import io

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Starte API-Transkription von Audio-Daten (Versuch {attempt + 1}/{self.max_retries})")

                start_time = time.time()

                # Erstelle file-like Objekt aus bytes
                audio_file = io.BytesIO(audio_data)
                audio_file.name = filename  # OpenAI benötigt einen Dateinamen

                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="de",  # Deutsche Sprache priorisieren
                    response_format="text"
                )

                duration = time.time() - start_time
                logger.info(".2f")

                # Validiere Ergebnis
                if self._validate_transcript(transcript):
                    return transcript.strip()
                else:
                    logger.warning("Transkript ist leer oder ungültig")
                    return None

            except Exception as e:
                logger.error(f"Fehler bei API-Transkription von Audio-Daten (Versuch {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error("Maximale Anzahl von Versuchen erreicht")
                    return None

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

            # Prüfe Dateigröße (max 25MB für Whisper)
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

    def estimate_cost(self, audio_duration_seconds: float) -> float:
        """Schätzt Kosten für Transkription"""
        if config.USE_LOCAL_TRANSCRIPTION:
            # Lokale Transkription ist kostenlos
            return 0.0
        else:
            # API-Transkription: Whisper $0.006/minute
            minutes = audio_duration_seconds / 60
            return minutes * 0.006

    def get_transcription_mode(self) -> str:
        """Gibt den aktuellen Transkriptionsmodus zurück"""
        if config.USE_LOCAL_TRANSCRIPTION:
            local_service = self._get_local_transcription_service()
            if local_service and local_service.is_available():
                model_info = local_service.get_model_info()
                return f"Lokal ({model_info.get('model_size', 'unbekannt')}, {model_info.get('device', 'unbekannt')})"
            else:
                return "Lokal (nicht verfügbar)"
        else:
            return "API (OpenAI)"