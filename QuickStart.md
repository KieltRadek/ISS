# Quick Start Guide - Line Follower Robot

## 🚀 Start w 5 minut!

### Krok 1: Przygotowanie sprzętu ⚙️

1. **Podłącz komponenty** zgodnie z pinami w `LineFollowerPID.ino`
2. **WYŁĄCZ SONAR** - interferuje z trackerem!
3. **Sprawdź baterie** - pełne naładowanie

### Krok 2: Upload kodu 📤

```
1. Otwórz Arduino IDE
2. Zainstaluj bibliotekę TRSensors (Sketch → Include Library → Add .ZIP)
3. Otwórz LineFollowerPID.ino
4. Upload do Arduino
```

### Krok 3: Uruchom interfejs Python 🐍

```bash
python ArduinoRobotPython.py
```

**LUB** dla szybkich testów:

```bash
python QuickPIDConfig.py
```

### Krok 4: Podstawowa konfiguracja 🎯

W interfejsie Python:

```
robot> calibrate
```
*Podczas kalibracji przesuwaj robota nad linią (lewo-prawo)*

```
robot> kp 20
robot> ki 0
robot> kd 5
robot> vref 100
robot> t 100
```

### Krok 5: TEST! 🏁

```
robot> P
```

**Robot jedzie!** 🎉

---

## ⚡ Szybkie poprawki

### Problem: Robot nie reaguje
```
robot> status         # Sprawdź parametry
robot> read-line      # Sprawdź czy widzi linię
robot> calibrate      # Ponowna kalibracja
```

### Problem: Robot oscyluje
```
robot> kp 15          # Zmniejsz Kp
robot> kd 8           # Zwiększ Kd
```

### Problem: Za wolny
```
robot> vref 120       # Zwiększ prędkość
```

### Problem: Traci linię na zakrętach
```
robot> vref 90        # Zmniejsz prędkość
robot> kp 25          # Zwiększ reaktywność
```

---

## 📊 Monitoring

Włącz telemetrię by widzieć co się dzieje:

```
robot> telemetry-on
robot> P
```

Zobaczysz:
```
POS:2050 ERR:0.025 OUT:0.5 L:99 R:100 ENC_L:10 ENC_R:11
```

---

## 🎮 Podstawowe komendy

| Komenda | Co robi |
|---------|---------|
| `P` | ▶️ Start |
| `S` | ⏹️ Stop |
| `kp 20` | Ustaw Kp |
| `ki 0.1` | Ustaw Ki |
| `kd 5` | Ustaw Kd |
| `vref 100` | Ustaw prędkość |
| `status` | Sprawdź status |
| `help` | Pełna pomoc |

---

## 📝 Gotowe konfiguracje

Użyj `QuickPIDConfig.py` dla:

1. **Bezpieczny Start** - Naucz się sterowania
2. **Łagodne Zakręty** - Standardowy tor
3. **Ostre Zakręty** - Zygzak
4. **Wysoka Prędkość** - Proste tory
5. **Tor Mieszany** - Uniwersalne

---

## 🎓 Nauka PID w 3 krokach

### 1. Tylko P (proporcjonalny)
```
robot> kp 10
robot> ki 0
robot> kd 0
robot> P
```
Zwiększaj `kp` aż robot zacznie oscylować.

### 2. Dodaj D (różniczkujący)
```
robot> kd 5
```
Zwiększaj `kd` aż oscylacje znikną.

### 3. Opcjonalnie I (całkujący)
```
robot> ki 0.1
```
Tylko jeśli robot ma stały offset.

---

## ✅ Checklist przed testem

- [ ] Biblioteka TRSensors zainstalowana
- [ ] Kod wgrany na Arduino
- [ ] Baterie naładowane
- [ ] Sonar wyłączony
- [ ] Tracker skalibrowany
- [ ] Tor przygotowany (czarna linia na białym tle)
- [ ] Interfejs Python połączony
- [ ] Parametry PID ustawione

---

## 🆘 Pomoc

- **Pełna dokumentacja:** `README_LineFollower.md`
- **Gotowe konfiguracje:** `PID_Configurations.md`
- **Notatki techniczne:** `Technical_Notes.md`
- **Błędy?** Wpisz `help` w interfejsie

---

**POWODZENIA!** 🏆
