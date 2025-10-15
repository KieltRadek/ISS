//Engine, encoder
#define PIN_LEFT_MOTOR_SPEED 5
#define PIN_LEFT_MOTOR_FORWARD A0
#define PIN_LEFT_MOTOR_REVERSE A1
#define PIN_LEFT_ENCODER 2

#define PIN_RIGHT_MOTOR_SPEED 6
#define PIN_RIGHT_MOTOR_FORWARD A2
#define PIN_RIGHT_MOTOR_REVERSE A3
#define PIN_RIGHT_ENCODER 3

//Sonar
#define TRIGER_PIN 11
#define ECHO_PIN 12
#define ANALOG_READ_IR_LEFT A4
#define DIGITAL_READ_IR_LEFT 7
#define ANALOG_READ_IR_RIGHT A5
#define DIGITAL_READ_IR_RIGHT 8 

#define SERIAL_BAUD_RATE 9600

// KALIBRACJA - Dostosuj te wartości dla swojego robota
#define PULSES_PER_CM 20           // Ile impulsów enkodera = 1 cm ruchu
#define PULSES_PER_360_DEGREES 800  // Ile impulsów enkodera = pełny obrót 360°

String inputBuffer="";
long duration;
int distance;
String motor1Role = "LEFT";
String motor2Role = "RIGHT";
String motor1Direction = "NORMAL";  // NORMAL lub REVERSED
String motor2Direction = "NORMAL";  // NORMAL lub REVERSED
String sensor1Role = "FRONT";
String sensor2Role = "BACK"; 

// Zmienne globalne
int speed = 150; // Domyślna prędkość
volatile int left_encoder_count = 0;
volatile int right_encoder_count = 0;

// Funkcje obsługi przerwań enkoderów
void left_encoder(){
  left_encoder_count++;  
}

void right_encoder(){
  right_encoder_count++;  
}

bool validateFrame(String frame){
  int sepIndex = frame.indexOf('|');
  if(sepIndex==-1) return false;

  String cmd = frame.substring(0,sepIndex); 
  String checksumStr = frame.substring(sepIndex +1);
  int receivedChecksum = checksumStr.toInt();

  int calculatedChecksum = 0;  
  for (int i=0;i<cmd.length();i++){
    calculatedChecksum +=cmd[i];
  }
  calculatedChecksum %= 256;

  return receivedChecksum == calculatedChecksum;
}

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
    speed = constrain(v,0,255);
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
    String cfgBody = cmd.substring(4,cmd.length()-1); //usuwamy "CFG(" i ")"
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

// Funkcja pomocnicza do ustawienia kierunku silnika z uwzględnieniem odwrócenia
void setMotorDirection(int motorNum, bool forward) {
  bool isReversed = (motorNum == 1 && motor1Direction == "REVERSED") || 
                    (motorNum == 2 && motor2Direction == "REVERSED");
  
  // Jeśli silnik jest odwrócony, zamień kierunek
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
  // Resetuj liczniki enkoderów
  left_encoder_count = 0;
  right_encoder_count = 0;
  
  // val to liczba centymetrów
  // Przelicz centymetry na impulsy enkodera
  int target_pulses = abs(val) * PULSES_PER_CM;
  
  if(val < 0 ){
    // Ruch do tyłu
    setMotorDirection(1, false);  // Silnik 1 - tył
    setMotorDirection(2, false);  // Silnik 2 - tył
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed);
    
    // Czekaj aż osiągniemy zadaną odległość
    while(left_encoder_count < target_pulses || right_encoder_count < target_pulses){
      delay(10);
    }
    
    // Zatrzymaj
    stopRobot();
    
  } else if(val > 0 ){
    // Ruch do przodu
    setMotorDirection(1, true);   // Silnik 1 - przód
    setMotorDirection(2, true);   // Silnik 2 - przód
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed);
    
    // Czekaj aż osiągniemy zadaną odległość
    while(left_encoder_count < target_pulses || right_encoder_count < target_pulses){
      delay(10);
    }
    
    // Zatrzymaj
    stopRobot();
  }
}

void rotateRobot(int val){
  // Resetuj liczniki enkoderów
  left_encoder_count = 0;
  right_encoder_count = 0;
  
  // val to liczba stopni (0-360)
  // Przelicz stopnie na impulsy enkodera
  // Wzór: impulsy = (stopnie / 360) * PULSES_PER_360_DEGREES
  int target_pulses = (abs(val) * PULSES_PER_360_DEGREES) / 360;
  
  if(val < 0 ){
    // Obrót w lewo - lewy silnik do tyłu, prawy do przodu
    setMotorDirection(1, false);  // Silnik 1 - tył
    setMotorDirection(2, true);   // Silnik 2 - przód
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed/2);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed/2);
    
    // Czekaj aż osiągniemy zadany obrót
    while(left_encoder_count < target_pulses || right_encoder_count < target_pulses){
      delay(10);
    }
    
    // Zatrzymaj
    stopRobot();
    
  } else if(val > 0 ){
    // Obrót w prawo - lewy silnik do przodu, prawy do tyłu
    setMotorDirection(1, true);   // Silnik 1 - przód
    setMotorDirection(2, false);  // Silnik 2 - tył
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed/2);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed/2);
    
    // Czekaj aż osiągniemy zadany obrót
    while(left_encoder_count < target_pulses || right_encoder_count < target_pulses){
      delay(10);
    }
    
    // Zatrzymaj
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

  long duration = pulseIn(ECHO_PIN, HIGH, 30000); //timeout 30ms
  long distance = duration * 0.034/2;

  return distance;
}

String readIR(){
  int analogLeft = analogRead(ANALOG_READ_IR_LEFT);
  int digitalLeft = digitalRead(DIGITAL_READ_IR_LEFT);
  int analogRight = analogRead(ANALOG_READ_IR_RIGHT);
  int digitalRight = digitalRead(DIGITAL_READ_IR_RIGHT);

  return String("AL=") + analogLeft + ",DL=" + digitalLeft + ",AR=" + analogRight + ",DR=" + digitalRight;  
}
 

void setup() {
  Serial.begin(SERIAL_BAUD_RATE); 
  
  // Motor pins setup
  pinMode(PIN_LEFT_MOTOR_SPEED, OUTPUT);
  pinMode(PIN_LEFT_MOTOR_FORWARD, OUTPUT);
  pinMode(PIN_LEFT_MOTOR_REVERSE, OUTPUT);
  pinMode(PIN_LEFT_ENCODER, INPUT);
  
  pinMode(PIN_RIGHT_MOTOR_SPEED, OUTPUT);
  pinMode(PIN_RIGHT_MOTOR_FORWARD, OUTPUT);
  pinMode(PIN_RIGHT_MOTOR_REVERSE, OUTPUT);
  pinMode(PIN_RIGHT_ENCODER, INPUT);
  
  // Sonar pins setup
  pinMode(TRIGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // IR pins setup
  pinMode(DIGITAL_READ_IR_LEFT, INPUT);
  pinMode(DIGITAL_READ_IR_RIGHT, INPUT);
  
  // Attach encoder interrupts
  attachInterrupt(digitalPinToInterrupt(PIN_LEFT_ENCODER), left_encoder, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_RIGHT_ENCODER), right_encoder, RISING);
  
  // Stop motors on startup
  stopRobot();
}

void loop() {
  while(Serial.available()){
    char c = Serial.read();
    if(c=='#'){
      if(validateFrame(inputBuffer)){
        parseCommand(inputBuffer);
      } else{
        Serial.println("NACK|BAD_CHECKSUM#");
      }
      inputBuffer="";
    } else{
      inputBuffer +=c;
    }
  }
}