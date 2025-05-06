import time
import tkinter as tk
from tkinter import filedialog
import pyautogui
import threading
from pynput import keyboard
from pynput.keyboard import Controller as KeyboardController, Key as PynputKey
from pynput.mouse import Controller as MouseController
import screeninfo
import mousekey

keyboard_controller = KeyboardController()
mouse_controller = MouseController()
mk = mousekey.MouseKey()
mk.enable_failsafekill()

def parse_key(k):
    special_keys = {
        'Key.enter': PynputKey.enter,
        'Key.esc': PynputKey.esc,
        'Key.tab': PynputKey.tab,
        'Key.space': PynputKey.space,
        'Key.shift': PynputKey.shift,
        'Key.ctrl': PynputKey.ctrl,
        'Key.alt': PynputKey.alt,
        'Key.backspace': PynputKey.backspace,
        'Key.delete': PynputKey.delete,
        'Key.up': PynputKey.up,
        'Key.down': PynputKey.down,
        'Key.left': PynputKey.left,
        'Key.right': PynputKey.right,
        'Key.f1': PynputKey.f1,
        'Key.f2': PynputKey.f2,
        'Key.f3': PynputKey.f3,
        'Key.f4': PynputKey.f4,
        'Key.f5': PynputKey.f5,
        'Key.f6': PynputKey.f6,
        'Key.f7': PynputKey.f7,
        'Key.f8': PynputKey.f8,
        'Key.f9': PynputKey.f9,
        'Key.f10': PynputKey.f10,
        'Key.f11': PynputKey.f11,
        'Key.f12': PynputKey.f12,
    }

    if k == 'Key.f1':
        return None

    return special_keys.get(k, k.strip("'\""))

def run_macro(path):
    with open(path, "r") as f:
        lines = f.readlines()

    instructions = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('?'):
            continue
        if '?' in line:
            line = line.split('?')[0].strip()
        if line.startswith("SCW") or line.startswith("SCH"):
            continue
        instructions.append(line)

    monitors = screeninfo.get_monitors()
    primary_monitor = next((m for m in monitors if getattr(m, "is_primary", True)), monitors[0])
    screen_width = primary_monitor.width
    screen_height = primary_monitor.height

    for instr in instructions:
        parts = instr.split()
        if not parts:
            continue
        cmd, *args = parts

        match cmd:
            case "HOLLUP":
                delay = int(args[0]) / 1000.0
                time.sleep(delay)

            case "MOV":
                x = round(float(args[0]) * screen_width)
                y = round(float(args[1]) * screen_height)
                mk.move_to(x, y)

            case "MOVP":
                x = round(float(args[0]) * screen_width)
                y = round(float(args[1]) * screen_height)
                mk.move_to(x, y)

            case "LCL":
                x = round(float(args[0]) * screen_width)
                y = round(float(args[1]) * screen_height)
                mk.move_to(x, y)
                mk.left_click()

            case "LCLP":
                x = round(float(args[0]) * screen_width)
                y = round(float(args[1]) * screen_height)
                mk.move_to(x, y)
                mk.left_click()

            case "RCL":
                x = round(float(args[0]) * screen_width)
                y = round(float(args[1]) * screen_height)
                mk.move_to(x, y)
                mk.right_click()

            case "RCLP":
                x = round(float(args[0]) * screen_width)
                y = round(float(args[1]) * screen_height)
                mk.move_to(x, y)
                mk.right_click()

            case "LCD":
                x = round(float(args[0]) * screen_width)
                y = round(float(args[1]) * screen_height)
                pyautogui.mouseDown(button='left')
                mk.move_to(x, y)
                pyautogui.mouseUp(button='left')

            case "LCDP":
                x = round(float(args[0]) * screen_width)
                y = round(float(args[1]) * screen_height)
                pyautogui.mouseDown(button='left')
                mk.move_to(x, y)
                pyautogui.mouseUp(button='left')

            case "RCD":
                x = round(float(args[0]) * screen_width)
                y = round(float(args[1]) * screen_height)
                pyautogui.mouseDown(button='right')
                mk.move_to(x, y)
                pyautogui.mouseUp(button='right')

            case "RCDP":
                x = round(float(args[0]) * screen_width)
                y = round(float(args[1]) * screen_height)
                pyautogui.mouseDown(button='right')
                mk.move_to(x, y)
                pyautogui.mouseUp(button='right')


            case "MWU":
                mouse_controller.scroll(100)

            case "MWD":
                mouse_controller.scroll(-100)

            case "SKI":
                key = parse_key(args[0].strip("'\""))
                if key:
                    keyboard_controller.press(key)
                    keyboard_controller.release(key)

            case "HOLD":
                key = parse_key(args[0].strip("'\""))
                if key:
                    keyboard_controller.press(key)

            case "RELEASE":
                key = parse_key(args[0].strip("'\""))
                if key:
                    keyboard_controller.release(key)

            case "DBL":
                x = round(float(args[0]) * screen_width)
                y = round(float(args[1]) * screen_height)
                pyautogui.doubleClick(x, y)

            case _:
                print(f"Unknown command: {cmd}")
    print("Finished")

def choose_and_run():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Macro Script", "*.mms")])
    if file_path:
        print(f"Running macro from: {file_path}")
        run_macro(file_path)

if __name__ == "__main__":
    print("Press F3 to start playback...")

    def on_press(key):
        if key == keyboard.Key.f3:
            threading.Thread(target=choose_and_run, daemon=True).start()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
