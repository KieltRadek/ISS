# Tabela komend - Quick Reference

## 🎮 Komendy Line Follower (Projekt 2)

### Sterowanie robotem

| Komenda | Format | Opis | Przykład |
|---------|--------|------|----------|
| **P** | `P` | Włącz tryb jazdy po linii | `robot> P` |
| **S** | `S` | Zatrzymaj robota | `robot> S` |

### Parametry PID

| Komenda | Format | Zakres | Opis | Przykład |
|---------|--------|--------|------|----------|
| **Kp** | `Kp <wartość>` | 0-100 | Ustaw wzmocnienie proporcjonalne | `robot> kp 20` |
| **Ki** | `Ki <wartość>` | 0-10 | Ustaw wzmocnienie całkujące | `robot> ki 0.5` |
| **Kd** | `Kd <wartość>` | 0-50 | Ustaw wzmocnienie różniczkujące | `robot> kd 5` |
| **Vref** | `Vref <wartość>` | 0-255 | Ustaw prędkość bazową (PWM) | `robot> vref 100` |
| **T** | `T <wartość>` | 50-300 | Ustaw okres próbkowania [ms] | `robot> t 100` |

### Kalibracja i diagnostyka

| Komenda | Format | Opis | Przykład |
|---------|--------|------|----------|
| **CALIBRATE** | `calibrate` | Kalibruj tracker (przesuwaj nad linią!) | `robot> calibrate` |
| **READ_LINE** | `read-line` | Odczyt pozycji linii (0-4000) | `robot> read-line` |
| **STATUS** | `status` | Wyświetl wszystkie parametry | `robot> status` |
| **PING** | - | Test połączenia (automatyczny) | - |

### Telemetria

| Komenda | Format | Opis | Przykład |
|---------|--------|------|----------|
| **TELEMETRY_ON** | `telemetry-on` | Włącz monitoring w czasie rzeczywistym | `robot> telemetry-on` |
| **TELEMETRY_OFF** | `telemetry-off` | Wyłącz monitoring | `robot> telemetry-off` |
| **MONITOR** | `monitor [s]` | Podgląd telemetrii (opcjonalnie s sekund) | `robot> monitor 30` |

---

## 📊 Komendy Pochylni (Projekt 1)

### Konfiguracja

| Komenda | Format | Opis | Przykład |
|---------|--------|------|----------|
| **CFG** | `cfg` | Interaktywna konfiguracja PID | `robot> cfg` |
| **SET_TARGET** | `set-target <cm>` | Ustaw punkt docelowy | `robot> set-target 20` |
| **SET_SERVO_ZERO** | `set-servo <stopnie>` | Ustaw zero serwomechanizmu | `robot> set-servo 95` |

### Tryby pracy

| Komenda | Format | Opis | Przykład |
|---------|--------|------|----------|
| **TEST_START** | `test-start` | Uruchom tryb testowy (ciągła telemetria) | `robot> test-start` |
| **TEST_STOP** | `test-stop` | Zatrzymaj tryb testowy | `robot> test-stop` |
| **EXAM_START** | `exam` | Tryb egzaminacyjny (10s+3s, MAE) | `robot> exam` |

### Diagnostyka

| Komenda | Format | Opis | Przykład |
|---------|--------|------|----------|
| **STATUS** | `params` | Odczyt parametrów z Arduino | `robot> params` |
| **READ_DISTANCE** | `read-dist` | Jednorazowy pomiar odległości | `robot> read-dist` |

---

## 🛠️ Komendy systemowe (oba projekty)

| Komenda | Format | Opis | Przykład |
|---------|--------|------|----------|
| **HELP** | `help` lub `h` | Wyświetl pomoc | `robot> help` |
| **HISTORY** | `history` | Historia ostatnich komend | `robot> history` |
| **SAVE_LOG** | `save-log` | Zapisz log do pliku | `robot> save-log` |
| **QUIT** | `quit` lub `q` | Zakończ program | `robot> quit` |

---

## 📡 Format protokołu komunikacji

### Ramka do Arduino

```
[KOMENDA]|[CHECKSUM]#
```

**Przykłady:**
- `P|80#` - Uruchom robota
- `Kp 20|xxx#` - Ustaw Kp=20
- `PING|xxx#` - Test połączenia

### Checksum

```
checksum = (suma_kodów_ASCII_komendy) % 256
```

**Przykład dla "P":**
```
'P' = 80 (ASCII)
checksum = 80 % 256 = 80
ramka = "P|80#"
```

### Odpowiedzi z Arduino

| Format | Znaczenie | Przykład |
|--------|-----------|----------|
| `ACK|dane#` | Sukces + dane | `ACK|LINE_FOLLOW_ON|xxx#` |
| `NACK|błąd#` | Błąd | `NACK|UNKNOWN_CMD|xxx#` |
| `RESULT|dane#` | Wynik (tryb exam) | `RESULT|MAE:0.52#` |
| Bez `#` | Telemetria | `POS:2050 ERR:0.025 OUT:0.5...` |

---

## 📈 Format telemetrii Line Follower

```
POS:2150 ERR:0.075 OUT:1.5 L:98 R:101 ENC_L:12 ENC_R:13
```

| Pole | Zakres | Opis |
|------|--------|------|
| **POS** | 0-4000 | Pozycja linii (2000 = środek) |
| **ERR** | -1.0 ... 1.0 | Błąd znormalizowany |
| **OUT** | -255 ... 255 | Wyjście regulatora PID |
| **L** | -255 ... 255 | PWM lewego silnika |
| **R** | -255 ... 255 | PWM prawego silnika |
| **ENC_L** | 0+ | Impulsy lewego enkodera |
| **ENC_R** | 0+ | Impulsy prawego enkodera |

**Interpretacja:**
- `POS > 2000` → Linia w prawo → Robot skręci w lewo
- `POS < 2000` → Linia w lewo → Robot skręci w prawo
- `ERR > 0` → Linia w prawo
- `OUT > 0` → Zwiększ prawe koło (skręt w lewo)

---

## 🎯 Typowe sekwencje komend

### Uruchomienie Line Followera

```bash
robot> calibrate          # 1. Kalibruj (przesuwaj nad linią)
robot> kp 20              # 2. Ustaw PID
robot> ki 0
robot> kd 5
robot> vref 100
robot> t 100
robot> status             # 3. Sprawdź konfigurację
robot> telemetry-on       # 4. Włącz monitoring
robot> P                  # 5. START!
```

### Strojenie PID w locie

```bash
robot> P                  # Robot jedzie
robot> telemetry-on       # Obserwuj zachowanie
# Robot oscyluje? →
robot> kp 15              # Zmniejsz Kp
robot> kd 8               # Zwiększ Kd
# Za wolno reaguje? →
robot> kp 25              # Zwiększ Kp
# Sprawdź efekt...
robot> S                  # Zatrzymaj gdy gotowe
```

### Test pochylni

```bash
robot> cfg                # Interaktywna konfiguracja
robot> set-target 20      # Punkt docelowy 20cm
robot> test-start         # Tryb testowy
# Obserwuj telemetrię...
robot> test-stop          # Zatrzymaj
robot> exam               # Tryb egzaminacyjny (13s)
# Czekaj na RESULT|MAE:...
```

---

## ⚡ Skróty klawiszowe (w interfejsie Python)

| Klawisz | Akcja |
|---------|-------|
| **↑** | Poprzednia komenda (jeśli dostępne) |
| **↓** | Następna komenda (jeśli dostępne) |
| **Ctrl+C** | Przerwij monitor/telemetrię |
| **Tab** | Autouzupełnienie (jeśli dostępne) |

---

## 🔧 Przykładowe wartości PID

### Line Follower - Tor prosty
```
kp 15
ki 0
kd 3
vref 80
t 100
```

### Line Follower - Zakręty
```
kp 25
ki 0.2
kd 8
vref 100
t 80
```

### Pochylnia - Stabilizacja
```
distance_point: 20 cm
kp: 15.0
ki: 0.5
kd: 8.0
servo_zero: 95°
t: 100 ms
```

---

## 📱 QuickPIDConfig.py - Menu

Gdy używasz `python QuickPIDConfig.py`:

```
1 - Bezpieczny Start (Kp=15, Ki=0, Kd=3, Vref=80)
2 - Łagodne Zakręty (Kp=20, Ki=0, Kd=5, Vref=100)
3 - Ostre Zakręty (Kp=30, Ki=0.2, Kd=8, Vref=90)
4 - Wysoka Prędkość (Kp=25, Ki=0, Kd=10, Vref=140)
5 - Tor Mieszany (Kp=22, Ki=0.1, Kd=6, Vref=110)
6 - Tor z Przerwami (Kp=20, Ki=0.5, Kd=5, Vref=100)

c - Kalibracja
s - Status
p - Uruchom (P)
x - Zatrzymaj (S)
t - Telemetria
q - Wyjście
```

---

## 🆘 Troubleshooting - Komendy diagnostyczne

### Problem: Brak połączenia
```
robot> status             # Sprawdź status połączenia
# Jeśli timeout → sprawdź port COM, baudrate
```

### Problem: Robot nie reaguje
```
robot> status             # Parametry OK?
robot> read-line          # Tracker widzi linię?
robot> calibrate          # Ponowna kalibracja
robot> P                  # Spróbuj ponownie
```

### Problem: Oscylacje
```
robot> telemetry-on       # Zobacz co się dzieje
# Obserwuj ERR i OUT
robot> kp 15              # Zmniejsz Kp
robot> kd 8               # Zwiększ Kd
```

### Problem: Dziwne znaki / błędy checksum
```
# Sprawdź baudrate (powinien być 9600)
# Sprawdź kabel USB
# Restart Arduino i interfejsu Python
```

---

## 📚 Pliki referencyjne

- **Pełna dokumentacja:** `README_LineFollower.md`
- **Gotowe konfiguracje:** `PID_Configurations.md`
- **Notatki techniczne:** `Technical_Notes.md`
- **Quick Start:** `QuickStart.md`
- **Schemat połączeń:** `Wiring_Diagram.md`

---

**Drukuj tę stronę i trzymaj obok podczas testów!** 📄✨
