#include <AccelStepper.h>

// --- BROCHES DU SHIELD CNC ---
#define EN 8       
#define STEP_Y 3   
#define DIR_Y 6    
#define STEP_X 2   
#define DIR_X 5    

// --- RÉSOLUTION MÉCANIQUE (FULL STEP) ---
const int MICROSTEPPING = 1; // Pas de jumpers = 1

const int multiplicateur_mecanique = 2.83; 
const int stepsPerRevolutionX = (200 * MICROSTEPPING)*multiplicateur_mecanique; 
const int stepsPerRevolutionY = 200 * MICROSTEPPING; 

// --- CONSTANTES PHYSIQUES ---
const float VITESSE_TANGENTIELLE_CIBLE = 15.0; // Vitesse de ton train en cm/s
const float vitesseY_RPM = 0.5;                
const int pasParCycle = 290 * MICROSTEPPING;   // Déplacement total du pion       
const float RAYON_MAX = 7.5;                   // cm
const float RAYON_MIN = 1.35;                  // cm

// --- CONSTANTES DE RÉGLAGE LOGICIEL ---
const long SEUIL_PAS_Y = 2;             // Seuil plus bas en Full Step
const float VITESSE_X_MIN = 10.0;      
const float VITESSE_X_MAX = 1000.0;     // Plafond de sécurité adapté au Full Step
const float SEUIL_DIFF_VITESSE_X = 2.0;

AccelStepper moteurY(AccelStepper::DRIVER, STEP_Y, DIR_Y);
AccelStepper moteurX(AccelStepper::DRIVER, STEP_X, DIR_X);

long positionDepart = 0;
long positionCible = pasParCycle;
long dernierPasY = 0;
float vitesseX_actuelle = 0.0;

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

void loop() {
  moteurY.runSpeed();
  moteurX.runSpeed();

  // --- GESTION DU MOTEUR Y (ALLER-RETOUR DU PION) ---
  if ((moteurY.currentPosition() >= positionCible && moteurY.speed() > 0) ||
      (moteurY.currentPosition() <= positionCible && moteurY.speed() < 0)) {
    
    moteurY.setSpeed(-moteurY.speed());
    positionDepart = moteurY.currentPosition();
    positionCible = positionDepart + (pasParCycle * (moteurY.speed() > 0 ? 1 : -1));
    
    Serial.print("Inversion Y. Cible : ");
    Serial.println(positionCible);
  }

  // --- ASSERVISSEMENT DU MOTEUR X (VITESSE DU DISQUE) ---
  long positionY = abs(moteurY.currentPosition());

  if (abs(positionY - dernierPasY) >= SEUIL_PAS_Y) {
    float rayon = mapPasToRayonSymetrique(positionY);
    
    // Application stricte de w = Vt / r
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

// --- FONCTIONS MATHÉMATIQUES ---
float convertRPMToStepsPerSec(float rpm, int stepsPerRev) {
  return (rpm * stepsPerRev) / 60.0;
}

float mapPasToRayonSymetrique(long pas) {
  long cycle = pas % (2 * pasParCycle);
  float phase = (cycle < pasParCycle) ? (float)(pasParCycle - cycle) / pasParCycle 
                                      : (float)(cycle - pasParCycle) / pasParCycle;
  return RAYON_MIN + (RAYON_MAX - RAYON_MIN) * phase;
}