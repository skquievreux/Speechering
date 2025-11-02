"""
Tests für Error-Handling in main.py
Testet das verbesserte Exception-Handling in _perform_recording()
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.main import VoiceTranscriberApp
from src.exceptions import (
    AudioRecordingError,
    AudioCompressionError,
    TranscriptionError,
    NetworkError,
    ClipboardError
)


class TestPerformRecordingErrorHandling:
    """Tests für _perform_recording() Error-Handling"""

    def setup_method(self):
        """Setup: Erstelle App-Instanz mit gemockten Komponenten"""
        self.app = VoiceTranscriberApp()

        # Mock alle kritischen Komponenten
        self.app.audio_recorder = Mock()
        self.app._transcription_service_instance = Mock()
        self.app.text_processor = Mock()
        self.app.clipboard_injector = Mock()
        self.app.recording_stop_event = Mock()

    @patch('src.main.notification_service')
    @patch('src.main.logger')
    def test_audio_recording_error_is_caught(self, mock_logger, mock_notification):
        """Test: AudioRecordingError wird korrekt abgefangen"""
        # Simuliere Audio-Recording-Fehler
        self.app.audio_recorder.start_recording.return_value = None

        # Führe Aufnahme aus
        self.app._perform_recording()

        # Prüfe, dass Fehler geloggt wurde
        mock_logger.error.assert_called()

        # Prüfe, dass User-Notification gesendet wurde
        mock_notification.notify_error.assert_called()

    @patch('src.main.notification_service')
    @patch('src.main.logger')
    @patch('src.main.config')
    def test_audio_compression_error_is_caught(self, mock_config, mock_logger, mock_notification):
        """Test: AudioCompressionError wird korrekt abgefangen"""
        # Aktiviere Komprimierung
        mock_config.AUDIO_COMPRESSION_ENABLED = True

        # Simuliere Komprimierungs-Fehler
        self.app.audio_recorder.record_and_compress.return_value = None

        with patch('src.main.PYDUB_AVAILABLE', True):
            # Führe Aufnahme aus
            self.app._perform_recording()

        # Prüfe, dass Fehler geloggt wurde
        mock_logger.error.assert_called()

        # Prüfe, dass User-Notification gesendet wurde
        mock_notification.notify_error.assert_called()

    @patch('src.main.notification_service')
    @patch('src.main.logger')
    @patch('src.main.config')
    def test_transcription_error_is_caught(self, mock_config, mock_logger, mock_notification):
        """Test: TranscriptionError wird korrekt abgefangen"""
        # Deaktiviere Komprimierung für einfacheren Test
        mock_config.AUDIO_COMPRESSION_ENABLED = False
        mock_config.MAX_RECORDING_DURATION = 30

        # Setup erfolgreiche Audio-Aufnahme
        self.app.audio_recorder.start_recording.return_value = "/tmp/audio.wav"
        self.app.audio_recorder.stop_recording.return_value = "/tmp/audio.wav"
        self.app.audio_recorder.last_recording_duration = 1.0

        # Simuliere Transkriptions-Fehler
        self.app._transcription_service_instance.transcribe.return_value = None

        with patch('src.main.PYDUB_AVAILABLE', False):
            # Führe Aufnahme aus
            self.app._perform_recording()

        # Prüfe, dass Fehler geloggt wurde
        mock_logger.error.assert_called()

        # Prüfe, dass User-Notification gesendet wurde
        mock_notification.notify_error.assert_called()

    @patch('src.main.notification_service')
    @patch('src.main.logger')
    @patch('src.main.config')
    def test_successful_workflow_sends_success_notification(self, mock_config, mock_logger, mock_notification):
        """Test: Erfolgreicher Workflow sendet Success-Notification"""
        # Deaktiviere Komprimierung
        mock_config.AUDIO_COMPRESSION_ENABLED = False
        mock_config.MAX_RECORDING_DURATION = 30

        # Setup erfolgreiche Audio-Aufnahme
        self.app.audio_recorder.start_recording.return_value = "/tmp/audio.wav"
        self.app.audio_recorder.stop_recording.return_value = "/tmp/audio.wav"
        self.app.audio_recorder.last_recording_duration = 1.0

        # Setup erfolgreiche Transkription
        self.app._transcription_service_instance.transcribe.return_value = "Test transcript"

        # Setup erfolgreiche Text-Verarbeitung
        self.app.text_processor.process_text.return_value = "Corrected text"

        # Setup erfolgreiche Text-Einfügung
        self.app.clipboard_injector.inject_text.return_value = True

        with patch('src.main.PYDUB_AVAILABLE', False):
            # Führe Aufnahme aus
            self.app._perform_recording()

        # Prüfe, dass Success-Notification gesendet wurde
        mock_notification.notify_success.assert_called_once()

    @patch('src.main.notification_service')
    @patch('src.main.logger')
    @patch('src.main.config')
    def test_short_recording_sends_warning(self, mock_config, mock_logger, mock_notification):
        """Test: Zu kurze Aufnahme sendet Warning"""
        # Deaktiviere Komprimierung
        mock_config.AUDIO_COMPRESSION_ENABLED = False
        mock_config.MAX_RECORDING_DURATION = 30

        # Setup erfolgreiche Audio-Aufnahme, aber zu kurz
        self.app.audio_recorder.start_recording.return_value = "/tmp/audio.wav"
        self.app.audio_recorder.stop_recording.return_value = "/tmp/audio.wav"
        self.app.audio_recorder.last_recording_duration = 0.3  # Zu kurz!

        with patch('src.main.PYDUB_AVAILABLE', False):
            # Führe Aufnahme aus
            self.app._perform_recording()

        # Prüfe, dass Warning geloggt wurde
        mock_logger.warning.assert_called()

        # Prüfe, dass Warning-Notification gesendet wurde
        mock_notification.notify_warning.assert_called_once()

    @patch('src.main.notification_service')
    @patch('src.main.logger')
    @patch('src.main.config')
    @patch('src.main.pyperclip')
    def test_clipboard_fallback_on_injection_failure(self, mock_pyperclip, mock_config, mock_logger, mock_notification):
        """Test: Fallback auf Clipboard wenn Injection fehlschlägt"""
        # Deaktiviere Komprimierung
        mock_config.AUDIO_COMPRESSION_ENABLED = False
        mock_config.MAX_RECORDING_DURATION = 30

        # Setup erfolgreiche Audio-Aufnahme & Transkription
        self.app.audio_recorder.start_recording.return_value = "/tmp/audio.wav"
        self.app.audio_recorder.stop_recording.return_value = "/tmp/audio.wav"
        self.app.audio_recorder.last_recording_duration = 1.0
        self.app._transcription_service_instance.transcribe.return_value = "Test"
        self.app.text_processor.process_text.return_value = "Test"

        # Simuliere Injection-Fehler
        self.app.clipboard_injector.inject_text.return_value = False

        with patch('src.main.PYDUB_AVAILABLE', False):
            # Führe Aufnahme aus
            self.app._perform_recording()

        # Prüfe, dass Clipboard-Fallback verwendet wurde
        mock_pyperclip.copy.assert_called_once_with("Test")

        # Prüfe, dass Warning-Notification gesendet wurde
        mock_notification.notify_warning.assert_called()

    @patch('src.main.notification_service')
    @patch('src.main.logger')
    def test_cleanup_runs_on_exception(self, mock_logger, mock_notification):
        """Test: Cleanup läuft auch bei Exception"""
        # Simuliere Exception
        self.app.audio_recorder.start_recording.side_effect = Exception("Test error")

        # Führe Aufnahme aus
        self.app._perform_recording()

        # Prüfe, dass is_recording zurückgesetzt wurde
        assert self.app.is_recording is False

    @patch('src.main.notification_service')
    @patch('src.main.logger')
    def test_keyboard_interrupt_handled_gracefully(self, mock_logger, mock_notification):
        """Test: KeyboardInterrupt wird graceful behandelt"""
        # Simuliere KeyboardInterrupt
        self.app.audio_recorder.start_recording.side_effect = KeyboardInterrupt()

        # Sollte nicht crashen
        self.app._perform_recording()

        # Prüfe, dass Info-Log geschrieben wurde
        mock_logger.info.assert_called()

        # Prüfe, dass Info-Notification gesendet wurde
        mock_notification.notify_info.assert_called()


class TestExceptionUserMessages:
    """Tests für User-Messages in Exceptions"""

    def test_audio_recording_error_has_user_message(self):
        """Test: AudioRecordingError hat user-friendly message"""
        exc = AudioRecordingError(
            "Technical details",
            user_message="Mikrofon nicht gefunden"
        )
        assert exc.user_message == "Mikrofon nicht gefunden"

    def test_transcription_error_has_user_message(self):
        """Test: TranscriptionError hat user-friendly message"""
        exc = TranscriptionError(
            "API returned 500",
            user_message="Transkription fehlgeschlagen"
        )
        assert exc.user_message == "Transkription fehlgeschlagen"

    def test_network_error_has_user_message(self):
        """Test: NetworkError hat user-friendly message"""
        exc = NetworkError(
            "Connection timeout after 30s",
            user_message="Netzwerkproblem"
        )
        assert exc.user_message == "Netzwerkproblem"


class TestErrorHandlingIntegration:
    """Integration Tests für Error-Handling"""

    @patch('src.main.notification_service')
    @patch('src.main.logger')
    @patch('src.main.config')
    def test_full_error_flow_from_recording_to_notification(self, mock_config, mock_logger, mock_notification):
        """Test: Vollständiger Error-Flow von Exception bis Notification"""
        app = VoiceTranscriberApp()

        # Mock Komponenten
        app.audio_recorder = Mock()
        app._transcription_service_instance = Mock()
        app.text_processor = Mock()
        app.clipboard_injector = Mock()
        app.recording_stop_event = Mock()

        # Deaktiviere Komprimierung
        mock_config.AUDIO_COMPRESSION_ENABLED = False

        # Simuliere Recording-Fehler
        app.audio_recorder.start_recording.side_effect = OSError("Device not found")

        with patch('src.main.PYDUB_AVAILABLE', False):
            # Führe Aufnahme aus
            app._perform_recording()

        # Prüfe gesamten Flow:
        # 1. Exception wird geworfen
        # 2. Als AudioRecordingError wrapped
        # 3. Geloggt
        mock_logger.error.assert_called()

        # 4. User-Notification gesendet
        mock_notification.notify_error.assert_called()

        # 5. Cleanup durchgeführt
        assert app.is_recording is False
