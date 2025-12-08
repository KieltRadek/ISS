import serial
import serial.tools.list_ports
import time
from datetime import datetime

# Pip install pyserial

class RobotInterface:
    def __init__(self):
        self.ser = None
        self.log = []
        self.history = []
        self.timeout = 1.0
        self.max_retries = 3
        self.connected = False
        self.telemetry_enabled = False  
        
    def calculate_checksum(self, cmd):
        return sum(ord(c) for c in cmd) % 256
    
    def list_ports(self):
        ports = serial.tools.list_ports.comports()
        print("\n=== Dostępne porty szeregowe ===")
        for i, port in enumerate(ports, 1):
            print(f"{i}. {port.device} - {port.description}")
        return [p.device for p in ports]
    
    def connect(self, port, baudrate=9600):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=self.timeout)
            time.sleep(2)
            print(f"Połączono z {port} ({baudrate} baud)")
            self.connected = True
            self.watchdog_test()
            return True
        except Exception as e:
            print(f"Błąd połączenia: {e}")
            return False
    
    def watchdog_test(self):
        response = self.send_command("PING", retries=1)
        if response and "PONG" in response:
            print("Watchdog: Połączenie aktywne")
            return True
        else:
            print("Watchdog: Brak odpowiedzi")
            self.connected = False
            return False
        
    def send_command(self, cmd, retries=None):
        if not self.ser or not self.ser.is_open:
            print("Brak połączenia")
            return None
        
        retries = retries if retries is not None else self.max_retries
        checksum = self.calculate_checksum(cmd)
        frame = f"{cmd}|{checksum}#"
        
        for attempt in range(retries):
            try:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                
                self.ser.write(frame.encode())
                self.ser.flush()
                self.log_message(f"TX: {frame.strip('#')}")
                
                start = time.time()
                while (time.time() - start) < self.timeout:
                    if self.ser.in_waiting > 0:
                        line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                        if not line:
                            continue
                        # Telemetria (bez '#') – pokaż jeśli włączona i pomiń
                        if not line.endswith('#'):
                            if self.telemetry_enabled:
                                print(line)
                            continue
                        # Ramka z '#'
                        self.log_message(f"RX: {line.strip('#')}")
                        if line.startswith("ACK"):
                            return line.strip('#')
                        if line.startswith("NACK"):
                            print(line)
                            return None
                        print(f"[FRAME] {line}")
                    else:
                        time.sleep(0.01)
                
                print(f"Timeout (próba {attempt+1}/{retries})")
                time.sleep(0.1)
                    
            except Exception as e:
                print(f"Błąd komunikacji: {e}")
        
        print("Brak odpowiedzi po wszystkich próbach")
        return None
    
    
    def log_message(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log.append(f"[{timestamp}] {msg}")
    
    
    def configure(self, config_dict):
        cfg_str = ",".join([f"{k}={v}" for k, v in config_dict.items()])
        response = self.send_command(f"CFG({cfg_str})")
        if response:
            print(f"Konfiguracja zastosowana: {cfg_str}")
        return response
    
    def start_test_mode(self, auto_monitor=False, seconds=0):
        """Uruchomienie trybu testowego; od teraz telemetria leci ciągle aż do TEST_STOP."""
        response = self.send_command("TEST_START")
        if response:
            print("Tryb testowy uruchomiony")
            self.telemetry_enabled = True   # <— telemetria on
        return response
    
    def stop_test_mode(self):
        """Zatrzymanie trybu testowego"""
        response = self.send_command("TEST_STOP")
        if response:
            print("Tryb testowy zatrzymany")
            self.telemetry_enabled = False  # <— telemetria off
        return response
    
    def set_target(self, distance_cm):
        """Ustawienie punktu docelowego"""
        response = self.send_command(f"SET_TARGET({distance_cm})")
        if response:
            print(f"Target ustawiony na: {distance_cm} cm")
        return response
    
    def set_servo_zero(self, angle):
        """Ustawienie wartości zero serwomechanizmu"""
        response = self.send_command(f"SET_SERVO_ZERO({angle})")
        if response:
            print(f"Servo zero ustawione na: {angle} stopni")
        return response
    
    def get_status(self):
        """Odczyt parametrów z Arduino"""
        response = self.send_command("STATUS")
        if response:
            print(f"Parametry: {response}")
        return response
    
    def read_distance(self):
        """Jednorazowy pomiar odległości"""
        response = self.send_command("READ_DISTANCE")
        if response:
            print(f"Odległość: {response}")
        return response
    
    def start_exam_mode(self):
        """Uruchomienie trybu egzaminacyjnego"""
        response = self.send_command("EXAM_START")
        if response:
            print("Tryb egzaminacyjny uruchomiony")
            print("Oczekiwanie na wynik (13s)...")
            
            # Czekaj na RESULT przez max 15s
            start = time.time()
            while (time.time() - start) < 15:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if not line:
                        continue
                    if line.startswith("RESULT"):
                        print(f"\n {line.strip('#')}")
                        return line
                else:
                    time.sleep(0.01)
            print("Timeout - brak wyniku")
        return response

    def interactive_config(self):
        print("\n=== KONFIGURACJA ROBOTA ===")
        
        config = {}

        while True:
            distance = input("distance_point (cm) = ").strip()
            try:
                distance_val = float(distance)
                config['DIST_POINT'] = distance_val
                break
            except ValueError:
                print("Błąd: Wprowadź wartość liczbową")

        while True:
            kp = input("kp = ").strip()
            try:
                kp_val = float(kp)
                config['KP'] = kp_val
                break
            except ValueError:
                print("Błąd: Wprowadź wartość liczbową")

        while True:
            ki = input("ki = ").strip()
            try:
                ki_val = float(ki)
                config['KI'] = ki_val
                break
            except ValueError:
                print("Błąd: Wprowadź wartość liczbową")

        while True:
            kd = input("kd = ").strip()
            try:
                kd_val = float(kd)
                config['KD'] = kd_val
                break
            except ValueError:
                print("Błąd: Wprowadź wartość liczbową")

        while True:
            servo_zero = input("servo_zero (stopnie) = ").strip()
            try:
                servo_zero_val = int(servo_zero)
                config['SERVO_ZERO'] = servo_zero_val
                break
            except ValueError:
                print("Błąd: Wprowadź wartość całkowitą")
        
        while True:
            t = input("t (ms, pętla PID) = ").strip()
            try:
                t_val = int(t)
                config['T'] = t_val
                break
            except ValueError:
                print("Błąd: Wprowadź wartość całkowitą")

        if config:
            self.configure(config)
    
    def show_help(self):
        print("""
╔════════════════════════════════════════════════════════════╗
║           INTERFEJS KOMUNIKACJI PC-ARDUINO                 ║
╠════════════════════════════════════════════════════════════╣
║ STEROWANIE ROBOTEM (JAZDA PO LINII):                       ║
║   P             - Włącz tryb jazdy po linii                ║
║   S             - Zatrzymaj robota                         ║
║   kp <val>      - Ustaw parametr Kp (np. kp 20)            ║
║   ki <val>      - Ustaw parametr Ki (np. ki 0.5)           ║
║   kd <val>      - Ustaw parametr Kd (np. kd 5)             ║
║   vref <val>    - Ustaw prędkość bazową (0-255)            ║
║   t <ms>        - Ustaw okres próbkowania (50-300ms)       ║
║                                                            ║
║ KALIBRACJA I DIAGNOSTYKA:                                  ║
║   calibrate     - Kalibruj tracker (przesuwaj nad linią)   ║
║   read-line     - Odczyt pozycji linii                     ║
║   status        - Status i parametry PID                   ║
║   telemetry-on  - Włącz telemetrię (POS/ERR/OUT)           ║
║   telemetry-off - Wyłącz telemetrię                        ║
║   monitor [s]   - Monitor telemetrii (opcjonalnie s sek)   ║
║                                                            ║
║ POCHYLNIA (PROJEKT 1):                                     ║
║   cfg           - Konfiguruj PID pochylni                  ║
║   set-target    - Ustaw punkt docelowy (cm)                ║
║   set-servo     - Ustaw servo zero (stopnie)               ║
║   test-start    - Uruchom tryb testowy pochylni            ║
║   test-stop     - Zatrzymaj tryb testowy                   ║
║   exam          - Uruchom tryb egzaminacyjny (13s)         ║
║   read-dist     - Jednorazowy pomiar odległości            ║
║                                                            ║
║ SYSTEM:                                                    ║
║   help          - Ta pomoc                                 ║
║   history       - Historia komend                          ║
║   save-log      - Zapisz log do pliku                      ║
║   quit          - Zakończ                                  ║
╚════════════════════════════════════════════════════════════╝
        """)
    
    def show_status(self):
        print(f"\n=== STATUS POŁĄCZENIA ===")
        print(f"Połączenie: {'Aktywne' if self.connected else 'Nieaktywne'}")
        if self.ser and self.ser.is_open:
            print(f"Port: {self.ser.port}")
            print(f"Baudrate: {self.ser.baudrate}")
            print(f"Timeout: {self.timeout}s")
        print(f"Liczba komend: {len(self.history)}")
        print(f"Liczba logów: {len(self.log)}")
        self.watchdog_test()
    
    def show_history(self):
        print("\n=== HISTORIA KOMEND ===")
        for i, cmd in enumerate(self.history[-10:], 1):
            print(f"{i}. {cmd}")
    
    def save_log(self):
        filename = f"robot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"=== LOG KOMUNIKACJI ROBOT ARDUINO ===\n")
                f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for entry in self.log:
                    f.write(entry + '\n')
            print(f"Log zapisany do: {filename}")
        except Exception as e:
            print(f"Błąd zapisu: {e}")

    def pump_telemetry(self):
        """Nieblokujące wypompowanie dostępnych linii. Drukuje tylko telemetrię bez '#'. """
        if not self.ser or not self.ser.is_open:
            return
        try:
            # Czytaj dopóki coś jest w buforze
            while self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue
                if line.endswith('#'):
                    # Ramki – można pokazać jako informację
                    print(f"[FRAME] {line}")
                else:
                    if self.telemetry_enabled:
                        print(line)
        except Exception:
            pass

    def monitor(self, seconds=0):
        """Podgląd telemetrii (DIST/ERR/OUT). seconds=0 => bez limitu, Ctrl+C aby przerwać."""
        if not self.ser or not self.ser.is_open:
            print("Brak połączenia")
            return
        print("Monitor telemetrii: uruchom TEST_START na Arduino. Ctrl+C aby przerwać.")
        deadline = time.time() + seconds if seconds > 0 else None
        try:
            while deadline is None or time.time() < deadline:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    # Ramki z # pokazuj jako [FRAME], reszta to telemetria
                    if line.endswith('#') or line.startswith(('ACK', 'NACK', 'RESULT')):
                        print(f"[FRAME] {line}")
                    else:
                        print(line)
                else:
                    time.sleep(0.01)
        except KeyboardInterrupt:
            pass

    def run(self):
        print("╔════════════════════════════════════════════╗")
        print("║      INTERFEJS KOMUNIKACJI BLUETOOTH       ║")
        print("║        (Line Follower Robot)               ║")
        print("╚════════════════════════════════════════════╝")
        
        # Wybór portu
        ports = self.list_ports()
        if not ports:
            print("Brak dostępnych portów szeregowych")
            print("\n⚠️  UWAGA: Sprawdź czy:")
            print("  - Moduł Bluetooth jest włączony")
            print("  - Arduino jest zasilane akumulatorem")
            print("  - Bluetooth HC-05/HC-06 jest sparowany")
            return
        
        print("\nWybierz port COM (zwykle COM3-COM6 dla Bluetooth):")
        try:
            choice = int(input("\nWybierz port (numer): ")) - 1
            port = ports[choice]
        except:
            print("Nieprawidłowy wybór")
            return
        
        baudrate = input("Baudrate [9600]: ").strip()
        baudrate = int(baudrate) if baudrate else 9600
        
        if not self.connect(port, baudrate):
            return
        
        print("\n✅ Połączono przez Bluetooth!")
        print("Wpisz 'help' aby zobaczyć dostępne komendy\n")
        
        while True:
            try:
                # Nieblokujący podgląd telemetrii między komendami
                self.pump_telemetry()

                cmd = input("robot> ").strip()
                if not cmd:
                    continue
                
                self.history.append(cmd)
                parts = cmd.split()
                command = parts[0].lower()
                
                if command == 'quit' or command == 'q':
                    print("Zamykanie połączenia...")
                    break
                
                elif command == 'help' or command == 'h':
                    self.show_help()
                
                elif command == 'status':
                    self.show_status()
                
                elif command == 'history':
                    self.show_history()
                
                elif command == 'save-log':
                    self.save_log()
                
                elif command == 'cfg':
                    self.interactive_config()
                
                elif command == 'set-target':
                    if len(parts) > 1:
                        try:
                            distance = float(parts[1])
                            self.set_target(distance)
                        except ValueError:
                            print("Błąd: Podaj wartość liczbową (cm)")
                    else:
                        distance = input("Podaj odległość docelową (cm): ").strip()
                        try:
                            self.set_target(float(distance))
                        except ValueError:
                            print("Błąd: Wartość musi być liczbą")
                
                elif command == 'set-servo':
                    if len(parts) > 1:
                        try:
                            angle = int(parts[1])
                            self.set_servo_zero(angle)
                        except ValueError:
                            print("Błąd: Podaj wartość całkowitą (stopnie)")
                    else:
                        angle = input("Podaj kąt servo zero (stopnie): ").strip()
                        try:
                            self.set_servo_zero(int(angle))
                        except ValueError:
                            print("Błąd: Wartość musi być liczbą całkowitą")
                
                elif command == 'test-start':
                    self.start_test_mode()
                elif command == 'test-stop':
                    self.stop_test_mode()

                elif command == 'monitor':
                    secs = int(parts[1]) if len(parts) > 1 else 0
                    self.monitor(secs)
                
                elif command == 'exam':
                    self.start_exam_mode()
                
                elif command == 'params':
                    self.get_status()
                
                elif command == 'read-dist':
                    self.read_distance()
                
                # Komendy jazdy po linii
                elif command == 'p':
                    response = self.send_command("P")
                    if response:
                        print("🚗 Tryb jazdy po linii WŁĄCZONY")
                
                elif command == 's':
                    response = self.send_command("S")
                    if response:
                        print("🛑 Robot ZATRZYMANY")
                
                elif command == 'kp':
                    if len(parts) > 1:
                        try:
                            val = float(parts[1])
                            response = self.send_command(f"Kp {val}")
                            if response:
                                print(f"✅ Kp ustawione na: {val}")
                        except ValueError:
                            print("Błąd: Podaj wartość liczbową")
                    else:
                        val = input("Podaj wartość Kp: ").strip()
                        try:
                            response = self.send_command(f"Kp {float(val)}")
                            if response:
                                print(f"✅ Kp ustawione na: {val}")
                        except ValueError:
                            print("Błąd: Wartość musi być liczbą")
                
                elif command == 'ki':
                    if len(parts) > 1:
                        try:
                            val = float(parts[1])
                            response = self.send_command(f"Ki {val}")
                            if response:
                                print(f"✅ Ki ustawione na: {val}")
                        except ValueError:
                            print("Błąd: Podaj wartość liczbową")
                    else:
                        val = input("Podaj wartość Ki: ").strip()
                        try:
                            response = self.send_command(f"Ki {float(val)}")
                            if response:
                                print(f"✅ Ki ustawione na: {val}")
                        except ValueError:
                            print("Błąd: Wartość musi być liczbą")
                
                elif command == 'kd':
                    if len(parts) > 1:
                        try:
                            val = float(parts[1])
                            response = self.send_command(f"Kd {val}")
                            if response:
                                print(f"✅ Kd ustawione na: {val}")
                        except ValueError:
                            print("Błąd: Podaj wartość liczbową")
                    else:
                        val = input("Podaj wartość Kd: ").strip()
                        try:
                            response = self.send_command(f"Kd {float(val)}")
                            if response:
                                print(f"✅ Kd ustawione na: {val}")
                        except ValueError:
                            print("Błąd: Wartość musi być liczbą")
                
                elif command == 'vref':
                    if len(parts) > 1:
                        try:
                            val = int(parts[1])
                            response = self.send_command(f"Vref {val}")
                            if response:
                                print(f"✅ Vref ustawione na: {val}")
                        except ValueError:
                            print("Błąd: Podaj wartość całkowitą (0-255)")
                    else:
                        val = input("Podaj prędkość bazową (0-255): ").strip()
                        try:
                            response = self.send_command(f"Vref {int(val)}")
                            if response:
                                print(f"✅ Vref ustawione na: {val}")
                        except ValueError:
                            print("Błąd: Wartość musi być liczbą całkowitą")
                
                elif command == 't' and len(parts) > 1:
                    try:
                        val = int(parts[1])
                        response = self.send_command(f"T {val}")
                        if response:
                            print(f"✅ Okres próbkowania ustawiony na: {val} ms")
                    except ValueError:
                        print("Błąd: Podaj wartość całkowitą (50-300)")
                
                elif command == 'calibrate':
                    print("📏 Kalibracja trackera - przesuwaj robota nad linią...")
                    response = self.send_command("CALIBRATE")
                    if response:
                        print("✅ Kalibracja zakończona")
                
                elif command == 'read-line':
                    response = self.send_command("READ_LINE")
                    if response:
                        print(f"📍 Pozycja linii: {response}")
                
                elif command == 'telemetry-on':
                    response = self.send_command("TELEMETRY_ON")
                    if response:
                        print("📊 Telemetria WŁĄCZONA")
                        self.telemetry_enabled = True
                
                elif command == 'telemetry-off':
                    response = self.send_command("TELEMETRY_OFF")
                    if response:
                        print("📊 Telemetria WYŁĄCZONA")
                        self.telemetry_enabled = False

                else:
                    print("Nieznana komenda. Wpisz 'help' aby zobaczyć pomoc.")
            
            except KeyboardInterrupt:
                print("\n\nPrzerwano przez użytkownika")
                break
            except Exception as e:
                print(f"Błąd: {e}")
        
        # Zamknięcie połączenia
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Połączenie zamknięte")


if __name__ == "__main__":
    robot = RobotInterface()
    robot.run()