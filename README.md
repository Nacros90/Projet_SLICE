# Projet SLICE
**Sliding Contact Investigation for Carbon Pantograph Wear Evaluation**

## Description
Ce projet est développé dans le cadre de la 2ème année de Licence de Physique / Sciences de l'Ingénieur. 
Il porte sur l'étude, la simulation et la conception d'un banc expérimental modélisant le contact glissant entre une caténaire et le pantographe d'un train. L'objectif principal est le maintien d'une **vitesse tangentielle constante ($V_t$)** lors du balayage d'un pion sur un disque en rotation, posant un défi cinématique d'asservissement non linéaire ($\omega = \frac{V_t}{r}$).

Ce dépôt regroupe l'intégralité du travail d'ingénierie : la modélisation mathématique initiale, la simulation interactive, le code de contrôle embarqué du banc d'essai et la conception assistée par ordinateur (CAO) des pièces mécaniques.

## Architecture du dépôt

* **Code/** : Contient les simulations cinématiques en Python (modélisation mathématique avec `pygame`).
* **Code_maquette_UNO_R4_MINIMA/** : Contient le programme C++ définitif pour le microcontrôleur, gérant l'asservissement en temps réel avec la bibliothèque `AccelStepper`.
* **Documentation/** : Manuels techniques, documentations des composants électroniques (Shield CNC, drivers) et rapports académiques.
* **CAO/** : Fichiers `.stl` (ex: `Support Disque.stl`) prêts pour l'impression 3D.

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
python Code/Slice.py
```

### Étape 3 : Déployer le Contrôle Matériel (Arduino)
Le programme embarqué opère en boucle ouverte et recalcule la vitesse du disque via un échantillonnage spatial régulier.
1. Ouvrez le fichier `Code_maquette_UNO_R4_MINIMA/Code_maquette_UNO_R4_MINIMA.ino` dans l'Arduino IDE.
2. Assurez-vous d'avoir installé le gestionnaire de carte **Arduino UNO R4 Boards**.
3. Sélectionnez le port COM correspondant à votre Arduino UNO R4 Minima.
4. **Important :** Effectuez le "Zéro Mécanique" en plaçant manuellement le pion sur le bord extérieur du disque ($R_{max} = 7.5$ cm) avant toute mise sous tension.
5. Téléversez le code et alimentez le Shield en puissance.

## Équipe Projet
* Naël CROSNIER
* Théliau FOULER
* Paul MITTLER
* Nysteroye Christ ZEBAZE NGUENA

*Supervisé par l'Université Marie et Louis Pasteur – UFR STGI Belfort*