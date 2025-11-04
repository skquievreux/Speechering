"""
Custom Exceptions für Voice Transcriber
Definiert spezifische Exception-Typen für besseres Error-Handling.
"""


class VoiceTranscriberError(Exception):
    """Basis-Exception für alle Voice Transcriber Fehler"""
    def __init__(self, message: str, user_message: str = None):
        super().__init__(message)
        self.user_message = user_message or message


class AudioRecordingError(VoiceTranscriberError):
    """Fehler bei Audio-Aufnahme"""
    pass


class AudioCompressionError(VoiceTranscriberError):
    """Fehler bei Audio-Komprimierung"""
    pass


class TranscriptionError(VoiceTranscriberError):
    """Fehler bei Transkription"""
    pass


class TextProcessingError(VoiceTranscriberError):
    """Fehler bei Text-Verarbeitung"""
    pass


class ClipboardError(VoiceTranscriberError):
    """Fehler bei Clipboard/Text-Einfügung"""
    pass


class ConfigurationError(VoiceTranscriberError):
    """Fehler in der Konfiguration"""
    pass


class APIError(VoiceTranscriberError):
    """Fehler bei API-Calls (OpenAI, etc.)"""
    pass


class NetworkError(VoiceTranscriberError):
    """Netzwerk-bezogene Fehler"""
    pass


# Retry-fähige Exceptions (temporäre Fehler)
RETRYABLE_EXCEPTIONS = (
    NetworkError,
    APIError,
)


# Kritische Exceptions (sofortiger Abbruch)
CRITICAL_EXCEPTIONS = (
    ConfigurationError,
    KeyboardInterrupt,
    SystemExit,
)
