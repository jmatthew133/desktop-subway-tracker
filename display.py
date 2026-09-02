import betterepd7in5
from PIL import Image, ImageDraw, ImageFont
from time_util import current_date_time_string
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
    return betterepd7in5.EPD(betterepd7in5.RaspberryPi())

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

def _paste_logo(canvas, top_y=8, right_aligned=False):
    if not MTA_LOGO.exists():
        return
    logo = Image.open(MTA_LOGO).convert("RGBA")
    # Fancy masking to get the logo to show on the display,
    # otherwise its a black box - thanks chat gippity
    alpha = logo.split()[-1]
    mask = alpha.point(lambda a: 255 if a > 0 else 0)
    
    if right_aligned:
        x = WIDTH - 32 - logo.width
    else:
        x = MID_X + (WIDTH - MID_X - logo.width) // 2
    canvas.paste(logo, (int(x), top_y), mask)


def _draw_right_header(draw, img, font):
    right_pad = 8
    top_y = 8
    draw.text((MID_X + right_pad, top_y), current_date_time_string(), font=font, fill=0)
    _paste_logo(img, top_y=top_y, right_aligned=True)
    return top_y + (Image.open(MTA_LOGO).height if MTA_LOGO.exists() else 60) + 10

# Draw the entire screen with a full refresh
def draw_weather_and_transit_lines(epd, img, weather_lines, transit_lines, outlook=""):
    img.paste(255, (0, 0, WIDTH, HEIGHT))
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
        f = font_m  # Use same font size for all weather lines
        draw.text((left_pad, y), line, font=f, fill=0)
        y += (f.size + 4)
        if y > HEIGHT - 80:  # Leave room for fact at bottom
            break
    
    # Left: Weather outlook (at bottom left)
    header_y = HEIGHT - 135
    draw.text((left_pad, header_y), "Outlook:", font=font_m, fill=0)
    
    fact_y = header_y + font_m.size + 6
    # Wrap outlook text to fit left column width (max 5 lines)
    left_col_width = int(MID_X - left_pad * 2)
    wrapped_outlook = _wrap_text(outlook, font_s, left_col_width, max_lines=5)
    for line in wrapped_outlook:
        draw.text((left_pad, fact_y), line, font=font_s, fill=0)
        fact_y += (font_s.size + 3)
        if fact_y > HEIGHT - 15:
            break

    # Right: Timestamp, logo, and transit
    y = _draw_right_header(draw, img, font_l)
    right_pad = 32

    line_h = font_m.size + 6
    for line in transit_lines:
        draw.text((MID_X + right_pad, y), line, font=font_m, fill=0)
        y += line_h
        if y > HEIGHT - (font_s.size + 14):
            break

    with epd.display_bilevel_full_refresh() as display:
        display(img)

# Draw only the right half of the display with a partial refresh, for updating transit info which changes often
def draw_right_half_only(epd, img, transit_lines):
    draw = ImageDraw.Draw(img)
    font_s = ImageFont.truetype(FONT_PATH, FONT_S)
    font_m = ImageFont.truetype(FONT_PATH, FONT_M)
    
    # Clear right half (white)
    draw.rectangle([int(MID_X), 0, WIDTH, HEIGHT], fill=255)
    
    # Center divider
    draw.line([(MID_X, 0), (MID_X, HEIGHT)], fill=0, width=1)
    
    # Right: Timestamp, logo, and transit
    font_l = ImageFont.truetype(FONT_PATH, FONT_L)
    y = _draw_right_header(draw, img, font_l)
    right_pad = 32

    line_h = font_m.size + 6
    for line in transit_lines:
        draw.text((MID_X + right_pad, y), line, font=font_m, fill=0)
        y += line_h
        if y > HEIGHT - (font_s.size + 14):
            break

    with epd.display_bilevel_partial_refresh() as display:
        display(img)
