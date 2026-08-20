#include <BluetoothSerial.h>
#include <TB6612.h>
#include <EEPROM.h>

BluetoothSerial SerialBT;

#define EEPROM_SIZE 512 // aantal bytes
#define EEPROM_FIRST_CHECK 0xBEEDCAFE // voor eerste flash van ESP
#define CHECK_ADDR 500 // Oude Check Adres, niet meer nodig maar voor backward compatibility


// DEBUG Toggle
#define DEBUG 0  // 0 = off , 1 = on 
#if DEBUG 
  #define Debug_println(x) Serial.println(x)
  #define Debug_print(x) Serial.print(x)
#else 
  #define Debug_print(x)
  #define Debug_println(x)
#endif

// --- STRUCTUREN ---

struct Motor {
  uint8_t nummer;
  int speed; // snelheid van motor 
  const uint8_t pwm;
  const uint8_t in1; // in 1 pin
  const uint8_t in2; // in 2 pin
};

struct Sensor {
  const char* naam;
  const uint8_t pin; 
  uint16_t zwart; // uit eeprom
  uint16_t wit; // uit eeprom
  int waarde; //raw
  int norm;  // genormaliseerd
};

struct pidController {
  float kp, ki, kd;
  float error;
  float lastError;
  float integral;
  float derivative;
  float output;
};

struct timer{
  uint32_t time;
  const uint16_t interval;
};

struct varIntervalTimer{
  uint32_t time;
  uint16_t interval;
};

struct status{
  bool run;
  bool verbonden;
  bool inSyncGestuurd;
  bool eenLijn;
};

struct ConfigParams {
  float kp, ki, kd;
  uint16_t power;
  uint16_t interval; // calc.interval
  float filterAlpha;
  uint16_t contrastDrempel;
};


Sensor sensoren[] = {
  {"DP_1", 33, 4095, 0, 0},
  {"DP_2", 32, 4095, 0, 0},
  {"DP_3", 27, 4095, 0, 0},
  {"DP_4", 14, 4095, 0, 0},
  {"DP_5", 39, 4095, 0, 0},
  {"DP_6", 36, 4095, 0, 0},
  {"DP_7", 34, 4095, 0, 0},
  {"DP_8", 35, 4095, 0, 0},
};

Motor motoren[]{
  {1, 0, 25, 17, 16},
  {2, 0, 26, 18, 19},
};

status robot;

pidController pid; // Operationeel PID struct
ConfigParams params; // EEPROM opslag struct

varIntervalTimer calc{0,2000};
varIntervalTimer send{0,200}; // interval voor telementry data 

timer ping{0,20000}; // vaste interval timer in millis onderhoud bt connectie
timer eepromCommitTimer{0, 2000}; //  Debounce timer voor EEPROM commit

const uint8_t AANTAL_SENSOREN = sizeof(sensoren) / sizeof(sensoren[0]);
const uint8_t AANTAL_MOTOREN = sizeof(motoren) / sizeof(motoren[0]);

uint16_t power = 0; // Gebruikt nu params.power, maar behouden voor backward compatibility in updatePID.
float filterAlpha = 0.8f; // Gebruikt nu params.filterAlpha
uint16_t contrastDrempel = 250; //  Gebruikt nu params.contrastDrempel

float position = 0;
float filterPosition = 0;

static unsigned long lastTime = 0; // Voor PID Delta t
bool telementry = true; // normaal telementry aan als GUI opstart
bool vorigeLijnStatus = true;
bool configChanged = false; //"Dirty" flag voor EEPROM

MotorDriver motors(
  motoren[0].pwm, motoren[0].in1, motoren[0].in2, 
  motoren[1].pwm, motoren[1].in1, motoren[1].in2
);

// Dynamische EEPROM Adressen 
struct eepromOffsets{
  const uint16_t checkAddr = 0;
  const uint16_t paramsAddr = sizeof(EEPROM_FIRST_CHECK); // Start direct na de 4-byte check
  const uint16_t witAddr = paramsAddr + sizeof(ConfigParams);
  const uint16_t zwartAddr = witAddr + (AANTAL_SENSOREN * sizeof(uint16_t));
};

eepromOffsets adressen; // Adressen struct

void setup() {
  Serial.begin(115200);
  SerialBT.begin("LineFollow_V2"); // init bt
  EEPROM.begin(EEPROM_SIZE);
  motors.motor_init();   // init motordriver

  // first flash veilige waarden zetten 
  uint32_t first;
  EEPROM.get(adressen.checkAddr, first); // Gebruik nieuwe checkAddr
  
  if(first != EEPROM_FIRST_CHECK){
    Debug_println("Eerste flash of EEPROM gereset. Schrijf veilige defaults.");
    
    // Default sensorwaarden
    for (uint8_t i = 0; i < AANTAL_SENSOREN; i++) {
      // Gebruik nieuwe adressen
      EEPROM.put(adressen.witAddr + i * sizeof(uint16_t), sensoren[i].wit);
      EEPROM.put(adressen.zwartAddr + i * sizeof(uint16_t), sensoren[i].zwart);
    }

    // Default ConfigParams struct
    ConfigParams defaultParams = {
      1.0f, 0.0f, 0.0f, // kp, ki, kd
      50, // power
      2000, // calc.interval
      0.8f, // filterAlpha
      250 // contrastDrempel
    };
    EEPROM.put(adressen.paramsAddr, defaultParams); // Schrijf het hele blok ConfigParams

    first = EEPROM_FIRST_CHECK;
    EEPROM.put(adressen.checkAddr, first);
    EEPROM.commit();
  }
  
  //Lees EEPROM waarden in struct

  //PID & Config
  EEPROM.get(adressen.paramsAddr, params);
  
  pid.kp = params.kp; 
  pid.ki = params.ki; 
  pid.kd = params.kd;
  power = params.power;
  calc.interval = params.interval;
  filterAlpha = params.filterAlpha;
  contrastDrempel = params.contrastDrempel;

  //Sensor Normalisatie waarden
  for (uint8_t i = 0; i < AANTAL_SENSOREN; i++) {
    EEPROM.get(adressen.witAddr + i * sizeof(uint16_t), sensoren[i].wit);
    EEPROM.get(adressen.zwartAddr + i * sizeof(uint16_t), sensoren[i].zwart);
  }
}


void loop() {
  uint32_t nuMillis = millis();
  uint32_t nuMicros = micros();
  
  // BT Altijd actieve checks
  if (SerialBT.available()) {
    String msg = SerialBT.readStringUntil('\n');
    msg.trim();
    // Debug_println("Ontvangen: " + msg);

    // PING / PONG handshake
    if (msg == "PING") {
      SerialBT.println("PONG");
      robot.verbonden = true;
      ping.time = millis();
    }
    // Verwerk JSON berichten
    else if (msg.startsWith("{") && msg.endsWith("}")) {

      // Essentiële commando's (run, telem) ALTIJD  verwerken
      if (msg.indexOf("\"run\"") != -1)  {
        bool newRunStatus = msg.indexOf("\"true\"") != -1;
        robot.run = newRunStatus; // Update status

        // Als de nieuwe status STOP is (false), zet de motoren struct direct stil
        if (!robot.run) { 
          motoren[0].speed = 0; // Zet motoren stil in struct
          motoren[1].speed = 0; // Zet motoren stil in struct
        }
      }
      
      // Telementry aan/uit 
      else if (msg.indexOf("\"telem\"") != -1) {
        telementry = msg.indexOf("\"true\"") != -1;
      }
      
      // Configuratie en manuele commando's verwerken ALLEEN als de robot.run = false is
      else if (!robot.run) {
        if (msg.indexOf("\"motor\"") != -1) handleManMotorSpeed(parseMotorJson(msg));
        else if (msg.indexOf("\"pid\"") != -1) handlePid(msg);
        else if (msg.indexOf("\"interval\"") != -1) handleInterval(msg);
        else if (msg.indexOf("\"speed\"") != -1) handleSpeed(msg);
        else if (msg.indexOf("\"filter\"") != -1) handleFilter(msg);
        else if (msg.indexOf("\"contrast\"") != -1) handleContrast(msg);
        else if (msg.indexOf("\"calib\"") != -1) {
          if (msg.indexOf("\"white\"") != -1) calibWit();
          else if (msg.indexOf("\"black\"") != -1) calibZwart();
        }
      }
    }
  }

  // EEPROM DEBOUNCED COMMIT LOGICA 
  // Dit zorgt ervoor dat meerdere config wijzigingen in één keer worden weggeschreven na een pauze van 2s.
  if (configChanged && (nuMillis - eepromCommitTimer.time >= eepromCommitTimer.interval)) {
    ConfigParams oldParams;
    EEPROM.get(adressen.paramsAddr, oldParams);
    
    // Gebruik memcmp om te controleren of er bytes zijn veranderd
    if (memcmp(&oldParams, &params, sizeof(ConfigParams)) != 0) {
      EEPROM.put(adressen.paramsAddr, params); // Schrijf het hele blok
      EEPROM.commit(); 
      Debug_println("EEPROM Config parameters committed na debouncing.");
    }
    
    configChanged = false; // Reset de flag
  }

  // TIMEOUT CONTROLE
  if (robot.verbonden && (nuMillis - ping.time > ping.interval)) {
    robot.verbonden = false;
    robot.inSyncGestuurd = false;
    Debug_println("Verbinding verbroken");
  }

  // TELEMENTRY VERZENDEN
  if(robot.verbonden && telementry){
    if (nuMillis - send.time >= send.interval) {
      send.time = nuMillis;
      // Stuur sensorwaarden, position, output
      for (uint8_t i = 0; i < AANTAL_SENSOREN; i++) {
        Sensor& s = sensoren[i];
        String json = JsonFormat(s.naam, s.norm);
        SerialBT.println(json);
      }
      String json = JsonFloatFormat("position", filterPosition);
      SerialBT.println(json);
      json = JsonFloatFormat("output", pid.output);
      SerialBT.println(json);
      
      // Stuurt eenmalig een sync bericht met de app (voor PID & power)
      if(robot.inSyncGestuurd == false && SerialBT.hasClient()){
        String json = JsonFormat("speed", power);
        SerialBT.println(json);
            
        json = JsonFormat("interval", calc.interval);
        SerialBT.println(json);
        
        json = JsonFloatFormat("filter", filterAlpha);
        SerialBT.println(json);
        
        json = JsonFormat("contrast", contrastDrempel);
        SerialBT.println(json);
            
        char c[512]; 
        sprintf(c, "{\"pid\": {\"kp\": %.2f, \"ki\": %.2f, \"kd\": %.2f}}", pid.kp, pid.ki, pid.kd);
        json = String(c);
        SerialBT.println(json);
            
        robot.inSyncGestuurd = true; // zet in sync flag hoog 
      }
    }
  }

  // --- REGELSYCLUS (DO CYCLUS) ---
  if (nuMicros - calc.time >= calc.interval){
    calc.time = nuMicros;
    unsigned long start = micros();
    
    // normaliseer sensor waarden 
    sensorNormalisatie();

    // Bepaal de zwaarste sensor
    uint8_t index = 0;
    for (uint8_t i = 1 ; i < AANTAL_SENSOREN; i++){
      if(sensoren[i].norm > sensoren[index].norm) index = i;
    }

    // controle op lijn 
    bool huidigeLijnStatus = geenLine(contrastDrempel);
    
    // Op positieve edge (van 'lijn gevonden' naar 'geen lijn') de motoren en run stil leggen
    if  (huidigeLijnStatus == true && vorigeLijnStatus == false){ 
      robot.run = false;
      motoren[0].speed = 0; // Zet motoren stil in struct
      motoren[1].speed = 0; // Zet motoren stil in struct
      
      // Verzend feedback naar GUI
      if (robot.verbonden) {
        SerialBT.println("{\"status\": \"LOST_LINE\"}"); 
      }
    }

    vorigeLijnStatus =  huidigeLijnStatus;

    // Kwadratische interpolatie voor positiebepaling
    float s1 = sensoren[index].norm;
    float s0;
    if (index == 0) {
        s0 = 0.0f; // Virtuele sensor 0
    } else {
        s0 = sensoren[index - 1].norm;
    }

    float s2;
    if (index == AANTAL_SENSOREN - 1) {
        s2 = 0.0f; // Virtuele sensor 0
    } else {
        s2 = sensoren[index + 1].norm;
    }

    float offset = 0.0f;
    float denom = (s2 + s0) - 2.0f * s1;
    if (fabs(denom) > 0.001f) {
        offset = 0.5f * (s2 - s0) / denom;
    }

    float mid = (float)index + offset;
    float center = (AANTAL_SENSOREN - 1) / 2.0f;
    float scale = 60.0f / (AANTAL_SENSOREN - 1);
    position = (mid - center) * scale;
    
    // Laag doorlaatfilter (Gebruikt nu filterAlpha)
    filterPosition = (1.0f - filterAlpha) * filterPosition + filterAlpha * position;

    // PID-controle
    if (robot.run) {
      updatePID(filterPosition, power);
    } 

    // Aansturen van motoren (Single Point of Control)
    motors.set_speed(motoren[0].speed, motoren[1].speed);

    unsigned long end = micros();
  }
}


// return true als geen lijn , false als wel lijn 
bool geenLine(int contrastDrempel) { 
  int minWaarde = sensoren[0].norm;
  int maxWaarde = sensoren[0].norm;
    
  for (uint8_t i = 1; i < AANTAL_SENSOREN; i++) { 
    if(sensoren[i].norm > maxWaarde) maxWaarde = sensoren[i].norm;
    if(sensoren[i].norm < minWaarde) minWaarde = sensoren[i].norm; 
  }

  int contrast = maxWaarde - minWaarde;
  if (contrast < contrastDrempel) {
      return true; // Contrast te klein = GEEN LIJN 
  } 
  else { 
      return false;
  } 
}

String JsonFormat(const char* naam, int waarde){
  char c[100];
  sprintf(c, "{\"%s\": %d}", naam , waarde);
  return String(c);
}

String JsonFloatFormat(const char* naam, float waarde) {
  char c[100];
  sprintf(c, "{\"%s\": %.2f}" , naam , waarde);
  return String(c);
}

// markeert de configuratie als 'dirty' om EEPROM commit te triggeren
// dirty betekent dat de waarde in RAM niet gelijk is aan de waarde in EEPROM
// we markeren dat er een configchange moet gebeuren maar in de loop wachten we
// pushen we de verandering maar om de 2s om EN niet als robot.run true is 
void markConfigAsDirty() {
  configChanged = true;
  eepromCommitTimer.time = millis(); // Reset de timer
}

// sensor calibratie witte waarden 
void calibWit() {
  for (uint8_t i = 0; i < AANTAL_SENSOREN; i++) {
    uint16_t value = analogRead(sensoren[i].pin);
    sensoren[i].wit = value;
    int address = adressen.witAddr + i * sizeof(uint16_t);
    EEPROM.put(address, value);
  }
  EEPROM.commit();
  Debug_println("Witte kalibratie opgeslagen");
}

// sensor calibratie zwarte waarden 
void calibZwart() {
  for (uint8_t i = 0; i < AANTAL_SENSOREN; i++) {
    uint16_t value = analogRead(sensoren[i].pin);
    sensoren[i].zwart = value;
    int address = adressen.zwartAddr + i * sizeof(uint16_t);
    EEPROM.put(address, value);
  }
  EEPROM.commit();
  Debug_println("Zwarte kalibratie opgeslagen");
}

void sensorNormalisatie() {
  for (uint8_t i = 0; i < AANTAL_SENSOREN; i++) {
    Sensor& s = sensoren[i];
    int reading = analogRead(s.pin);
    s.waarde = reading;
    s.norm = map(s.waarde,s.wit,s.zwart,0,4095);
  }
}

void updatePID(float position, int baseSpeed) {
  unsigned long now = millis();
  float dt = (float)(now - lastTime) / 1000.0f;
  lastTime = now;
  
  pid.error = -position;
  
  // I-term 
  pid.integral += pid.error * dt;
  pid.integral = constrain(pid.integral, -1000, 1000);

  // D-term
  if (dt > 0.0001f) { 
    pid.derivative = (pid.error - pid.lastError) / dt;
  } else {
    pid.derivative = 0.0f;
  }
  pid.lastError = pid.error;
  
  // PID berekening
  pid.output = pid.kp * pid.error
             + pid.ki * pid.integral
             + pid.kd * pid.derivative;
  pid.output = constrain(pid.output, -510, 510);

  int powerRight = constrain(baseSpeed - pid.output, -255, 255);
  int powerLeft  = constrain(baseSpeed + pid.output, -255, 255);

  motoren[0].speed = powerLeft;
  motoren[1].speed = -powerRight;
}

// CONFIG HANDLERS 
void handlePid(const String& msg) {
  params.kp = haalJsonWaarde(msg, "kp").toFloat();
  params.ki = haalJsonWaarde(msg, "ki").toFloat();
  params.kd = haalJsonWaarde(msg, "kd").toFloat();

  // Update operationele PID struct direct in RAM
  pid.kp = params.kp; pid.ki = params.ki; pid.kd = params.kd;

  markConfigAsDirty();
}

void handleInterval(const String& msg) {
  params.interval = haalJsonWaarde(msg, "interval").toInt();
  // Update operationele variabele
  calc.interval = params.interval; 
  
  markConfigAsDirty();
}

void handleSpeed(const String& msg) {
  params.power = constrain(haalJsonWaarde(msg, "speed").toInt(), 0, 255);
  // Update operationele variabele
  power = params.power; 
  
  markConfigAsDirty();
}

void handleFilter(const String& msg) {
  params.filterAlpha = constrain(haalJsonWaarde(msg, "filter").toFloat(), 0.0f, 1.0f);
  // Update operationele variabele
  filterAlpha = params.filterAlpha; 
  
  markConfigAsDirty();
}

void handleContrast(const String& msg) {
  params.contrastDrempel = constrain(haalJsonWaarde(msg, "contrast").toInt(), 0, 4095);
  // Update operationele variabele
  contrastDrempel = params.contrastDrempel; 
  
  markConfigAsDirty();
}

// JSON PARSERS
String haalJsonWaarde(const String& msg, const String& key) {
  int keyIndex = msg.indexOf("\"" + key + "\"");
  if (keyIndex == -1) return "";

  int colonIndex = msg.indexOf(":", keyIndex);
  if (colonIndex == -1) return "";
  int commaIndex = msg.indexOf(",", colonIndex);
  if (commaIndex == -1) commaIndex = msg.indexOf("}", colonIndex);

  if (commaIndex == -1) return "";
  String value = msg.substring(colonIndex + 1, commaIndex);
  value.trim();
  value.replace("\"", "");
  return value;
}

// Manueel bedienen van motor terwijl motor run false is kan 
Motor parseMotorJson(const String& msg) {
  Motor m = {0, 0, 0, 0, 0};
  m.nummer = haalJsonWaarde(msg, "motor").toInt();
  m.speed  = haalJsonWaarde(msg, "value").toInt();
  return m;
}

void handleManMotorSpeed(const Motor& m){
  if (m.nummer < 1 || m.nummer > 2) return; // motor.nummer 1 of 2
  motoren[m.nummer - 1].speed = m.speed; // m.nummer 1 is array index 0 , 2 is 1 
  
  Debug_print("Motor: "); Debug_print(m.nummer);
  Debug_print(" Value: ");Debug_println(m.speed);
}
