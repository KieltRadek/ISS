# Przewodnik - Konfiguracja Bluetooth dla Line Follower

## ⚡ Twoja konfiguracja

✅ **Zasilanie:** Akumulator (bateria)  
✅ **Moduł Bluetooth:** HC-05 lub HC-06 (już zmontowany na Arduino)  
✅ **Komunikacja:** Przez Bluetooth (bezprzewodowa)

## 🔌 Sprawdzenie podłączenia sprzętu

### 1. Pinout Arduino Uno + Bluetooth

```
Arduino Uno (seria RX/TX)
├─ Pin 0 (RX) ────┬──► HC-05 RX (przez dzielnik napięcia!)
│                 │
│                 ├─ Dzielnik napięcia (5V→3.3V)
│                 │   [1kΩ]────┬──── GND
│                 └─────────────┤
│                           HC-05 RX
│
├─ Pin 1 (TX) ────────► HC-05 TX
├─ 5V ────────────────► HC-05 VCC (lub 3.3V jeśli moduł to wspiera)
└─ GND ────────────────► HC-05 GND (WSPÓLNA MASA!)
```

**WAŻNE:** 
- HC-05 wymaga 3.3V na pinie RX
- Dzielnik napięcia: `Vout = 5V × (2kΩ/(1kΩ+2kΩ)) = 3.3V`
- Jeśli moduł ma regulator 3.3V, możesz podłączyć 5V bezpośrednio na VCC

### 2. Sprawdzenie przez LED

HC-05 powinien mieć:
- ✅ **LED ciągle świecący** = Bluetooth sparowany
- 🔴 **LED migający powoli (0.5s)** = Czeka na parowanie
- 🔴 **LED migający szybko (0.2s)** = Szuka urządzenia

## 📱 Parowanie Bluetooth (Windows)

### Krok 1: Włącz Bluetooth na komputerze
```
Ustawienia → Urządzenia → Bluetooth
```

### Krok 2: Szukaj urządzenia
```
Dodaj urządzenie Bluetooth lub inne
→ Szukaj HC-05 (zwykle nazwany "HC-05" lub "linefollower")
```

### Krok 3: PIN do parowania
```
Domyślny PIN: 1234 lub 0000
(Możesz zmienić przez AT commands)
```

### Krok 4: Przypisz COM port
```
Po sparowaniu pojawi się nowy COM port (np. COM4)
Zapamiętaj ten numer!
```

## 🚀 Uruchomienie programu

### Krok 1: Załóż zasilanie na Arduino
```
Akumulator → Arduino 5V + GND
(Robot powinien być na stole, gotów do testów)
```

### Krok 2: Uruchom program Python
```bash
python ArduinoRobotPython.py
```

### Krok 3: Wybierz COM port
```
=== Dostępne porty szeregowe ===
1. COM3 - Arduino Uno
2. COM4 - HC-05 Bluetooth Device  ← WYBIERZ TUTAJ!
3. COM5 - USB Serial

Wybierz port (numer): 2
Baudrate [9600]: 9600
```

### Krok 4: Test połączenia
```
robot> status
✓ Połączenie aktywne
```

## 🔧 Jeśli Bluetooth nie działa

### Problem 1: Port COM nie widać
**Rozwiązanie:**
```
1. Sprawdź czy HC-05 ma zasilanie (LED powinien świecić)
2. Sparuj jeszcze raz: Ustawienia → Urządzenia → Bluetooth
3. Restart komputera
4. Sprawdź Menedżer urządzeń (Device Manager):
   - Szukaj "Ports (COM & LPT)"
   - Powinna być dwulinię dla HC-05
```

### Problem 2: Timeout - brak odpowiedzi
**Rozwiązanie:**
```
1. Sprawdzić czy Arduino ma zasilanie (wciśnij reset)
2. Sprawdzić baudrate (powinien być 9600)
3. Sprawdzić czy nie ma konfliktu z innymi portami
4. Spróbuj inny COM port
```

### Problem 3: Znaki "śmieci" zamiast tekstu
**Rozwiązanie:**
```
Zmień baudrate:
- Domyślnie: 9600
- Spróbuj: 38400 jeśli zmieniano AT commands
```

## 🎮 Podstawowy workflow

```bash
# 1. Połącz przez Bluetooth
robot> status
✓ Połączenie aktywne

# 2. Kalibruj tracker (przesuwaj nad linią)
robot> calibrate
✓ Kalibracja zakończona

# 3. Ustaw parametry PID
robot> kp 20
robot> kd 5
robot> vref 100

# 4. Włącz telemetrię by zobaczyć co się dzieje
robot> telemetry-on
POS:2000 ERR:0.0 OUT:0.0 L:100 R:100 ENC_L:0 ENC_R:0

# 5. START!
robot> P
🚗 Tryb jazdy po linii WŁĄCZONY

# 6. Obserwuj telemetrię, dostrajaj PID w locie
robot> kp 25
✅ Kp ustawione na: 25.0

# 7. Gdy gotowe, zatrzymaj
robot> S
🛑 Robot ZATRZYMANY
```

## 📊 Telemetria przez Bluetooth

Format `POS:2050 ERR:0.025 OUT:0.5 L:99 R:100`:

| Pole | Znaczenie | Prawidłowy zakres |
|------|-----------|-------------------|
| **POS** | Pozycja linii | 0-4000 (środek=2000) |
| **ERR** | Błąd znormalizowany | -1.0 do 1.0 |
| **OUT** | Wyjście PID | -255 do 255 |
| **L/R** | PWM silników | 0-255 (lub -255 do 255) |
| **ENC_L/R** | Enkodery | liczba impulsów |

## ⚙️ Zmiana baudrate (zaawansowane)

Jeśli chcesz zmienić baudrate HC-05 (np. na 38400):

### Przez Arduino (AT commands)
```cpp
// Sketch do konfiguracji HC-05
void setup() {
  Serial.begin(9600);  // Domyślny baudrate
}

void loop() {
  if (Serial.available()) {
    Serial.write(Serial.read());  // Echo
  }
}
```

Wyślij przez Serial Monitor:
```
AT
OK

AT+BAUD4
OK (zmieniony na 38400)
```

### Przez program Python
```python
# W ArduinoRobotPython.py przy połączeniu
baudrate = int(input("Baudrate [9600]: ")) or 9600
# Wpisz: 38400
```

## 🔒 Bezpieczeństwo

### Zmień domyślny PIN HC-05
```
AT+PSWD1234
OK
```

### Zmień nazwę HC-05
```
AT+NAMELineFollower
OK
```

**WAŻNE:** Po zmianach AT commands, wciśnij reset na HC-05 lub Arduino!

## 📋 Checklist przed testem

- [ ] Moduł HC-05 ma zasilanie (LED świeci)
- [ ] Arduino ma zasilanie z akumulatora
- [ ] Dzielnik napięcia podłączony (RX HC-05)
- [ ] Wspólna masa Arduino i HC-05
- [ ] Bluetooth sparowany z komputerem
- [ ] COM port przypisany
- [ ] Program Python uruchomiony
- [ ] Test połączenia: `robot> status`
- [ ] Tracker skalibrowany: `robot> calibrate`

## 🧪 Test diagnostyczny

```bash
python TestSuite.py
# Wybierz COM port Bluetooth (np. COM4)
# Automatycznie sprawdzi wszystkie funkcje
```

## 📞 Troubleshooting - Szybkie rozwiązania

| Problem | Rozwiązanie |
|---------|-------------|
| Port COM nie widać | Sparuj HC-05 jeszcze raz w Ustawieniach |
| Timeout (brak odpowiedzi) | Sprawdź zasilanie Arduino, wciśnij reset |
| Znaki "śmieci" | Zmień baudrate na 38400 lub 115200 |
| Robot nie reaguje | Sprawdź `status`, kalibruj tracker |
| Telemetria nie przychodz | Wpisz `telemetry-on` |
| Oscylacje | Zmniejsz Kp, zwiększ Kd |

## 🎯 Gotowy do testów?

```bash
python ArduinoRobotPython.py

robot> calibrate           # Kalibruj
robot> kp 20; ki 0; kd 5   # Wstępne PID
robot> telemetry-on        # Włącz monitoring
robot> P                   # JAZZ!
```

**Powodzenia!** 🚗💨

---

**Notatka:** Kod Arduino obsługuje zarówno USB Serial (do debugowania) jak i Bluetooth. Jeśli podłączysz zarówno USB jak i Bluetooth, bądź ostrożny - mogą kolidować komunikaty. Najlepiej testować tylko przez Bluetooth z akumulatorem.
