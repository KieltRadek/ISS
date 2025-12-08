# Diagnostyka Bluetooth - Line Follower

## 🔍 Szybka diagnoza

Jeśli coś nie działa - przejdź przez tę tabelę od góry do dołu.

### ETAP 1: Sprzęt

| ✓/✗ | Co sprawdzić | Pytanie | Tak → | Nie → |
|-----|-------------|--------|-------|-------|
| - | **ZASILANIE** | Arduino ma zasilanie? | 2 | Podłącz baterię |
| - | **BLUETOOTH** | LED na HC-05 świeci? | 2 | Sprawdź zasilanie HC-05 |
| - | **LED HC-05** | LED **ciągle** świeci (nie miga)? | 3 | Sparuj HC-05 (patrz niżej) |

**Jak spaarować HC-05:**
```
Windows: Ustawienia → Bluetooth → Dodaj → HC-05 → PIN: 1234
```

### ETAP 2: Windows Bluetooth

| ✓/✗ | Co sprawdzić | Pytanie | Tak → | Nie → |
|-----|-------------|--------|-------|-------|
| - | **DISCOVERY** | HC-05 widać w Bluetooth? | 3 | Wciśnij reset na HC-05 |
| - | **PAIRING** | HC-05 jest "sparowany"? | 3 | Spaaruj (PIN 1234 lub 0000) |
| - | **COM PORT** | W Menedżerze urządzeń widzisz COM port? | 4 | Problem z driverem |

**Gdzie sprawdzić COM port:**
```
Menedżer urządzeń (Device Manager) 
→ Ports (COM & LPT) 
→ HC-05 powinna być listą (np. "COM4")
```

### ETAP 3: Program Python

| ✓/✗ | Co sprawdzić | Pytanie | Tak → | Nie → |
|-----|-------------|--------|-------|-------|
| - | **PYTHON** | Masz zainstalowany Python? | 4 | `pip install python` |
| - | **PYSERIAL** | Masz bibliotekę pyserial? | 4 | `pip install pyserial` |
| - | **PROGRAM** | Uruchomiłeś `python ArduinoRobotPython.py`? | 4 | Uruchom program |
| - | **PORTY** | Program pokazuje COM porty? | 5 | Problem z system-path |
| - | **TY PORT** | Widzisz HC-05 COM port w liście? | 5 | Sprawdź Menedżer urządzeń |

### ETAP 4: Połączenie

| ✓/✗ | Co sprawdzić | Pytanie | Tak → | Nie → |
|-----|-------------|--------|-------|-------|
| - | **WYBÓR PORTU** | Wybrałeś prawidłowy COM port? | 5 | Wybierz HC-05 port |
| - | **BAUDRATE** | Wpisałeś 9600? | 5 | Wpisz 9600 (Enter) |
| - | **POŁĄCZENIE** | Widzisz "✅ Połączono!"? | 6 | Patrz: **Problem A** |
| - | **WATCHDOG** | Widzisz "Watchdog: Połączenie aktywne"? | 6 | Patrz: **Problem B** |

### ETAP 5: Arduino

| ✓/✗ | Co sprawdzić | Pytanie | Tak → | Nie → |
|-----|-------------|--------|-------|-------|
| - | **STATUS** | Wpisz: `robot> status` | 6 | Patrz: **Problem B** |
| - | **ODPOWIEDŹ** | Widzisz "Parametry: ACK|..."? | 6 | Patrz: **Problem B** |
| - | **KALIBRACJA** | Wpisz: `robot> calibrate` | 6 | Patrz: **Problem C** |
| - | **PING** | Program odpowiada? | 7 | Arduino nie odpowiada |

### ETAP 6: Funkcjonalność

| ✓/✗ | Co sprawdzić | Pytanie | Tak → | Nie → |
|-----|-------------|--------|-------|-------|
| - | **READ-LINE** | Wpisz: `robot> read-line` | 7 | Problem z trackerem |
| - | **WYNIK** | Widzisz "Pozycja linii: ACK\|POS:xxxx"? | 7 | Tracker nie działa |
| - | **WARTOŚĆ** | Czy wartość zmienia się (0-4000)? | 7 | Sprawdzaj tracker |
| - | **PRZESUNIĘCIE** | Czy zmienia się jak przesuwasz robota? | 7 | Tracker nie kalibrowany |

### ETAP 7: Gotowy do testów!

```
robot> calibrate          # Przesuwaj nad linią
robot> kp 20; kd 5        # Ustaw PID
robot> vref 100           # Prędkość
robot> telemetry-on       # Włącz monitoring
robot> P                  # START!
```

---

## 🔴 PROBLEMY I ROZWIĄZANIA

### Problem A: Timeout - brak połączenia

**Symptomy:**
```
Timeout (próba 1/3)
Timeout (próba 2/3)
Timeout (próba 3/3)
Brak odpowiedzi
```

**Przyczyny i rozwiązania:**

1. **Arduino nie ma zasilania**
   ```
   ✓ Sprawdzić: Czy bateria jest włączona?
   ✓ Wciśnij reset na Arduino
   ✓ Czekaj 2 sekundy
   ✓ Spróbuj ponownie
   ```

2. **Zły COM port**
   ```
   ✓ Spróbuj inne COM (COM3, COM5, COM6...)
   ✓ Sprawdź Menedżer urządzeń
   ✓ HC-05 powinien mieć 2 COM porty (RX i TX)
   ```

3. **HC-05 nie ma zasilania lub nie sparowany**
   ```
   ✓ Sprawdź czy LED na HC-05 świeci
   ✓ Sparuj HC-05 w Ustawieniach Windows
   ✓ Wciśnij reset na Arduino
   ```

4. **Zły baudrate**
   ```
   ✓ Domyślnie: 9600
   ✓ Spróbuj: 38400 jeśli zmieniano
   ✓ Sprawdź dokumentację HC-05
   ```

**Krok po kroku:**
```
1. Wyłącz program (Ctrl+C)
2. Sprawdź zasilanie Arduino (LED powinien świecić)
3. Sprawdź HC-05 (LED powinien świecić)
4. Sparuj HC-05 w Windows jeszcze raz
5. Wciśnij reset na Arduino
6. Uruchom program ponownie
7. Wybierz inny COM port jeśli potrzeba
```

---

### Problem B: Połączenie OK, ale Arduino nie odpowiada

**Symptomy:**
```
✓ Połączono
Watchdog: Brak odpowiedzi
```

**Przyczyny:**

1. **Zła kalibracja trackera**
   ```
   ✓ Wpisz: robot> calibrate
   ✓ Przesuwaj robota nad linią 3 sekundy
   ✓ Spróbuj ponownie: robot> status
   ```

2. **Arduino "zawisło"**
   ```
   ✓ Wciśnij reset na Arduino
   ✓ Czekaj 2 sekundy
   ✓ Uruchom program Python ponownie
   ```

3. **Moduł nie reaguje (delay w Arduino IDE)**
   ```
   ✓ Upewnij się że nie ma delay() w loop()
   ✓ Sprawdź czy wgrałeś prawidłowy kod (LineFollowerPID.ino)
   ✓ Przywróć fabryczne ustawienia Arduino
   ```

4. **Konflikt USB + Bluetooth**
   ```
   ✓ Jeśli Arduino jest podłączone USB i Bluetooth:
   ✓ Odłącz USB, testuj tylko przez Bluetooth
   ✓ Lub: odłącz HC-05, testuj przez USB
   ```

**Rozwiązanie:**
```
1. Wciśnij reset na Arduino (guzik RST)
2. Czekaj 2 sekundy
3. Uruchom program Python: python ArduinoRobotPython.py
4. Wpisz: robot> status
5. Jeśli dalej nie działa → wgraj kod ponownie
```

---

### Problem C: Kalibracja się zawiesza

**Symptomy:**
```
robot> calibrate
(czeka długo, nic się nie dzieje...)
```

**Przyczyna:**
```
Arduino używa delay(10) w calibrate()
To jest jedyne wyjątek (kalibracja wymaga czasu)
Czekaj 10-15 sekund!
```

**Rozwiązanie:**
```
1. Nie przerywaj (Ctrl+C)!
2. Przesuwaj robota nad linią
3. Czekaj aż się skończy
4. Powinno być "✅ Kalibracja zakończona"
```

---

### Problem D: Robot się nie rusza

**Symptomy:**
```
robot> P
🚗 Tryb jazdy po linii WŁĄCZONY
(ale robot stoi w miejscu...)
```

**Przyczyny:**

1. **Tracker nie widzi linii**
   ```
   ✓ Wpisz: robot> read-line
   ✓ Powinna być wartość 0-4000
   ✓ Jeśli 0 lub 4000 ciągle → brak linii!
   ✓ Sprawdź: czy linia jest wystarczająco czarna/biała?
   ✓ Sprawdź: czy tracker jest 1-3cm od powierzchni?
   ```

2. **Parametry PID za niskie**
   ```
   ✓ Wpisz: robot> kp 30 (zamiast 20)
   ✓ Wpisz: robot> vref 120 (zamiast 100)
   ✓ Spróbuj: robot> P
   ```

3. **Silniki nie działają**
   ```
   ✓ Sprawdzić fizycznie czy koła się obracają
   ✓ Jeśli nie → problem z mostkiem H lub silnikami
   ✓ Test: Spróbuj ręcznie obracać koła (czy się opuszczają?)
   ```

4. **Tracker skalibrowany źle**
   ```
   ✓ Wpisz: robot> calibrate
   ✓ Tym razem przesuwaj POWOLI nad linią (lewa-prawa-lewa)
   ✓ Trwaj 5-10 sekund
   ✓ Spróbuj: robot> P
   ```

**Rozwiązanie:**
```
1. robot> read-line        # Czy tracker widzi linię?
2. robot> calibrate        # Przesuwaj nad linią
3. robot> kp 30            # Zwiększ reaktywność
4. robot> vref 120         # Zwiększ prędkość
5. robot> telemetry-on     # Włącz monitoring
6. robot> P                # Spróbuj
```

---

### Problem E: Oscylacje / szarpanie

**Symptomy:**
```
robot> telemetry-on
POS:1800 → POS:2200 → POS:1800 → POS:2200 (oscylacja!)
```

**Rozwiązanie:**
```
robot> kp 15     # Zmniejsz reaktywność
robot> kd 8      # Zwiększ tłumienie
robot> t 120     # Zwiększ okres próbkowania (wolniej)
robot> P         # Spróbuj
```

---

## ✅ CHECKLIST DIAGNOSTYKI

- [ ] Arduino ma zasilanie z akumulatora (LED świeci)
- [ ] HC-05 ma zasilanie (LED świeci/miga)
- [ ] HC-05 sparowany w Windows
- [ ] Program Python uruchomiony
- [ ] Wybrany prawidłowy COM port (HC-05)
- [ ] Baudrate 9600
- [ ] `robot> status` pokazuje Parametry
- [ ] `robot> read-line` pokazuje 0-4000
- [ ] Tracker skalibrowany (`robot> calibrate`)
- [ ] Parametry PID ustawione (`robot> kp 20` itd.)
- [ ] Telemetria włączona (`robot> telemetry-on`)
- [ ] Robot reaguje (`robot> P` → ruchy)

---

## 📞 Ostatnia deska ratunku

Jeśli nic nie działa, spróbuj **Electrical Reset**:

```
1. Wyłącz zasilanie Arduino (akumulator)
2. Czekaj 5 sekund
3. Wyłącz zasilanie HC-05 (lub czekaj aż bateria wysiądzie)
4. Włącz zasilanie Arduino
5. Włącz HC-05
6. Czekaj aż LED będzie świecić stabilnie
7. Sparuj HC-05 w Windows jeszcze raz
8. Uruchom program Python
```

Jeśli to nie pomoże → **coś jest nie tak ze sprzętem**, sprawdź:
- Czy Arduino jest oryginalne (a nie clone)?
- Czy HC-05 ma prawidłowe zasilanie (3.3V na logice)?
- Czy dzielnik napięcia jest wbudowany w moduł HC-05?

---

**Powodzenia w debugowaniu!** 🔍✨
