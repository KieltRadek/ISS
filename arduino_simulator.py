import serial
import serial.tools.list_ports
from datetime import datetime


class ArduinoSimulator:
    """Prosty symulator Arduino - odbiera i wyświetla komendy"""
    
    def __init__(self):
        self.ser = None
        self.current_velocity = 100  # Domyślna prędkość
        
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
        """Nawiązuje połączenie na porcie COM"""
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1.0)
            print(f"\n✅ Symulator nasłuchuje na {port} ({baudrate} baud)")
            print("=" * 70)
            return True
        except Exception as e:
            print(f"❌ Błąd połączenia: {e}")
            return False
    
    def validate_frame(self, frame):
        """Waliduje otrzymaną ramkę"""
        parts = frame.split('|')
        if len(parts) != 2:
            return False, "Brak separatora |"
        
        cmd = parts[0]
        try:
            received_checksum = int(parts[1])
        except:
            return False, "Nieprawidłowy checksum"
        
        calculated_checksum = self.calculate_checksum(cmd)
        
        if received_checksum == calculated_checksum:
            return True, "OK"
        else:
            return False, f"Checksum nieprawidłowy (otrzymano: {received_checksum}, oczekiwano: {calculated_checksum})"
    
    def parse_command(self, cmd):
        """Parsuje komendę i zwraca opis"""
        if cmd.startswith("M("):
            val = cmd[2:-1]
            direction = "PRZÓD" if int(val) > 0 else "TYŁ"
            return f"RUCH {direction} o {abs(int(val))} cm (prędkość: {self.current_velocity})"
        elif cmd.startswith("R("):
            val = cmd[2:-1]
            direction = "PRAWO" if int(val) > 0 else "LEWO"
            return f"OBRÓT {direction} o {abs(int(val))}° (stopni)"
        elif cmd.startswith("V("):
            val = cmd[2:-1]
            self.current_velocity = int(val)
            return f"PRĘDKOŚĆ ustawiona na {val}"
        elif cmd == "S":
            return "STOP - zatrzymanie robota"
        elif cmd == "B":
            return "ODCZYT SONARU"
        elif cmd == "I":
            return "ODCZYT CZUJNIKÓW IR"
        elif cmd.startswith("CFG("):
            config = cmd[4:-1]
            # Parsuj konfigurację
            params = []
            for item in config.split(','):
                if '=' in item:
                    key, val = item.split('=', 1)
                    params.append(f"{key.strip()}={val.strip()}")
            config_desc = ", ".join(params)
            return f"KONFIGURACJA: {config_desc}"
        elif cmd == "PING":
            return "PING - test połączenia"
        else:
            return f"NIEZNANA KOMENDA: {cmd}"
    
    def send_response(self, response):
        """Wysyła odpowiedź do PC"""
        self.ser.write(response.encode())
        self.ser.flush()
    
    def run(self):
        """Główna pętla symulatora"""
        print("╔════════════════════════════════════════════════════════════╗")
        print("║          SYMULATOR ARDUINO - ODBIERANIE KOMEND             ║")
        print("╚════════════════════════════════════════════════════════════╝")
        
        # Wybór portu
        ports = self.list_ports()
        if not ports:
            print("❌ Brak dostępnych portów szeregowych")
            return
        
        print("\n💡 Dla com0com wybierz port wirtualny (np. COM4)")
        try:
            choice = int(input("\nWybierz port (numer): ")) - 1
            port = ports[choice]
        except:
            print("❌ Nieprawidłowy wybór")
            return
        
        # Baudrate
        baudrate = input("Baudrate [9600]: ").strip()
        baudrate = int(baudrate) if baudrate else 9600
        
        # Połączenie
        if not self.connect(port, baudrate):
            return
        
        print("\n🎯 Symulator gotowy! Oczekiwanie na komendy...\n")
        print("=" * 70)
        
        input_buffer = ""
        
        # Główna pętla odbierania
        try:
            while True:
                if self.ser.in_waiting > 0:
                    char = self.ser.read().decode('utf-8', errors='ignore')
                    
                    if char == '#':
                        # Zakończenie ramki
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        
                        print(f"\n[{timestamp}] 📨 ODEBRANO RAMKĘ")
                        print(f"{'─' * 70}")
                        print(f"📦 Surowa ramka: '{input_buffer}'")
                        
                        # Walidacja
                        is_valid, msg = self.validate_frame(input_buffer)
                        
                        if is_valid:
                            cmd = input_buffer.split('|')[0]
                            description = self.parse_command(cmd)
                            
                            print(f"✅ WALIDACJA: {msg}")
                            print(f"📋 KOMENDA: {cmd}")
                            print(f"🎯 AKCJA: {description}")
                            
                            # Wysyłamy ACK
                            if cmd == "PING":
                                response = "ACK|PONG#"
                            elif cmd == "B":
                                response = "ACK|25#"  # Symulowany odczyt sonaru: 25 cm
                            elif cmd == "I":
                                response = "ACK|AL=512,DL=0,AR=498,DR=0#"  # Symulowany odczyt IR
                            else:
                                response = "ACK#"
                            
                            self.send_response(response)
                            print(f"📤 ODPOWIEDŹ: {response}")
                            
                        else:
                            print(f"❌ BŁĄD WALIDACJI: {msg}")
                            response = "NACK|BAD_CHECKSUM#"
                            self.send_response(response)
                            print(f"📤 ODPOWIEDŹ: {response}")
                        
                        print(f"{'─' * 70}\n")
                        
                        # Wyczyść bufor
                        input_buffer = ""
                    else:
                        input_buffer += char
                        
        except KeyboardInterrupt:
            print("\n\n⛔ Przerwano przez użytkownika")
        except Exception as e:
            print(f"\n❌ Błąd: {e}")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("🔌 Połączenie zamknięte")


if __name__ == "__main__":
    simulator = ArduinoSimulator()
    simulator.run()
