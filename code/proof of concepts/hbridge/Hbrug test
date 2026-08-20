#include <Arduino.h>

// Motor A
const int PWMA = 25;
const int AIN1 = 17;
const int AIN2 = 16;

// Motor B
const int PWMB = 26;
const int BIN1 = 18;
const int BIN2 = 19;

void stopMotoren() {
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, LOW);

  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, LOW);

  ledcWrite(PWMA, 0);
  ledcWrite(PWMB, 0);
}

void setup() {
  Serial.begin(115200);

  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);

  ledcAttach(PWMA, 5000, 8);
  ledcAttach(PWMB, 5000, 8);

  stopMotoren();

  Serial.println("=== MOTORTEST ===");

  delay(3000);
}

void loop() {

  // TEST 1 - MOTOR A richting 1
  Serial.println("TEST 1: Motor A richting 1");

  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, LOW);

  ledcWrite(PWMA, 180);
  ledcWrite(PWMB, 0);

  delay(2000);

  stopMotoren();
  delay(1500);


  // TEST 2 - MOTOR A richting 2
  Serial.println("TEST 2: Motor A richting 2");

  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, HIGH);

  ledcWrite(PWMA, 180);
  ledcWrite(PWMB, 0);

  delay(2000);

  stopMotoren();
  delay(1500);


  // TEST 3 - MOTOR B richting 1
  Serial.println("TEST 3: Motor B richting 1");

  digitalWrite(BIN1, HIGH);
  digitalWrite(BIN2, LOW);

  ledcWrite(PWMA, 0);
  ledcWrite(PWMB, 180);

  delay(2000);

  stopMotoren();
  delay(1500);


  // TEST 4 - MOTOR B richting 2
  Serial.println("TEST 4: Motor B richting 2");

  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, HIGH);

  ledcWrite(PWMA, 0);
  ledcWrite(PWMB, 180);

  delay(2000);

  stopMotoren();

  Serial.println("Test klaar");
  Serial.println("---------------------");

  delay(5000);
}
