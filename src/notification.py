"""
User Notification System - Toast-Benachrichtigungen
Zeigt dem User freundliche Fehler- und Status-Meldungen.
"""

import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification-Typen"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationService:
    """Service für User-Benachrichtigungen"""

    def __init__(self):
        self.enabled = True
        self._notification_history = []

    def notify(self,
               message: str,
               notification_type: NotificationType = NotificationType.INFO,
               title: str = "Voice Transcriber",
               duration: int = 3000) -> bool:
        """
        Zeigt eine Benachrichtigung an

        Args:
            message: Nachricht für User
            notification_type: Art der Benachrichtigung
            title: Titel der Benachrichtigung
            duration: Anzeigedauer in Millisekunden

        Returns:
            True wenn erfolgreich, False sonst
        """
        if not self.enabled:
            logger.debug(f"Notifications deaktiviert - überspringe: {message}")
            return False

        try:
            # Speichere in History
            self._notification_history.append({
                'message': message,
                'type': notification_type.value,
                'title': title
            })

            # Windows Toast Notification (optional)
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()

                # Icon basierend auf Type
                icon_path = "assets/icon.ico"

                toaster.show_toast(
                    title=title,
                    msg=message,
                    icon_path=icon_path,
                    duration=duration / 1000,  # Sekunden
                    threaded=True
                )
                return True

            except ImportError:
                # Fallback: Tkinter MessageBox
                logger.debug("win10toast nicht verfügbar, verwende Fallback")
                return self._fallback_notification(message, notification_type, title)
            except Exception as e:
                logger.warning(f"Toast-Notification fehlgeschlagen: {e}")
                return self._fallback_notification(message, notification_type, title)

        except Exception as e:
            logger.error(f"Fehler bei Notification: {e}")
            return False

    def _fallback_notification(self,
                               message: str,
                               notification_type: NotificationType,
                               title: str) -> bool:
        """Fallback: Einfache Benachrichtigung ohne externe Dependencies"""
        try:
            # Nur für kritische Fehler ein MessageBox anzeigen
            if notification_type == NotificationType.ERROR:
                import tkinter as tk
                from tkinter import messagebox

                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)

                messagebox.showerror(title, message, parent=root)
                root.destroy()
                return True
            else:
                # Für andere Typen nur loggen
                logger.info(f"[{notification_type.value.upper()}] {title}: {message}")
                return True

        except Exception as e:
            logger.error(f"Fallback-Notification fehlgeschlagen: {e}")
            return False

    def notify_error(self, message: str, title: str = "Fehler") -> bool:
        """Zeigt eine Fehler-Benachrichtigung"""
        return self.notify(message, NotificationType.ERROR, title, duration=5000)

    def notify_success(self, message: str, title: str = "Erfolg") -> bool:
        """Zeigt eine Erfolgs-Benachrichtigung"""
        return self.notify(message, NotificationType.SUCCESS, title, duration=2000)

    def notify_warning(self, message: str, title: str = "Warnung") -> bool:
        """Zeigt eine Warn-Benachrichtigung"""
        return self.notify(message, NotificationType.WARNING, title, duration=3000)

    def notify_info(self, message: str, title: str = "Info") -> bool:
        """Zeigt eine Info-Benachrichtigung"""
        return self.notify(message, NotificationType.INFO, title, duration=2000)

    def enable(self):
        """Aktiviert Benachrichtigungen"""
        self.enabled = True
        logger.info("Benachrichtigungen aktiviert")

    def disable(self):
        """Deaktiviert Benachrichtigungen"""
        self.enabled = False
        logger.info("Benachrichtigungen deaktiviert")

    def get_history(self, limit: int = 10) -> list:
        """Gibt die letzten N Benachrichtigungen zurück"""
        return self._notification_history[-limit:]


# Globale Instanz
notification_service = NotificationService()
