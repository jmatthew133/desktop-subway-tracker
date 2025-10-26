Components:
- Raspberry Pi 3B
- Waveshare 7.5in d-Paper Display (800x480)

Software:
- Running in python3 venv with system-site-packages = true
  - need this for local Raspi install of lgpio
- Other installs likely needed to venv
  - spidev
  - nyct-gtfs
- Install waveshare software via https://github.com/waveshare/e-Paper.git
  - add python lib to PYTHONPATH env variable for access to epd7in5_V2

Running:
- `python3 main.py`
