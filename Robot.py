import serial
import time

# pip install pyserial

TIMEOUT = 1.0
MAX_RETRIES = 3
BACKOFF_BASE = 0.3

# otwarcie portu
def open_port(port, baudrate):
    ser = serial.Serial(port, baudrate, timeout=TIMEOUT)
    time.sleep(2)   # wystarczy 2 sekundy na reset Arduino
    return ser

def checksum(payload):  # suma kontrolna
    checksum = sum(ord(c) for c in payload) % 256
    return f"{checksum:02X}"

def frame(cmd, arg, ts):
    core = f":{cmd}|{arg}|{ts}"
    return core + checksum(core) + "\n"

def send_with_retry(ser, cmd, arg, ts):
    attempt, delay = 0, BACKOFF_BASE
    frame_str = frame(cmd, arg, ts)
    while attempt <= MAX_RETRIES:
        print(f">>> {frame_str.strip()}")
        ser.write(frame_str.encode())
        resp = ser.readline().decode(errors="ignore").strip()
        if resp:
            print(f"<<< {resp}")
            return resp  # odebrano odpowiedź
        time.sleep(delay); delay *= 2; attempt += 1
    return f"NACK|{ts}|TIMEOUT"  # brak odpowiedzi po kilku próbach

def main():
    PORT = input("Podaj port [COM4]: ").strip() or "COM4"
    BAUDRATE = int(input("Podaj baudrate [9600]: ").strip() or "9600")

    ts = 1
    history = []

    try:
        ser = open_port(PORT, BAUDRATE)
        print("Połączono z Arduino!")
        print(send_with_retry(ser, "H", "", ts)); ts += 1

        while True:
            line = input("> ").strip()
            if not line: 
                continue
            if line.lower() in ("quit", "q"):
                break
            if line.lower() == "help":
                print("Komendy: M <cm>, R <deg>, V <v>, S, B, I, H, status, save-log, quit")
                continue
            if line.lower() == "status":
                resp = send_with_retry(ser, "H", "", ts); ts += 1
                history.append(("H", resp))
                print(resp)
                continue
            if line.lower() == "save-log":
                with open("log.txt", "w") as f:
                    for s, r in history:
                        f.write(f"{s} -> {r}\n")
                print("Zapisano log do log.txt")
                continue

            parts = line.split(maxsplit=1)
            cmd = parts[0].upper()
            arg = parts[1] if len(parts) > 1 else ""
            if cmd not in ("M", "R", "V", "S", "B", "I", "H"):
                print("unknown cmd")
                continue

            frame_str = frame(cmd, arg, ts).strip()
            resp = send_with_retry(ser, cmd, arg, ts); ts += 1
            history.append((frame_str, resp))
            print(resp)

    except Exception as e:
        print("error:", e)
    finally:
        try:
            ser.close()
        except:
            pass

if __name__ == "__main__":
    main()
