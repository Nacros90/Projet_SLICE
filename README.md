# Projet_SLICE

## Description
Ce projet est réalisé dans le cadre de la 2ème année de Licence de Physique (projet SLICE).
Il porte sur l'étude, la simulation et la conception d'un banc expérimental avec maintien d'une vitesse tangentielle constante (V0). 
Ce dépôt regroupe la simulation cinématique, le code de contrôle matériel, ainsi que les modèles 3D des pièces du dispositif.

## Prérequis
Liste des outils, langages et bibliothèques nécessaires :
- Python 3.x avec la bibliothèque `pygame`
- Arduino IDE (pour compiler et téléverser le code matériel)
- Un Slicer (ex: Ultimaker Cura, PrusaSlicer) pour exploiter les modèles 3D

## Installation
Pour exécuter ce projet localement :

    git clone <url-du-depot>
    cd Projet_SLICE

## Utilisation
### 1. Simulation (Python)
Pour lancer la simulation interactive du banc expérimental :
    python Code/Slice.py

### 2. Contrôle Matériel (Arduino)
Ouvrez les fichiers `.ino` avec l'Arduino IDE, sélectionnez le port COM correspondant à votre carte, puis téléversez le programme.

### 3. Conception et Impression 3D
Les pièces mécaniques du banc sont fournies au format `.stl`. Elles peuvent être directement importées dans votre logiciel de tranchage (Slicer) pour être imprimées en 3D.