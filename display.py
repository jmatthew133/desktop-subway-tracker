from waveshare_epd import epd7in5_V2 as epd7in5
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from time_util import current_time_string, current_date_time_string
from pathlib import Path

WIDTH, HEIGHT = 800, 480
MID_X = WIDTH / 2

# Should be pre-installed on raspberry pi os
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SIZE = 17
FONT_S, FONT_M, FONT_L = 16, 20, 24

HERE = Path(__file__).resolve().parent
MTA_LOGO = HERE / "assets" / "MTA_LOGO.png"

def init_display():
    epd = epd7in5.EPD()
    epd.init()
    epd.Clear()
    return epd

def _wrap_text(text, font, max_width, max_lines=3):
    """Wrap text to fit within max_width pixels. Returns list of lines, truncated to max_lines."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0]
        
        if line_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                if len(lines) >= max_lines:
                    return lines
            current_line = [word]
    
    if current_line and len(lines) < max_lines:
        lines.append(" ".join(current_line))
    
    return lines

def _paste_logo(canvas, top_y=8):
    if not MTA_LOGO.exists():
        return
    logo = Image.open(MTA_LOGO).convert("RGBA")
    # Fancy masking to get the logo to show on the display,
    # otherwise its a black box - thanks chat gippity
    alpha = logo.split()[-1]
    mask = alpha.point(lambda a: 255 if a > 0 else 0)
    
    x = MID_X + (WIDTH - MID_X - logo.width) // 2
    canvas.paste(logo, (int(x), top_y), mask)

def draw_weather_and_transit_lines(epd, weather_lines, transit_lines, daily_fact=""):
    img = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    font_s = ImageFont.truetype(FONT_PATH, FONT_S)
    font_m = ImageFont.truetype(FONT_PATH, FONT_M)
    font_l = ImageFont.truetype(FONT_PATH, FONT_L)

    # Center divider
    draw.line([(MID_X, 0), (MID_X, HEIGHT)], fill=0, width=1)

    # Left: Weather
    left_pad = 16
    y = 16
    for i, line in enumerate(weather_lines):
        f = font_l if (i == 0 | i == 1) else font_m
        draw.text((left_pad, y), line, font=f, fill=0)
        y += (f.size + 8)
        if y > HEIGHT - 80:  # Leave room for fact at bottom
            break
    
    # Left: Daily fact (at bottom left)
    fact_y = HEIGHT - 85
    # Wrap fact text to fit left column width (max 3 lines)
    left_col_width = int(MID_X - left_pad * 2)
    wrapped_fact = _wrap_text(daily_fact, font_s, left_col_width, max_lines=3)
    for line in wrapped_fact:
        draw.text((left_pad, fact_y), line, font=font_s, fill=0)
        fact_y += (font_s.size + 3)
        if fact_y > HEIGHT - 15:
            break

    # Right: Transit
    _paste_logo(img, top_y=8)
    right_pad = 32
    y = 8 + (Image.open(MTA_LOGO).height if MTA_LOGO.exists() else 60) + 10

    line_h = font_m.size + 6
    for line in transit_lines:
        draw.text((MID_X + right_pad, y), line, font=font_m, fill=0)
        y += line_h
        if y > HEIGHT - (font_s.size + 14):
            break

    # Bottom-right: Footer (last updated)
    stamp = current_date_time_string()
    draw.text((WIDTH - 8, HEIGHT - 10),
              stamp, font=font_s, fill=0, anchor="rb")

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
