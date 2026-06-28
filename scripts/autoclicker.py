import tkinter as tk
from tkinter import ttk
import pyautogui
import pytesseract
from PIL import ImageGrab
import threading
import time
import keyboard
import ctypes

# Configuration

# Path to Tesseract executable
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Hotkey with optional explainer text
# Leave HOTKEY_HELP_TEXT as empty string to disable
HOTKEY = "f13"
HOTKEY_HELP_TEXT = 'circle'

# Main click target (screen coordinates)
CLICK_X = 1842
CLICK_Y = 2054

# Bounding box to scan for "Skip" text (top-left and bottom-right screen coords)
SKIP_BOX_X1 = 1815
SKIP_BOX_Y1 = 1366
SKIP_BOX_X2 = 2021
SKIP_BOX_Y2 = 1498

# How often to check for Skip button (in seconds)
SKIP_CHECK_INTERVAL = 60

# Keyword to check for
SKIP_KEYWORD = 'Skip'

# Setup

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
pyautogui.PAUSE = 0

def fast_click(x, y):
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # left down
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # left up

# State

class AutoClicker:
    """
    Autoclicker main class.
    """
    def __init__(self):
        self.clicking = False
        self.click_interval_ms = 100
        self.click_thread = None
        self.skip_thread = None
        self.skip_detected = False
        self.lock = threading.Lock()

    def start(self):
        if self.clicking:
            return
        self.clicking = True
        self.click_thread = threading.Thread(target=self._click_loop, daemon=True)
        self.skip_thread = threading.Thread(target=self._skip_loop, daemon=True)
        self.click_thread.start()
        self.skip_thread.start()

    def stop(self):
        self.clicking = False

    def _click_loop(self):
        while self.clicking:
            with self.lock:
                skip = self.skip_detected

            if skip:
                # Click center of the Skip bounding box
                cx = (SKIP_BOX_X1 + SKIP_BOX_X2) // 2
                cy = (SKIP_BOX_Y1 + SKIP_BOX_Y2) // 2
                fast_click(cx, cy)
                print(f'Clicked "{SKIP_KEYWORD}"')
                with self.lock:
                    self.skip_detected = False
                time.sleep(3)
            else:
                fast_click(CLICK_X, CLICK_Y)

            time.sleep(self.click_interval_ms / 1000.0)

    def _skip_loop(self):
        while self.clicking:
            self._check_for_skip()
            time.sleep(SKIP_CHECK_INTERVAL)

    def _check_for_skip(self):
        try:
            screenshot = ImageGrab.grab(bbox=(
                SKIP_BOX_X1, SKIP_BOX_Y1,
                SKIP_BOX_X2, SKIP_BOX_Y2
            ))
            text = pytesseract.image_to_string(screenshot).strip().lower()
            if SKIP_KEYWORD.lower() in text:
                with self.lock:
                    self.skip_detected = True
        except Exception as e:
            print(f"Skip check error: {e}")


# GUI

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker")
        self.root.resizable(False, False)
        self.clicker = AutoClicker()

        self._build_ui()
        self._register_hotkey()
        self._update_status_loop()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # Status indicator
        self.status_var = tk.StringVar(value="Stopped")
        self.status_label = tk.Label(
            self.root, 
            textvariable=self.status_var,
            font=("Segoe UI", 14, "bold"), 
            fg="red"
        )
        self.status_label.grid(row=0, column=0, columnspan=2, **pad)

        # Click interval slider
        tk.Label(
            self.root, 
            text="Click Interval (ms):"
        ).grid(row=1, column=0, sticky="w", **pad)

        self.interval_var = tk.IntVar(value=100)
        slider = ttk.Scale(
            self.root, 
            from_=1, 
            to=1000,
            variable=self.interval_var, 
            orient="horizontal",
            length=200, 
            command=self._on_slider_change
        )
        slider.grid(row=1, column=1, **pad)

        # Interval display
        self.interval_display = tk.Label(self.root, text="100 ms")
        self.interval_display.grid(row=2, column=0, columnspan=2)

        # Start/Stop buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        self.start_btn = tk.Button(
            btn_frame, 
            text="Start", 
            width=10,
            bg="green", fg="white",
            command=self._start
        )
        self.start_btn.pack(side="left", padx=5)
        self.stop_btn = tk.Button(
            btn_frame, 
            text="Stop", 
            width=10,
            bg="red", 
            fg="white",
            command=self._stop, 
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)

        # Hotkey hint
        if HOTKEY_HELP_TEXT:
            hint_text = f"Hotkey: {HOTKEY} ({HOTKEY_HELP_TEXT}) to toggle"
        else:
            hint_text = f"Hotkey: {HOTKEY} to toggle"

        tk.Label(
            self.root, 
            text=hint_text,
            fg="gray"
        ).grid(row=4, column=0, columnspan=2, pady=(0, 8))

    def _on_slider_change(self, val):
        ms = int(float(val))
        self.interval_display.config(text=f"{ms} ms")
        self.clicker.click_interval_ms = ms

    def _register_hotkey(self):
        keyboard.add_hotkey(HOTKEY, lambda: self.root.after(0, self._toggle), suppress=False)

    def _toggle(self):
        if self.clicker.clicking:
            self._stop()
        else:
            self._start()

    def _start(self):
        self.clicker.click_interval_ms = self.interval_var.get()
        self.clicker.start()
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

    def _stop(self):
        self.clicker.stop()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def _update_status_loop(self):
        if self.clicker.clicking:
            self.status_var.set("Running")
            self.status_label.config(fg="green")
        else:
            self.status_var.set("Stopped")
            self.status_label.config(fg="red")
        self.root.after(200, self._update_status_loop)


# Entry Point

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
