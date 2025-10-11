#!/usr/bin/env python3
"""
Test-Script um zu prüfen, ob das Programm startet
"""

import sys
import threading
import time


def test_main():
    try:
        from src.main import main
        main()
    except Exception as e:
        print(f"Fehler beim Starten: {e}")
        import traceback
        traceback.print_exc()

# Starte in separatem Thread mit Timeout
main_thread = threading.Thread(target=test_main, daemon=True)
main_thread.start()

# Warte 5 Sekunden
time.sleep(5)

if main_thread.is_alive():
    print("Programm läuft noch (Tray-Icon sollte sichtbar sein)")
    sys.exit(0)
else:
    print("Programm beendet")