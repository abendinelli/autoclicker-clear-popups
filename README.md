# autoclicker-clear-popups

An autoclicker that clicks a fixed point on screen at a configurable speed, and
periodically checks a region of the screen for a keyword (such as "Skip"). When
that keyword is detected, the clicker temporarily redirects its next click into
that region to dismiss the pop-up, then returns to its normal click point.

It was built for an idle game in which floating objects can
trigger a pop-up that pauses resource gains until a "Skip" button is clicked. A
plain fixed-position autoclicker can accidentally hit the wrong button as the
pop-up slides into place, so this tool watches for the pop-up and clears it
safely.

## Features

- Clicks a fixed screen coordinate at an interval you choose (1 to 1000 ms).
- Uses low-level Windows mouse input for high click rates.
- Scans a bounding box for a keyword using OCR (Tesseract) on a timer.
- When the keyword is found, clicks the center of that box once, then waits
  3 seconds before resuming normal clicking.
- Simple GUI with Start/Stop buttons and a live speed slider.
- Global hotkey to toggle clicking on and off, even when the window is not
  focused.

## Requirements

- Windows (the fast-click path uses the Windows user32 API).
- Python 3.9 or newer.
- Tesseract OCR (installed separately, see below).
- Python packages: pyautogui, pytesseract, Pillow, keyboard.

Note: tkinter ships with Python but is sometimes left out of the default
install. If you get an error importing tkinter, re-run the Python installer,
choose Modify, and make sure "tcl/tk and IDLE" is checked.

## Installation

### 1. Install Python

Download Python from python.org and install it. During installation, check the
box that says "Add Python to PATH".

### 2. Install Tesseract OCR

Tesseract is the OCR engine that reads the pop-up text. On Windows, the
recommended build is the UB-Mannheim installer, since the upstream project does
not ship Windows binaries:

  https://github.com/UB-Mannheim/tesseract/wiki

Install it, then note the install path. The default is usually:

  C:\Program Files\Tesseract-OCR\tesseract.exe

If you install it somewhere else, update TESSERACT_PATH at the top of
autoclicker.py to match.

### 3. Install the Python packages

Open Command Prompt and run:

  pip install pyautogui pytesseract Pillow keyboard

## Configuration

All settings live in the Configuration block near the top of autoclicker.py.

- TESSERACT_PATH: full path to tesseract.exe (see above).
- HOTKEY: the key that toggles clicking on and off. Examples: "f13",
  "subtract" (numpad minus), "`" (the accent/backtick key).
- HOTKEY_HELP_TEXT: optional label shown in the GUI next to the hotkey. Set it
  to an empty string to hide the label.
- CLICK_X, CLICK_Y: the screen coordinates the clicker hits during normal
  operation.
- SKIP_BOX_X1, SKIP_BOX_Y1: top-left corner of the region to scan for the
  keyword.
- SKIP_BOX_X2, SKIP_BOX_Y2: bottom-right corner of that region.
- SKIP_CHECK_INTERVAL: how often, in seconds, to scan for the keyword.
- SKIP_KEYWORD: the word to look for (default "Skip").

These coordinates are specific to one display setup. You will need to set your
own. See the next section.

### Finding your coordinates

A helper script, coord_finder.py, prints your mouse position every 2 seconds:

  python coord_finder.py

Hover your mouse over the spot you want and read the printed X and Y values.

- For CLICK_X / CLICK_Y, hover over your normal click target.
- For the bounding box, hover over the top-left corner of where the pop-up
  keyword appears for the first pair, then the bottom-right corner for the
  second pair.

Notes for multi-monitor and high-DPI setups:

- Screen coordinates span all monitors. If a monitor sits to the left of your
  primary one, its coordinates can be negative.
- If Windows display scaling is set above 100 percent, reported coordinates may
  not match true pixel coordinates. Grab the values with coord_finder.py while
  the game is in its normal playing position and use them as-is.
- Borderless windowed mode tends to give the most consistent coordinates.

## Running

From the folder that contains the script:

  python autoclicker.py

The GUI opens. Use the slider to set click speed, then press Start (or your
hotkey) to begin. Press Stop or the hotkey again to halt.

## Running from anywhere with a batch file

Navigating to the script folder every time is tedious. A small batch file fixes
this. Create a file named autoclicker.bat somewhere convenient (for example,
your Desktop) with these contents, adjusting the path to where your script
lives:

  @echo off
  cd /d "C:\path\to\autoclicker-clear-popups\scripts"
  python autoclicker.py

Double-click the .bat file to launch the program. You can also right-click it
and pin it to the Start menu, or pin a shortcut to it on the taskbar.

## Optional: build a standalone .exe

If you want an app you can pin to the taskbar with no Command Prompt window,
package it with PyInstaller:

  pip install pyinstaller
  pyinstaller --onefile --windowed autoclicker.py

The result is a single autoclicker.exe inside a new "dist" folder. The
--windowed flag hides the console window.

One caveat: with --windowed there is no console, so the status messages the
script prints (such as the skip-click notice) will not be visible. That is fine
for normal use; it only matters if you are debugging.

## How it works

Two background threads run while clicking is active. One thread clicks the fixed
point on a loop at your chosen interval. The other wakes up every
SKIP_CHECK_INTERVAL seconds, screenshots the bounding box, and runs OCR on it.
If the keyword is present, it sets a flag. The click thread sees the flag on its
next pass, clicks the center of the box once, clears the flag, and pauses for
3 seconds before resuming.

## Disclaimer

This tool automates input for a single-player idle game. Use it in accordance
with the terms of service of any software you run it against. It is provided
as-is, without warranty.