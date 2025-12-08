# ✅ PODSUMOWANIE - Line Follower z Bluetooth

## 🎉 Twoja konfiguracja jest GOTOWA!

Wszystko co potrzebujesz do uruchomienia robota:

### 📦 Pliki

| Plik | Przeznaczenie |
|------|--------------|
| `LineFollowerPID.ino` | Kod Arduino (wgraj do Arduino IDE) |
| `ArduinoRobotPython.py` | Interfejs Python (uruchamiaj na PC) |
| `QuickStart_Bluetooth.md` | **← START TUTAJ** (5 minut) |
| `Bluetooth_Setup_Guide.md` | Szczegółowa konfiguracja |
| `Bluetooth_Diagnostics.md` | Rozwiązywanie problemów |
| `README_LineFollower.md` | Pełna dokumentacja |
| `PID_Configurations.md` | Gotowe konfiguracje PID |
| `Command_Reference.md` | Wszystkie komendy |

### 🔧 Sprzęt - masz już

✅ Arduino + Akumulator  
✅ Moduł Bluetooth HC-05 (zmontowany na TX1/RX0)  
✅ Tracker TRSensors (5 czujników)  
✅ Silniki + Mostek H  
✅ Enkodery (opcjonalnie)  

### 🚀 Co teraz zrobić

**Zamiast USB → Bluetooth:**

```
Stara metoda:
  Arduino --USB--> Komputer

Nowa metoda (Twoja):
  Arduino --Bluetooth--> PC
  Zasilanie: Akumulator (bateryjnie)
```

## ⚡ SZYBKIE URUCHOMIENIE (jeśli masz doświadczenie)

```bash
# 1. Włącz Arduino (akumulator)
# 2. Sparuj HC-05 w Windows (PIN: 1234)
# 3. Uruchom program
python ArduinoRobotPython.py

# 4. Wybierz HC-05 port (COM4 lub wyżej)
# 5. Zapamiętaj komendy
robot> calibrate           # Kalibruj
robot> kp 20; kd 5; vref 100  # PID
robot> P                   # START
```

## 📚 DOKUMENTACJA PO PORZĄDKU

1. **Zaczynasz?** → `QuickStart_Bluetooth.md` (5 min)
2. **Potrzebujesz help?** → `Bluetooth_Diagnostics.md`
3. **Chcesz zrozumieć?** → `README_LineFollower.md`
4. **Szukasz komendy?** → `Command_Reference.md`
5. **Stroiłeś PID?** → `PID_Configurations.md`
6. **Problemy z HW?** → `Wiring_Diagram.md`

## 🎮 GŁÓWNE KOMENDY

| Komenda | Efekt |
|---------|-------|
| `calibrate` | Kalibruj tracker (przesuwaj nad linią) |
| `kp 20` `kd 5` | Ustaw parametry PID |
| `vref 100` | Ustaw prędkość (0-255) |
| `P` | **START** - robot jedzie po linii |
| `S` | **STOP** - zatrzymaj robota |
| `telemetry-on` | Włącz monitoring (zobacz co się dzieje) |
| `status` | Sprawdź parametry |
| `help` | Pełna lista komend |

## 🔴 JEŚli coś nie działa

**Połączenie Bluetooth:**
- [ ] Arduino ma zasilanie (LED świeci)?
- [ ] HC-05 ma zasilanie (LED świeci)?
- [ ] HC-05 sparowany w Windows?
- [ ] Port COM widoczny w programie?

→ Jeśli coś nie, patrz: `Bluetooth_Diagnostics.md`

**Robot nie reaguje:**
```
robot> status              # Czy Arduino odpowiada?
robot> read-line           # Czy tracker widzi linię?
robot> calibrate           # Przesuwaj nad linią
robot> kp 25; kd 5; P      # Zwiększ Kp, spróbuj
```

**Robot oscyluje:**
```
robot> kp 15               # Zmniejsz Kp
robot> kd 8                # Zwiększ Kd
robot> t 120               # Zwiększ okres próbkowania
robot> P                   # Spróbuj
```

## 📊 PRZEWIDYWANE PARAMETRY PID

Dla standardowego toru:
```
Kp = 20-25 (reaktywność)
Ki = 0-0.1 (eliminacja offsetu)
Kd = 5-8   (stabilizacja)
Vref = 90-120 (prędkość PWM)
T = 80-100 (okres próbkowania ms)
```

Dostrajaj metodą *trial & error*:
1. Start z małymi wartościami (Kp=15, Kd=3)
2. Zwiększaj Kp aż robot będzie oscylować
3. Zwiększaj Kd aż oscylacje znikną
4. Dodaj Ki jeśli robot ma offset

## 🧪 TEST DIAGNOSTYCZNY

```bash
python TestSuite.py
# Automatycznie sprawdzi wszystko
# Wygeneruje raport: test_report_*.txt
```

## 📋 PRZED PIERWSZYM TESTEM

- [ ] Tracker skalibrowany (`robot> calibrate`)
- [ ] Parametry PID ustawione (zaczynaj od: `kp 15; kd 3`)
- [ ] Vref nie za wysoki (zacznij od 80)
- [ ] Telemetria włączona (`robot> telemetry-on`)
- [ ] Tor przygotowany (czarna linia na białym tle)
- [ ] Nie ma przeszkód w drodze robota

## 🎯 CELE DO OSIĄGNIĘCIA

1. ✅ Robot jedzie po prostej linii
2. ✅ Robot pokonuje łagodne zakręty
3. ✅ Robot pokonuje ostre zakręty (zygzak)
4. ✅ Robot jedzie szybko bez upadku z toru
5. ✅ Strojenie PID w locie (bez resetu)

## 🔐 WAŻNE UWAGI

⚠️ **SONAR MUSI BYĆ WYŁĄCZONY** - interferuje z trackerem!

⚠️ **Bluetooth XOR USB** - nie testuj jednocześnie:
- Albo tylko Bluetooth (z akumulatorem)
- Albo tylko USB (do debugowania)

⚠️ **Okres próbkowania** - 50-300ms:
- Za krótki (50ms) = szum, oscylacje
- Za długi (300ms) = ospała jazda
- Domyślnie: 100ms

⚠️ **Dead-zone** - MIN_PWM = 30:
- Silniki nie ruszą przy PWM < 30
- To jest normalne, kompensuj Vref

## 📞 SZYBKIE SOS

| Problem | Komenda |
|---------|---------|
| Brak połączenia | Sparuj HC-05 w Windows |
| Timeout | Wciśnij reset na Arduino |
| Robot nie reaguje | `robot> calibrate` |
| Oscylacje | `robot> kp 15; kd 8` |
| Wolna jaad | `robot> vref 120` |
| Zguba linii | `robot> vref 90; kp 25` |

## 🚗 GOTOWY?

```
1. python ArduinoRobotPython.py
2. robot> calibrate
3. robot> telemetry-on
4. robot> kp 20; kd 5; vref 100
5. robot> P
6. 🎉 JAZZ!
```

---

## 📖 Gdzie znaleźć odpowiedź

| Pytanie | Plik |
|---------|------|
| Jak uruchomić? | QuickStart_Bluetooth.md |
| Jak sparować? | Bluetooth_Setup_Guide.md |
| Coś nie działa | Bluetooth_Diagnostics.md |
| Jakie są komendy? | Command_Reference.md |
| Jak stroić PID? | PID_Configurations.md |
| Jak podłączyć? | Wiring_Diagram.md |
| Wszystko o systemie | README_LineFollower.md |
| Zaawansowane | Technical_Notes.md |

---

## 🎓 Teoria (jeśli interesuje)

**Podstawy PID:**
- **P (proporcjonalny)** - szybka reakcja na błąd
- **I (całkujący)** - eliminuje błąd ustalony
- **D (różniczkujący)** - tłumi oscylacje

**Twoja implementacja:**
- Filtr D (redukcja szumu)
- Anty-windup (limit całki)
- Dead-zone kompensacja
- Nieblokująca architektura (brak delay!)

---

**Powodzenia w projekcie!** 🏆

Wszystkie pliki są w jednym katalogu: `/ISS/`

Pytania? Patrz odpowiednie dokumenty wyżej. 📚
