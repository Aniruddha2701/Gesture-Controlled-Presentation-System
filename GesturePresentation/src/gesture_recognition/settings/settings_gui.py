import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Settings file path relative to this script
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "gesture_settings.json")

DEFAULT_SETTINGS = {
    "hold_duration_required": 0.8,
    "swipe_horizontal_threshold": 0.05,
    "scroll_vertical_threshold": 0.04,
    "finger_motion_cooldown": 0.8,
    "zoom_cooldown": 0.6,
    "smoothing_window": 5
}

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
            settings = {**DEFAULT_SETTINGS, **data}  # merge with defaults
            return settings
        except Exception as e:
            print(f"Failed to load settings: {e}")
            return dict(DEFAULT_SETTINGS)
    return dict(DEFAULT_SETTINGS)

def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save settings: {e}")
        return False

class SettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gesture Sensitivity & Calibration Settings")
        self.settings = load_settings()

        self.hold_var = tk.DoubleVar(value=self.settings["hold_duration_required"])
        self.swipe_var = tk.DoubleVar(value=self.settings["swipe_horizontal_threshold"])
        self.scroll_var = tk.DoubleVar(value=self.settings["scroll_vertical_threshold"])
        self.cooldown_var = tk.DoubleVar(value=self.settings["finger_motion_cooldown"])
        self.zoom_cooldown_var = tk.DoubleVar(value=self.settings["zoom_cooldown"])
        self.smooth_var = tk.IntVar(value=self.settings["smoothing_window"])

        pad = {'padx': 10, 'pady': 8}

        ttk.Label(root, text="Hold-to-Confirm Duration (seconds):").grid(row=0, column=0, sticky='e', **pad)
        ttk.Scale(root, from_=0.3, to=2.0, orient='horizontal', variable=self.hold_var, length=220).grid(row=0, column=1, **pad)
        ttk.Label(root, textvariable=self.hold_var, width=5).grid(row=0, column=2)

        ttk.Label(root, text="Swipe Horizontal Threshold:").grid(row=1, column=0, sticky='e', **pad)
        ttk.Scale(root, from_=0.01, to=0.2, orient='horizontal', variable=self.swipe_var, length=220).grid(row=1, column=1, **pad)
        ttk.Label(root, textvariable=self.swipe_var, width=6).grid(row=1, column=2)

        ttk.Label(root, text="Scroll Vertical Threshold:").grid(row=2, column=0, sticky='e', **pad)
        ttk.Scale(root, from_=0.01, to=0.2, orient='horizontal', variable=self.scroll_var, length=220).grid(row=2, column=1, **pad)
        ttk.Label(root, textvariable=self.scroll_var, width=6).grid(row=2, column=2)

        ttk.Label(root, text="Finger Motion Cooldown (seconds):").grid(row=3, column=0, sticky='e', **pad)
        ttk.Scale(root, from_=0.1, to=2.0, orient='horizontal', variable=self.cooldown_var, length=220).grid(row=3, column=1, **pad)
        ttk.Label(root, textvariable=self.cooldown_var, width=5).grid(row=3, column=2)

        ttk.Label(root, text="Zoom Gesture Cooldown (seconds):").grid(row=4, column=0, sticky='e', **pad)
        ttk.Scale(root, from_=0.1, to=2.0, orient='horizontal', variable=self.zoom_cooldown_var, length=220).grid(row=4, column=1, **pad)
        ttk.Label(root, textvariable=self.zoom_cooldown_var, width=5).grid(row=4, column=2)

        ttk.Label(root, text="Landmark Smoothing Window (frames):").grid(row=5, column=0, sticky='e', **pad)
        ttk.Scale(root, from_=1, to=15, orient='horizontal', variable=self.smooth_var, length=220).grid(row=5, column=1, **pad)
        ttk.Label(root, textvariable=self.smooth_var, width=4).grid(row=5, column=2)

        ttk.Button(root, text="Save Settings", command=self.save).grid(row=6, column=0, columnspan=3, pady=(20, 10))

    def save(self):
        new_settings = {
            "hold_duration_required": float(self.hold_var.get()),
            "swipe_horizontal_threshold": float(self.swipe_var.get()),
            "scroll_vertical_threshold": float(self.scroll_var.get()),
            "finger_motion_cooldown": float(self.cooldown_var.get()),
            "zoom_cooldown": float(self.zoom_cooldown_var.get()),
            "smoothing_window": int(self.smooth_var.get()),
        }
        if save_settings(new_settings):
            messagebox.showinfo("Settings Saved", "Calibration/settings saved successfully.\nThey will be used at next program run.")
            self.root.quit()
        else:
            messagebox.showerror("Save Failed", "Could not save settings. Please check write permissions.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SettingsGUI(root)
    root.mainloop()
