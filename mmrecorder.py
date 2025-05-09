import time
import tkinter as tk
from tkinter import filedialog, messagebox
from pynput import mouse, keyboard
import threading
import pyautogui

recording = False
recording_started = False
events = []
last_time = None
dragging = {'left': False, 'right': False}
drag_start_pos = {'left': None, 'right': None}
held_keys = set()
sampling_thread = None

screen_width, screen_height = pyautogui.size()

VER = "1.0.0"

def add_event(instruction, data=None, comment=None):
    global last_time
    current_time = time.time()
    if last_time:
        delay = int((current_time - last_time) * 1000)
        events.append(f"HOLLUP {delay}")
    last_time = current_time

    line = instruction
    if data:
        line += " " + " ".join(map(str, data))
    if comment:
        line += f" ? {comment}"
    events.append(line)

def normalize_coords(x, y):
    return round(x / screen_width, 6), round(y / screen_height, 6)

def on_move(x, y):
    if recording and recording_started and not dragging['left'] and not dragging['right']:
        x_p, y_p = normalize_coords(x, y)
        add_event("MOVP", [x_p, y_p])

def on_click(x, y, button, pressed):
    global recording_started
    btn = str(button)

    if not recording or not recording_started:
        return

    x_p, y_p = normalize_coords(x, y)

    if pressed:
        if 'left' in btn:
            dragging['left'] = True
            drag_start_pos['left'] = (x_p, y_p)
        elif 'right' in btn:
            dragging['right'] = True
            drag_start_pos['right'] = (x_p, y_p)
    else:
        if 'left' in btn:
            dragging['left'] = False
            drag_start_pos['left'] = None
            add_event("LCLP", [x_p, y_p])
        elif 'right' in btn:
            dragging['right'] = False
            drag_start_pos['right'] = None
            add_event("RCLP", [x_p, y_p])


def on_scroll(x, y, dx, dy):
    if not recording or not recording_started:
        return
    if dy > 0:
        add_event("MWU")
    else:
        add_event("MWD")

def on_press(key):
    global recording, events, last_time, recording_started, sampling_thread

    if key == keyboard.Key.f1:
        if not recording:
            recording = True
            recording_started = True
            print("Recording started.")
            last_time = time.time()
            sampling_thread = threading.Thread(target=sample_mouse_drag, daemon=True)
            sampling_thread.start()
        else:
            print("Recording stopped.")
            recording = False
            recording_started = False
            ask_to_save()
        return

    if not recording or not recording_started:
        return

    try:
        k = key.char
    except AttributeError:
        k = str(key)

    if k not in held_keys:
        held_keys.add(k)
        add_event("HOLD", [k])

def on_release(key):
    if not recording or not recording_started:
        return

    try:
        k = key.char
    except AttributeError:
        k = str(key)

    if k in held_keys:
        held_keys.remove(k)
        add_event("RELEASE", [k])
    else:
        add_event("SKI", [k])

def sample_mouse_drag():
    while recording and recording_started:
        if dragging['left']:
            x, y = pyautogui.position()
            x_p, y_p = normalize_coords(x, y)
            start = drag_start_pos['left']
            if start:
                dx = round(x_p - start[0], 6)
                dy = round(y_p - start[1], 6)
                add_event("LCDR", [dx, dy])
        elif dragging['right']:
            x, y = pyautogui.position()
            x_p, y_p = normalize_coords(x, y)
            start = drag_start_pos['right']
            if start:
                dx = round(x_p - start[0], 6)
                dy = round(y_p - start[1], 6)
                add_event("RCDR", [dx, dy])
        time.sleep(0.01)


def ask_to_save():
    root = tk.Tk()
    root.withdraw()
    if messagebox.askyesno("Save Recording", "Do you want to save the steps?"):
        file_path = filedialog.asksaveasfilename(defaultextension=".mms", filetypes=[("MiniMacro Script", "*.mms")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(f"SCW {screen_width}\n")
                f.write(f"SCH {screen_height}\n")
                f.write(f"? This script was recorded in MiniMacro v{VER}\n")
                for event in events:
                    f.write(event + "\n")
            print(f"Saved to {file_path}")
    else:
        print("Recording discarded.")
    events.clear()

def start_listeners():
    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    mouse_listener.start()
    keyboard_listener.start()
    mouse_listener.join()
    keyboard_listener.join()

if __name__ == "__main__":
    print("Press F1 to start/stop recording.")
    start_listeners()
