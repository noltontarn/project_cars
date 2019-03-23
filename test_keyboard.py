from pynput import keyboard
import time

def on_press(key):
    if key == keyboard.Key.f10:
        return False

with keyboard.Listener(on_press=on_press) as listener:
    while(True):
        print('still running...')
        time.sleep(1)
        if not listener.running:
            break