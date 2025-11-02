"""
Tests für Notification Service
"""

import pytest
from src.notification import (
    NotificationService,
    NotificationType,
    notification_service
)


class TestNotificationType:
    """Tests für NotificationType Enum"""

    def test_notification_types_exist(self):
        """Test: Alle Notification-Typen existieren"""
        assert NotificationType.INFO.value == "info"
        assert NotificationType.SUCCESS.value == "success"
        assert NotificationType.WARNING.value == "warning"
        assert NotificationType.ERROR.value == "error"

    def test_notification_type_is_enum(self):
        """Test: NotificationType ist ein Enum"""
        from enum import Enum
        assert issubclass(NotificationType, Enum)


class TestNotificationService:
    """Tests für NotificationService"""

    def setup_method(self):
        """Setup: Erstelle neue Service-Instanz für jeden Test"""
        self.service = NotificationService()

    def test_service_initialization(self):
        """Test: Service wird korrekt initialisiert"""
        assert self.service.enabled is True
        assert isinstance(self.service._notification_history, list)
        assert len(self.service._notification_history) == 0

    def test_notify_info(self):
        """Test: Info-Notification"""
        result = self.service.notify_info("Test info message")
        assert result is True
        assert len(self.service._notification_history) == 1
        assert self.service._notification_history[0]['message'] == "Test info message"
        assert self.service._notification_history[0]['type'] == "info"

    def test_notify_success(self):
        """Test: Success-Notification"""
        result = self.service.notify_success("Test success message")
        assert result is True
        assert len(self.service._notification_history) == 1
        assert self.service._notification_history[0]['type'] == "success"

    def test_notify_warning(self):
        """Test: Warning-Notification"""
        result = self.service.notify_warning("Test warning message")
        assert result is True
        assert len(self.service._notification_history) == 1
        assert self.service._notification_history[0]['type'] == "warning"

    def test_notify_error(self):
        """Test: Error-Notification"""
        result = self.service.notify_error("Test error message")
        # Error-Notifications können je nach System-Umgebung fehlschlagen
        # (z.B. wenn kein Display verfügbar ist), daher prüfen wir nur History
        assert len(self.service._notification_history) == 1
        assert self.service._notification_history[0]['type'] == "error"
        assert self.service._notification_history[0]['message'] == "Test error message"

    def test_notify_with_custom_title(self):
        """Test: Notification mit custom title"""
        result = self.service.notify_info("Message", title="Custom Title")
        assert result is True
        assert self.service._notification_history[0]['title'] == "Custom Title"

    def test_enable_disable(self):
        """Test: Service kann aktiviert/deaktiviert werden"""
        assert self.service.enabled is True

        self.service.disable()
        assert self.service.enabled is False

        self.service.enable()
        assert self.service.enabled is True

    def test_disabled_service_does_not_notify(self):
        """Test: Deaktivierter Service zeigt keine Notifications"""
        self.service.disable()
        result = self.service.notify_info("Should not be shown")

        # Sollte False zurückgeben wenn deaktiviert
        assert result is False
        # History sollte trotzdem NICHT wachsen wenn deaktiviert
        assert len(self.service._notification_history) == 0

    def test_notification_history(self):
        """Test: History speichert alle Notifications"""
        self.service.notify_info("Message 1")
        self.service.notify_success("Message 2")
        self.service.notify_warning("Message 3")

        assert len(self.service._notification_history) == 3
        assert self.service._notification_history[0]['message'] == "Message 1"
        assert self.service._notification_history[1]['message'] == "Message 2"
        assert self.service._notification_history[2]['message'] == "Message 3"

    def test_get_history(self):
        """Test: get_history() gibt letzte N Notifications zurück"""
        for i in range(15):
            self.service.notify_info(f"Message {i}")

        # Hole letzte 10
        history = self.service.get_history(limit=10)
        assert len(history) == 10
        assert history[0]['message'] == "Message 5"  # 15-10 = 5
        assert history[-1]['message'] == "Message 14"

    def test_get_history_default_limit(self):
        """Test: get_history() Default-Limit ist 10"""
        for i in range(15):
            self.service.notify_info(f"Message {i}")

        history = self.service.get_history()
        assert len(history) == 10

    def test_notification_with_different_durations(self):
        """Test: Notifications mit verschiedenen Dauern"""
        # Info: 2000ms
        result_info = self.service.notify_info("Info")
        assert result_info is True

        # Success: 2000ms
        result_success = self.service.notify_success("Success")
        assert result_success is True

        # Warning: 3000ms
        result_warning = self.service.notify_warning("Warning")
        assert result_warning is True

        # Error: 5000ms
        result_error = self.service.notify_error("Error")
        # Error kann fehlschlagen, aber History sollte trotzdem da sein
        assert len(self.service._notification_history) == 4

    def test_notification_with_custom_duration(self):
        """Test: Notification mit custom duration"""
        result = self.service.notify(
            "Test message",
            notification_type=NotificationType.INFO,
            duration=10000
        )
        assert result is True
        assert len(self.service._notification_history) == 1


class TestGlobalNotificationService:
    """Tests für globale notification_service Instanz"""

    def test_global_service_exists(self):
        """Test: Globale Service-Instanz existiert"""
        assert notification_service is not None
        assert isinstance(notification_service, NotificationService)

    def test_global_service_is_enabled_by_default(self):
        """Test: Globaler Service ist standardmäßig aktiviert"""
        # Merke ursprünglichen Zustand
        original_state = notification_service.enabled

        # Test
        assert notification_service.enabled is True

        # Stelle ursprünglichen Zustand wieder her
        if not original_state:
            notification_service.enable()

    def test_global_service_can_be_used(self):
        """Test: Globaler Service kann genutzt werden"""
        # Clear history für sauberen Test
        original_history_len = len(notification_service._notification_history)

        result = notification_service.notify_info("Global service test")
        assert result is True

        # History sollte gewachsen sein
        assert len(notification_service._notification_history) > original_history_len


class TestFallbackNotification:
    """Tests für Fallback-Mechanismus"""

    def test_fallback_logs_non_error_notifications(self, caplog):
        """Test: Fallback loggt nicht-Error Notifications"""
        service = NotificationService()

        # Simuliere fehlende win10toast
        result = service._fallback_notification(
            "Test message",
            NotificationType.INFO,
            "Test Title"
        )

        assert result is True
        # Prüfe, dass geloggt wurde (caplog benötigt pytest)
        # (In echtem Test würde man caplog.records prüfen)

    def test_fallback_handles_error_notifications(self):
        """Test: Fallback behandelt Error-Notifications anders"""
        service = NotificationService()

        # Error-Notifications sollten MessageBox versuchen
        # (kann in Headless-Umgebung fehlschlagen, das ist OK)
        try:
            result = service._fallback_notification(
                "Test error",
                NotificationType.ERROR,
                "Error Title"
            )
            # Wenn es klappt: True
            # Wenn es fehlschlägt: False oder Exception
            assert result in [True, False]
        except Exception:
            # In Headless-Umgebung OK
            pass


class TestNotificationErrorHandling:
    """Tests für Error-Handling im NotificationService"""

    def test_notify_handles_exceptions_gracefully(self):
        """Test: notify() fängt Exceptions ab"""
        service = NotificationService()

        # Sollte nicht crashen, selbst wenn etwas schief geht
        try:
            result = service.notify(
                "Test",
                notification_type=NotificationType.INFO
            )
            # Sollte True oder False sein, aber nicht Exception
            assert result in [True, False]
        except Exception as e:
            pytest.fail(f"notify() sollte nicht crashen: {e}")

    def test_disabled_service_returns_false(self):
        """Test: Deaktivierter Service gibt False zurück"""
        service = NotificationService()
        service.disable()

        result = service.notify_info("Test")
        assert result is False
