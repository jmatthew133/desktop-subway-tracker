from waveshare_epd import epd7in5_V2 as epd7in5
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 800, 480
MID = WIDTH / 2

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SIZE = 17

def init_display():
    epd = epd7in5.EPD()
    epd.init()
    epd.Clear()
    return epd

def _paste_logo(canvas, top_y=8):
    """Paste centered logo at top of right half. Assumes 1-bit PNG."""
    if not LOGO_PATH.exists():
        return
    logo = Image.open(LOGO_PATH).convert("1")
    right_x1, right_x2 = MID_X, WIDTH
    x = right_x1 + (right_x2 - right_x1 - logo.width) // 2
    canvas.paste(logo, (x, top_y))

def draw_weather_and_transit_lines(epd, weather_lines, transit_lines):
    """
    Left half:  weather_lines (drawn top-down)
    Right half: MTA logo (top), then transit_lines, then footer (last updated)
    All full-screen (no partial refresh yet).
    """
    img = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    font_s = ImageFont.truetype(FONT_PATH, FONT_S),
    font_m = ImageFont.truetype(FONT_PATH, FONT_M),
    font_l = ImageFont.truetype(FONT_PATH, FONT_L)

    # Center divider
    draw.line([(MID_X, 0), (MID_X, HEIGHT)], fill=0, width=1)

    # ----- LEFT: WEATHER -----
    left_pad = 16
    y = 16
    for i, line in enumerate(weather_lines):
        # First line larger for emphasis; others medium
        f = font_l if i == 0 else font_m
        draw.text((left_pad, y), line, font=f, fill=0)
        y += (f.size + 8)
        if y > HEIGHT - 16:
            break

    # ----- RIGHT: TRANSIT -----
    _paste_logo(img, top_y=8)
    right_pad = 16
    y = 8 + (Image.open(LOGO_PATH).height if LOGO_PATH.exists() else 60) + 10

    line_h = font_m.size + 6
    for line in transit_lines:
        draw.text((MID_X + right_pad, y), line, font=font_m, fill=0)
        y += line_h
        if y > HEIGHT - (font_s.size + 14):
            break  # keep room for footer

    # Footer (last updated) bottom-right
    stamp = datetime.now().strftime("Last updated — %a %b %d • %I:%M:%S %p")
    draw.text((MID_X + right_pad, HEIGHT - (font_s.size + 8)),
              stamp, font=font_s, fill=0)

    epd.display(epd.getbuffer(img))

def draw_lines(epd, lines):
    print("attempting draw lines to screen:")
    print(lines)
    print()
    
    image = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    y = 10
    
    for line in lines:
        draw.text((10, y), line, font=font, fill=0)
        y += FONT_SIZE + 5
    
    epd.display(epd.getbuffer(image))
    
def clear_and_sleep(epd):
    epd.init()
    epd.Clear()
    epd.sleep()
    GPIO.cleanup()
    print("Display cleared and GPIO released")
