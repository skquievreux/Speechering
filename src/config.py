"""
Konfigurationsverwaltung für Voice Transcriber.
Lädt Umgebungsvariablen aus .env Datei und stellt zentrale Konfiguration bereit.
"""

import logging
import os
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

    # Temporary Files
    TEMP_DIR: str = os.getenv('TEMP_DIR', 'temp/')

    # Application Settings
    APP_NAME: str = os.getenv('APP_NAME', 'Voice Transcriber')
    APP_VERSION: str = os.getenv('APP_VERSION', '1.1.0')

    @classmethod
    def validate(cls) -> bool:
        """Validiert kritische Konfigurationseinstellungen"""
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "sk-your-openai-api-key-here":
            logging.warning("OPENAI_API_KEY ist nicht gesetzt oder ist Platzhalter - API-Funktionen deaktiviert")
            # return False  # Temporär deaktiviert für GUI-Test

        if cls.MAX_RECORDING_DURATION <= 0 or cls.MAX_RECORDING_DURATION > 60:
            logging.error(f"MAX_RECORDING_DURATION muss zwischen 1-60 Sekunden sein: {cls.MAX_RECORDING_DURATION}")
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