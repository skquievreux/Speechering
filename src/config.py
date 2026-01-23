"""
Konfigurationsverwaltung für Voice Transcriber.
Lädt Umgebungsvariablen aus .env Datei und benutzerspezifische Einstellungen aus AppData.
"""

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

from dotenv import load_dotenv

try:
    # Versuche relative Imports (für python -m src)
    from .encryption import secure_storage
    from .user_config import user_config
except ImportError:
    # Fallback für direkte Ausführung oder PyInstaller
    from encryption import secure_storage
    from user_config import user_config

# Lade .env Datei
load_dotenv()

class Config:
    """Zentrale Konfigurationsklasse mit Unterstützung für benutzerspezifische Einstellungen"""

    def __init__(self):
        # Lade UserConfig falls verfügbar
        self.user_config_loaded = user_config.load()

        # OpenAI API (aus sicherer User-Konfiguration oder .env Fallback)
        self.OPENAI_API_KEY: str = user_config.get_decrypted('api.openai_key', os.getenv('OPENAI_API_KEY', ''))

        # Cloudflare R2 Storage (aus sicherer User-Konfiguration oder .env Fallback)
        self.R2_BASE_URL: str = user_config.get_decrypted('r2.base_url', os.getenv('R2_BASE_URL', 'https://pub-fce2dd545d3648c38571dc323c7b403d.r2.dev'))
        self.R2_ACCESS_TOKEN: str = user_config.get_decrypted('r2.access_token', os.getenv('R2_ACCESS_TOKEN', ''))

        # Recording Settings (benutzerspezifisch konfigurierbar)
        self.MAX_RECORDING_DURATION: int = int(os.getenv('MAX_RECORDING_DURATION', '30'))
        self.SAMPLE_RATE: int = int(os.getenv('SAMPLE_RATE', '16000'))
        self.CHANNELS: int = int(os.getenv('CHANNELS', '1'))

        # Audio Feedback (benutzerspezifisch konfigurierbar)
        self.BEEP_FREQUENCY_START: int = int(os.getenv('BEEP_FREQUENCY_START', '1000'))
        self.BEEP_FREQUENCY_STOP: int = int(os.getenv('BEEP_FREQUENCY_STOP', '800'))
        self.BEEP_DURATION: int = int(os.getenv('BEEP_DURATION', '200'))

        # Logging
        self.LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE: str = os.getenv('LOG_FILE', 'voice_transcriber.log')
        # Für EXE: Log in AppData-Verzeichnis
        if getattr(sys, 'frozen', False):
            # Wir sind in einer EXE
            appdata = os.path.join(os.environ.get('APPDATA', ''), 'VoiceTranscriber')
            os.makedirs(appdata, exist_ok=True)
            self.LOG_FILE = os.path.join(appdata, 'voice_transcriber.log')

        # Temporary Files
        self.TEMP_DIR: str = os.getenv('TEMP_DIR', 'temp/')

        # Application Settings
        self.APP_NAME: str = os.getenv('APP_NAME', 'Voice Transcriber')

        # Version aus version_manager laden für Konsistenz
        # Temporär deaktiviert nach Struktur-Änderung
        self.APP_VERSION: str = os.getenv('APP_VERSION', '1.5.1')

        # Audio-Komprimierung (benutzerspezifisch konfigurierbar)
        self.AUDIO_COMPRESSION_ENABLED: bool = os.getenv('AUDIO_COMPRESSION_ENABLED', 'true').lower() == 'true'
        self.AUDIO_COMPRESSION_FORMAT: str = os.getenv('AUDIO_COMPRESSION_FORMAT', 'mp3')
        self.AUDIO_COMPRESSION_BITRATE: str = os.getenv('AUDIO_COMPRESSION_BITRATE', '64k')

        # Audio Device (benutzerspezifisch konfigurierbar)
        self.AUDIO_DEVICE_INDEX: int = int(os.getenv('AUDIO_DEVICE_INDEX', '-1'))  # -1 = default

        # Local Transcription (benutzerspezifisch konfigurierbar)
        self.USE_LOCAL_TRANSCRIPTION: bool = user_config.get('transcription.use_local', False) if self.user_config_loaded else os.getenv('USE_LOCAL_TRANSCRIPTION', 'false').lower() == 'true'
        self.WHISPER_MODEL_SIZE: str = user_config.get('transcription.whisper_model_size', 'base') if self.user_config_loaded else os.getenv('WHISPER_MODEL_SIZE', 'base')

        # Audio Device Name (für bessere Persistenz als Index)
        self.AUDIO_DEVICE_NAME: str = user_config.get('audio.device_name', '') if self.user_config_loaded else os.getenv('AUDIO_DEVICE_NAME', '')

        # Migriere bestehende .env-Werte in user config falls nötig
        self._migrate_env_to_user_config()

    def _migrate_env_to_user_config(self):
        """Migriert relevante .env-Werte in die benutzerspezifische Konfiguration"""
        if not self.user_config_loaded:
            return

        # Migriere Audio-Komprimierung
        if os.getenv('AUDIO_COMPRESSION_ENABLED'):
            user_config.set('audio.compression_enabled',
                          os.getenv('AUDIO_COMPRESSION_ENABLED', 'true').lower() == 'true')

        # Migriere Audio Device
        if os.getenv('AUDIO_DEVICE_INDEX'):
            user_config.set('audio.device_index',
                          int(os.getenv('AUDIO_DEVICE_INDEX', '-1')))

        # Migriere Local Transcription
        if os.getenv('USE_LOCAL_TRANSCRIPTION'):
            user_config.set('transcription.use_local',
                           os.getenv('USE_LOCAL_TRANSCRIPTION', 'false').lower() == 'true')

        if os.getenv('WHISPER_MODEL_SIZE'):
            user_config.set('transcription.whisper_model_size',
                           os.getenv('WHISPER_MODEL_SIZE', 'small'))

        # Migriere OpenAI API Key (verschlüsselt)
        if os.getenv('OPENAI_API_KEY') and not user_config.get('api.openai_key'):
            api_key = os.getenv('OPENAI_API_KEY', '')
            if api_key and api_key != 'sk-your-openai-api-key-here':
                user_config.set_encrypted('api.openai_key', api_key)
                logger.info("OpenAI API-Key erfolgreich migriert und verschlüsselt")

        # Migriere R2 Storage Konfiguration (verschlüsselt)
        if os.getenv('R2_ACCESS_TOKEN') and not user_config.get('r2.access_token'):
            r2_token = os.getenv('R2_ACCESS_TOKEN', '')
            if r2_token:
                user_config.set_encrypted('r2.access_token', r2_token)
                logger.info("R2 Access Token erfolgreich migriert und verschlüsselt")

        if os.getenv('R2_BASE_URL') and not user_config.get('r2.base_url'):
            r2_url = os.getenv('R2_BASE_URL', '')
            if r2_url:
                user_config.set_encrypted('r2.base_url', r2_url)
                logger.info("R2 Base URL erfolgreich migriert und verschlüsselt")

        # Speichere migrierte Werte
        user_config.save()

    def validate(self) -> bool:
        """Validiert kritische Konfigurationseinstellungen"""
        if not self.OPENAI_API_KEY or self.OPENAI_API_KEY == "sk-your-openai-api-key-here":
            logging.warning("OPENAI_API_KEY ist nicht gesetzt oder ist Platzhalter - API-Funktionen deaktiviert")
            # return False  # Temporär deaktiviert für GUI-Test

        if self.MAX_RECORDING_DURATION <= 0 or self.MAX_RECORDING_DURATION > 60:
            logging.error(f"MAX_RECORDING_DURATION muss zwischen 1-60 Sekunden sein: {self.MAX_RECORDING_DURATION}")
            return False

        # Validierung der lokalen Transkription
        valid_model_sizes = ['tiny', 'base', 'small', 'medium', 'large']
        if self.WHISPER_MODEL_SIZE not in valid_model_sizes:
            logging.error(f"WHISPER_MODEL_SIZE muss einer der folgenden sein: {valid_model_sizes}, aktuell: {self.WHISPER_MODEL_SIZE}")
            return False

        return True

    def get_temp_dir(self) -> Path:
        """Gibt das temporäre Verzeichnis zurück"""
        # Für EXE: Verwende AppData statt relativem temp/
        if getattr(sys, 'frozen', False):
            # Wir sind in einer EXE - verwende AppData für temp-Dateien
            appdata = Path(os.environ.get('APPDATA', '')) / 'VoiceTranscriber'
            temp_path = appdata / 'temp'
        else:
            # Für Entwicklung: relatives temp/ Verzeichnis
            temp_path = Path(self.TEMP_DIR)

        temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path

    def get_log_level(self) -> int:
        """Konvertiert Log-Level String zu Integer"""
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return levels.get(self.LOG_LEVEL.upper(), logging.INFO)

    def setup_logging(self):
        """Konfiguriert das Logging-System"""
        import logging.handlers

        # Erweitertes Format mit Zeitstempel
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File Handler mit Rotation (max 5MB pro Datei, 5 Backups)
        file_handler = logging.handlers.RotatingFileHandler(
            self.LOG_FILE,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            encoding='utf-8-sig'  # UTF-8 with BOM für korrekte Umlaute in Logs
        )
        file_handler.setFormatter(formatter)

        # Console Handler (ohne Zeitstempel für bessere Lesbarkeit)
        console_formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)

        # Root Logger konfigurieren
        root_logger = logging.getLogger()
        root_logger.setLevel(self.get_log_level())
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        # Vermeide doppelte Logs durch bereits konfigurierte Handler
        logging.getLogger().handlers.clear()
        logging.getLogger().addHandler(file_handler)
        logging.getLogger().addHandler(console_handler)

    # UserConfig-Integration
    def get_user_hotkey(self, level: str = 'primary') -> str:
        """Gibt einen benutzerspezifischen Hotkey zurück"""
        if self.user_config_loaded:
            return user_config.get_hotkey(level)
        return 'f12'  # Fallback

    def set_user_hotkey(self, level: str, hotkey: str):
        """Setzt einen benutzerspezifischen Hotkey"""
        if self.user_config_loaded:
            user_config.set_hotkey(level, hotkey)
            user_config.save()

    def is_mouse_wheel_enabled(self) -> bool:
        """Prüft ob mittleres Mausrad aktiviert ist"""
        if self.user_config_loaded:
            return user_config.is_mouse_wheel_enabled()
        return False

    def enable_mouse_wheel(self, enabled: bool):
        """Aktiviert/deaktiviert mittleres Mausrad"""
        if self.user_config_loaded:
            user_config.enable_mouse_wheel(enabled)
            user_config.save()

    def get_input_method(self) -> str:
        """Gibt die Eingabemethode zurück"""
        if self.user_config_loaded:
            return user_config.get_input_method()
        return 'hotkey'

    def get_vocabulary(self) -> str:
        """Gibt das benutzerspezifische Vokabular (AI-Prompt) zurück"""
        if self.user_config_loaded:
            return user_config.get('transcription.vocabulary', '')
        return ""

def load_config() -> Config:
    """Lädt und validiert die Konfiguration"""
    config_instance = Config()

    if not config_instance.validate():
        raise ValueError("Konfiguration ist ungültig. Bitte .env Datei überprüfen.")

    config_instance.setup_logging()
    logging.info(f"{config_instance.APP_NAME} v{config_instance.APP_VERSION} - Konfiguration geladen")

    return config_instance

# Globale Config-Instanz
config = load_config()