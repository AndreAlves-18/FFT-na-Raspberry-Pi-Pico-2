import serial
import csv
import time
import sys

# === Verifica argumento de linha de comando ===
if len(sys.argv) < 2:
    print("Uso: python salvar_fft.py nome_arquivo.csv")
    sys.exit(1)

CSV_FILE = sys.argv[1]

# === Configurações ===
PORT = '/dev/ttyACM0'     # ajuste conforme necessário
BAUD = 230400             # deve bater com o da Pico

# === Inicialização da porta serial ===
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
except serial.SerialException as e:
    print(f"Erro ao abrir a porta serial: {e}")
    sys.exit(1)

# === Cria o CSV e escreve o cabeçalho ===
with open(CSV_FILE, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['timestamp_pc_ms', 'frequencia_hz', 'magnitude'])

    print(f"Gravando FFT em {CSV_FILE}... Pressione Ctrl+C para parar.")

    try:
        while True:
            if ser.in_waiting:
                raw_line = ser.readline().decode(errors='ignore').strip()
                try:
                    freq, mag = map(float, raw_line.split(','))
                    timestamp = int(time.time() * 1000)
                    csv_writer.writerow([timestamp, freq, mag])
                    csv_file.flush()
                    print(f"{timestamp}, {freq}, {mag}")
                except ValueError:
                    pass  # ignora linhas malformadas
    except KeyboardInterrupt:
        print("\nGravação encerrada pelo usuário.")
    finally:
        ser.close()
