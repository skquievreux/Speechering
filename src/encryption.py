"""
Verschlüsselungsmodul für sichere Speicherung sensibler Daten.
Verwendet Fernet (AES-256) mit PBKDF2-generiertem Schlüssel.
"""

import base64
import hashlib
import logging
import os
import platform
from typing import Optional

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logging.warning("cryptography Paket nicht verfügbar - verwende Fallback-Modus")

logger = logging.getLogger(__name__)

class SecureStorage:
    """Sichere Speicherung sensibler Daten mit Verschlüsselung"""

    def __init__(self):
        self._fernet: Optional[Fernet] = None
        self._salt = self._get_machine_salt()

        if CRYPTOGRAPHY_AVAILABLE:
            self._init_cipher()
        else:
            logger.warning("Verschlüsselung nicht verfügbar - sensible Daten werden unverschlüsselt gespeichert")

    def _get_machine_salt(self) -> bytes:
        """Generiert einen maschinen-spezifischen Salt"""
        try:
            # Verwende System-Informationen für Salt-Generierung
            system_info = platform.uname()
            salt_source = f"{system_info.node}{system_info.machine}{system_info.processor}"

            # Erstelle deterministischen Salt aus Hardware-Info
            salt = hashlib.sha256(salt_source.encode('utf-8')).digest()
            return salt[:16]  # PBKDF2 braucht 16 Bytes

        except Exception as e:
            logger.warning(f"Fehler bei Salt-Generierung: {e}")
            # Fallback-Salt
            return b"VoiceTranscriberSalt2024"

    def _init_cipher(self):
        """Initialisiert den Verschlüsselungs-Cipher"""
        try:
            # Erstelle Schlüssel aus Salt und festem Passwort
            # Das Passwort ist fest kodiert, aber durch Salt maschinen-spezifisch
            password = b"VoiceTranscriberSecureKey2024"

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self._salt,
                iterations=100000,
            )

            key = base64.urlsafe_b64encode(kdf.derive(password))
            self._fernet = Fernet(key)

            logger.debug("Verschlüsselung erfolgreich initialisiert")

        except Exception as e:
            logger.error(f"Fehler bei Verschlüsselungs-Initialisierung: {e}")
            self._fernet = None

    def encrypt(self, plaintext: str) -> str:
        """Verschlüsselt einen Text"""
        if not CRYPTOGRAPHY_AVAILABLE or not self._fernet:
            # Fallback: Base64-Encoding ohne Verschlüsselung
            logger.warning("Verwende ungesicherte Fallback-Verschlüsselung")
            return base64.b64encode(plaintext.encode('utf-8')).decode('utf-8')

        try:
            encrypted = self._fernet.encrypt(plaintext.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Fehler bei Verschlüsselung: {e}")
            # Fallback
            return base64.b64encode(plaintext.encode('utf-8')).decode('utf-8')

    def decrypt(self, encrypted_text: str) -> str:
        """Entschlüsselt einen Text"""
        if not CRYPTOGRAPHY_AVAILABLE or not self._fernet:
            # Fallback: Base64-Decoding
            try:
                return base64.b64decode(encrypted_text.encode('utf-8')).decode('utf-8')
            except Exception as e:
                logger.debug(f"Fehler bei Fallback-Entschlüsselung: {e}")
                return None

        try:
            decrypted = self._fernet.decrypt(encrypted_text.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Fehler bei Entschlüsselung: {e}")
            # Versuche Fallback (Base64)
            try:
                return base64.b64decode(encrypted_text.encode('utf-8')).decode('utf-8')
            except Exception:
                logger.error("Auch Fallback-Entschlüsselung fehlgeschlagen")
                return None  # WICHTIG: None zurückgeben, nicht den verschlüsselten Text!

    def is_encryption_available(self) -> bool:
        """Prüft ob echte Verschlüsselung verfügbar ist"""
        return CRYPTOGRAPHY_AVAILABLE and self._fernet is not None

# Globale Instanz
secure_storage = SecureStorage()