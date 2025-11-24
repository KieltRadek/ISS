# ISS - Intelligent Stabilization System
## System sterowania pochylnią z regulatorem PID

Projekt implementuje zaawansowany system sterowania pochylnią oparty na regulatorze PID. System składa się z oprogramowania Arduino (C++) kontrolującego fizyczne urządzenie oraz interfejsu PC w Pythonie umożliwiającego konfigurację i monitoring.

## 🎯 Opis projektu

System ISS to platforma do testowania i demonstracji działania regulatora PID w czasie rzeczywistym. Urządzenie wykorzystuje czujnik IR do pomiaru odległości piłki na pochylni i dynamicznie reguluje kąt nachylenia za pomocą serwomechanizmu, aby utrzymać piłkę w zadanym punkcie.

### Główne funkcje:
- **Regulator PID** z konfigurowalnymi parametrami (Kp, Ki, Kd)
- **Tryb testowy** z telemetrią w czasie rzeczywistym
- **Tryb egzaminacyjny** z automatyczną oceną stabilizacji (MAE)
- **Komunikacja szeregowa** z protokołem ramkowym i sumą kontrolną
- **Interaktywny interfejs** PC do konfiguracji i monitoringu
- **Watchdog** do monitorowania połączenia

## 🔧 Technologie

- **Python** (74.5%) - interfejs użytkownika, komunikacja PC-Arduino
- **C++** (25.5%) - Arduino, regulator PID, obsługa czujników

## 📋 Wymagania

### Sprzęt:
- Arduino (Uno/Nano/Mega)
- Serwomechanizm (podłączony do pin 9)
- Czujnik odległości IR Sharp GP2Y0A21YK (podłączony do A0)
- Pochylnia mechaniczna
- Kabel USB do komunikacji PC-Arduino

### Oprogramowanie:
- **Python 3.x** z biblioteką `pyserial`
- **Arduino IDE** (do wgrania firmware)
- System operacyjny: Windows/Linux/macOS

## 🚀 Instalacja

### 1. Przygotowanie środowiska Python

```bash
# Sklonuj repozytorium
git clone https://github.com/KieltRadek/ISS.git
cd ISS

# Zainstaluj wymaganą bibliotekę
pip install pyserial
```

### 2. Wgranie firmware na Arduino

1. Otwórz plik `RobotArduino.ino` w Arduino IDE
2. Podłącz Arduino przez USB
3. Wybierz odpowiedni port i typ płytki
4. Wgraj program (Upload)
5. Czujnik IR powinien być podłączony do A0, serwomechanizm do pin 9

### 3. Uruchomienie interfejsu Python

```bash
python ArduinoRobotPython.py
```

## 📖 Użycie

### Uruchomienie aplikacji

Po uruchomieniu skryptu Python:
1. Wybierz port szeregowy z listy
2. Ustaw baudrate (domyślnie 9600)
3. Połączenie zostanie nawiązane automatycznie

### Podstawowy przepływ pracy

```
robot> help                          # Wyświetl dostępne komendy
robot> cfg                           # Skonfiguruj parametry PID
robot> set-target 15                 # Ustaw punkt docelowy na 15 cm
robot> test-start                    # Uruchom tryb testowy
robot> test-stop                     # Zatrzymaj tryb testowy
robot> exam                          # Uruchom tryb egzaminacyjny (13s)
```

## 🎮 Dostępne komendy

### Konfiguracja:
- `cfg` - Interaktywna konfiguracja parametrów PID i systemu
- `set-target [cm]` - Ustaw punkt docelowy (odległość w cm)
- `set-servo [stopnie]` - Ustaw pozycję zero serwomechanizmu

### Tryby pracy:
- `test-start` - Uruchom tryb testowy z telemetrią
- `test-stop` - Zatrzymaj tryb testowy
- `exam` - Tryb egzaminacyjny (10s na stabilizację + 3s pomiar MAE)
- `monitor [s]` - Monitor telemetrii (opcjonalnie czas w sekundach)

### Diagnostyka:
- `status` - Sprawdź status połączenia i watchdog
- `params` - Odczyt aktualnych parametrów z Arduino
- `read-dist` - Jednorazowy pomiar odległości

### System:
- `help` / `h` - Wyświetl pomoc
- `history` - Historia wykonanych komend
- `save-log` - Zapisz log komunikacji do pliku
- `quit` / `q` - Zakończ program

## 🔬 Tryb egzaminacyjny

Tryb egzaminacyjny przeprowadza automatyczny test stabilizacji:

1. **Faza 1 (10s)**: System stabilizuje piłkę w punkcie docelowym
2. **Faza 2 (3s)**: Pomiar Mean Absolute Error (MAE)
3. **Wynik**: Zwracana jest wartość MAE - im niższa, tym lepsza stabilizacja

```
robot> exam
Tryb egzaminacyjny uruchomiony
Oczekiwanie na wynik (13s)...

RESULT|MAE:0.87
```

## 📊 Telemetria

W trybie testowym system wysyła dane w formacie:
```
<odległość> : <błąd> : <wyjście_PID>
```

Przykład:
```
15.23 : 0.23 : 2.45
14.89 : -0.11 : -1.12
15.01 : 0.01 : 0.08
```

## 🔌 Protokół komunikacji

### Format ramki:
```
KOMENDA|CHECKSUM#
```

### Przykłady komend:
- `PING|80#` - Test połączenia
- `CFG(KP=1.5,KI=0.1,KD=0.05)|123#` - Konfiguracja
- `TEST_START|245#` - Start trybu testowego
- `SET_TARGET(15)|198#` - Ustaw cel na 15 cm

### Odpowiedzi:
- `ACK#` - Potwierdzenie wykonania
- `NACK|UNKNOWN_CMD#` - Nieznana komenda
- `NACK|BAD_CHECKSUM#` - Błąd sumy kontrolnej
- `RESULT|MAE:0.87#` - Wynik pomiaru

## ⚙️ Parametry konfiguracyjne

| Parametr | Opis | Domyślna wartość |
|----------|------|------------------|
| `KP` | Wzmocnienie proporcjonalne | 0.0 |
| `KI` | Wzmocnienie całkujące | 0.0 |
| `KD` | Wzmocnienie różniczkujące | 0.0 |
| `DIST_POINT` | Punkt docelowy [cm] | 0.0 |
| `SERVO_ZERO` | Pozycja zero serwa [°] | 95 |
| `T` | Okres pętli PID [ms] | 100 |

## 📁 Struktura projektu

```
ISS/
├── ArduinoRobotPython.py    # Interfejs PC (Python)
├── RobotArduino.ino         # Firmware Arduino (C++)
└── README.md                # Dokumentacja
```

## 🧪 Przykładowa sesja

```bash
$ python ArduinoRobotPython.py

╔════════════════════════════════════════════╗
║      INTERFEJS KOMUNIKACJI PC-ARDUINO      ║
╚════════════════════════════════════════════╝

=== Dostępne porty szeregowe ===
1. COM3 - Arduino Uno
Wybierz port (numer): 1
Baudrate [9600]: 
Połączono z COM3 (9600 baud)
Watchdog: Połączenie aktywne

robot> cfg
=== KONFIGURACJA ROBOTA ===
distance_point (cm) = 15
kp = 2.5
ki = 0.3
kd = 1.2
servo_zero (stopnie) = 95
t (ms, pętla PID) = 100
Konfiguracja zastosowana: DIST_POINT=15.0,KP=2.5,KI=0.3,KD=1.2,SERVO_ZERO=95,T=100

robot> test-start
Tryb testowy uruchomiony
15.23 : 0.23 : 2.45
14.89 : -0.11 : -1.12
15.01 : 0.01 : 0.08

robot> test-stop
Tryb testowy zatrzymany

robot> exam
Tryb egzaminacyjny uruchomiony
Oczekiwanie na wynik (13s)...

RESULT|MAE:0.65

robot> save-log
Log zapisany do: robot_log_20251124_235147.txt

robot> quit
Zamykanie połączenia...
Połączenie zamknięte
```

## 🐛 Troubleshooting

### Problem: Brak dostępnych portów szeregowych
- Sprawdź czy Arduino jest podłączone przez USB
- Zainstaluj sterowniki CH340/FTDI jeśli wymagane
- Na Linuxie sprawdź uprawnienia: `sudo usermod -a -G dialout $USER`

### Problem: Timeout przy komunikacji
- Zwiększ timeout: `self.timeout = 2.0` w kodzie Python
- Sprawdź baudrate (musi być zgodny: 9600)
- Zresetuj Arduino

### Problem: Niestabilna regulacja
- Dostosuj parametry PID (zacznij od małych wartości Kp)
- Sprawdź mechanikę pochylni
- Skalibruj `servo_zero` dla poziomu pochylni

### Problem: Czujnik IR daje nieprawidłowe odczyty
- Sprawdź zakres pomiaru czujnika (10-80 cm dla GP2Y0A21YK)
- Wyczyść obiektyw czujnika
- Unikaj odbić od błyszczących powierzchni

## 📝 Logowanie

System automatycznie loguje całą komunikację z timestampami:

```
[23:51:47.123] TX: CFG(KP=2.5,KI=0.3,KD=1.2)|245
[23:51:47.156] RX: ACK
[23:51:50.001] TX: TEST_START|245
[23:51:50.023] RX: ACK|TEST_MODE_ON
```

Zapisz log komendą `save-log` do pliku.

## 🤝 Rozwój projektu

Aby przyczynić się do rozwoju:
1. Fork repozytorium
2. Stwórz branch: `git checkout -b feature/nowa-funkcja`
3. Commit zmian: `git commit -am 'Dodaj nową funkcję'`
4. Push: `git push origin feature/nowa-funkcja`
5. Otwórz Pull Request

## 📄 Licencja

Projekt stworzony na potrzeby edukacyjne.

## 👤 Autor

**KieltRadek**
- GitHub: [@KieltRadek](https://github.com/KieltRadek)

## 🙏 Podziękowania

Projekt powstał jako demonstracja zastosowania regulatora PID w systemach embedded.

---

**Ostatnia aktualizacja**: 2025-11-24