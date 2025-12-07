"""
Quick PID Configuration Tool
Szybkie ustawianie predefiniowanych konfiguracji PID dla Line Followera
"""

import serial
import serial.tools.list_ports
import time

class QuickConfig:
    def __init__(self):
        self.ser = None
        
    def calculate_checksum(self, cmd):
        return sum(ord(c) for c in cmd) % 256
    
    def send_command(self, cmd):
        if not self.ser or not self.ser.is_open:
            print("Brak połączenia")
            return False
        
        checksum = self.calculate_checksum(cmd)
        frame = f"{cmd}|{checksum}#"
        
        try:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.write(frame.encode())
            self.ser.flush()
            
            start = time.time()
            while (time.time() - start) < 1.0:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.endswith('#') and line.startswith("ACK"):
                        return True
            return False
        except Exception as e:
            print(f"Błąd: {e}")
            return False
    
    def connect(self, port, baudrate=9600):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1.0)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Błąd połączenia: {e}")
            return False
    
    def apply_config(self, config):
        print(f"\n{'='*50}")
        print(f"Ustawiam konfigurację: {config['name']}")
        print(f"{'='*50}")
        print(f"Opis: {config['description']}")
        print(f"\nParametry:")
        print(f"  Kp = {config['Kp']}")
        print(f"  Ki = {config['Ki']}")
        print(f"  Kd = {config['Kd']}")
        print(f"  Vref = {config['Vref']}")
        print(f"  T = {config['T']} ms")
        print()
        
        success = True
        success &= self.send_command(f"Kp {config['Kp']}")
        success &= self.send_command(f"Ki {config['Ki']}")
        success &= self.send_command(f"Kd {config['Kd']}")
        success &= self.send_command(f"Vref {config['Vref']}")
        success &= self.send_command(f"T {config['T']}")
        
        if success:
            print("✓ Konfiguracja zastosowana pomyślnie!")
        else:
            print("✗ Wystąpił błąd podczas konfiguracji")
        
        return success

# Predefiniowane konfiguracje
CONFIGS = {
    '1': {
        'name': 'Bezpieczny Start',
        'description': 'Powolna, stabilna jazda - dobry punkt startowy',
        'Kp': 15,
        'Ki': 0,
        'Kd': 3,
        'Vref': 80,
        'T': 100
    },
    '2': {
        'name': 'Łagodne Zakręty',
        'description': 'Średnia prędkość, dobra reaktywność',
        'Kp': 20,
        'Ki': 0,
        'Kd': 5,
        'Vref': 100,
        'T': 100
    },
    '3': {
        'name': 'Ostre Zakręty (Zygzak)',
        'description': 'Agresywne sterowanie dla trudnych tras',
        'Kp': 30,
        'Ki': 0.2,
        'Kd': 8,
        'Vref': 90,
        'T': 80
    },
    '4': {
        'name': 'Wysoka Prędkość',
        'description': 'Maksymalna prędkość na prostych odcinkach',
        'Kp': 25,
        'Ki': 0,
        'Kd': 10,
        'Vref': 140,
        'T': 80
    },
    '5': {
        'name': 'Tor Mieszany',
        'description': 'Uniwersalne ustawienia ogólnego przeznaczenia',
        'Kp': 22,
        'Ki': 0.1,
        'Kd': 6,
        'Vref': 110,
        'T': 100
    },
    '6': {
        'name': 'Tor z Przerwami',
        'description': 'Silny Ki utrzymuje kierunek przy lukach',
        'Kp': 20,
        'Ki': 0.5,
        'Kd': 5,
        'Vref': 100,
        'T': 120
    }
}

def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║      QUICK PID CONFIGURATION - LINE FOLLOWER           ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    qc = QuickConfig()
    
    # Wybór portu
    ports = serial.tools.list_ports.comports()
    print("\nDostępne porty:")
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port.device} - {port.description}")
    
    try:
        choice = int(input("\nWybierz port (numer): ")) - 1
        port = [p.device for p in ports][choice]
    except:
        print("Nieprawidłowy wybór")
        return
    
    baudrate = input("Baudrate [9600]: ").strip()
    baudrate = int(baudrate) if baudrate else 9600
    
    if not qc.connect(port, baudrate):
        return
    
    print("\n✓ Połączono!")
    
    while True:
        print("\n" + "="*60)
        print("DOSTĘPNE KONFIGURACJE:")
        print("="*60)
        for key, config in CONFIGS.items():
            print(f"{key}. {config['name']}")
            print(f"   {config['description']}")
            print(f"   Kp={config['Kp']}, Ki={config['Ki']}, Kd={config['Kd']}, "
                  f"Vref={config['Vref']}, T={config['T']}")
            print()
        
        print("Inne opcje:")
        print("  c - Kalibracja trackera")
        print("  s - Status parametrów")
        print("  p - Uruchom robota (P)")
        print("  x - Zatrzymaj robota (S)")
        print("  t - Włącz telemetrię")
        print("  q - Wyjście")
        
        choice = input("\nWybór: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice in CONFIGS:
            qc.apply_config(CONFIGS[choice])
        elif choice == 'c':
            print("\nKalibracja - przesuwaj robota nad linią...")
            if qc.send_command("CALIBRATE"):
                print("✓ Kalibracja zakończona")
        elif choice == 's':
            if qc.send_command("STATUS"):
                time.sleep(0.5)
                while qc.ser.in_waiting > 0:
                    line = qc.ser.readline().decode('utf-8', errors='ignore').strip()
                    print(line)
        elif choice == 'p':
            if qc.send_command("P"):
                print("✓ Robot uruchomiony - jedzie po linii!")
        elif choice == 'x':
            if qc.send_command("S"):
                print("✓ Robot zatrzymany")
        elif choice == 't':
            if qc.send_command("TELEMETRY_ON"):
                print("✓ Telemetria włączona")
                print("Odczytywanie telemetrii (Ctrl+C aby przerwać)...")
                try:
                    while True:
                        if qc.ser.in_waiting > 0:
                            line = qc.ser.readline().decode('utf-8', errors='ignore').strip()
                            if not line.endswith('#'):
                                print(line)
                        time.sleep(0.01)
                except KeyboardInterrupt:
                    print("\n")
        else:
            print("Nieznana opcja")
    
    if qc.ser and qc.ser.is_open:
        qc.ser.close()
    print("\nPołączenie zamknięte")

if __name__ == "__main__":
    main()
