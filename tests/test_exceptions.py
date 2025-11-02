"""
Tests für Custom Exceptions
"""

import pytest
from src.exceptions import (
    VoiceTranscriberError,
    AudioRecordingError,
    AudioCompressionError,
    TranscriptionError,
    TextProcessingError,
    ClipboardError,
    ConfigurationError,
    APIError,
    NetworkError,
    RETRYABLE_EXCEPTIONS,
    CRITICAL_EXCEPTIONS
)


class TestVoiceTranscriberError:
    """Tests für Basis-Exception"""

    def test_base_exception_with_message(self):
        """Test: Exception mit nur message"""
        exc = VoiceTranscriberError("Test error")
        assert str(exc) == "Test error"
        assert exc.user_message == "Test error"

    def test_base_exception_with_user_message(self):
        """Test: Exception mit separater user_message"""
        exc = VoiceTranscriberError(
            "Technical error details",
            user_message="User-friendly message"
        )
        assert str(exc) == "Technical error details"
        assert exc.user_message == "User-friendly message"

    def test_base_exception_inheritance(self):
        """Test: Exception erbt von Exception"""
        exc = VoiceTranscriberError("Test")
        assert isinstance(exc, Exception)


class TestAudioExceptions:
    """Tests für Audio-bezogene Exceptions"""

    def test_audio_recording_error(self):
        """Test: AudioRecordingError"""
        exc = AudioRecordingError(
            "Recording failed",
            user_message="Mikrofon nicht gefunden"
        )
        assert isinstance(exc, VoiceTranscriberError)
        assert exc.user_message == "Mikrofon nicht gefunden"

    def test_audio_compression_error(self):
        """Test: AudioCompressionError"""
        exc = AudioCompressionError(
            "Compression failed",
            user_message="Komprimierung fehlgeschlagen"
        )
        assert isinstance(exc, VoiceTranscriberError)
        assert exc.user_message == "Komprimierung fehlgeschlagen"


class TestTranscriptionError:
    """Tests für TranscriptionError"""

    def test_transcription_error(self):
        """Test: TranscriptionError"""
        exc = TranscriptionError(
            "API call failed",
            user_message="Keine Sprache erkannt"
        )
        assert isinstance(exc, VoiceTranscriberError)
        assert exc.user_message == "Keine Sprache erkannt"


class TestTextProcessingError:
    """Tests für TextProcessingError"""

    def test_text_processing_error(self):
        """Test: TextProcessingError"""
        exc = TextProcessingError(
            "GPT-4 call failed",
            user_message="Text-Korrektur fehlgeschlagen"
        )
        assert isinstance(exc, VoiceTranscriberError)
        assert exc.user_message == "Text-Korrektur fehlgeschlagen"


class TestClipboardError:
    """Tests für ClipboardError"""

    def test_clipboard_error(self):
        """Test: ClipboardError"""
        exc = ClipboardError(
            "inject_text() failed",
            user_message="Text konnte nicht eingefügt werden"
        )
        assert isinstance(exc, VoiceTranscriberError)
        assert exc.user_message == "Text konnte nicht eingefügt werden"


class TestNetworkErrors:
    """Tests für Netzwerk-bezogene Exceptions"""

    def test_network_error(self):
        """Test: NetworkError"""
        exc = NetworkError(
            "Connection timeout",
            user_message="Netzwerkproblem"
        )
        assert isinstance(exc, VoiceTranscriberError)
        assert exc.user_message == "Netzwerkproblem"

    def test_api_error(self):
        """Test: APIError"""
        exc = APIError(
            "OpenAI API returned 429",
            user_message="API-Limit erreicht"
        )
        assert isinstance(exc, VoiceTranscriberError)
        assert exc.user_message == "API-Limit erreicht"


class TestConfigurationError:
    """Tests für ConfigurationError"""

    def test_configuration_error(self):
        """Test: ConfigurationError"""
        exc = ConfigurationError(
            "Missing API key",
            user_message="Konfiguration ungültig"
        )
        assert isinstance(exc, VoiceTranscriberError)
        assert exc.user_message == "Konfiguration ungültig"


class TestExceptionCategories:
    """Tests für Exception-Kategorisierung"""

    def test_retryable_exceptions(self):
        """Test: RETRYABLE_EXCEPTIONS enthält richtige Typen"""
        assert NetworkError in RETRYABLE_EXCEPTIONS
        assert APIError in RETRYABLE_EXCEPTIONS
        assert len(RETRYABLE_EXCEPTIONS) == 2

    def test_critical_exceptions(self):
        """Test: CRITICAL_EXCEPTIONS enthält richtige Typen"""
        assert ConfigurationError in CRITICAL_EXCEPTIONS
        assert KeyboardInterrupt in CRITICAL_EXCEPTIONS
        assert SystemExit in CRITICAL_EXCEPTIONS
        assert len(CRITICAL_EXCEPTIONS) == 3

    def test_network_error_is_retryable(self):
        """Test: NetworkError ist als retryable kategorisiert"""
        exc = NetworkError("Test")
        assert isinstance(exc, RETRYABLE_EXCEPTIONS)

    def test_configuration_error_is_critical(self):
        """Test: ConfigurationError ist als critical kategorisiert"""
        exc = ConfigurationError("Test")
        assert isinstance(exc, CRITICAL_EXCEPTIONS)


class TestExceptionChaining:
    """Tests für Exception Chaining (from e)"""

    def test_exception_can_be_raised_from_another(self):
        """Test: Exception kann mit 'from e' geworfen werden"""
        try:
            try:
                raise IOError("Original error")
            except IOError as e:
                raise AudioRecordingError(
                    "Wrapped error",
                    user_message="User message"
                ) from e
        except AudioRecordingError as exc:
            assert exc.user_message == "User message"
            assert exc.__cause__ is not None
            assert isinstance(exc.__cause__, IOError)
            assert str(exc.__cause__) == "Original error"


class TestExceptionRaising:
    """Tests für Exception-Throwing"""

    def test_can_raise_and_catch_custom_exception(self):
        """Test: Custom Exception kann geworfen und gefangen werden"""
        with pytest.raises(AudioRecordingError) as exc_info:
            raise AudioRecordingError("Test error")

        assert str(exc_info.value) == "Test error"

    def test_can_catch_base_class(self):
        """Test: Spezifische Exception kann als Basis-Exception gefangen werden"""
        with pytest.raises(VoiceTranscriberError):
            raise AudioRecordingError("Test error")

    def test_can_catch_specific_type(self):
        """Test: Nur spezifische Exception wird gefangen"""
        with pytest.raises(AudioRecordingError):
            raise AudioRecordingError("Test error")

        # Andere Exception sollte nicht gefangen werden
        with pytest.raises(TranscriptionError):
            raise TranscriptionError("Different error")
