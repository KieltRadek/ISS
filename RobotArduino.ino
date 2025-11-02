#define SERIAL_BAUD_RATE 9600

#include <Wire.h>
#include <Servo.h>

unsigned long myTime;
Servo myservo;
float distance;
float kp = 0.0;
float ki = 0.0;
float kd = 0.0;
float integral = 0.0;
float derivative = 0.0;
float previousError = 0.0;
float distance_point = 0.0;
int servo_zero = 95;
int t = 100;  // domyślnie 100ms
String inputBuffer = "";
bool testMode = false;
bool examMode = false;
unsigned long examStartTime = 0;
unsigned long stabilizationStartTime = 0;
bool stabilizationPhase = false;
float errorSum = 0.0;
int errorCount = 0;

// Pomiar odległości z czujnika IR
float get_dist(int n){
  long sum = 0;
  for(int i = 0; i < n; i++){
    sum = sum + analogRead(A0);
  }  
  float adc = sum / n;
  float distance_cm = 17569.7 * pow(adc, -1.2062);
  return distance_cm;
}

// Regulator PID
void PID(){
  float error = distance - distance_point;
  integral = integral + error * (t / 1000.0);
  derivative = (error - previousError) / (t / 1000.0);
  float output = kp * error + ki * integral + kd * derivative;
  
  // Telemetria w trybie TEST
  if(testMode){
    Serial.print("DIST:");
    Serial.print(distance);
    Serial.print(" ERR:");
    Serial.print(error);
    Serial.print(" OUT:");
    Serial.println(output);
  }
  
  previousError = error;
  
  // Ograniczenie wyjścia (zakładam ±45 stopni)
  output = constrain(output, -45, 45);
  int servoAngle = servo_zero + (int)output;
  servoAngle = constrain(servoAngle, 0, 180);  // Bezpieczeństwo
  myservo.write(servoAngle);
}

// Walidacja ramki
bool validateFrame(String frame){
  int sepIndex = frame.indexOf('|');
  if(sepIndex == -1) return false;

  String cmd = frame.substring(0, sepIndex); 
  String checksumStr = frame.substring(sepIndex + 1);
  int receivedChecksum = checksumStr.toInt();

  int calculatedChecksum = 0;  
  for (int i = 0; i < cmd.length(); i++){
    calculatedChecksum += cmd[i];
  }
  calculatedChecksum %= 256;

  return receivedChecksum == calculatedChecksum;
}

// Parsowanie komendy CFG
void applyConfig(String cfgBody){
  int pos = 0;
  while(pos < cfgBody.length()){
    int eq = cfgBody.indexOf('=', pos);
    int comma = cfgBody.indexOf(',', eq);
    if (comma == -1) comma = cfgBody.length();

    String key = cfgBody.substring(pos, eq);
    String val = cfgBody.substring(eq + 1, comma);

    if (key == "KP") kp = val.toFloat();
    else if(key == "KI") ki = val.toFloat();
    else if(key == "KD") kd = val.toFloat();
    else if(key == "DIST_POINT") distance_point = val.toFloat();
    else if(key == "SERVO_ZERO") servo_zero = val.toInt();
    else if(key == "T") t = val.toInt();

    pos = comma + 1;
  }
}

// Parsowanie komend
void parseCommand(String frame){
  int sepIndex = frame.indexOf('|');
  String cmd = frame.substring(0, sepIndex);

  if(cmd.startsWith("CFG(")){
    String cfgBody = cmd.substring(4, cmd.length() - 1);
    applyConfig(cfgBody);
    Serial.println("ACK#");
  }
  else if(cmd == "TEST_START"){
    testMode = true;
    examMode = false;
    integral = 0.0;
    previousError = 0.0;
    Serial.println("ACK|TEST_MODE_ON#");
  }
  else if(cmd == "TEST_STOP"){
    testMode = false;
    Serial.println("ACK|TEST_MODE_OFF#");
  }
  else if(cmd.startsWith("SET_TARGET(")){
    String val = cmd.substring(11, cmd.length() - 1);
    distance_point = val.toFloat();
    Serial.println("ACK|TARGET_SET#");
  }
  else if(cmd.startsWith("SET_SERVO_ZERO(")){
    String val = cmd.substring(15, cmd.length() - 1);
    servo_zero = val.toInt();
    myservo.write(servo_zero);
    Serial.println("ACK|SERVO_ZERO_SET#");
  }
  else if(cmd == "EXAM_START"){
    examMode = true;
    testMode = false;
    stabilizationPhase = false;
    examStartTime = millis();
    integral = 0.0;
    previousError = 0.0;
    errorSum = 0.0;
    errorCount = 0;
    Serial.println("ACK|EXAM_STARTED#");
  }
  else if(cmd == "PING"){
    Serial.println("ACK|PONG#");
  }
  else{
    Serial.println("NACK|UNKNOWN_CMD#");
  }
}

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);
  myservo.attach(9);
  myservo.write(servo_zero);
  pinMode(A0, INPUT);
  myTime = millis();
}

void loop() {
  // Obsługa komunikacji
  while(Serial.available()){
    char c = Serial.read();
    if(c == '#'){
      if(validateFrame(inputBuffer)){
        parseCommand(inputBuffer);
      } else{
        Serial.println("NACK|BAD_CHECKSUM#");
      }
      inputBuffer = "";
    } else{
      inputBuffer += c;
    }
  }
  
  // Pętla PID
  if (millis() > myTime + t){
    distance = get_dist(100); 
    myTime = millis();
    
    if(testMode || examMode){
      PID();
    }
    
    // Tryb egzaminacyjny
    if(examMode){
      unsigned long elapsed = millis() - examStartTime;
      
      // Faza 1: Osiągnięcie celu (10s)
      if(elapsed >= 10000 && !stabilizationPhase){
        stabilizationPhase = true;
        stabilizationStartTime = millis();
        errorSum = 0.0;
        errorCount = 0;
      }
      
      // Faza 2: Pomiar MAE (3s)
      if(stabilizationPhase){
        float error = abs(distance - distance_point);
        errorSum += error;
        errorCount++;
        
        unsigned long stabilizationTime = millis() - stabilizationStartTime;
        if(stabilizationTime >= 3000){
          float mae = errorSum / errorCount;
          Serial.print("RESULT|MAE:");
          Serial.print(mae, 2);
          Serial.println("#");
          examMode = false;
          integral = 0.0;
          previousError = 0.0;
          myservo.write(servo_zero);
        }
      }
    }
  }
}