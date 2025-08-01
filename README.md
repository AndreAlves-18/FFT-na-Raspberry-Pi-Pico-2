# FFT Logger com Raspberry Pi Pico

Este projeto realiza a aquisição e gravação de espectros de frequência de sinais elétricos usando a Transformada Rápida de Fourier (FFT) implementada na Raspberry Pi Pico. Os dados são enviados via porta serial e salvos automaticamente no computador para futura análise.

---

## Objetivo

Registrar e analisar o comportamento espectral de cargas eletroeletrônicas conectadas a sensores via Raspberry Pi Pico. O sistema calcula a FFT embarcada e transmite os dados para o PC.

---

## Estrutura do Projeto

├── fft.ino -> Código da Pico (Arduino) que envia a FFT pela serial<br>
├── salvar_fft.py -> Script Python para registrar os dados em CSV<br>
├── FFT_Plot.py -> Script de visualização da FFT<br>
├── BD/ -> Conjunto de arquivos CSV com medições reais de equipamentos<br>
│ ├── airfryer.csv<br>
│ ├── carregador_de_celular.csv<br>
│ ├── ...<br>
├── Relatório.pdf -> Relatório explicativo do projeto (FFT na Pico)<br>

