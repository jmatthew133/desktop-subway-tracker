Components:
- Raspberry Pi 3B
- Waveshare 7.5in d-Paper Display (800x480)

Software:
- Running in python3 venv with system-site-packages = true
  - need this for local Raspi install of lgpio
- Other installs likely needed to venv
  - spidev
  - nyct-gtfs
  - betterepd7in5
- Install the display driver in the venv:
  - `python3 -m pip install betterepd7in5`
  - experimenting with this one as well, for better support for `display_Partial`: https://github.com/hchargois/betterepd7in5/

Running:
- `python3 main.py`
