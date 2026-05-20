#include <AccelStepper.h>

// --- BROCHES ---
#define STEP_Y 3
#define DIR_Y 6
#define STEP_X 2
#define DIR_X 5

const int multiplicateur_mecanique = 2.83;

// --- CONSTANTES PHYSIQUES ---
const int stepsPerRevolutionX = 200 * multiplicateur_mecanique; // À vérifier (souvent 200 pour NEMA 17)
const int stepsPerRevolutionY = 200; 

const float VITESSE_TANGENTIELLE_CIBLE = 15.0; // Vitesse de "l'avancée du train" en cm/s
const float vitesseY_RPM = 0.5;                // Vitesse radiale du pion
const int pasParCycle = 290;                   // Déplacement max du pion en pas
const float RAYON_MAX = 7.5;                   // en cm
const float RAYON_MIN = 1.35;                  // en cm

// --- CONSTANTES DE RÉGLAGE LOGICIEL ---
const long SEUIL_PAS_Y = 5;            
const float VITESSE_X_MIN = 10.0;      
const float VITESSE_X_MAX = 2000.0;    
const float SEUIL_DIFF_VITESSE_X = 5.0;

AccelStepper moteurY(AccelStepper::DRIVER, STEP_Y, DIR_Y);
AccelStepper moteurX(AccelStepper::DRIVER, STEP_X, DIR_X);

long positionDepart = 0;
long positionCible = pasParCycle;
long dernierPasY = 0;
float vitesseX_actuelle = 0.0;

void setup() {
  // CRUCIAL : Un baud rate élevé évite de bloquer les moteurs lors de l'affichage
  Serial.begin(115200);

  // Initialisation Moteur Y
  moteurY.setMaxSpeed(convertRPMToStepsPerSec(vitesseY_RPM, stepsPerRevolutionY));
  moteurY.setSpeed(convertRPMToStepsPerSec(vitesseY_RPM, stepsPerRevolutionY));

  // Initialisation Moteur X
  moteurX.setMaxSpeed(VITESSE_X_MAX);
  moteurX.setSpeed(100); 
}

void loop() {
  // Les appels doivent être exécutés en boucle continue, sans aucun delay()
  moteurY.runSpeed();
  moteurX.runSpeed();

  // --- GESTION DU MOTEUR Y (ALLER-RETOUR) ---
  if ((moteurY.currentPosition() >= positionCible && moteurY.speed() > 0) ||
      (moteurY.currentPosition() <= positionCible && moteurY.speed() < 0)) {
    
    moteurY.setSpeed(-moteurY.speed());
    positionDepart = moteurY.currentPosition();
    positionCible = positionDepart + (pasParCycle * (moteurY.speed() > 0 ? 1 : -1));

    Serial.print("Inversion Y. Cible : ");
    Serial.println(positionCible);
  }

  // --- ASSERVISSEMENT DU MOTEUR X (DISQUE) ---
  long positionY = abs(moteurY.currentPosition());

  if (abs(positionY - dernierPasY) >= SEUIL_PAS_Y) {
    float rayon = mapPasToRayonSymetrique(positionY);
    
    // Calcul rigoureux de la vitesse angulaire pour garantir Vt constant
    float vitesseX = (VITESSE_TANGENTIELLE_CIBLE * stepsPerRevolutionX) / (2.0 * PI * rayon);

    // Sécurité : bridage de la vitesse aux extrêmes
    vitesseX = constrain(vitesseX, VITESSE_X_MIN, VITESSE_X_MAX);

    // Mise à jour si la variation est significative
    if (abs(vitesseX - vitesseX_actuelle) > SEUIL_DIFF_VITESSE_X) {
      moteurX.setSpeed(vitesseX);
      vitesseX_actuelle = vitesseX;

      Serial.print("Rayon: ");
      Serial.print(rayon);
      Serial.print(" cm | VitesseX (pas/s): ");
      Serial.println(vitesseX);
    }
    
    dernierPasY = positionY;
  }
}

// --- FONCTIONS UTILITAIRES ---
float convertRPMToStepsPerSec(float rpm, int stepsPerRev) {
  return (rpm * stepsPerRev) / 60.0;
}

float mapPasToRayonSymetrique(long pas) {
  long cycle = pas % (2 * pasParCycle);
  float phase = (cycle < pasParCycle) ? (float)(pasParCycle - cycle) / pasParCycle 
                                      : (float)(cycle - pasParCycle) / pasParCycle;
  return RAYON_MIN + (RAYON_MAX - RAYON_MIN) * phase;
}