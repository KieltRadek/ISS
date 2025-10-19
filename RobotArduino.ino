// Silniki i enkodery
#define PIN_LEFT_MOTOR_SPEED 5
#define PIN_LEFT_MOTOR_FORWARD A0
#define PIN_LEFT_MOTOR_REVERSE A1
#define PIN_LEFT_ENCODER 2

#define PIN_RIGHT_MOTOR_SPEED 6
#define PIN_RIGHT_MOTOR_FORWARD A2
#define PIN_RIGHT_MOTOR_REVERSE A3
#define PIN_RIGHT_ENCODER 3

// Sonar i czujniki podczerwieni (IR)
#define TRIGER_PIN 11
#define ECHO_PIN 12
#define ANALOG_READ_IR_LEFT A4
#define DIGITAL_READ_IR_LEFT 7
#define ANALOG_READ_IR_RIGHT A5
#define DIGITAL_READ_IR_RIGHT 8 

#define SERIAL_BAUD_RATE 9600

// Do kalibracji
#define PULSES_PER_CM 20           // Ile impulsów = 1 cm ruchu
#define PULSES_PER_360_DEGREES 800  // Ile impulsów = pełny obrót 360°

String inputBuffer="";
long duration;
int distance;
String motor1Role = "LEFT";
String motor2Role = "RIGHT";
String motor1Direction = "NORMAL";  // NORMAL lub REVERSED
String motor2Direction = "NORMAL";  // NORMAL lub REVERSED
String sensor1Role = "FRONT";
String sensor2Role = "BACK"; 

int speed = 100;
volatile int left_encoder_count = 0;  // Licznik impulsów lewego enkodera volatile żeby nie było stałej z początku
volatile int right_encoder_count = 0; // Licznik impulsów prawego enkodera volatile żeby nie było stałej z początku

// Funkcje obsługi przerwań enkoderów - wywoływane automatycznie przy każdym impulsie
void left_encoder(){
  left_encoder_count++;  
}

void right_encoder(){
  right_encoder_count++;  
}

// Walidacja ramki - sprawdza poprawność sumy kontrolnej
// Format ramki: KOMENDA|SUMA_KONTROLNA#
bool validateFrame(String frame){
  int sepIndex = frame.indexOf('|');
  if(sepIndex==-1) return false;

  String cmd = frame.substring(0,sepIndex); 
  String checksumStr = frame.substring(sepIndex +1);
  int receivedChecksum = checksumStr.toInt();

  // Suma znaków(ASCII) modulo 256
  int calculatedChecksum = 0;  
  for (int i=0;i<cmd.length();i++){
    calculatedChecksum +=cmd[i];
  }
  calculatedChecksum %= 256;

  return receivedChecksum == calculatedChecksum;
}

// Wyciągamy wartość z komendy
int extractInt(String cmd){
  int start = cmd.indexOf('(');
  int end = cmd.indexOf(")");
  if(start == -1 || end == -1) return 0;
  String valStr = cmd.substring(start+1,end);
  
  return valStr.toInt();
}

void parseCommand(String frame){
  int sepIndex = frame.indexOf('|');
  String cmd = frame.substring(0,sepIndex);

  if(cmd.startsWith("M(")){
    int val = extractInt(cmd);
    moveRobot(val);
    Serial.println("ACK#");
  } else if(cmd.startsWith("R(")){
    int val = extractInt(cmd);
    rotateRobot(val);
    Serial.println("ACK#");
  } else if(cmd == "S"){
    stopRobot();
    Serial.println("ACK#");
  }else if(cmd.startsWith("V(")){
    int v = extractInt(cmd);
    speed = constrain(v,0,255);  // Ograniczenie 255
    Serial.println("ACK#");
  }else if(cmd == "B"){
    long dist = readSonar();
    Serial.print("ACK|");
    Serial.print(dist);
    Serial.println("#");  
  }else if(cmd == "I"){
    String irData = readIR();  
    Serial.print("ACK|");
    Serial.print(irData);
    Serial.println("#");  
  }else if(cmd.startsWith("CFG(")){
    String cfgBody = cmd.substring(4,cmd.length()-1); // Usuwamy "CFG(" i ")"
    applyConfig(cfgBody);
    Serial.println("ACK#");
  }else if(cmd=="PING"){
    Serial.println("ACK|PONG#");
  }
  else{
    Serial.println("NACK|UNKNOWN_CMD#");
  }
}

void applyConfig(String cfgBody){
  int pos = 0;
  while(pos<cfgBody.length()){
    int eq = cfgBody.indexOf('=',pos);
    int comma = cfgBody.indexOf(',',eq);
    if (comma == -1) comma = cfgBody.length();

    String key = cfgBody.substring(pos,eq);
    String val = cfgBody.substring(eq+1,comma);

    if (key == "M1") motor1Role = val;
    else if(key == "M2") motor2Role = val;
    else if(key == "M1_DIR") motor1Direction = val;
    else if(key == "M2_DIR") motor2Direction = val;
    else if(key == "S1") sensor1Role = val;
    else if(key == "S2") sensor2Role = val;

    pos = comma + 1;
  }
}

void setMotorDirection(int motorNum, bool forward) {
  bool isReversed = (motorNum == 1 && motor1Direction == "REVERSED") || 
                    (motorNum == 2 && motor2Direction == "REVERSED");
  
  if (isReversed) {
    forward = !forward;
  }
  
  if (motorNum == 1) {
    // Silnik 1 (lewy)
    if (forward) {
      digitalWrite(PIN_LEFT_MOTOR_FORWARD, HIGH);
      digitalWrite(PIN_LEFT_MOTOR_REVERSE, LOW);
    } else {
      digitalWrite(PIN_LEFT_MOTOR_FORWARD, LOW);
      digitalWrite(PIN_LEFT_MOTOR_REVERSE, HIGH);
    }
  } else if (motorNum == 2) {
    // Silnik 2 (prawy)
    if (forward) {
      digitalWrite(PIN_RIGHT_MOTOR_FORWARD, HIGH);
      digitalWrite(PIN_RIGHT_MOTOR_REVERSE, LOW);
    } else {
      digitalWrite(PIN_RIGHT_MOTOR_FORWARD, LOW);
      digitalWrite(PIN_RIGHT_MOTOR_REVERSE, HIGH);
    }
  }
}

void moveRobot(int val){
  left_encoder_count = 0;
  right_encoder_count = 0;
  
  // Przelicz centymetry na impulsy enkodera według kalibracji
  int target_pulses = abs(val) * PULSES_PER_CM;
  
  if(val < 0 ){
    setMotorDirection(1, false); 
    setMotorDirection(2, false);
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed);
    
    while(left_encoder_count < target_pulses || right_encoder_count < target_pulses){
      delay(10);
    }
    
    stopRobot();
    
  } else if(val > 0 ){
    setMotorDirection(1, true); 
    setMotorDirection(2, true);
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed);
    
    while(left_encoder_count < target_pulses || right_encoder_count < target_pulses){
      delay(10);
    }
    
    stopRobot();
  }
}

void rotateRobot(int val){
  left_encoder_count = 0;
  right_encoder_count = 0;
  
  // Wzór: impulsy = (stopnie / 360) * PULSES_PER_360_DEGREES
  int target_pulses = (abs(val) * PULSES_PER_360_DEGREES) / 360;
  
  if(val < 0 ){
    setMotorDirection(1, false);
    setMotorDirection(2, true);
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed/2);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed/2);
    
    while(left_encoder_count < target_pulses || right_encoder_count < target_pulses){
      delay(10);
    }
    
    stopRobot();
    
  } else if(val > 0 ){
    setMotorDirection(1, true);
    setMotorDirection(2, false);
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed/2);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed/2);
    
    while(left_encoder_count < target_pulses || right_encoder_count < target_pulses){
      delay(10);
    }

    stopRobot();
  }
}

void stopRobot(){
  digitalWrite(PIN_LEFT_MOTOR_FORWARD,LOW);
  digitalWrite(PIN_LEFT_MOTOR_REVERSE,LOW);
  digitalWrite(PIN_RIGHT_MOTOR_FORWARD,LOW);
  digitalWrite(PIN_RIGHT_MOTOR_REVERSE,LOW);
}

long readSonar(){
  digitalWrite(TRIGER_PIN,LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGER_PIN,HIGH); 
  delayMicroseconds(10);
  digitalWrite(TRIGER_PIN,LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  long distance = duration * 0.034/2;

  return distance;
}

// Zwraca zarówno wartości analogowe (0-1023) jak i cyfrowe (0/1) dla obu czujników
String readIR(){
  int analogLeft = analogRead(ANALOG_READ_IR_LEFT);
  int digitalLeft = digitalRead(DIGITAL_READ_IR_LEFT);
  int analogRight = analogRead(ANALOG_READ_IR_RIGHT);
  int digitalRight = digitalRead(DIGITAL_READ_IR_RIGHT);

  return String("AL=") + analogLeft + ",DL=" + digitalLeft + ",AR=" + analogRight + ",DR=" + digitalRight;  
}
 

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);
  
  pinMode(PIN_LEFT_MOTOR_SPEED, OUTPUT);
  pinMode(PIN_LEFT_MOTOR_FORWARD, OUTPUT);
  pinMode(PIN_LEFT_MOTOR_REVERSE, OUTPUT);
  pinMode(PIN_LEFT_ENCODER, INPUT);
  
  pinMode(PIN_RIGHT_MOTOR_SPEED, OUTPUT);
  pinMode(PIN_RIGHT_MOTOR_FORWARD, OUTPUT);
  pinMode(PIN_RIGHT_MOTOR_REVERSE, OUTPUT);
  pinMode(PIN_RIGHT_ENCODER, INPUT);
  
  pinMode(TRIGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  pinMode(DIGITAL_READ_IR_LEFT, INPUT);
  pinMode(DIGITAL_READ_IR_RIGHT, INPUT);
  
  attachInterrupt(digitalPinToInterrupt(PIN_LEFT_ENCODER), left_encoder, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_RIGHT_ENCODER), right_encoder, RISING);
  
  stopRobot();
}

void loop() {
  while(Serial.available()){
    char c = Serial.read();
    if(c=='#'){  // '#' = koniec ramki
      if(validateFrame(inputBuffer)){
        parseCommand(inputBuffer);  // Wykonaj komendę jeśli suma kontrolna się zgadza
      } else{
        Serial.println("NACK|BAD_CHECKSUM#");  // Błąd sumy kontrolnej
      }
      inputBuffer="";  // czyszczenie
    } else{
      inputBuffer +=c;  // Dodaj znak do bufora
    }
  }
}