# GameVox 🎮🗣️

![Version](https://img.shields.io/github/v/release/Djkawada/GameVox?include_prereleases&style=flat-square)
![License](https://img.shields.io/github/license/Djkawada/GameVox?style=flat-square)
![Downloads](https://img.shields.io/github/downloads/Djkawada/GameVox/total?style=flat-square)


**GameVox** est un lecteur d'écran intelligent pour Linux (**Hyprland/Wayland**) conçu pour les jeux vidéo.
Il capture le texte à l'écran (dialogues, sous-titres), le nettoie et le lit instantanément avec une voix naturelle.

## ✨ Fonctionnalités

*   **Voix Naturelle Locale** : Utilise l'IA **Piper** pour une synthèse vocale neuronale fluide sans aucun délai et sans connexion internet.
*   **Sélection de Zone (Slurp)** : Définissez précisément la zone de l'écran à lire (ex: la boîte de dialogue) pour éviter les lectures inutiles.
*   **Système de Profils** : Sauvegardez et chargez des zones spécifiques pour chaque jeu.
*   **Nettoyage Intelligent** : Filtre les caractères spéciaux de l'OCR tout en conservant les lettres et les chiffres.
*   **Contrôle à la Manette** : Activez/Désactivez la lecture à tout moment via un bouton de votre manette (configurable dynamiquement).

## 🚀 Installation

### Via AUR (Recommandé pour Arch Linux / Omarchy)
C'est la méthode la plus simple, tout est configuré automatiquement.
```bash
yay -S gamevox-git
```

### Installation Manuelle (Développement)
Si vous souhaitez installer depuis les sources :

1.  **Cloner le dépôt** :
    ```bash
    git clone https://github.com/Djkawada/GameVox.git
    cd GameVox
    ```

2.  **Installer les dépendances système** :
    ```bash
    sudo pacman -S tesseract tesseract-data-fra grim slurp paplay python libevdev
    ```

3.  **Configurer l'environnement Python** :
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4.  **Installer Piper (TTS)** :
    Le moteur vocal n'est pas inclus (trop lourd). Un script dans le PKGBUILD le fait, mais manuellement vous devez :
    ```bash
    mkdir -p piper_tts && cd piper_tts
    wget https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz
    tar -xvf piper_linux_x86_64.tar.gz
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json
    cd ..
    ```

## 🛠️ Utilisation

Si installé via AUR, lancez simplement :
```bash
gamevox
```
*(Vous pouvez aussi trouver "GameVox" dans votre lanceur d'applications)*

### Menu de démarrage interactif :
*   **Mode Auto** : Scanne la moitié inférieure de l'écran actif.
*   **Sélectionner un Profil** : Charge une zone déjà enregistrée.
*   **Créer un nouveau profil** : Demande un nom, puis vous permet de dessiner un rectangle à l'écran avec la souris.
*   **Configurer la manette** : Détecte automatiquement votre manette et le bouton de pause souhaité.

## 🎮 Contrôles
*   **Bouton Manette** : Play / Pause (vocalise l'état).
*   **Ctrl + C** : Quitter proprement.
