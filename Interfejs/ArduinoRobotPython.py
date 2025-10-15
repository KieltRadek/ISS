import serial
import serial.tools.list_ports
import time
from datetime import datetime


class RobotInterface:
    """Główna klasa interfejsu komunikacji z robotem Arduino"""
    
    def __init__(self):
        self.ser = None
        self.log = []
        self.history = []
        self.timeout = 1.0  # Zmniejszony timeout
        self.max_retries = 3
        self.current_velocity = 150  # Domyślna prędkość
        self.connected = False
        
    def calculate_checksum(self, cmd):
        """Oblicza sumę kontrolną komendy"""
        return sum(ord(c) for c in cmd) % 256
    
    def list_ports(self):
        """Wyświetla dostępne porty szeregowe"""
        ports = serial.tools.list_ports.comports()
        print("\n=== Dostępne porty szeregowe ===")
        for i, port in enumerate(ports, 1):
            print(f"{i}. {port.device} - {port.description}")
        return [p.device for p in ports]
    
    def connect(self, port, baudrate=9600):
        """Nawiązuje połączenie z Arduino"""
        try:
            self.ser = serial.Serial(port, baudrate, timeout=self.timeout)
            time.sleep(2)  # Czas na inicjalizację Arduino
            print(f"Połączono z {port} ({baudrate} baud)")
            self.connected = True
            self.watchdog_test()
            return True
        except Exception as e:
            print(f"Błąd połączenia: {e}")
            return False
    
    def watchdog_test(self):
        """Test połączenia (watchdog)"""
        response = self.send_command("PING", retries=1)
        if response and "PONG" in response:
            print("Watchdog: Połączenie aktywne")
            return True
        else:
            print("Watchdog: Brak odpowiedzi")
            self.connected = False
            return False
        
    def send_command(self, cmd, retries=None):
        """Wysyła komendę z walidacją i ponowieniami"""
        if not self.ser or not self.ser.is_open:
            print("Brak połączenia")
            return None
        
        retries = retries if retries is not None else self.max_retries
        checksum = self.calculate_checksum(cmd)
        frame = f"{cmd}|{checksum}#"
        
        for attempt in range(retries):
            try:
                # Wyczyść bufory przed wysłaniem
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                
                # Wyślij ramkę
                self.ser.write(frame.encode())
                self.ser.flush()  # Upewnij się, że dane zostały wysłane
                self.log_message(f"TX: {frame.strip('#')}")
                
                # Czekaj na odpowiedź ze stałym timeoutem
                start = time.time()
                response = ""
                
                while (time.time() - start) < self.timeout:
                    if self.ser.in_waiting > 0:
                        char = self.ser.read().decode('utf-8', errors='ignore')
                        response += char
                        if char == '#':
                            break
                    time.sleep(0.01)  # Krótkie opóźnienie, aby nie blokować CPU
                
                if response:
                    self.log_message(f"RX: {response.strip('#')}")
                    
                    if response.startswith("ACK"):
                        return response.strip('#')
                    elif response.startswith("NACK"):
                        print(f"NACK otrzymany: {response}")
                        return None
                else:
                    print(f"Timeout (próba {attempt+1}/{retries})")
                    time.sleep(0.1)  # Krótka pauza przed kolejną próbą
                    
            except Exception as e:
                print(f"Błąd komunikacji: {e}")
        
        print("Brak odpowiedzi po wszystkich próbach")
        return None
    
    
    def log_message(self, msg):
        """Loguje wiadomość z timestampem"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log.append(f"[{timestamp}] {msg}")
    
    def move(self, cm):
        """M(cm) - Ruch o zadaną odległość"""
        response = self.send_command(f"M({cm})")
        if response:
            print(f"Robot porusza się o {cm} cm (prędkość: {self.current_velocity})")
        return response
    
    def rotate(self, degrees):
        """R(degrees) - Obrót o zadaną liczbę stopni"""
        response = self.send_command(f"R({degrees})")
        if response:
            direction = "prawo" if degrees > 0 else "lewo"
            print(f"Robot obraca się {direction} o {abs(degrees)}°")
        return response
    
    def set_velocity(self, v):
        """V(v) - Ustawienie prędkości (0-255)"""
        response = self.send_command(f"V({v})")
        if response:
            self.current_velocity = v
            print(f"Prędkość ustawiona na {v}")
        return response
    
    def stop(self):
        """S - Zatrzymanie robota"""
        response = self.send_command("S")
        if response:
            print("Robot zatrzymany")
        return response
    
    def read_sonar(self):
        """B - Odczyt sonaru"""
        response = self.send_command("B")
        if response:
            parts = response.split('|')
            if len(parts) > 1:
                distance = parts[1]
                print(f"Sonar: {distance} cm")
                return distance
        return None
    
    def read_ir(self):
        """I - Odczyt czujników IR"""
        response = self.send_command("I")
        if response:
            parts = response.split('|')
            if len(parts) > 1:
                data = parts[1]
                print(f"✓ IR: {data}")
                return data
        return None
    
    def configure(self, config_dict):
        """CFG - Konfiguracja silników i czujników"""
        cfg_str = ",".join([f"{k}={v}" for k, v in config_dict.items()])
        response = self.send_command(f"CFG({cfg_str})")
        if response:
            print(f"Konfiguracja zastosowana: {cfg_str}")
        return response
    
    def show_help(self):
        """Wyświetla pomoc"""
        print("""
╔════════════════════════════════════════════════════════════╗
║           KOMENDY INTERFEJSU ROBOTA ARDUINO                ║
╠════════════════════════════════════════════════════════════╣
║ STEROWANIE:                                                ║
║   m <cm>        - Ruch (+ przód, - tył)                    ║
║   r <stopnie>   - Obrót (+ prawo, - lewo) 0-360°           ║
║   v <0-255>     - Ustaw prędkość                           ║
║   s             - STOP (natychmiast)                       ║
║                                                            ║
║ SENSORY:                                                   ║
║   b             - Odczyt sonaru [cm]                       ║
║   i             - Odczyt IR                                ║
║                                                            ║
║ KONFIGURACJA (interaktywna z terminala):                   ║
║   cfg           - Konfiguruj silniki/sensory               ║
║                                                            ║
║   Parametry konfiguracji:                                  ║
║     M1 / M2          = LEFT / RIGHT                        ║
║     M1_DIR / M2_DIR  = NORMAL / REVERSED                   ║
║     S1 / S2          = FRONT / BACK                        ║
║                                                            ║
║  Przykład: robot> cfg                                      ║
║     M1 = LEFT                                              ║
║     M1_DIR = NORMAL                                        ║
║     M2 = RIGHT                                             ║
║     M2_DIR = REVERSED  (jeśli silnik jedzie odwrotnie)     ║
║     S1 = FRONT                                             ║
║     S2 = BACK                                              ║
║                                                            ║
║ KALIBRACJA (edycja pliku RobotArduino.ino):                ║
║   Zmień wartości stałych w kodzie Arduino:                 ║
║     PULSES_PER_CM          - Impulsy enkodera na 1 cm      ║
║     PULSES_PER_360_DEGREES - Impulsy na pełny obrót 360°   ║
║                                                            ║
║ SYSTEM:                                                    ║
║   help          - Ta pomoc                                 ║
║   status        - Status połączenia                        ║
║   history       - Historia komend                          ║
║   save-log      - Zapisz log do pliku                      ║
║   quit          - Zakończ                                  ║
╚════════════════════════════════════════════════════════════╝
        """)
    
    def show_status(self):
        """Wyświetla status połączenia"""
        print(f"\n=== STATUS POŁĄCZENIA ===")
        print(f"Połączenie: {'✓ Aktywne' if self.connected else '✗ Nieaktywne'}")
        if self.ser and self.ser.is_open:
            print(f"Port: {self.ser.port}")
            print(f"Baudrate: {self.ser.baudrate}")
            print(f"Timeout: {self.timeout}s")
        print(f"Liczba komend: {len(self.history)}")
        print(f"Liczba logów: {len(self.log)}")
        self.watchdog_test()
    
    def show_history(self):
        """Wyświetla historię komend"""
        print("\n=== HISTORIA KOMEND ===")
        for i, cmd in enumerate(self.history[-10:], 1):
            print(f"{i}. {cmd}")
    
    def save_log(self):
        """Zapisuje log do pliku"""
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

    def interactive_config(self):
        """Interaktywna konfiguracja silników i czujników"""
        print("\n=== KONFIGURACJA ROBOTA ===")
        
        config = {}
        
        # Konfiguracja silnika M1
        while True:
            print("Silnik 1 (M1): LEFT/RIGHT")
            m1 = input("M1 = ").strip().upper()
            if m1 in ['LEFT', 'RIGHT']:
                config['M1'] = m1
                break
            else:
                print("Błąd: Wprowadź LEFT lub RIGHT")
        
        # Konfiguracja kierunku silnika M1
        while True:
            print("Kierunek Silnika 1 (M1_DIR): NORMAL/REVERSED")
            m1_dir = input("M1_DIR = ").strip().upper()
            if m1_dir in ['NORMAL', 'REVERSED']:
                config['M1_DIR'] = m1_dir
                break
            else:
                print("Błąd: Wprowadź NORMAL lub REVERSED")
        
        # Konfiguracja silnika M2
        while True:
            print("Silnik 2 (M2): LEFT/RIGHT")
            m2 = input("M2 = ").strip().upper()
            if m2 in ['LEFT', 'RIGHT']:
                config['M2'] = m2
                break
            else:
                print("Błąd: Wprowadź LEFT lub RIGHT")
        
        # Konfiguracja kierunku silnika M2
        while True:
            print("Kierunek Silnika 2 (M2_DIR): NORMAL/REVERSED")
            m2_dir = input("M2_DIR = ").strip().upper()
            if m2_dir in ['NORMAL', 'REVERSED']:
                config['M2_DIR'] = m2_dir
                break
            else:
                print("Błąd: Wprowadź NORMAL lub REVERSED")
        
        # Konfiguracja czujnika S1
        while True:
            print("Czujnik 1 (S1): FRONT/BACK")
            s1 = input("S1 = ").strip().upper()
            if s1 in ['FRONT', 'BACK']:
                config['S1'] = s1
                break
            else:
                print("Błąd: Wprowadź FRONT lub BACK")
        
        # Konfiguracja czujnika S2
        while True:
            print("Czujnik 2 (S2): FRONT/BACK")
            s2 = input("S2 = ").strip().upper()
            if s2 in ['FRONT', 'BACK']:
                config['S2'] = s2
                break
            else:
                print("Błąd: Wprowadź FRONT lub BACK")
        
        if config:
            self.configure(config)
    
    def run(self):
        """Główna pętla interfejsu"""
        print("╔════════════════════════════════════════════╗")
        print("║      INTERFEJS KOMUNIKACJI PC-ARDUINO      ║")
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
        
        # Baudrate
        baudrate = input("Baudrate [9600]: ").strip()
        baudrate = int(baudrate) if baudrate else 9600
        
        # Połączenie
        if not self.connect(port, baudrate):
            return
        
        print("\nWpisz 'help' aby zobaczyć dostępne komendy\n")
        
        # Główna pętla
        while True:
            try:
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
                
                elif command == 'm' and len(parts) > 1:
                    self.move(int(parts[1]))
                
                elif command == 'r' and len(parts) > 1:
                    self.rotate(int(parts[1]))
                
                elif command == 'v' and len(parts) > 1:
                    self.set_velocity(int(parts[1]))
                
                elif command == 's':
                    self.stop()
                
                elif command == 'b':
                    self.read_sonar()
                
                elif command == 'i':
                    self.read_ir()
                
                elif command == 'cfg':
                    self.interactive_config()
                
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