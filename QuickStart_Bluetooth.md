# SZYBKI START - Line Follower z Bluetooth

## 📋 CHECKLIST SPRZĘTU

- ✅ Arduino zasilane akumulatorem
- ✅ Moduł HC-05 Bluetooth zmontowany na Arduino (TX1/RX0)
- ✅ Tracker (5 czujników) podłączony do A1-A5
- ✅ Silniki podłączone do pinów 5,6 i A0-A3
- ✅ SONAR WYŁĄCZONY ⚠️
- ✅ Bluetooth sparowany z komputerem

## 🚀 KROK PO KROKU (5 minut)

### 1. Włącz zasilanie akumulatora
```
Wciśnij przycisk lub podłącz baterię
→ Arduino powinno się włączyć
→ LED na HC-05 powinien świecić
```

### 2. Uruchom program Python
```bash
python ArduinoRobotPython.py
```

### 3. Wybierz port Bluetooth
```
=== Dostępne porty szeregowe ===
1. COM3 - Arduino Uno
2. COM4 - HC-05 Bluetooth

Wybierz port (numer): 2
Baudrate [9600]: 9600

✓ Połączono!
```

### 4. Skalibruj tracker
```
robot> calibrate
```
**Przesuwaj robota w lewo i prawo nad linią przez 3 sekundy!**

### 5. Ustaw parametry PID
```
robot> kp 20
robot> ki 0
robot> kd 5
robot> vref 100
robot> t 100
```

### 6. Włącz monitoring
```
robot> telemetry-on
POS:2050 ERR:0.025 OUT:0.5 L:100 R:100
```

### 7. START!
```
robot> P
🚗 Tryb jazdy po linii WŁĄCZONY
```

## 🎮 KOMENDY DO PAMIĘTANIA

| Komenda | Co robi |
|---------|---------|
| `P` | ▶️ Start |
| `S` | ⏹️ Stop |
| `kp 20` | Ustaw Kp |
| `kd 5` | Ustaw Kd |
| `vref 100` | Ustaw prędkość |
| `telemetry-on` | Włącz monitoring |
| `calibrate` | Ponowna kalibracja |
| `help` | Pełna pomoc |

## ⚙️ STROJENIE PID W LOCIE

**Robot oscyluje?**
```
robot> kp 15   # Zmniejsz Kp
robot> kd 8    # Zwiększ Kd
```

**Robot reaguje wolno?**
```
robot> kp 25   # Zwiększ Kp
robot> vref 120 # Zwiększ prędkość
```

**Robot traci linię?**
```
robot> vref 90  # Zwolnij
robot> kp 25    # Zwiększ reaktywność
robot> t 80     # Szybsze próbkowanie
```

## 📊 INTERPRETACJA TELEMETRII

```
POS:2150 ERR:0.075 OUT:1.5 L:98 R:101
```

- **POS > 2000** → Linia w prawo (robot skręci w lewo)
- **POS < 2000** → Linia w lewo (robot skręci w prawo)
- **ERR > 0** → Błąd dodatni (prawo)
- **OUT > 0** → Prawe koło szybsze (skręt w lewo)
- **L < R** → Asymetria (dostrajaj)

## 🔴 BŁĘDY I ROZWIĄZANIA

| Błąd | Co robić |
|------|----------|
| Port COM nie widać | Sparuj HC-05 jeszcze raz |
| Timeout/brak odpowiedzi | Sprawdź zasilanie, wciśnij reset |
| Robot się nie rusza | `calibrate` → `status` → `P` |
| Telemetria nie przychodzi | `telemetry-on` |
| Znaki śmieci | Zmień baudrate na 38400 |

## 🎯 PRZYKŁADOWE KONFIGURACJE

**Tor prosty (safe)**
```
kp 15; kd 3; vref 80; t 100
```

**Tor ze zakrętami (standard)**
```
kp 20; kd 5; vref 100; t 100
```

**Ostre zakręty (zygzak)**
```
kp 30; ki 0.2; kd 8; vref 90; t 80
```

## 📝 NOTATKA WAŻNA

**Bluetooth ≠ USB**
- Program pracuje PRZEZ BLUETOOTH (bezprzewodowo)
- Arduino musi być zasilane **AKUMULATOREM**, nie USB
- Jeśli podłączysz USB, może być konflikt - nie rób tego jednocześnie

## 🧪 TEST SZYBKI

Czy robot działa?

```bash
1. robot> status          # Sprawdzenie połączenia
2. robot> read-line       # Sprawdzenie trackera
3. robot> P               # START
4. robot> S               # STOP
5. Jeśli wszystko OK → robot> help
```

---

**GOTÓW? Włącz zasilanie i zacznij!** 🚀

Szczegółowe instrukcje: patrz `Bluetooth_Setup_Guide.md` i `README_LineFollower.md`
