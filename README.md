Components:
- Raspberry Pi 3B
- [Waveshare 7.5in d-Paper Display](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual?srsltid=AfmBOorY7zlVESQsZ1XoE-7oDZPVm4z4jNEZuNF3A8wPKTR5KW4Ui928&utm_source=chatgpt.com) (800x480) 

Software:
- Running in python3 venv with system-site-packages = true
  - need this for local Raspi install of lgpio
- Other dependencies needed to install to venv
  - spidev
  - nyct-gtfs
  - betterepd7in5 - we are using this instead of the official drivers because they have better support for partial display refreshes
  - groq

Running:
- `python3 main.py`

Running as a service (boot-time autostart, no SSH/manual start needed):
- Not committed to this repo — the unit file needs a machine-specific deployment path, so it's created directly on the Pi rather than checked in.
- Uses a **systemd user unit** (`~/.config/systemd/user/subway-tracker.service`), pointing `WorkingDirectory=`/`ExecStart=` at wherever this repo + its venv live, with `Restart=on-failure` for crash recovery.
- User units need `sudo loginctl enable-linger <user>` once so they start at boot without a login session.
- Logs: `journalctl --user -u subway-tracker.service -f`. Stop/restart: `systemctl --user stop|restart subway-tracker.service` (the app catches `SIGTERM` and clears/sleeps the e-ink display before exiting, same as `Ctrl+C`).




