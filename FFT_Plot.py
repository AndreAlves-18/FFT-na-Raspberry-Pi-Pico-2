import sys
import serial
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore

# Configurações da porta serial
SERIAL_PORT = '/dev/ttyACM0'  # ajuste conforme seu sistema
BAUD_RATE = 115200

# Eixo X logarítmico
class LogAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [f"{10**v:.0f}" if v > 0 else "1" for v in values]

class FFTSerialPlotter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FFT em Tempo Real (Escala Log)")
        self.resize(800, 600)

        # Substitui eixo X por eixo log
        log_axis = LogAxisItem(orientation='bottom')
        self.plot_widget = pg.PlotWidget(title="Espectro FFT", axisItems={'bottom': log_axis})
        self.setCentralWidget(self.plot_widget)
        self.plot_widget.setLabel('bottom', 'Frequência (Hz)')
        self.plot_widget.setLabel('left', 'Magnitude (dB)')
        self.plot_widget.showGrid(x=True, y=True)

        self.curve = self.plot_widget.plot(pen='y', symbol=None)

        # Serial
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            print(f"[INFO] Porta serial {SERIAL_PORT} aberta.")
        except serial.SerialException:
            print(f"[ERRO] Não foi possível abrir {SERIAL_PORT}.")
            sys.exit(1)

        # Buffer para armazenar linhas do pacote FFT
        self.reading_fft = False
        self.freqs = []
        self.mags = []

        # Timer para leitura serial e atualização
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.timer.start(10)

    def read_serial(self):
        while self.ser.in_waiting:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                if line == "---FFT_START---":
                    self.reading_fft = True
                    self.freqs = []
                    self.mags = []
                    continue

                if line == "---FFT_END---":
                    self.reading_fft = False
                    self.update_plot()
                    continue

                if self.reading_fft:
                    parts = line.split(',')
                    if len(parts) == 2:
                        try:
                            f = float(parts[0])
                            m = float(parts[1])
                            if f > 0:
                                self.freqs.append(np.log10(f))  # transformação log10 para escala log
                                self.mags.append(m)
                        except ValueError:
                            print(f"[WARNING] Valor inválido: {line}")
                    else:
                        print(f"[WARNING] Linha inesperada: {line}")
            except Exception as e:
                print(f"[ERROR] Exceção ao ler serial: {e}")

    def update_plot(self):
        if self.freqs and self.mags:
            self.curve.setData(self.freqs, self.mags)
            # print(f"[INFO] Gráfico atualizado com {len(self.freqs)} pontos.")

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_win = FFTSerialPlotter()
    main_win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

