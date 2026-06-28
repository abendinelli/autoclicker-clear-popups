import pyautogui
import time

print("Move your mouse to the target position. Coordinates will print every 2 seconds.")
print("Press Ctrl+C to stop.")

while True:
    x, y = pyautogui.position()
    print(f"X: {x}, Y: {y}")
    time.sleep(2)
