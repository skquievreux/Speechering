"""
Entry point für direkte Modul-Ausführung: python -m src
"""

try:
    # Versuche relative Imports (für python -m src)
    from .main import main
except ImportError:
    # Fallback für direkte Ausführung oder PyInstaller
    from main import main

if __name__ == "__main__":
    main()