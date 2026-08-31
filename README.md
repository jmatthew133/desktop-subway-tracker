Components:
- Raspberry Pi 3B
- [Waveshare 7.5in d-Paper Display](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual?srsltid=AfmBOorY7zlVESQsZ1XoE-7oDZPVm4z4jNEZuNF3A8wPKTR5KW4Ui928&utm_source=chatgpt.com) (800x480) 

Software:
- Running in python3 venv with system-site-packages = true
  - need this for local Raspi install of lgpio
- Other installs likely needed to venv
  - spidev
  - nyct-gtfs
  - betterepd7in5 - we are using this instead of the official drivers because they have better support for partial display refreshes
- Install the display driver in the venv:
  - `python3 -m pip install betterepd7in5`

Running:
- `python3 main.py`
