"""
Transcription Service - OpenAI Whisper Integration
Transkribiert Audio-Dateien zu Text mittels OpenAI Whisper API.
"""

import logging
import time
import openai
from pathlib import Path
from typing import Optional

from .config import config

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Service für Audio-zu-Text Transkription"""

    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY
        self.max_retries = 3
        self.retry_delay = 1.0  # Sekunden

    def transcribe(self, audio_path: str) -> Optional[str]:
        """Transkribiert Audio-Datei zu Text"""
        if not self._validate_audio_file(audio_path):
            return None

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Starte Transkription (Versuch {attempt + 1}/{self.max_retries})")

                start_time = time.time()

                with open(audio_path, 'rb') as audio_file:
                    transcript = openai.Audio.transcribe(
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

            except openai.APIError as e:
                logger.warning(f"OpenAI API Fehler (Versuch {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error("Maximale Anzahl von Versuchen erreicht")
                    return None

            except Exception as e:
                logger.error(f"Unerwarteter Fehler bei Transkription: {e}")
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
        """Schätzt Kosten für Transkription (Whisper: $0.006/minute)"""
        minutes = audio_duration_seconds / 60
        return minutes * 0.006