"""
Konfigurationsverwaltung für Voice Transcriber.
Lädt Umgebungsvariablen aus .env Datei und stellt zentrale Konfiguration bereit.
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Lade .env Datei
load_dotenv()

class Config:
    """Zentrale Konfigurationsklasse"""

    # OpenAI API
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')

    # Recording Settings
    MAX_RECORDING_DURATION: int = int(os.getenv('MAX_RECORDING_DURATION', '30'))
    SAMPLE_RATE: int = int(os.getenv('SAMPLE_RATE', '16000'))
    CHANNELS: int = int(os.getenv('CHANNELS', '1'))

    # Audio Feedback
    BEEP_FREQUENCY_START: int = int(os.getenv('BEEP_FREQUENCY_START', '1000'))
    BEEP_FREQUENCY_STOP: int = int(os.getenv('BEEP_FREQUENCY_STOP', '800'))
    BEEP_DURATION: int = int(os.getenv('BEEP_DURATION', '200'))

    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'voice_transcriber.log')
    # Für EXE: Log in AppData-Verzeichnis
    if getattr(sys, 'frozen', False):
        # Wir sind in einer EXE
        appdata = os.path.join(os.environ.get('APPDATA', ''), 'VoiceTranscriber')
        os.makedirs(appdata, exist_ok=True)
        LOG_FILE = os.path.join(appdata, 'voice_transcriber.log')

    # Temporary Files
    TEMP_DIR: str = os.getenv('TEMP_DIR', 'temp/')

    # Application Settings
    APP_NAME: str = os.getenv('APP_NAME', 'Voice Transcriber')
    APP_VERSION: str = os.getenv('APP_VERSION', '1.3.0')

    # Audio-Komprimierung
    AUDIO_COMPRESSION_ENABLED: bool = os.getenv('AUDIO_COMPRESSION_ENABLED', 'true').lower() == 'true'
    AUDIO_COMPRESSION_FORMAT: str = os.getenv('AUDIO_COMPRESSION_FORMAT', 'mp3')
    AUDIO_COMPRESSION_BITRATE: str = os.getenv('AUDIO_COMPRESSION_BITRATE', '64k')

    # Audio Device
    AUDIO_DEVICE_INDEX: int = int(os.getenv('AUDIO_DEVICE_INDEX', '-1'))  # -1 = default

    # Local Transcription
    USE_LOCAL_TRANSCRIPTION: bool = os.getenv('USE_LOCAL_TRANSCRIPTION', 'false').lower() == 'true'
    WHISPER_MODEL_SIZE: str = os.getenv('WHISPER_MODEL_SIZE', 'small')

    @classmethod
    def validate(cls) -> bool:
        """Validiert kritische Konfigurationseinstellungen"""
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "sk-your-openai-api-key-here":
            logging.warning("OPENAI_API_KEY ist nicht gesetzt oder ist Platzhalter - API-Funktionen deaktiviert")
            # return False  # Temporär deaktiviert für GUI-Test

        if cls.MAX_RECORDING_DURATION <= 0 or cls.MAX_RECORDING_DURATION > 60:
            logging.error(f"MAX_RECORDING_DURATION muss zwischen 1-60 Sekunden sein: {cls.MAX_RECORDING_DURATION}")
            return False

        # Validierung der lokalen Transkription
        valid_model_sizes = ['tiny', 'base', 'small', 'medium', 'large']
        if cls.WHISPER_MODEL_SIZE not in valid_model_sizes:
            logging.error(f"WHISPER_MODEL_SIZE muss einer der folgenden sein: {valid_model_sizes}, aktuell: {cls.WHISPER_MODEL_SIZE}")
            return False

        return True

    @classmethod
    def get_temp_dir(cls) -> Path:
        """Gibt das temporäre Verzeichnis zurück"""
        temp_path = Path(cls.TEMP_DIR)
        temp_path.mkdir(exist_ok=True)
        return temp_path

    @classmethod
    def get_log_level(cls) -> int:
        """Konvertiert Log-Level String zu Integer"""
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return levels.get(cls.LOG_LEVEL.upper(), logging.INFO)

    @classmethod
    def setup_logging(cls):
        """Konfiguriert das Logging-System"""
        # PowerShell-kompatibles Format (keine Datumsangaben am Anfang)
        logging.basicConfig(
            level=cls.get_log_level(),
            format='[%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )

def load_config() -> Config:
    """Lädt und validiert die Konfiguration"""
    config = Config()

    if not config.validate():
        raise ValueError("Konfiguration ist ungültig. Bitte .env Datei überprüfen.")

    config.setup_logging()
    logging.info(f"{config.APP_NAME} v{config.APP_VERSION} - Konfiguration geladen")

    return config

# Globale Config-Instanz
config = load_config()