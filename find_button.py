import evdev
import sys

def list_devices():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    if not devices:
        print("Aucun périphérique détecté (peut nécessiter sudo).")
        return []
    
    print("Périphériques disponibles :")
    for i, dev in enumerate(devices):
        print(f"{i}: {dev.name} ({dev.path})")
    return devices

def main():
    print("=== Détection de Bouton Manette ===")
    devices = list_devices()
    
    if not devices:
        return

    try:
        idx = int(input("Entrez le numéro de votre manette : "))
        device = devices[idx]
        print(f"Vous avez choisi : {device.name}")
        print("Appuyez MAINTENANT sur le bouton que vous voulez utiliser pour PAUSE/LECTURE...")
        
        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                # On s'intéresse aux événements "KEY" (boutons)
                # event.value 1 = pressé, 0 = relâché
                if event.value == 1:
                    print(f"BOUTON DÉTECTÉ !")
                    print(f"Code : {event.code}")
                    print(f"Nom  : {evdev.ecodes.KEY[event.code]}")
                    print("-" * 30)
                    print(f"Notez le code '{event.code}' ou le nom '{evdev.ecodes.KEY[event.code]}'")
                    print("Appuyez sur Ctrl+C pour quitter.")
                    
    except ValueError:
        print("Numéro invalide.")
    except IndexError:
        print("Périphérique introuvable.")
    except KeyboardInterrupt:
        print("\nFin.")
    except PermissionError:
        print("\nERREUR : Permission refusée. Lancez ce script avec 'sudo'.")

if __name__ == "__main__":
    main()
