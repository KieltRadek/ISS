// --- Piny silników i enkoderów ---
#define PIN_LEFT_MOTOR_SPEED     5
#define PIN_LEFT_MOTOR_FORWARD   A0
#define PIN_LEFT_MOTOR_REVERSE   A1
#define PIN_LEFT_ENCODER         2

#define PIN_RIGHT_MOTOR_SPEED    6
#define PIN_RIGHT_MOTOR_FORWARD  A2
#define PIN_RIGHT_MOTOR_REVERSE  A3
#define PIN_RIGHT_ENCODER        3

#define SERIAL_BAUD_RATE 9600

volatile int left_encoder_count = 0;
volatile int right_encoder_count = 0;

int speedPWM = 150;   // domyślna prędkość (0–255)

void left_encoder()  { left_encoder_count++; }
void right_encoder() { right_encoder_count++; }

// --- suma kontrolna ---
String checksumHex(const String &payload) {
  int sum = 0;
  for (int i=0; i<payload.length(); i++) sum += payload[i];
  sum &= 0xFF;
  char buf[3];
  sprintf(buf, "%02X", sum);
  return String(buf);
}

// --- odpowiedzi ---
void sendACK(String ts, String msg) {
  Serial.print("ACK|"); Serial.print(ts); Serial.print("|"); Serial.println(msg);
}
void sendNACK(String ts, String reason) {
  Serial.print("NACK|"); Serial.print(ts); Serial.print("|"); Serial.println(reason);
}

// --- sterowanie silnikami ---
void motorsStop() {
  digitalWrite(PIN_LEFT_MOTOR_FORWARD, LOW);
  digitalWrite(PIN_LEFT_MOTOR_REVERSE, LOW);
  analogWrite(PIN_LEFT_MOTOR_SPEED, 0);

  digitalWrite(PIN_RIGHT_MOTOR_FORWARD, LOW);
  digitalWrite(PIN_RIGHT_MOTOR_REVERSE, LOW);
  analogWrite(PIN_RIGHT_MOTOR_SPEED, 0);
}

void motorsForward(int pwm) {
  digitalWrite(PIN_LEFT_MOTOR_FORWARD, HIGH);
  digitalWrite(PIN_LEFT_MOTOR_REVERSE, LOW);
  analogWrite(PIN_LEFT_MOTOR_SPEED, pwm);

  digitalWrite(PIN_RIGHT_MOTOR_FORWARD, HIGH);
  digitalWrite(PIN_RIGHT_MOTOR_REVERSE, LOW);
  analogWrite(PIN_RIGHT_MOTOR_SPEED, pwm);
}

void motorsBackward(int pwm) {
  digitalWrite(PIN_LEFT_MOTOR_FORWARD, LOW);
  digitalWrite(PIN_LEFT_MOTOR_REVERSE, HIGH);
  analogWrite(PIN_LEFT_MOTOR_SPEED, pwm);

  digitalWrite(PIN_RIGHT_MOTOR_FORWARD, LOW);
  digitalWrite(PIN_RIGHT_MOTOR_REVERSE, HIGH);
  analogWrite(PIN_RIGHT_MOTOR_SPEED, pwm);
}

void rotateRight(int pwm) {
  digitalWrite(PIN_LEFT_MOTOR_FORWARD, HIGH);
  digitalWrite(PIN_LEFT_MOTOR_REVERSE, LOW);
  analogWrite(PIN_LEFT_MOTOR_SPEED, pwm);

  digitalWrite(PIN_RIGHT_MOTOR_FORWARD, LOW);
  digitalWrite(PIN_RIGHT_MOTOR_REVERSE, HIGH);
  analogWrite(PIN_RIGHT_MOTOR_SPEED, pwm);
}

void rotateLeft(int pwm) {
  digitalWrite(PIN_LEFT_MOTOR_FORWARD, LOW);
  digitalWrite(PIN_LEFT_MOTOR_REVERSE, HIGH);
  analogWrite(PIN_LEFT_MOTOR_SPEED, pwm);

  digitalWrite(PIN_RIGHT_MOTOR_FORWARD, HIGH);
  digitalWrite(PIN_RIGHT_MOTOR_REVERSE, LOW);
  analogWrite(PIN_RIGHT_MOTOR_SPEED, pwm);
}

// --- setup ---
void setup() {
  Serial.begin(SERIAL_BAUD_RATE);

  pinMode(PIN_LEFT_MOTOR_SPEED, OUTPUT);
  pinMode(PIN_LEFT_MOTOR_FORWARD, OUTPUT);
  pinMode(PIN_LEFT_MOTOR_REVERSE, OUTPUT);

  pinMode(PIN_RIGHT_MOTOR_SPEED, OUTPUT);
  pinMode(PIN_RIGHT_MOTOR_FORWARD, OUTPUT);
  pinMode(PIN_RIGHT_MOTOR_REVERSE, OUTPUT);

  attachInterrupt(digitalPinToInterrupt(PIN_LEFT_ENCODER), left_encoder, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_RIGHT_ENCODER), right_encoder, RISING);

  motorsStop();
  Serial.println("READY");
}

// --- loop ---
void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length() < 4) return;

    if (line[0] != ':') return;

    String rest = line.substring(1);
    String payload = rest.substring(0, rest.length()-2);
    String recvChk = rest.substring(rest.length()-2);

    String calc = checksumHex(payload);
    int p1 = payload.indexOf('|');
    int p2 = payload.lastIndexOf('|');
    if (p1<0 || p2<=p1) { sendNACK("0","BADFMT"); return; }
    String cmd = payload.substring(0,p1);
    String arg = payload.substring(p1+1,p2);
    String ts  = payload.substring(p2+1);

    if (!recvChk.equalsIgnoreCase(calc)) {
      sendNACK(ts,"BADCHK");
      return;
    }

    cmd.toUpperCase();

    // --- komendy ---
    if (cmd=="M") {
      int dist = arg.toInt();
      if (dist>0) motorsForward(speedPWM);
      else motorsBackward(speedPWM);
      delay(1000);
      motorsStop();
      sendACK(ts,"DONE");
    }
    else if (cmd=="R") {
      int deg = arg.toInt();
      if (deg>0) rotateRight(speedPWM);
      else rotateLeft(speedPWM);
      delay(constrain(abs(deg)*5, 50, 3000));
      motorsStop();
      sendACK(ts,"DONE");
    }
    else if (cmd=="V") {
      int v = arg.toInt();
      if (v<0 || v>255) sendNACK(ts,"BADVAL");
      else { speedPWM = v; sendACK(ts,"SET"); }
    }
    else if (cmd=="S") {
      motorsStop();
      sendACK(ts,"STOPPED");
    }
    else if (cmd=="B") {
      int fakeSonar = 42;
      sendACK(ts,String(fakeSonar));
    }
    else if (cmd=="I") {
      int fakeIR = analogRead(A4);
      sendACK(ts,String(fakeIR));
    }
    else if (cmd=="H") {
      String status = String("SPD=")+speedPWM;
      sendACK(ts,status);
    }
    else {
      sendNACK(ts,"UNKNOWN");
    }

    left_encoder_count=0;
    right_encoder_count=0;
  }
}
