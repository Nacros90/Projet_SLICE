#include <AccelStepper.h>

#define STEP_Y 3
#define DIR_Y 6

#define STEP_X 2
#define DIR_X 5

const int stepsPerRevolution = 20;
const float vitesseY_RPM = 0.5;  // constante
const int pasParCycle = 290;

AccelStepper moteurY(AccelStepper::DRIVER, STEP_Y, DIR_Y);
AccelStepper moteurX(AccelStepper::DRIVER, STEP_X, DIR_X);

long positionDepart = 0;
long positionCible = pasParCycle;

long dernierPasY = 0;
float vitesseX_actuelle = 0;

void setup() {
  Serial.begin(9600);

  // Initialiser moteur Y
  moteurY.setMaxSpeed(convertRPMToStepsPerSec(vitesseY_RPM));
  moteurY.setSpeed(convertRPMToStepsPerSec(vitesseY_RPM));

  // Initialiser moteur X
  moteurX.setMaxSpeed(2000);  // max possible
  moteurX.setSpeed(100);      // valeur initiale
}

void loop() {
  // --- MOTEUR Y ---
  moteurY.runSpeed();

  if ((moteurY.currentPosition() >= positionCible && moteurY.speed() > 0) ||
      (moteurY.currentPosition() <= positionCible && moteurY.speed() < 0)) {

    moteurY.setSpeed(-moteurY.speed());
    positionDepart = moteurY.currentPosition();
    positionCible = positionDepart + (pasParCycle * (moteurY.speed() > 0 ? 1 : -1));

    Serial.print("Direction Y inversée. Nouvelle cible : ");
    Serial.println(positionCible);
  }

  // --- MOTEUR X ---
  moteurX.runSpeed();

  long positionY = abs(moteurY.currentPosition());

  if (abs(positionY - dernierPasY) >= 5) {
    float rayon = mapPasToRayonSymetrique(positionY);  // en cm
    float vitesseX = (vitesseY_RPM * 1e6) / (60.0 * 2 * PI * rayon);

    // Imposer une vitesse minimale
    if (vitesseX < 10) vitesseX = 10;
    if (vitesseX > 2000) vitesseX = 2000;

    // N'appliquer la nouvelle vitesse que si elle change vraiment
    if (abs(vitesseX - vitesseX_actuelle) > 5) {
      moteurX.setSpeed(vitesseX);
      vitesseX_actuelle = vitesseX;

      Serial.print("Y pos: ");
      Serial.print(positionY);
      Serial.print(" | Rayon: ");
      Serial.print(rayon);
      Serial.print(" cm | VitesseX: ");
      Serial.println(vitesseX);
    }

    dernierPasY = positionY;
  }
}

// Conversion tr/min → pas/sec
float convertRPMToStepsPerSec(float rpm) {
  return (rpm * stepsPerRevolution) / 60.0;
}

// Correction : commence à 7.5 cm et va vers 1.35 cm
float mapPasToRayonSymetrique(long pas) {
  float rayonMax = 7.5;
  float rayonMin = 1.35;
  long cycle = pas % (2 * pasParCycle);
  float phase = (cycle < pasParCycle) ? (float)(pasParCycle - cycle) / pasParCycle
                                      : (float)(cycle - pasParCycle) / pasParCycle;
  return rayonMin + (rayonMax - rayonMin) * phase;
}

