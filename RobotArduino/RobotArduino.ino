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

String inputBuffer="";
int speed = 100;
long duration;
int distance;
String motor1Role = "LEFT";
String motor2Role = "RIGHT";
String sensor1Role = "FRONT";
String sensor2Role = "BACK"; 

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
    else if(key == "S1") sensor1Role = val;
    else if(key == "S2") sensor2Role = val;

    pos = comma + 1;
  }
}

void moveRobot(int val){
  if(val < 0 ){
    digitalWrite(PIN_LEFT_MOTOR_FORWARD,LOW);
    digitalWrite(PIN_LEFT_MOTOR_REVERSE,HIGH);
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed);

    digitalWrite(PIN_RIGHT_MOTOR_FORWARD,LOW);
    digitalWrite(PIN_RIGHT_MOTOR_REVERSE,HIGH);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed);
  } else if(val > 0 ){
    digitalWrite(PIN_LEFT_MOTOR_FORWARD,HIGH);
    digitalWrite(PIN_LEFT_MOTOR_REVERSE,LOW);
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed);

    digitalWrite(PIN_RIGHT_MOTOR_FORWARD,HIGH);
    digitalWrite(PIN_RIGHT_MOTOR_REVERSE,LOW);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed);
  }
}

void rotateRobot(int val){
  if(val < 0 ){
    digitalWrite(PIN_LEFT_MOTOR_FORWARD,LOW);
    digitalWrite(PIN_LEFT_MOTOR_REVERSE,HIGH);
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed/2);

    digitalWrite(PIN_RIGHT_MOTOR_FORWARD,HIGH);
    digitalWrite(PIN_RIGHT_MOTOR_REVERSE,LOW);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed/2);
  } else if(val > 0 ){
    digitalWrite(PIN_LEFT_MOTOR_FORWARD,HIGH);
    digitalWrite(PIN_LEFT_MOTOR_REVERSE,LOW);
    analogWrite(PIN_LEFT_MOTOR_SPEED, speed/2);

    digitalWrite(PIN_RIGHT_MOTOR_FORWARD,LOW);
    digitalWrite(PIN_RIGHT_MOTOR_REVERSE,HIGH);
    analogWrite(PIN_RIGHT_MOTOR_SPEED, speed/2);
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
