# Robot jadący po linii z regulatorem PID

## Opis projektu

Robot różnicowy wyposażony w listwę czujników odbiciowych (tracker), który samodzielnie jedzie po wyznaczonej linii. Sterowanie realizuje regulator PID, którego parametry można stroić w czasie rzeczywistym przez interfejs szeregowy (Bluetooth/Serial). Implementacja w pełni nieblokująca - bez `delay()`.

## Wymagania sprzętowe

- **Robot różnicowy** z mostkiem H (sterowanie silnikami)
- **Listwa czujników odbiciowych** (tracker) - 5 czujników
- **Moduł Bluetooth** (opcjonalnie, do bezprzewodowej komunikacji)
- **Enkodery** (opcjonalnie, do telemetrii)
- **Arduino** (np. Uno, Nano)

### Podłączenie pinów (zgodnie z kodem)

```
Silnik lewy:
- PWM: pin 5
- Forward: A0
- Reverse: A1
- Enkoder: pin 2

Silnik prawy:
- PWM: pin 6
- Forward: A2
- Reverse: A3
- Enkoder: pin 3

Tracker:
- Biblioteka TRSensors (5 czujników)
```

## Instalacja biblioteki TRSensors

1. Pobierz plik `TRSensors.zip`
2. W Arduino IDE: `Sketch` → `Include Library` → `Add .ZIP Library...`
3. Wybierz pobrany plik ZIP

## Pliki projektu

- **`LineFollowerPID.ino`** - główny kod Arduino z regulatorem PID
- **`ArduinoRobotPython.py`** - interfejs Python do komunikacji i strojenia
- **`example_tracking.ino`** - przykładowy kod z podstawowym trackerem

## Algorytm PID

### Parametry regulatora

- **Kp** (proporcjonalny) - reakcja na bieżący błąd
- **Ki** (całkujący) - eliminacja błędu ustalonego
- **Kd** (różniczkujący) - tłumienie oscylacji

### Implementacja

```cpp
error = (pozycja_linii - 2000) / 2000.0  // Normalizacja do [-1, 1]
integral += error * dt
derivative = (error - previousError) / dt
derivative_filtered = alpha * derivative + (1-alpha) * derivative_filtered
output = Kp * error + Ki * integral + Kd * derivative_filtered
```

### Sterowanie różnicowe

```cpp
PWM_lewy = Vref - output
PWM_prawy = Vref + output
```

### Zabezpieczenia

- **Anty-windup** - ograniczenie całki (MAX_INTEGRAL)
- **Filtr dolnoprzepustowy** dla składnika D (redukcja szumu)
- **Dead-zone kompensacja** (MIN_PWM = 30)
- **Ograniczenia PWM** (0-255)

## Komunikacja (Protokół z Projektu 1)

### Format ramki
```
KOMENDA|CHECKSUM#
```

Checksum = suma ASCII znaków komendy % 256

### Komendy sterowania

| Komenda | Opis | Przykład |
|---------|------|----------|
| `P` | Włącz tryb jazdy po linii | `P\|80#` |
| `S` | Zatrzymaj robota | `S\|83#` |
| `Kp <val>` | Ustaw parametr Kp | `Kp 20\|xxx#` |
| `Ki <val>` | Ustaw parametr Ki | `Ki 0.5\|xxx#` |
| `Kd <val>` | Ustaw parametr Kd | `Kd 5\|xxx#` |
| `Vref <val>` | Ustaw prędkość bazową (0-255) | `Vref 100\|xxx#` |
| `T <ms>` | Ustaw okres próbkowania (50-300) | `T 100\|xxx#` |

### Komendy diagnostyczne

| Komenda | Opis |
|---------|------|
| `CALIBRATE` | Kalibracja trackera |
| `READ_LINE` | Odczyt pozycji linii (0-4000) |
| `STATUS` | Odczyt wszystkich parametrów |
| `TELEMETRY_ON` | Włącz telemetrię |
| `TELEMETRY_OFF` | Wyłącz telemetrię |
| `PING` | Test połączenia |

### Odpowiedzi

```
ACK|dane#           - Sukces
NACK|błąd#          - Błąd
POS:xxx ERR:yyy...  - Telemetria (bez #)
```

## Użycie interfejsu Python

### Uruchomienie

```bash
python ArduinoRobotPython.py
```

### Podstawowy workflow

1. **Wybór portu** - wybierz COM port Arduino/Bluetooth
2. **Kalibracja trackera**:
   ```
   robot> calibrate
   ```
   Podczas kalibracji przesuwaj robota nad linią (w lewo i w prawo)

3. **Ustawienie parametrów** (przykładowe wartości startowe):
   ```
   robot> kp 20
   robot> ki 0
   robot> kd 5
   robot> vref 100
   robot> t 100
   ```

4. **Uruchomienie jazdy**:
   ```
   robot> P
   ```

5. **Strojenie w czasie rzeczywistym**:
   ```
   robot> kp 25      # Zwiększ reakcję
   robot> kd 8       # Zwiększ tłumienie
   robot> telemetry-on  # Zobacz co się dzieje
   ```

6. **Zatrzymanie**:
   ```
   robot> S
   ```

### Dostępne komendy w interfejsie

```
p                - Włącz tryb jazdy
s                - Zatrzymaj
kp <val>         - Ustaw Kp
ki <val>         - Ustaw Ki
kd <val>         - Ustaw Kd
vref <val>       - Ustaw prędkość bazową
t <ms>           - Ustaw okres próbkowania
calibrate        - Kalibruj tracker
read-line        - Odczyt pozycji
status           - Status i parametry
telemetry-on     - Włącz monitoring
telemetry-off    - Wyłącz monitoring
monitor [s]      - Monitor telemetrii
help             - Pomoc
quit             - Wyjście
```

## Strojenie regulatora PID

### Metoda Zieglera-Nicholsa (uproszczona)

1. **Rozpocznij z Kp=0, Ki=0, Kd=0**
2. **Zwiększaj Kp** aż robot zacznie oscylować wokół linii
   - Za małe Kp → robot reaguje zbyt wolno
   - Za duże Kp → oscylacje
3. **Dodaj Kd** aby stłumić oscylacje
   - Start: Kd = Kp / 4
   - Zwiększaj aż oscylacje znikną
4. **Opcjonalnie dodaj Ki** jeśli robot ma stały błąd
   - Ki usuwa błąd ustalony (offset)
   - Start: Ki = 0.1 * Kp
   - Uważaj: za duże Ki → niestabilność

### Przykładowe wartości startowe

```
Kp = 20.0
Ki = 0.0
Kd = 5.0
Vref = 100 (40% mocy)
T_sample = 100 ms
```

### Obserwacje podczas strojenia

| Objaw | Przyczyna | Rozwiązanie |
|-------|-----------|-------------|
| Robot reaguje wolno | Za małe Kp | Zwiększ Kp |
| Oscylacje wokół linii | Za duże Kp | Zmniejsz Kp, zwiększ Kd |
| Trzęsienie/szarpanie | Szum w D | Zwiększ filtr (zmniejsz alpha) |
| Stały offset od linii | Brak Ki | Dodaj małe Ki |
| Niestabilność | Za duże Ki | Zmniejsz Ki |

## Telemetria

Format telemetrii (gdy włączona):
```
POS:2150 ERR:0.075 OUT:1.5 L:98 R:101 ENC_L:12 ENC_R:13
```

- **POS** - pozycja linii (0-4000, środek=2000)
- **ERR** - błąd znormalizowany (-1.0 do 1.0)
- **OUT** - wyjście regulatora PID
- **L/R** - PWM lewego/prawego silnika
- **ENC_L/R** - liczba impulsów enkoderów

## Parametry konfiguracyjne

### W kodzie Arduino

```cpp
#define SERIAL_BAUD_RATE 9600
#define NUM_SENSORS 5
#define MAX_INTEGRAL 1000.0    // Limit anty-windup
#define MIN_PWM 30             // Dead-zone kompensacja
#define MAX_PWM 255            // Max PWM
#define TELEMETRY_INTERVAL 200 // Co ile ms wysyłać telemetrię

float alpha = 0.7;  // Filtr D (0-1), mniejszy = mocniejsze filtrowanie
```

### Zmienialne w runtime

- `Kp`, `Ki`, `Kd` - parametry PID
- `Vref` - prędkość bazowa (0-255)
- `T_sample` - okres próbkowania (50-300 ms)

## Rozwiązywanie problemów

### Robot nie reaguje na linię
- Sprawdź kalibrację: `robot> calibrate`
- Upewnij się że tryb jest włączony: `robot> P`
- Sprawdź pozycję linii: `robot> read-line`

### Robot oscyluje
- Zmniejsz Kp
- Zwiększ Kd
- Zwiększ filtrowanie (zmniejsz alpha w kodzie)

### Robot jedzie zbyt wolno
- Zwiększ Vref: `robot> vref 120`
- Sprawdź czy nie ma martwej strefy (MIN_PWM)

### Komunikacja nie działa
- Sprawdź baudrate (9600)
- Sprawdź format ramek (komenda|checksum#)
- Użyj: `robot> status` aby przetestować

### Sonar interferuje z trackerem
- **WYŁĄCZ SONAR!** (wymagane dla poprawnej pracy trackera)

## Schemat działania pętli głównej

```
loop() {
  // 1. Nieblokująca komunikacja
  if (Serial.available()) {
    parsuj_komendy();
  }
  
  // 2. Nieblokująca pętla PID (co T_sample ms)
  if (lineFollowMode && time_elapsed >= T_sample) {
    pozycja = odczytaj_tracker();
    błąd = oblicz_błąd(pozycja);
    wyjście = PID(błąd);
    ustaw_silniki(Vref - wyjście, Vref + wyjście);
  }
}
```

## Testy i ocena

Robot oceniany jest na podstawie najdłuższego odcinka pokonanego bez wyjechania poza tor.

### Przygotowanie do testu

1. Kalibracja trackera na torze testowym
2. Strojenie PID na prostych odcinkach
3. Optymalizacja dla zakrętów
4. Test na zygzaku
5. Dostrojenie końcowe

### Wskazówki

- Zacznij od niskich prędkości (Vref=80-100)
- Najpierw opanuj proste, potem zakręty
- Używaj telemetrii do debugowania
- Zapisuj logi udanych konfiguracji
- Testuj różne okresy próbkowania

## Licencja

Kod zgodny z wymaganiami projektu ISS.

## Autor

Projekt studencki - Inteligentne Systemy Sterowania
