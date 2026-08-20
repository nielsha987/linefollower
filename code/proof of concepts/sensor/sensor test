// MIR-3.0Y - analoge test met ESP32

const int sensorPins[8] = {
  33,  // D1
  32,  // D2
  27,  // D3
  14,  // D4
  39,  // D5
  36,  // D6
  34,  // D7
  35   // D8
};

void setup() {
  Serial.begin(115200);

  // ESP32 ADC = standaard 12 bit: 0 - 4095
  analogReadResolution(12);

  delay(1000);

  Serial.println();
  Serial.println("MIR-3.0Y ANALOGE TEST");
  Serial.println("D1    D2    D3    D4    D5    D6    D7    D8");
}

void loop() {

  for (int i = 0; i < 8; i++) {

    int waarde = analogRead(sensorPins[i]);

    Serial.print(waarde);
    Serial.print("   ");
  }

  Serial.println();

  delay(200);
}
