#include <Arduino.h>
#include <arduinoFFT.h>
#include <math.h>

// Configuração do ADC 
const uint8_t PIN_LOAD = A0;  
constexpr float    V_REF   = 3.3f;
constexpr uint16_t ADC_MAX = 4095;

//FFT
constexpr uint16_t N_AMOSTRA   = 1024;    // potência de 2 (≤ 4096)
constexpr double   FREQ_AMOS = 8000.0;  // Hz

static double vReal[N_AMOSTRA];
static double vImag[N_AMOSTRA];
ArduinoFFT FFT(vReal, vImag, N_AMOSTRA, FREQ_AMOS);

// Envio a cada FFT_PERIOD_MS
constexpr uint32_t FFT_PERIOD_MS = 500; //  Período entre execuções da FFT.
uint32_t lastFFTMs = 0;

// Funções Auxiliares 
inline float adcRawToVoltage(uint16_t raw) {
    return (static_cast<float>(raw) * V_REF) / static_cast<float>(ADC_MAX);
}

void performFFTandSend() {
    const uint32_t samplePeriodUs = static_cast<uint32_t>(1e6 / FREQ_AMOS); // Calcula o intervalo entre amostras.
    uint32_t t0 = micros();
    double sum = 0.0;

    // Aquisição do sinal
    for (uint16_t i = 0; i < N_AMOSTRA; ++i) {
        while ((micros() - t0) < i * samplePeriodUs) {
            /* busy‑wait */
        }
        double sample = adcRawToVoltage(analogRead(PIN_LOAD));
        vReal[i] = sample;
        vImag[i] = 0.0;
        sum += sample;
    }

    // Remove componente DC
    double dc = sum / N_AMOSTRA;
    for (uint16_t i = 0; i < N_AMOSTRA; ++i) vReal[i] -= dc;

    // FFT
    FFT.windowing(FFT_WIN_TYP_HANN, FFT_FORWARD); //Aplica janela de Hann (minimiza efeitos de descontinuidade).
    FFT.compute(FFT_FORWARD); //Executa a FFT.
    FFT.complexToMagnitude(); // Converte os resultados para magnitudes (módulo dos vetores complexos)

    // Transmissão UART
    Serial.println("---FFT_START---");

    const double freqResolution = FREQ_AMOS / N_AMOSTRA; // Hz por bin
    for (uint16_t i = 1; i < (N_AMOSTRA / 2); ++i) {       // bin 0 é DC
        double freq = i * freqResolution;
        double mag  = vReal[i];           // volts (pico)
        
        Serial.print(freq, 2);
        Serial.print(',');
        Serial.println(mag, 6);
    }

    Serial.println("---FFT_END---");
}

// --------------------------------------------------
void setup() {
    Serial.begin(115200);
    analogReadResolution(12);
    pinMode(PIN_LOAD, INPUT);
    delay(500);
}

void loop() {
    uint32_t now = millis();
    if (now - lastFFTMs >= FFT_PERIOD_MS) {
        lastFFTMs = now;
        performFFTandSend();
    }
}
