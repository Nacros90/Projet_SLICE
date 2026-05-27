# Projet SLICE
**Sliding Contact Investigation for Carbon Pantograph Wear Evaluation**

## Description
Ce projet est développé dans le cadre de la 2ème année de Licence de Physique / Sciences de l'Ingénieur. 
Il porte sur l'étude, la simulation et la conception d'un banc expérimental modélisant le contact glissant entre une caténaire et le pantographe d'un train. L'objectif principal est le maintien d'une **vitesse tangentielle constante ($V_t$)** lors du balayage d'un pion sur un disque en rotation, posant un défi cinématique d'asservissement non linéaire ($\omega = \frac{V_t}{r}$).

Ce dépôt regroupe l'intégralité du travail d'ingénierie : la modélisation mathématique initiale, la simulation interactive, le code de contrôle embarqué du banc d'essai et la conception assistée par ordinateur (CAO) des pièces mécaniques.

## Architecture du dépôt

* **Code/** : Contient les simulations cinématiques en Python (modélisation mathématique avec `pygame`) et les programmes C++ Arduino.
* **Documentation/** : Manuels techniques, documentations des composants électroniques (Shield CNC, drivers) et rapports académiques.
* **CAO/** : Fichiers `.stl` (ex: `support_disque.stl`) prêts pour l'impression 3D.

## Matériel et Prérequis

### Composants de la maquette physique
Le banc d'essai s'appuie sur une architecture matérielle spécifique pour s'affranchir des limites de calcul à haute fréquence :
* **Microcontrôleur :** Arduino UNO R4 Minima (Processeur ARM Cortex-M4 32-bits, 48 MHz)
* **Contrôle Moteur :** Shield CNC V3 avec Drivers A4988
* **Actionneurs :** Moteurs pas-à-pas (Axe X pour le disque rotatif, Axe Y pour le balayage linéaire)
* **Configuration mécanique :** Les drivers A4988 doivent être configurés en **Microstepping 1/8** (pontage matériel sur les broches M0 et M1) pour assurer la fluidité du mouvement.

### Outils logiciels
* [Python 3.x](https://www.python.org/) avec la bibliothèque `pygame` (pour la simulation logicielle)
* [Arduino IDE 2.x](https://www.arduino.cc/en/software) (pour la compilation et le téléversement du code embarqué)
* Un logiciel de tranchage (UltiMaker Cura, PrusaSlicer...) pour exploiter les modèles 3D

## Installation et Utilisation

### Étape 1 : Cloner le dépôt
```bash
git clone [https://github.com/nacros90/projet_slice.git](https://github.com/nacros90/projet_slice.git)
cd projet_slice
```

### Étape 2 : Lancer la Simulation (Python)
La simulation permet de visualiser la courbe de vitesse requise par rapport à la position du pion sans nécessiter le déploiement du matériel physique.
```bash
# Installation de la dépendance
pip install pygame

# Lancement du script principal
python Code/Python/slice.py
```

### Étape 3 : Déployer le Contrôle Matériel (Arduino)
Le programme embarqué opère en boucle ouverte et recalcule la vitesse du disque via un échantillonnage spatial régulier.

#### 3.1 Préparation matérielle
1. Ouvrez le fichier `Code/Arduino/Code_maquette_UNO_R4_MINIMA/Code_maquette_UNO_R4_MINIMA.ino` dans l'Arduino IDE.
2. Assurez-vous d'avoir installé le gestionnaire de carte **Arduino UNO R4 Boards**.
3. **Important :** Effectuez le "Zéro Mécanique" en plaçant manuellement le pion sur le bord extérieur du disque ($R_{max} = 7.5$ cm) avant toute mise sous tension.

#### 3.2 Configuration Système et Ports de communication
Avant de téléverser, configurez l'accès aux ports série selon votre système d'exploitation.

**Sous Microsoft Windows :**
* Branchez la carte et ouvrez le **Gestionnaire de périphériques** (`Win + X`).
* Déroulez l'onglet **Ports (COM et LPT)** pour identifier le port attribué (ex: `COM6`).
* *Note :* L'UNO R4 est reconnue nativement. Si vous utilisez une ancienne Nano, le pilote **CH340** peut être requis.
* Dans l'IDE Arduino, sélectionnez ce port COM.

**Sous GNU/Linux (Gestion des droits POSIX) :**
Par défaut, Linux restreint l'accès aux ports série (`/dev/ttyACM0` ou `/dev/ttyUSB0`), ce qui provoquera une erreur `Permission denied` lors du téléversement ou de l'exécution du code Arduino.
* Pour octroyer les droits de manière permanente, ajoutez votre utilisateur au groupe propriétaire du périphérique série :
  * Sous Debian / Ubuntu / Mint : `sudo usermod -aG dialout $USER`
  * Sous Arch Linux / Fedora : `sudo usermod -aG uucp $USER`
* Appliquez la modification sans redémarrer la session en tapant : `newgrp dialout` (ou `newgrp uucp`).
* Dans l'IDE Arduino, sélectionnez le port `/dev/tty...` correspondant.

#### 3.3 Téléversement et Diagnostic
* Cliquez sur **Téléverser** dans l'IDE. Une fois terminé, alimentez le Shield en puissance (8V).

*Matrice de résolution des problèmes courants :*
| Symptôme observé | Cause probable | Action corrective |
| :--- | :--- | :--- |
| **`Permission denied` (Linux)** | Droits restreints sur le port série. | Exécuter la commande `usermod` et `newgrp` (voir 3.2). |
| **Port COM invisible (Windows)** | Absence du pilote USB-Série. | Télécharger et installer le pilote CH340. |
| **`not in sync: resp=0x00`** | Parasitage matériel ou port occupé. | Débrancher le Shield CNC de l'Arduino pour le téléversement ou fermer les logiciels de tranchage 3D. |
| **Décrochage en fin de course** | Limite physique atteinte (FCEM sous 8V). | Vérifier que l'écrêtage à 10 000 pas/s (`constrain`) est bien actif dans le code. |

## Équipe Projet
* Naël CROSNIER
* Théliau FOULER
* Paul MITTLER
* Nysteroye Christ ZEBAZE NGUENA

*Supervisé par l'Université Marie et Louis Pasteur – UFR STGI Belfort*