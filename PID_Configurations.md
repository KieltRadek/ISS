# Przykładowe konfiguracje PID dla Line Follower

## Scenariusz 1: Tor prosty (bezpieczny start)

Dobry punkt startowy do pierwszych testów.

```
kp 15
ki 0
kd 3
vref 80
t 100
```

**Charakterystyka:**
- Powolna, stabilna jazda
- Minimalne oscylacje
- Dobre do nauki i debugowania

---

## Scenariusz 2: Tor z łagodnymi zakrętami

Zwiększona reaktywność przy zachowaniu stabilności.

```
kp 20
ki 0
kd 5
vref 100
t 100
```

**Charakterystyka:**
- Średnia prędkość
- Dobra reakcja na zakręty
- Zbalansowane sterowanie

---

## Scenariusz 3: Tor z ostrymi zakrętami (zygzak)

Agresywne sterowanie dla trudnych tras.

```
kp 30
ki 0.2
kd 8
vref 90
t 80
```

**Charakterystyka:**
- Szybka reakcja na zmiany
- Składnik Ki kompensuje błąd w zakrętach
- Krótszy okres próbkowania dla lepszej reaktywności

---

## Scenariusz 4: Wysoka prędkość (tor prosty)

Maksymalizacja prędkości na prostych odcinkach.

```
kp 25
ki 0
kd 10
vref 140
t 80
```

**Charakterystyka:**
- Wysoka prędkość bazowa
- Silne tłumienie (Kd) zapobiega oscylacjom
- Szybkie próbkowanie

---

## Scenariusz 5: Tor mieszany (optymalizacja ogólna)

Kompromis między prędkością a stabilnością.

```
kp 22
ki 0.1
kd 6
vref 110
t 100
```

**Charakterystyka:**
- Uniwersalne ustawienia
- Mała wartość Ki dla długoterminowej stabilności
- Dobry punkt startowy do dalszej optymalizacji

---

## Scenariusz 6: Tor z przerwami (luki w linii)

Silny składnik całkujący utrzymuje kierunek.

```
kp 20
ki 0.5
kd 5
vref 100
t 120
```

**Charakterystyka:**
- Silny Ki "pamięta" kierunek
- Wolniejsze próbkowanie zmniejsza szum
- Utrzymuje tor przy krótkich przerwach

---

## Proces strojenia (Workflow)

### Krok 1: Tylko P (proporcjonalny)
```
kp 10
ki 0
kd 0
vref 80
```
Stopniowo zwiększaj Kp aż robot zacznie oscylować.

### Krok 2: Dodaj D (różniczkujący)
```
kp 20   # Wartość przy której zaczęły się oscylacje
ki 0
kd 5    # Start: Kd = Kp / 4
vref 80
```
Zwiększaj Kd aż oscylacje znikną.

### Krok 3: Opcjonalnie dodaj I (całkujący)
```
kp 20
ki 0.1  # Start: Ki = 0.1 * Kp (bardzo małe!)
kd 5
vref 80
```
Dodaj tylko jeśli robot ma stały offset od linii.

### Krok 4: Optymalizacja prędkości
```
kp 20
ki 0
kd 5
vref 100  # Stopniowo zwiększaj
```
Zwiększaj Vref dopóki robot nie straci kontroli, potem cofnij 10-20%.

### Krok 5: Optymalizacja czasu próbkowania
```
kp 20
ki 0
kd 5
vref 100
t 80   # Zmniejsz jeśli robot reaguje zbyt wolno
```
Zmniejszaj T jeśli potrzebujesz szybszej reakcji (ale uwaga na szum!).

---

## Diagnostyka problemów

### Problem: Robot reaguje zbyt wolno na zakręty

**Rozwiązanie:**
```bash
robot> kp 25      # Zwiększ Kp o 20-30%
robot> t 80       # Zmniejsz okres próbkowania
```

### Problem: Robot oscyluje wokół linii

**Rozwiązanie:**
```bash
robot> kp 18      # Zmniejsz Kp o 20%
robot> kd 8       # Zwiększ Kd o 30-50%
```

### Problem: Robot ma stały offset (jedzie obok linii)

**Rozwiązanie:**
```bash
robot> ki 0.2     # Dodaj składnik całkujący
```

### Problem: Robot trzęsie się / szarpie

**Rozwiązanie:**
```bash
robot> kd 4       # Zmniejsz Kd
robot> t 120      # Wydłuż okres próbkowania
```
Ewentualnie w kodzie: zmniejsz `alpha` (mocniejsze filtrowanie D).

### Problem: Robot traci linię na ostrych zakrętach

**Rozwiązanie:**
```bash
robot> kp 30      # Zwiększ reaktywność
robot> vref 90    # Zmniejsz prędkość bazową
robot> t 80       # Szybsze próbkowanie
```

### Problem: Robot wylatuje na prostych (za szybko)

**Rozwiązanie:**
```bash
robot> vref 90    # Zmniejsz prędkość
robot> kd 10      # Zwiększ tłumienie
```

---

## Zaawansowane techniki

### 1. Adaptacyjne Vref (w kodzie)

Zmniejszaj prędkość bazową proporcjonalnie do błędu:
```cpp
int adaptiveVref = Vref * (1.0 - abs(error) * 0.3);
```

### 2. Selektywne Ki (w kodzie)

Aktywuj Ki tylko gdy błąd jest mały (redukuje windup):
```cpp
if (abs(error) < 0.2) {
  integral += error * dt;
}
```

### 3. Nieliniowe Kp (w kodzie)

Silniejsza reakcja na duże błędy:
```cpp
float adaptiveKp = Kp * (1.0 + abs(error) * 0.5);
```

---

## Sekwencja testowa

### Test 1: Podstawowa stabilność
```
1. Kalibracja trackera
2. Ustaw scenariusz 1 (bezpieczny start)
3. robot> P
4. Obserwuj czy robot utrzymuje linię przez 30s
```

### Test 2: Odporność na zakręty
```
1. Ustaw scenariusz 2 (łagodne zakręty)
2. Test na torze z 90° zakrętami
3. Zwiększaj Kp/Kd jeśli traci linię
```

### Test 3: Maksymalna prędkość
```
1. Ustaw scenariusz 4 (wysoka prędkość)
2. Stopniowo zwiększaj Vref
3. Znajdź maksymalną prędkość dla stabilnej jazdy
```

### Test 4: Egzamin (ciągły przejazd)
```
1. Najlepsze ustawienia z testów 1-3
2. robot> telemetry-on
3. robot> P
4. Mierz najdłuższy dystans bez błędu
5. robot> save-log (zapisz wynik)
```

---

## Notatki

- Zawsze rozpoczynaj od scenariusza 1
- Zmieniaj JEDEN parametr na raz
- Zapisuj działające konfiguracje (save-log)
- Telemetria to klucz do zrozumienia zachowania
- W razie wątpliwości: zmniejsz prędkość, zwiększ stabilność

---

## Quick Reference

| Parametr | Typowy zakres | Efekt zwiększenia |
|----------|---------------|-------------------|
| Kp | 10-40 | Szybsza reakcja, więcej oscylacji |
| Ki | 0-1 | Usuwa offset, może niestabilizować |
| Kd | 3-15 | Tłumi oscylacje, łagodzi ruch |
| Vref | 60-150 | Wyższa prędkość, mniej kontroli |
| T | 50-300 | Szybsza reakcja, więcej szumu |

**Złota zasada:** Start conservatively, optimize gradually!
