#!/usr/bin/env python3
"""
Test-Script für Hotkey-Funktionalität
"""

import logging
import time

import keyboard

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')

def on_press():
    print("Hotkey gedrückt!")

def on_release():
    print("Hotkey losgelassen!")

print("Registriere F12...")
try:
    keyboard.on_press_key('f12', lambda e: on_press())
    keyboard.on_release_key('f12', lambda e: on_release())
    print("F12 erfolgreich registriert. Drücke F12 zum Testen (Strg+C zum Beenden)")
except Exception as e:
    print(f"Fehler bei Hotkey-Registrierung: {e}")

# Warte auf Eingabe
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Beendet")
    keyboard.unhook_all()