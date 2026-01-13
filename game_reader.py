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
import re
import os
import shutil

# --- CONFIGURATION ---
CHECK_INTERVAL = 1.5
MIN_TEXT_LENGTH = 3
LANG = 'fra'
SIMILARITY_THRESHOLD = 0.5
CONTROLLER_PATH = '/dev/input/event17' # Votre Zikway HID gamepad
TOGGLE_BUTTON_CODE = 314               # Le bouton que vous avez choisi

# Chemins absolus pour Piper (nécessaire car lancé depuis venv parfois)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIPER_BIN = os.path.join(BASE_DIR, "piper_tts/piper/piper")
PIPER_MODEL = os.path.join(BASE_DIR, "piper_tts/fr_FR-upmc-medium.onnx")
PROFILES_FILE = os.path.join(BASE_DIR, "profiles.json")
# ---------------------

PAUSED = False
CURRENT_REGION = None # Si None, utilise le mode automatique (bas de l'écran actif)

def load_profiles():
    if not os.path.exists(PROFILES_FILE):
        return {}
    try:
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_profile(name, region):
    profiles = load_profiles()
    profiles[name] = region
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles, f, indent=4)

def delete_profile(name):
    profiles = load_profiles()
    if name in profiles:
        del profiles[name]
        with open(PROFILES_FILE, 'w') as f:
            json.dump(profiles, f, indent=4)
        return True
    return False

def select_zone_with_slurp():
    print("Sélectionnez une zone à l'écran avec votre souris...", flush=True)
    try:
        # slurp permet de sélectionner une zone et retourne "x,y wxh"
        # On ajoute -d pour ne pas lancer la commande si on annule
        res = subprocess.run(['slurp', '-d'], capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout.strip()
    except FileNotFoundError:
        print("Erreur: 'slurp' n'est pas installé. Installez-le avec 'sudo pacman -S slurp'", flush=True)
    except Exception as e:
        print(f"Erreur lors de la sélection : {e}", flush=True)
    return None

def choose_profile_menu():
    global CURRENT_REGION
    
    while True:
        # On recharge les profils à chaque tour de boucle pour voir les nouveaux
        profiles = load_profiles()
        
        print("\n=== MENU DE DÉMARRAGE ===")
        print("1. Mode Auto (Bas de l'écran actif)")
        
        idx = 2
        profile_names = list(profiles.keys())
        for name in profile_names:
            print(f"{idx}. Profil : {name}")
            idx += 1
            
        create_idx = idx
        print(f"{create_idx}. Créer un nouveau profil")
        
        delete_idx = idx + 1
        print(f"{delete_idx}. Supprimer un profil")
        
        print("0. Quitter")
        
        try:
            choice = input("\nVotre choix : ").strip()
        except EOFError:
            choice = "0"

        if choice == "0":
            sys.exit(0)
        elif choice == "1":
            CURRENT_REGION = None
            print(">>> Mode Auto activé.")
            break
        elif choice == str(create_idx):
            name = input("Nom du nouveau profil : ").strip()
            if name:
                region = select_zone_with_slurp()
                if region:
                    save_profile(name, region)
                    print(f"Profil '{name}' sauvegardé !")
                else:
                    print("Sélection annulée.")
        elif choice == str(delete_idx):
            print("\n--- SUPPRESSION ---")
            d_idx = 1
            d_names = list(profiles.keys())
            if not d_names:
                print("Aucun profil à supprimer.")
                continue
                
            for name in d_names:
                print(f"{d_idx}. {name}")
                d_idx += 1
            print("0. Annuler")
            
            try:
                d_choice = input("Profil à supprimer (numéro) : ").strip()
                if d_choice != "0":
                    sel = int(d_choice) - 1
                    if 0 <= sel < len(d_names):
                        name_to_del = d_names[sel]
                        if delete_profile(name_to_del):
                            print(f"Profil '{name_to_del}' supprimé.")
                    else:
                        print("Choix invalide.")
            except ValueError:
                print("Choix invalide.")
        else:
            try:
                sel_idx = int(choice) - 2
                if 0 <= sel_idx < len(profile_names):
                    name = profile_names[sel_idx]
                    CURRENT_REGION = profiles[name]
                    print(f">>> Profil '{name}' chargé ({CURRENT_REGION}).")
                    break
            except ValueError:
                pass

def toggle_pause():
    global PAUSED
    PAUSED = not PAUSED
    if PAUSED:
        print(">>> PAUSE ACTIVÉE", flush=True)
        speak_system("Pause")
    else:
        print(">>> LECTURE ACTIVÉE", flush=True)
        speak_system("Lecture activée")

def speak_system(text):
    """Message système prioritaire (court)."""
    # On utilise Piper aussi pour les messages système pour la cohérence
    speak(text)

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

def capture_zone():
    region = None
    
    if CURRENT_REGION:
        # Mode Profil Fixe
        region = CURRENT_REGION
    else:
        # Mode Auto (Bas de l'écran)
        geo = get_active_monitor_geometry()
        if geo:
            x = geo['x']
            y = geo['y'] + (geo['height'] // 2)
            w = geo['width']
            h = geo['height'] // 2
            region = f"{int(x)},{int(y)} {int(w)}x{int(h)}"
    
    if region:
        try:
            cmd = ['grim', '-g', region, '-t', 'png', '-']
            # On supprime les erreurs stderr pour éviter le spam si grim échoue (ex: écran verrouillé)
            res = subprocess.run(cmd, capture_output=True)
            if res.returncode == 0:
                return Image.open(io.BytesIO(res.stdout))
        except:
            pass
    return None

def clean_text(text):
    # Remplace les retours à la ligne par des espaces
    text = text.replace('\n', ' ')
    # Garde lettres, accents, ponctuation de base ET chiffres
    text = re.sub(r'[^a-zA-Z0-9àâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ\s.,!?:;\'"-]', ' ', text)
    # Réduit les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def speak(text):
    def _speak_thread(t):
        try:
            print(f"PARLE: {t}", flush=True)
            
            # Méthode fichier temporaire (100% fiable)
            # Les pipes causent trop de problèmes aléatoires avec mpv/aplay/paplay
            # Piper est tellement rapide que l'écriture disque est négligeable
            
            filename = f"/tmp/gamereader_{int(time.time())}_{threading.get_ident()}.wav"
            
            # 1. Générer le fichier WAV avec Piper
            with open(filename, 'wb') as f:
                p_piper = subprocess.Popen(
                    [PIPER_BIN, '--model', PIPER_MODEL, '--output_file', '-'],
                    stdin=subprocess.PIPE,
                    stdout=f,
                    stderr=subprocess.DEVNULL
                )
                p_piper.communicate(input=t.encode('utf-8'))
            
            # 2. Jouer le fichier avec mpv (ou paplay)
            if os.path.getsize(filename) > 0:
                subprocess.run(['paplay', filename], stderr=subprocess.DEVNULL)
            
            # 3. Nettoyer
            if os.path.exists(filename):
                os.remove(filename)
            
        except Exception as e:
            print(f"Erreur TTS (Piper): {e}", flush=True)

    threading.Thread(target=_speak_thread, args=(text,), daemon=True).start()

def main():
    print("=== GAMEREADER AVEC MANETTE ===", flush=True)
    
    choose_profile_menu()
    
    # Lancement de l'écoute manette dans un thread séparé
    thread = threading.Thread(target=controller_listener, daemon=True)
    thread.start()
    
    last_text = ""
    
    try:
        while True:
            if PAUSED:
                time.sleep(0.5)
                continue

            # Capture selon le mode choisi (Zone fixe ou Auto)
            img = capture_zone()
            
            if img:
                text = pytesseract.image_to_string(img.convert('L'), lang=LANG)
                cleaned = clean_text(text)
                
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
