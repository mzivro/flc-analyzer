# Ferroelectric Liquid Crystals Measurement Tool

A Python-based application for measuring and analyzing parameters of ferroelectric liquid crystals using the electric field reversal method.

## Features

- Automatic analysis of oscilloscope voltage-time data
- Detection of characteristic switching points
- Calculation of key parameters (e.g., spontaneous polarization)
- Visualization of measurement data

## Methodology

This tool is based on the electric field reversal method, widely used in the study of ferroelectric liquid crystals. It automates data processing and analysis to standardize measurements and reduce manual workload.

## Technologies Used

- Python 3.10+
- Tkinter
- Matplotlib
- NumPy
- PyVISA

## Installation
For Windows:
```bash
git clone https://github.com/mzivro/flc-analyzer.git
cd flc-analyzer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

For Linux:
```bash
git clone https://github.com/mzivro/flc-analyzer.git
cd flc-analyzer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## License

MIT – free for educational and research use

## References

Vaksman, V., & Panarin, Y. (1992). Measurement of ferroelectric liquid crystal parameters. [https://doi.org/10.21427/D7FF8R](https://doi.org/10.21427/D7FF8R)

Panov, V., Vij, J. K., & Shtykov, N. M. (2001). A field-reversal method for measuring the parameters of a ferroelectric liquid crystal. Liquid Crystals, 28(4), 615-620. [https://doi.org/10.1080/02678290010020175](https://doi.org/10.1080/02678290010020175)