//Maquette de démonstration pour le projet SLICE
//Objectif : Contrôler un moteur linéaire (pion) et un moteur rotatif (disque) en synchronisation
//avec une vitesse tangentielle constante pour le pion.
//
//Matériel :
//- Arduino UNO R4 MINIMA
//- Shield CNC pour contrôler les moteurs pas à pas
//- Moteur linéaire (pion) avec driver compatible
//- Moteur rotatif (disque) avec driver compatible
//
//Fonctionnement :
//- Le moteur Y (pion) effectue un mouvement linéaire aller-retour entre deux positions définies.
//- Le moteur X (disque) ajuste sa vitesse de rotation en fonction de la position du pion pour maintenir une vitesse tangentielle constante.
//
//Note : Ce code est conçu pour être utilisé en mode Microstepping 1/8 de pas pour une meilleure précision et un contrôle plus fin des moteurs. Assurez-vous que les drivers de vos moteurs sont configurés pour le microstepping approprié (1/8 dans ce cas) pour correspondre aux constantes définies dans le code.

// 1. --- Initialisation et Variables globales ---
#include <AccelStepper.h>

// --- BROCHES DU SHIELD CNC ---
#define EN 8       // Broche d'activation du shield
#define STEP_Y 3   // Broche STEP du moteur Y (pion)
#define DIR_Y 6    // Broche DIR du moteur Y
#define STEP_X 2   // Broche STEP du moteur X (plateau/disque)
#define DIR_X 5    // Broche DIR du moteur X

// --- RÉSOLUTION MÉCANIQUE (MICROSTEPPING 1/8) ---
const int MICROSTEPPING = 8; // Microstepping du driver (1/8 de pas)

const float multiplicateur_mecanique = 2.83; 
const int stepsPerRevolutionX = (200 * MICROSTEPPING) * multiplicateur_mecanique; // Pas par tour du moteur X
const int stepsPerRevolutionY = 200 * MICROSTEPPING; // Pas par tour du moteur Y

// --- CONSTANTES PHYSIQUES ---
const float VITESSE_TANGENTIELLE_CIBLE = 25.0; // Vitesse tangentielle du pion en cm/s
const float vitesseY_RPM = 0.5;                // Vitesse de rotation du moteur Y en RPM
const int pasParCycle = 290 * MICROSTEPPING;   // Nombre de pas pour un cycle aller-retour du pion
const float RAYON_MAX = 7.5;                   // Rayon maximal du disque en cm
const float RAYON_MIN = 1.35;                  // Rayon minimal du disque en cm

// --- CONSTANTES DE RÉGLAGE LOGICIEL ---
const long SEUIL_PAS_Y = 16;             // Seuil de variation en pas pour recalculer la vitesse X
const float VITESSE_X_MIN = 10.0;         // Vitesse minimale autorisée pour le plateau X
const float VITESSE_X_MAX = 10000.0;      // Vitesse maximale autorisée pour le plateau X
const float SEUIL_DIFF_VITESSE_X = 2.0;   // Seuil de variation de vitesse pour appliquer un nouveau réglage

AccelStepper moteurY(AccelStepper::DRIVER, STEP_Y, DIR_Y);
AccelStepper moteurX(AccelStepper::DRIVER, STEP_X, DIR_X);

long positionDepart = 0;            // Position au début du cycle Y
long positionCible = pasParCycle;   // Position cible initiale pour le mouvement Y
long dernierPasY = 0;               // Position Y mémorisée pour limiter les recalculs
float vitesseX_actuelle = 0.0;      // Vitesse courante appliquée au moteur X

void setup() {
  Serial.begin(115200);

  // --- ACTIVATION DU SHIELD ---
  pinMode(EN, OUTPUT);      
  digitalWrite(EN, LOW);    

  // Initialisation Moteur Y (Pion)
  moteurY.setMaxSpeed(convertRPMToStepsPerSec(vitesseY_RPM, stepsPerRevolutionY));
  moteurY.setSpeed(convertRPMToStepsPerSec(vitesseY_RPM, stepsPerRevolutionY));

  // Initialisation Moteur X (Disque)
  moteurX.setMaxSpeed(VITESSE_X_MAX);
  moteurX.setSpeed(100); 
  
  Serial.println("Initialisation SLICE (Mode FULL STEP) OK.");
}

// 2. --- BOUCLE PRINCIPALE ---
void loop() {
  moteurY.runSpeed();
  moteurX.runSpeed();

  // --- GESTION DU MOTEUR Y (ALLER-RETOUR DU PION) ---
  // Quand le pion atteint la cible, on inverse sa direction
  if ((moteurY.currentPosition() >= positionCible && moteurY.speed() > 0) ||
      (moteurY.currentPosition() <= positionCible && moteurY.speed() < 0)) {
    
    moteurY.setSpeed(-moteurY.speed());
    positionDepart = moteurY.currentPosition();
    // Nouvelle cible dépendante du sens actuel du mouvement
    positionCible = positionDepart + (pasParCycle * (moteurY.speed() > 0 ? 1 : -1));
    
    Serial.print("Inversion Y. Cible : ");
    Serial.println(positionCible);
  }

  // --- ASSERVISSEMENT DU MOTEUR X (VITESSE DU DISQUE) ---
  long positionY = abs(moteurY.currentPosition());

  if (abs(positionY - dernierPasY) >= SEUIL_PAS_Y) {
    float rayon = mapPasToRayonSymetrique(positionY);
    
    // Calcul de la vitesse angulaire nécessaire pour garder la vitesse tangentielle cible
    float vitesseX = (VITESSE_TANGENTIELLE_CIBLE * stepsPerRevolutionX) / (2.0 * PI * rayon);

    vitesseX = constrain(vitesseX, VITESSE_X_MIN, VITESSE_X_MAX);

    if (abs(vitesseX - vitesseX_actuelle) > SEUIL_DIFF_VITESSE_X) {
      moteurX.setSpeed(vitesseX);
      vitesseX_actuelle = vitesseX;
      
      Serial.print("Rayon(cm):");
      Serial.print(rayon);
      Serial.print("\tVitesse_Plateau(pas/s):");
      Serial.print(vitesseX);
      Serial.print("\tPosition_Pion(pas):");
      Serial.println(positionY);
    }
    
    dernierPasY = positionY;
  }
}

//  --- FONCTIONS MATHÉMATIQUES ---
float convertRPMToStepsPerSec(float rpm, int stepsPerRev) {
  return (rpm * stepsPerRev) / 60.0;
}

float mapPasToRayonSymetrique(long pas) {
  long cycle = pas % (2 * pasParCycle);
  float phase = (cycle < pasParCycle) ? (float)(pasParCycle - cycle) / pasParCycle 
                                      : (float)(cycle - pasParCycle) / pasParCycle;
  return RAYON_MIN + (RAYON_MAX - RAYON_MIN) * phase;
}