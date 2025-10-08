"""
Icon Generator - Erstellt einfache Icons für die Anwendung
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_microphone_icon(size=256):
    """Erstellt ein einfaches Mikrofon-Icon"""
    # Erstelle neues Bild
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Berechne Proportionen
    center_x = size // 2
    center_y = size // 2

    # Mikrofon-Körper (Ellipse)
    body_width = int(size * 0.4)
    body_height = int(size * 0.6)
    body_x = center_x - body_width // 2
    body_y = center_y - body_height // 2 + int(size * 0.1)

    # Zeichne Mikrofon-Körper
    draw.ellipse([body_x, body_y, body_x + body_width, body_y + body_height],
                fill=(64, 128, 255), outline=(32, 64, 128), width=3)

    # Mikrofon-Kopf (kleinere Ellipse oben)
    head_width = int(size * 0.25)
    head_height = int(size * 0.15)
    head_x = center_x - head_width // 2
    head_y = body_y - head_height - int(size * 0.05)

    draw.ellipse([head_x, head_y, head_x + head_width, head_y + head_height],
                fill=(96, 160, 255), outline=(32, 64, 128), width=2)

    # Standfuß
    foot_width = int(size * 0.6)
    foot_height = int(size * 0.08)
    foot_x = center_x - foot_width // 2
    foot_y = body_y + body_height

    draw.rectangle([foot_x, foot_y, foot_x + foot_width, foot_y + foot_height],
                  fill=(128, 128, 128), outline=(64, 64, 64), width=1)

    # Stand
    stand_width = int(size * 0.05)
    stand_height = int(size * 0.3)
    stand_x = center_x - stand_width // 2
    stand_y = foot_y + foot_height

    draw.rectangle([stand_x, stand_y, stand_x + stand_width, stand_y + stand_height],
                  fill=(160, 160, 160), outline=(96, 96, 96), width=1)

    return img

def create_tray_icon(size=64):
    """Erstellt ein kleineres Tray-Icon"""
    return create_microphone_icon(size)

def save_icons():
    """Speichert Icons in verschiedenen Größen"""
    # Vollständiges Icon
    icon_256 = create_microphone_icon(256)
    icon_256.save('icon.png')
    print("Icon (256x256) gespeichert: icon.png")

    # Tray Icon
    tray_icon = create_tray_icon(64)
    tray_icon.save('tray_icon.png')
    print("Tray Icon (64x64) gespeichert: tray_icon.png")

    # ICO für Windows
    try:
        # Erstelle ICO mit mehreren Größen
        icon_sizes = [16, 32, 48, 64, 128, 256]
        icons = []
        for size in icon_sizes:
            icons.append(create_microphone_icon(size))

        # Speichere als ICO
        icons[0].save('icon.ico', format='ICO', sizes=[(s, s) for s in icon_sizes], append_images=icons[1:])
        print("Windows ICO gespeichert: icon.ico")
    except Exception as e:
        print(f"Fehler beim Erstellen der ICO-Datei: {e}")

if __name__ == "__main__":
    save_icons()
    print("Icon-Generierung abgeschlossen!")