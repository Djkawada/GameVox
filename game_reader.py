import time
import subprocess
import json
import sys
from PIL import Image
import pytesseract
import io
import difflib
import signal
import threading
import evdev

# --- CONFIGURATION ---
CHECK_INTERVAL = 1.5
MIN_TEXT_LENGTH = 3
LANG = 'fra'
SIMILARITY_THRESHOLD = 0.5
CONTROLLER_PATH = '/dev/input/event17' # Votre Zikway HID gamepad
TOGGLE_BUTTON_CODE = 314               # Le bouton que vous avez choisi
# ---------------------

PAUSED = False

def toggle_pause():
    global PAUSED
    PAUSED = not PAUSED
    if PAUSED:
        print(">>> PAUSE ACTIVÉE", flush=True)
        subprocess.Popen(['espeak-ng', '-v', 'fr', 'Pause'])
    else:
        print(">>> LECTURE ACTIVÉE", flush=True)
        subprocess.Popen(['espeak-ng', '-v', 'fr', 'Lecture activée'])

def controller_listener():
    """Écoute la manette en arrière-plan."""
    try:
        device = evdev.InputDevice(CONTROLLER_PATH)
        print(f"Écoute de la manette : {device.name}", flush=True)
        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                if event.code == TOGGLE_BUTTON_CODE and event.value == 1: # 1 = pressé
                    toggle_pause()
    except Exception as e:
        print(f"Erreur manette : {e}", flush=True)

def get_active_monitor_geometry():
    try:
        result = subprocess.run(['hyprctl', 'monitors', '-j'], capture_output=True, text=True)
        monitors = json.loads(result.stdout)
        for m in monitors:
            if m['focused']:
                return m
        return monitors[0] if monitors else None
    except Exception as e:
        return None

def capture_bottom_half(geo):
    x = geo['x']
    y = geo['y'] + (geo['height'] // 2)
    w = geo['width']
    h = geo['height'] // 2
    region = f"{int(x)},{int(y)} {int(w)}x{int(h)}"
    try:
        cmd = ['grim', '-g', region, '-t', 'png', '-']
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode == 0:
            return Image.open(io.BytesIO(res.stdout))
    except:
        pass
    return None

def speak(text):
    try:
        print(f"PARLE: {text}", flush=True)
        subprocess.run(['espeak-ng', '-v', 'fr', '-s', '160', text])
    except:
        pass

def main():
    print("=== GAMEREADER AVEC MANETTE ===", flush=True)
    
    # Lancement de l'écoute manette dans un thread séparé
    thread = threading.Thread(target=controller_listener, daemon=True)
    thread.start()
    
    last_text = ""
    
    try:
        while True:
            if PAUSED:
                time.sleep(0.5)
                continue

            geo = get_active_monitor_geometry()
            if not geo:
                time.sleep(1)
                continue
                
            img = capture_bottom_half(geo)
            if img:
                text = pytesseract.image_to_string(img.convert('L'), lang=LANG)
                cleaned = " ".join(text.split())
                
                if len(cleaned) >= MIN_TEXT_LENGTH:
                    sim = difflib.SequenceMatcher(None, last_text, cleaned).ratio()
                    if sim < SIMILARITY_THRESHOLD:
                        speak(cleaned)
                        last_text = cleaned
            
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("Arrêt.")

if __name__ == "__main__":
    main()
