# GameReader 🎮🗣️

Un lecteur d'écran automatique pour Linux (Hyprland/Wayland) conçu pour les jeux vidéo.
Il capture automatiquement la moitié inférieure de l'écran, détecte le texte (dialogues, sous-titres) et le lit à voix haute.

**Nouvelle fonctionnalité :** Supporte l'activation/désactivation via une manette de jeu !

## Prérequis

Ce logiciel est conçu pour fonctionner sous **Linux** avec l'environnement graphique **Hyprland** (Wayland).

Il nécessite les paquets systèmes suivants :
*   `python`
*   `tesseract` (et les données de langue, ex: `tesseract-data-fra`)
*   `grim` (capture d'écran Wayland)
*   `espeak-ng` (synthèse vocale)
*   `libevdev` (pour la manette)

Sous Arch Linux / Omarchy :
```bash
sudo pacman -S tesseract tesseract-data-fra espeak-ng grim python libevdev
```

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/Djkawada/GameReader.git
   cd GameReader
   ```

2. Créez un environnement virtuel et installez les dépendances :
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Configuration de la manette

Pour utiliser le bouton de votre manette pour mettre en pause/lecture :

1. Lancez l'outil de détection (avec sudo pour accéder aux périphériques) :
   ```bash
   sudo ./venv/bin/python find_button.py
   ```
2. Suivez les instructions, appuyez sur votre bouton et notez le **Code** affiché (ex: 304, 314).
3. Ouvrez `game_reader.py` et modifiez les lignes :
   ```python
   CONTROLLER_PATH = '/dev/input/eventXX' # Chemin de votre manette
   TOGGLE_BUTTON_CODE = 314               # Votre code
   ```

## Utilisation

Lancez le logiciel (avec sudo si vous utilisez la manette) :

```bash
sudo ./venv/bin/python game_reader.py
```

*   **Lecture automatique** : Le logiciel lit tout texte apparaissant dans la moitié inférieure.
*   **Bouton Manette** : Appuyez pour mettre en pause ou réactiver la lecture.
*   `Ctrl+C` dans le terminal pour quitter.

## Personnalisation

Vous pouvez modifier les variables dans `game_reader.py` :
*   `CHECK_INTERVAL` : La fréquence de lecture.
*   `LANG` : La langue à détecter (par défaut 'fra').