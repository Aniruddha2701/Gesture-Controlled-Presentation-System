import pyautogui
import json
import os
from playsound import playsound
import threading

# Path for the keybindings configuration file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'keybindings.json')

# Default keybindings, can be overridden by the config file
DEFAULT_KEYBINDINGS = {
    "next_slide": "right",
    "previous_slide": "left",
    "start_slideshow": "f5",
    "stop_slideshow": "esc",
    "zoom_in": ["ctrl", "+"],
    "zoom_out": ["ctrl", "-"],
    "pointer_toggle": "ctrl",
    "fullscreen_toggle": "f11",
    "black_screen": "b",
    "white_screen": "w",
    # Added default bindings for new controls, you can customize in keybindings.json
    "mute_toggle": "m",            # Common mute toggle key in many presentation apps
    "laser_pointer_toggle": ["ctrl", "l"],  # Example for laser pointer toggle shortcut
    "annotation_toggle": ["ctrl", "p"],     # Example key combo for annotation (Pen tool)
    "next_section": "pageup",      # Jump to next section (example)
    "previous_section": "pagedown", # Jump to previous section (example)
}

# Load keybindings from config file if available
def load_keybindings():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                kb = json.load(f)
            print("[INFO] Loaded user keybindings from keybindings.json.")
            return {**DEFAULT_KEYBINDINGS, **kb}  # Merge defaults with overrides
        except Exception as e:
            print(f"[WARN] Failed to load keybindings.json: {e}")
    print("[INFO] Using default keybindings.")
    return DEFAULT_KEYBINDINGS

keybindings = load_keybindings()

# Helper to press single key or key combo
def _do_action(key_or_combo):
    try:
        if isinstance(key_or_combo, list):
            pyautogui.hotkey(*key_or_combo)
        else:
            pyautogui.press(key_or_combo)
    except Exception as e:
        print(f"[ERROR] Failed to send keys {key_or_combo}: {e}")

# Presentation controls
def next_slide():
    _do_action(keybindings["next_slide"])

def previous_slide():
    _do_action(keybindings["previous_slide"])

def start_slideshow():
    _do_action(keybindings["start_slideshow"])

def stop_slideshow():
    _do_action(keybindings["stop_slideshow"])

def zoom_in():
    _do_action(keybindings["zoom_in"])

def zoom_out():
    _do_action(keybindings["zoom_out"])

def pointer_toggle():
    _do_action(keybindings["pointer_toggle"])

def fullscreen_toggle():
    _do_action(keybindings["fullscreen_toggle"])

def black_screen():
    _do_action(keybindings["black_screen"])

def white_screen():
    _do_action(keybindings["white_screen"])

def scroll_up(amount=5):
    """
    Scroll up by the specified amount.
    Positive values scroll up.
    """
    pyautogui.scroll(amount)

def scroll_down(amount=5):
    """
    Scroll down by the specified amount.
    Positive values scroll down.
    """
    pyautogui.scroll(-amount)

# New feature functions for added gestures

def mute_toggle():
    """
    Toggle audio mute using a keybinding.
    """
    _do_action(keybindings["mute_toggle"])

def laser_pointer_toggle():
    """
    Toggle laser pointer mode.
    """
    _do_action(keybindings["laser_pointer_toggle"])

def annotation_toggle():
    """
    Toggle annotation (pen) mode.
    """
    _do_action(keybindings["annotation_toggle"])

def next_section():
    """
    Jump to next presentation section.
    """
    _do_action(keybindings["next_section"])

def previous_section():
    """
    Jump to previous presentation section.
    """
    _do_action(keybindings["previous_section"])

def play_feedback_sound():
    def _play():
        sound_file = os.path.join(os.path.dirname(__file__), "bell.mp3")
        if os.path.exists(sound_file):
            try:
                playsound(sound_file, block=False)
            except Exception as e:
                print(f"[WARN] Could not play sound: {e}")
    threading.Thread(target=_play, daemon=True).start()
