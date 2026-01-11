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
        self. connected = False
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
            print("Watchdog:  Połączenie aktywne")
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
                self.log_message(f"TX: {frame. strip('#')}")
                
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
                        self.log_message(f"RX: {line. strip('#')}")
                        if line.startswith("ACK"):
                            return line. strip('#')
                        if line.startswith("NACK"):
                            print(line)
                            return None
                        # Inne ramki (RESULT itp.)
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
        timestamp = datetime.now().strftime("%H:%M:%S. %f")[:-3]
        self.log.append(f"[{timestamp}] {msg}")
    
    # ========================= PROJEKT 4 - FUNKCJE =========================
    
    def start_wall_approach(self):
        """Uruchomienie jazdy do ściany"""
        response = self.send_command("START")
        if response: 
            print("✓ Jazda do ściany uruchomiona")
            self.telemetry_enabled = True
        return response
    
    def stop_wall_approach(self):
        """Zatrzymanie jazdy do ściany"""
        response = self.send_command("STOP")
        if response:
            print("✓ Robot zatrzymany")
            self.telemetry_enabled = False
        return response
    
    def set_pid_left(self, kp=None, ki=None, kd=None):
        """Ustaw parametry PID lewego koła"""
        results = []
        if kp is not None:
            response = self.send_command(f"KP_L {kp}")
            if response:
                print(f"✓ Kp_left = {kp}")
                results. append(response)
        if ki is not None:
            response = self.send_command(f"KI_L {ki}")
            if response:
                print(f"✓ Ki_left = {ki}")
                results.append(response)
        if kd is not None: 
            response = self.send_command(f"KD_L {kd}")
            if response: 
                print(f"✓ Kd_left = {kd}")
                results.append(response)
        return results
    
    def set_pid_right(self, kp=None, ki=None, kd=None):
        """Ustaw parametry PID prawego koła"""
        results = []
        if kp is not None: 
            response = self.send_command(f"KP_R {kp}")
            if response: 
                print(f"✓ Kp_right = {kp}")
                results.append(response)
        if ki is not None:
            response = self.send_command(f"KI_R {ki}")
            if response:
                print(f"✓ Ki_right = {ki}")
                results.append(response)
        if kd is not None:
            response = self.send_command(f"KD_R {kd}")
            if response:
                print(f"✓ Kd_right = {kd}")
                results.append(response)
        return results
    
    def set_vmax(self, vmax):
        """Ustaw prędkość maksymalną"""
        response = self.send_command(f"VMAX {vmax}")
        if response:
            print(f"✓ V_max = {vmax}")
        return response
    
    def read_distance(self):
        """Jednorazowy pomiar odległości"""
        response = self.send_command("READ_DISTANCE")
        if response:
            print(f"Odległość: {response}")
        return response
    
    def get_status(self):
        """Odczyt parametrów z Arduino"""
        response = self.send_command("STATUS")
        if response:
            print(f"Parametry: {response}")
        return response
    
    def interactive_config_wheels(self):
        """Interaktywna konfiguracja PID kół"""
        print("\n=== KONFIGURACJA PID KÓŁ ===")
        
        print("\n--- LEWE KOŁO ---")
        kp_l = input("Kp_left [2.0]:  ").strip()
        kp_l = float(kp_l) if kp_l else 2.0
        
        ki_l = input("Ki_left [0.5]: ").strip()
        ki_l = float(ki_l) if ki_l else 0.5
        
        kd_l = input("Kd_left [0.1]: ").strip()
        kd_l = float(kd_l) if kd_l else 0.1
        
        print("\n--- PRAWE KOŁO ---")
        kp_r = input("Kp_right [2.0]: ").strip()
        kp_r = float(kp_r) if kp_r else 2.0
        
        ki_r = input("Ki_right [0.5]: ").strip()
        ki_r = float(ki_r) if ki_r else 0.5
        
        kd_r = input("Kd_right [0.1]: ").strip()
        kd_r = float(kd_r) if kd_r else 0.1
        
        print("\n--- PRĘDKOŚĆ ---")
        vmax = input("V_max [50. 0]: ").strip()
        vmax = float(vmax) if vmax else 50.0
        
        print("\nWysyłanie konfiguracji...")
        self.set_pid_left(kp_l, ki_l, kd_l)
        self.set_pid_right(kp_r, ki_r, kd_r)
        self.set_vmax(vmax)
        print("\n✓ Konfiguracja zakończona")
    
    def pump_telemetry(self):
        """Nieblokujące wypompowanie dostępnych linii."""
        if not self.ser or not self. ser.is_open:
            return
        try:
            while self.ser.in_waiting > 0:
                line = self. ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue
                if line.endswith('#'):
                    print(f"[FRAME] {line}")
                else:
                    if self.telemetry_enabled:
                        print(line)
        except Exception: 
            pass

    def monitor(self, seconds=0):
        """Podgląd telemetrii.  seconds=0 => bez limitu, Ctrl+C aby przerwać."""
        if not self.ser or not self. ser.is_open:
            print("Brak połączenia")
            return
        print("Monitor telemetrii:  uruchom START na Arduino.  Ctrl+C aby przerwać.")
        deadline = time.time() + seconds if seconds > 0 else None
        try:
            while deadline is None or time.time() < deadline:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    if line.endswith('#') or line.startswith(('ACK', 'NACK')):
                        print(f"[FRAME] {line}")
                    else:
                        print(line)
                else:
                    time.sleep(0.01)
        except KeyboardInterrupt:
            pass
    
    def show_help(self):
        print("""
╔════════════════════════════════════════════════════════════╗
║      INTERFEJS PROJEKT 4 - JAZDA DO ŚCIANY (PID+FUZZY)     ║
╠════════════════════════════════════════════════════════════╣
║ STEROWANIE ROBOTEM:                                        ║
║   start         - Uruchom jazdę do ściany                  ║
║   stop          - Zatrzymaj robota                         ║
║   config        - Konfiguruj parametry PID kół             ║
║   kp-l <val>    - Ustaw Kp lewego koła                     ║
║   ki-l <val>    - Ustaw Ki lewego koła                     ║
║   kd-l <val>    - Ustaw Kd lewego koła                     ║
║   kp-r <val>    - Ustaw Kp prawego koła                    ║
║   ki-r <val>    - Ustaw Ki prawego koła                    ║
║   kd-r <val>    - Ustaw Kd prawego koła                    ║
║   vmax <val>    - Ustaw prędkość maksymalną                ║
║                                                            ║
║ DIAGNOSTYKA:                                               ║
║   status        - Status i parametry robota                ║
║   read-dist     - Jednorazowy pomiar odległości            ║
║   telemetry-on  - Włącz telemetrię (DIST/VREF/PWM)         ║
║   telemetry-off - Wyłącz telemetrię                        ║
║   monitor [s]   - Monitor telemetrii (opcjonalnie s sek)   ║
║                                                            ║
║ SYSTEM:                                                     ║
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
        for i, cmd in enumerate(self. history[-10:], 1):
            print(f"{i}. {cmd}")
    
    def save_log(self):
        filename = f"robot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"=== LOG KOMUNIKACJI ROBOT ARDUINO - PROJEKT 4 ===\n")
                f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for entry in self.log:
                    f.write(entry + '\n')
            print(f"Log zapisany do:  {filename}")
        except Exception as e:
            print(f"Błąd zapisu: {e}")

    def run(self):
        print("╔════════════════════════════════════════════╗")
        print("║   PROJEKT 4 - JAZDA DO ŚCIANY (PID+FUZZY) ║")
        print("╚════════════════════════════════════════════╝")
        
        # Wybór portu
        ports = self.list_ports()
        if not ports:
            print("Brak dostępnych portów szeregowych")
            return
        
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
        
        print("\nWpisz 'help' aby zobaczyć dostępne komendy\n")
        
        while True:
            try:
                # Nieblokujący podgląd telemetrii między komendami
                self.pump_telemetry()

                cmd = input("robot> ").strip()
                if not cmd:
                    continue
                
                self.history.append(cmd)
                parts = cmd.split()
                command = parts[0]. lower()
                
                if command == 'quit' or command == 'q':
                    print("Zamykanie połączenia...")
                    break
                
                elif command == 'help' or command == 'h': 
                    self.show_help()
                
                elif command == 'status': 
                    self.show_status()
                    self.get_status()
                
                elif command == 'history':
                    self.show_history()
                
                elif command == 'save-log':
                    self.save_log()
                
                elif command == 'config':
                    self.interactive_config_wheels()
                
                elif command == 'start':
                    self.start_wall_approach()
                
                elif command == 'stop': 
                    self.stop_wall_approach()
                
                elif command == 'kp-l': 
                    if len(parts) > 1:
                        try:
                            self.set_pid_left(kp=float(parts[1]))
                        except ValueError:
                            print("Błąd: Podaj wartość liczbową")
                    else: 
                        val = input("Podaj wartość Kp_left: ").strip()
                        try:
                            self.set_pid_left(kp=float(val))
                        except ValueError:
                            print("Błąd: Wartość musi być liczbą")
                
                elif command == 'ki-l':
                    if len(parts) > 1:
                        try:
                            self.set_pid_left(ki=float(parts[1]))
                        except ValueError:
                            print("Błąd:  Podaj wartość liczbową")
                    else:
                        val = input("Podaj wartość Ki_left: ").strip()
                        try:
                            self.set_pid_left(ki=float(val))
                        except ValueError:
                            print("Błąd:  Wartość musi być liczbą")
                
                elif command == 'kd-l': 
                    if len(parts) > 1:
                        try: 
                            self.set_pid_left(kd=float(parts[1]))
                        except ValueError:
                            print("Błąd: Podaj wartość liczbową")
                    else:
                        val = input("Podaj wartość Kd_left: ").strip()
                        try:
                            self.set_pid_left(kd=float(val))
                        except ValueError:
                            print("Błąd:  Wartość musi być liczbą")
                
                elif command == 'kp-r': 
                    if len(parts) > 1:
                        try: 
                            self.set_pid_right(kp=float(parts[1]))
                        except ValueError:
                            print("Błąd: Podaj wartość liczbową")
                    else:
                        val = input("Podaj wartość Kp_right: ").strip()
                        try:
                            self.set_pid_right(kp=float(val))
                        except ValueError:
                            print("Błąd:  Wartość musi być liczbą")
                
                elif command == 'ki-r':
                    if len(parts) > 1:
                        try: 
                            self.set_pid_right(ki=float(parts[1]))
                        except ValueError: 
                            print("Błąd: Podaj wartość liczbową")
                    else:
                        val = input("Podaj wartość Ki_right: ").strip()
                        try:
                            self.set_pid_right(ki=float(val))
                        except ValueError:
                            print("Błąd: Wartość musi być liczbą")
                
                elif command == 'kd-r':
                    if len(parts) > 1:
                        try:
                            self.set_pid_right(kd=float(parts[1]))
                        except ValueError:
                            print("Błąd:  Podaj wartość liczbową")
                    else:
                        val = input("Podaj wartość Kd_right:  ").strip()
                        try:
                            self.set_pid_right(kd=float(val))
                        except ValueError:
                            print("Błąd: Wartość musi być liczbą")
                
                elif command == 'vmax':
                    if len(parts) > 1:
                        try:
                            self.set_vmax(float(parts[1]))
                        except ValueError:
                            print("Błąd: Podaj wartość liczbową")
                    else:
                        val = input("Podaj V_max: ").strip()
                        try:
                            self.set_vmax(float(val))
                        except ValueError: 
                            print("Błąd: Wartość musi być liczbą")
                
                elif command == 'read-dist':
                    self.read_distance()
                
                elif command == 'telemetry-on':
                    response = self.send_command("TELEMETRY_ON")
                    if response:
                        print("Telemetria WŁĄCZONA")
                        self.telemetry_enabled = True
                
                elif command == 'telemetry-off':
                    response = self.send_command("TELEMETRY_OFF")
                    if response:
                        print("Telemetria WYŁĄCZONA")
                        self.telemetry_enabled = False

                elif command == 'monitor': 
                    secs = int(parts[1]) if len(parts) > 1 else 0
                    self.monitor(secs)

                else:
                    print("Nieznana komenda. Wpisz 'help' aby zobaczyć pomoc.")
            
            except KeyboardInterrupt: 
                print("\n\nPrzerwano przez użytkownika")
                break
            except Exception as e:
                print(f"Błąd: {e}")
        
        # Zamknięcie połączenia
        if self.ser and self.ser. is_open:
            self. ser.close()
            print("Połączenie zamknięte")


if __name__ == "__main__":
    robot = RobotInterface()
    robot.run()