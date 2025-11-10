# Pystray Documentation - System Tray Icon Management

## Overview

Pystray is a Python library for creating and managing system tray icons across
different platforms (Windows, macOS, Linux).

## Key Features

- Cross-platform system tray icon support
- Dynamic menu creation
- Icon image management
- Notification support
- Thread-safe operations

## Basic Usage

### Creating a System Tray Icon

```python
import pystray
from PIL import Image

# Create icon image
def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

# Create and run icon
icon = pystray.Icon(
    'app_name',
    icon=create_image(64, 64, 'black', 'white'),
    title='App Title'
)

icon.run()  # Blocking call
```

### Adding Menus

```python
from pystray import Menu as menu, MenuItem as item

def on_quit(icon, item):
    icon.stop()

def on_settings(icon, item):
    # Open settings
    pass

# Create menu
menu_items = menu(
    item('Settings', on_settings),
    item('Quit', on_quit)
)

icon = pystray.Icon('app', icon, menu=menu_items)
```

### Dynamic Menu Items

```python
state = False

def toggle_state(icon, item):
    global state
    state = not state

def get_checked(item):
    return state

menu_items = menu(
    item('Toggle', toggle_state, checked=get_checked),
    item('Quit', on_quit)
)
```

## Platform Support

### Windows (win32 backend)

- Full feature support
- Default backend
- Reliable icon display

### macOS (darwin backend)

- Full feature support
- Icon.run() must be called from main thread
- Status bar integration

### Linux

- Multiple backends: appindicator, gtk, xorg
- appindicator preferred for guaranteed display
- GTK may require plugins for some desktop environments

## Important Methods

### Icon Class

- `icon.run()` - Start the icon (blocking)
- `icon.stop()` - Stop the icon
- `icon.notify(message, title)` - Show notification
- `icon.remove_notification()` - Remove notification
- `icon.update_menu()` - Refresh dynamic menu items

### Menu Item Properties

- `text` - Display text (required)
- `action` - Callback function (required)
- `checked` - Boolean or callable for checkbox state
- `enabled` - Whether item is clickable
- `visible` - Whether item is shown
- `submenu` - Nested menu

## Threading Considerations

- Icon operations are thread-safe
- Menu callbacks run in separate threads
- Use `icon.update_menu()` to refresh dynamic content
- For GUI framework integration, run icon in separate thread

## Common Patterns

### Status Indicator

```python
def get_status_text():
    return f"Status: {'Active' if is_active else 'Inactive'}"

menu_items = menu(
    item(get_status_text, lambda: None, enabled=False),
    item('Toggle', toggle_status),
    item('Quit', on_quit)
)
```

### Submenus

```python
submenu = menu(
    item('Option 1', action1),
    item('Option 2', action2)
)

main_menu = menu(
    item('Actions', submenu=submenu),
    item('Quit', on_quit)
)
```

## Error Handling

- Check `Icon.HAS_MENU` for menu support
- Check `Icon.HAS_DEFAULT` for default menu items
- Handle platform-specific limitations
- Use try/except for icon creation failures

## Integration with Tkinter

When using with tkinter GUIs, run pystray in separate thread:

```python
import threading

# Start pystray in background thread
threading.Thread(target=icon.run, daemon=True).start()

# Run tkinter mainloop in main thread
root.mainloop()
```

## Best Practices

1. Always provide a meaningful icon image
2. Include a quit option in menus
3. Use descriptive menu item text
4. Handle exceptions in menu callbacks
5. Test on target platforms
6. Consider accessibility (screen readers, etc.)
