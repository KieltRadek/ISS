#define SERIAL_BAUD_RATE 9600

#include "TRSensors.h"

// Piny silników
#define PIN_LEFT_MOTOR_SPEED 5
#define PIN_LEFT_MOTOR_FORWARD A0            
#define PIN_LEFT_MOTOR_REVERSE A1
#define PIN_LEFT_ENCODER 2
   
#define PIN_RIGHT_MOTOR_SPEED 6
#define PIN_RIGHT_MOTOR_FORWARD A2            
#define PIN_RIGHT_MOTOR_REVERSE A3
#define PIN_RIGHT_ENCODER 3

// Konfiguracja trackera
#define NUM_SENSORS 5
TRSensors trs = TRSensors();
unsigned int sensorValues[NUM_SENSORS];

// Zmienne enkoderów
volatile int left_encoder_count = 0;
volatile int right_encoder_count = 0;

// Parametry PID
float Kp = 20.0;
float Ki = 0.0;
float Kd = 5.0;
float integral = 0.0;
float previousError = 0.0;
float derivative = 0.0;

// Filtr dolnoprzepustowy dla składnika D
float filteredDerivative = 0.0;
float alpha = 0.7;  // Współczynnik filtra (0-1), mniejszy = bardziej wygładzone

// Parametry sterowania
int Vref = 100;  // Prędkość bazowa (0-255)
int T_sample = 100;  // Okres próbkowania w ms (50-300ms)
unsigned long lastPIDTime = 0;

// Ograniczenia
#define MAX_INTEGRAL 1000.0
#define MIN_PWM 30  // Dead-zone kompensacja
#define MAX_PWM 255

// Stan robota
bool lineFollowMode = false;
String inputBuffer = "";

// Telemetria
bool telemetryEnabled = false;
unsigned long lastTelemetryTime = 0;
#define TELEMETRY_INTERVAL 200

// Bluetooth - używamy standardowego Serial (pin 0,1)
// HC-05/HC-06 podłączony do TX(1)/RX(0) Arduino
// Jeśli chcesz debugowanie przez USB podczas testów, 
// rozkomentuj poniżej i podłącz USB obok Bluetooth
// (ale nie jednocześnie!)

// ========================= FUNKCJE POMOCNICZE =========================

void left_encoder() {
  left_encoder_count++;  
}

void right_encoder() {
  right_encoder_count++;  
}

// Walidacja ramki (z Projektu 1)
bool validateFrame(String frame) {
  int sepIndex = frame.indexOf('|');
  if(sepIndex == -1) return false;

  String cmd = frame.substring(0, sepIndex); 
  String checksumStr = frame.substring(sepIndex + 1);
  int receivedChecksum = checksumStr.toInt();

  int calculatedChecksum = 0;  
  for (int i = 0; i < cmd.length(); i++) {
    calculatedChecksum += cmd[i];
  }
  calculatedChecksum %= 256;

  return receivedChecksum == calculatedChecksum;
}

// Obliczanie sumy kontrolnej
int calculateChecksum(String cmd) {
  int sum = 0;
  for (int i = 0; i < cmd.length(); i++) {
    sum += cmd[i];
  }
  return sum % 256;
}

// Wysyłanie odpowiedzi
void sendResponse(String response) {
  int checksum = calculateChecksum(response);
  Serial.print(response);
  Serial.print("|");
  Serial.print(checksum);
  Serial.println("#");
}

// Ustawienie silników
void setMotors(int leftPWM, int rightPWM) {
  // Lewy silnik
  if (leftPWM >= 0) {
    digitalWrite(PIN_LEFT_MOTOR_FORWARD, HIGH);
    digitalWrite(PIN_LEFT_MOTOR_REVERSE, LOW);
    analogWrite(PIN_LEFT_MOTOR_SPEED, constrain(leftPWM, MIN_PWM, MAX_PWM));
  } else {
    digitalWrite(PIN_LEFT_MOTOR_FORWARD, LOW);
    digitalWrite(PIN_LEFT_MOTOR_REVERSE, HIGH);
    analogWrite(PIN_LEFT_MOTOR_SPEED, constrain(-leftPWM, MIN_PWM, MAX_PWM));
  }
  
  // Prawy silnik
  if (rightPWM >= 0) {
    digitalWrite(PIN_RIGHT_MOTOR_FORWARD, LOW);
    digitalWrite(PIN_RIGHT_MOTOR_REVERSE, HIGH);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, constrain(rightPWM, MIN_PWM, MAX_PWM));
  } else {
    digitalWrite(PIN_RIGHT_MOTOR_FORWARD, HIGH);
    digitalWrite(PIN_RIGHT_MOTOR_REVERSE, LOW);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, constrain(-rightPWM, MIN_PWM, MAX_PWM));
  }
}

// Zatrzymanie silników
void stopMotors() {
  analogWrite(PIN_LEFT_MOTOR_SPEED, 0);
  analogWrite(PIN_RIGHT_MOTOR_SPEED, 0);
}

// ========================= REGULATOR PID =========================

void computePID() {
  // Odczyt pozycji linii (0-4000, środek = 2000)
  unsigned int position = trs.readLine(sensorValues);
  
  // Błąd: pozycja względem środka
  float error = (float)position - 2000.0;
  
  // Normalizacja błędu do zakresu -1.0 do 1.0
  error = error / 2000.0;
  
  // Czas próbkowania w sekundach
  float dt = T_sample / 1000.0;
  
  // Człon całkujący z anty-windup
  integral += error * dt;
  if (integral > MAX_INTEGRAL) integral = MAX_INTEGRAL;
  if (integral < -MAX_INTEGRAL) integral = -MAX_INTEGRAL;
  
  // Człon różniczkujący (pochodna po błędzie)
  derivative = (error - previousError) / dt;
  
  // Filtr dolnoprzepustowy dla składnika D (redukcja szumu)
  filteredDerivative = alpha * derivative + (1.0 - alpha) * filteredDerivative;
  
  // Wyjście PID
  float output = Kp * error + Ki * integral + Kd * filteredDerivative;
  
  // Zastosowanie wyjścia różnicowo do kół
  int leftPWM = Vref - (int)output;
  int rightPWM = Vref + (int)output;
  
  // Ograniczenie PWM
  leftPWM = constrain(leftPWM, -MAX_PWM, MAX_PWM);
  rightPWM = constrain(rightPWM, -MAX_PWM, MAX_PWM);
  
  // Kompensacja martwej strefy
  if (leftPWM > 0 && leftPWM < MIN_PWM) leftPWM = MIN_PWM;
  if (leftPWM < 0 && leftPWM > -MIN_PWM) leftPWM = -MIN_PWM;
  if (rightPWM > 0 && rightPWM < MIN_PWM) rightPWM = MIN_PWM;
  if (rightPWM < 0 && rightPWM > -MIN_PWM) rightPWM = -MIN_PWM;
  
  setMotors(leftPWM, rightPWM);
  
  // Telemetria
  if (telemetryEnabled && (millis() - lastTelemetryTime) >= TELEMETRY_INTERVAL) {
    Serial.print("POS:");
    Serial.print(position);
    Serial.print(" ERR:");
    Serial.print(error, 3);
    Serial.print(" OUT:");
    Serial.print(output, 2);
    Serial.print(" L:");
    Serial.print(leftPWM);
    Serial.print(" R:");
    Serial.print(rightPWM);
    Serial.print(" ENC_L:");
    Serial.print(left_encoder_count);
    Serial.print(" ENC_R:");
    Serial.println(right_encoder_count);
    
    left_encoder_count = 0;
    right_encoder_count = 0;
    lastTelemetryTime = millis();
  }
  
  previousError = error;
}

// ========================= PARSOWANIE KOMEND =========================

void parseCommand(String frame) {
  int sepIndex = frame.indexOf('|');
  String cmd = frame.substring(0, sepIndex);
  cmd.trim();
  
  // P - włącz tryb jazdy po linii
  if (cmd == "P") {
    lineFollowMode = true;
    integral = 0.0;
    previousError = 0.0;
    filteredDerivative = 0.0;
    left_encoder_count = 0;
    right_encoder_count = 0;
    sendResponse("ACK|LINE_FOLLOW_ON");
  }
  
  // S - zatrzymaj robota
  else if (cmd == "S") {
    lineFollowMode = false;
    stopMotors();
    sendResponse("ACK|LINE_FOLLOW_OFF");
  }
  
  // Kp <wartość>
  else if (cmd.startsWith("Kp ")) {
    String val = cmd.substring(3);
    Kp = val.toFloat();
    sendResponse("ACK|Kp=" + String(Kp, 2));
  }
  
  // Ki <wartość>
  else if (cmd.startsWith("Ki ")) {
    String val = cmd.substring(3);
    Ki = val.toFloat();
    integral = 0.0;  // Reset całki przy zmianie Ki
    sendResponse("ACK|Ki=" + String(Ki, 2));
  }
  
  // Kd <wartość>
  else if (cmd.startsWith("Kd ")) {
    String val = cmd.substring(3);
    Kd = val.toFloat();
    filteredDerivative = 0.0;  // Reset filtra przy zmianie Kd
    sendResponse("ACK|Kd=" + String(Kd, 2));
  }
  
  // Vref <wartość> - prędkość bazowa
  else if (cmd.startsWith("Vref ")) {
    String val = cmd.substring(5);
    Vref = val.toInt();
    Vref = constrain(Vref, 0, MAX_PWM);
    sendResponse("ACK|Vref=" + String(Vref));
  }
  
  // T <wartość> - okres próbkowania
  else if (cmd.startsWith("T ")) {
    String val = cmd.substring(2);
    T_sample = val.toInt();
    T_sample = constrain(T_sample, 50, 300);
    sendResponse("ACK|T_sample=" + String(T_sample));
  }
  
  // TELEMETRY_ON - włącz telemetrię
  else if (cmd == "TELEMETRY_ON") {
    telemetryEnabled = true;
    sendResponse("ACK|TELEMETRY_ON");
  }
  
  // TELEMETRY_OFF - wyłącz telemetrię
  else if (cmd == "TELEMETRY_OFF") {
    telemetryEnabled = false;
    sendResponse("ACK|TELEMETRY_OFF");
  }
  
  // STATUS - odczyt parametrów
  else if (cmd == "STATUS") {
    String status = "ACK|Kp:" + String(Kp, 2) + 
                    ",Ki:" + String(Ki, 2) + 
                    ",Kd:" + String(Kd, 2) + 
                    ",Vref:" + String(Vref) + 
                    ",T:" + String(T_sample) + 
                    ",Mode:" + String(lineFollowMode ? "ON" : "OFF");
    sendResponse(status);
  }
  
  // CALIBRATE - kalibracja trackera
  else if (cmd == "CALIBRATE") {
    sendResponse("ACK|CALIBRATING");
    for (int i = 0; i < 100; i++) {
      trs.calibrate();
      delay(10);
    }
    sendResponse("ACK|CALIBRATION_DONE");
  }
  
  // PING - test połączenia
  else if (cmd == "PING") {
    sendResponse("ACK|PONG");
  }
  
  // READ_LINE - odczyt pozycji linii
  else if (cmd == "READ_LINE") {
    unsigned int position = trs.readLine(sensorValues);
    sendResponse("ACK|POS:" + String(position));
  }
  
  // Nieznana komenda
  else {
    sendResponse("NACK|UNKNOWN_CMD");
  }
}

// ========================= SETUP =========================

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);
  
  // Konfiguracja silników
  pinMode(PIN_LEFT_MOTOR_SPEED, OUTPUT);
  pinMode(PIN_LEFT_MOTOR_FORWARD, OUTPUT);
  pinMode(PIN_LEFT_MOTOR_REVERSE, OUTPUT);
  pinMode(PIN_RIGHT_MOTOR_SPEED, OUTPUT);
  pinMode(PIN_RIGHT_MOTOR_FORWARD, OUTPUT);
  pinMode(PIN_RIGHT_MOTOR_REVERSE, OUTPUT);
  
  stopMotors();
  
  // Konfiguracja enkoderów
  pinMode(PIN_LEFT_ENCODER, INPUT);
  pinMode(PIN_RIGHT_ENCODER, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_LEFT_ENCODER), left_encoder, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_RIGHT_ENCODER), right_encoder, RISING);
  
  // Wstępna kalibracja trackera
  // UWAGA: Przed pierwszym użyciem uruchom komendę CALIBRATE
  // podczas przesuwania robota nad linią
  for (int i = 0; i < 100; i++) {
    trs.calibrate();
  }
  
  lastPIDTime = millis();
  
  sendResponse("ACK|READY");
}

// ========================= LOOP =========================

void loop() {
  unsigned long currentTime = millis();
  
  // Nieblokująca obsługa komunikacji szeregowej
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '#') {
      if (validateFrame(inputBuffer)) {
        parseCommand(inputBuffer);
      } else {
        sendResponse("NACK|BAD_CHECKSUM");
      }
      inputBuffer = "";
    } else if (c != '\r' && c != '\n') {
      inputBuffer += c;
    }
  }
  
  // Nieblokująca pętla PID
  if (lineFollowMode && (currentTime - lastPIDTime) >= T_sample) {
    computePID();
    lastPIDTime = currentTime;
  }
  
  // Jeśli tryb wyłączony, upewnij się że silniki są zatrzymane
  if (!lineFollowMode) {
    stopMotors();
  }
}
