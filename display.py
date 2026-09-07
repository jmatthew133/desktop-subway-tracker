import betterepd7in5
from PIL import Image, ImageDraw, ImageFont
from time_util import current_date_time_string, minutes_ago_string
from pathlib import Path
from weather_icons import draw_weather_icon

WIDTH, HEIGHT = 800, 480
MID_X = WIDTH / 2

# Should be pre-installed on raspberry pi os
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SIZE = 17
FONT_S, FONT_M, FONT_L, FONT_XL = 16, 20, 26, 38

HERE = Path(__file__).resolve().parent
MTA_LOGO = HERE / "assets" / "MTA_LOGO.png"

# Nimbus Sans is metric-compatible with Helvetica (the real MTA bullet typeface) and looks far
# closer than DejaVu; install via `apt install fonts-urw-base35` on Raspberry Pi OS. Falls back
# to DejaVu Bold, then DejaVu Regular, if unavailable.
FONT_PATH_BOLD_CANDIDATES = [
    "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

# Left column reserved for the bullet/label of each transit group; arrival times start after it.
GROUP_LABEL_WIDTH = 80
GROUP_TIMES_GAP = 28
GROUP_GAP = 20
BULLET_SIZE_RATIO = 0.75
TOP_TRANSIT_BUFFER = 44

# Weather icon column sized independently from the transit bullet column (per design decision).
WEATHER_ICON_COLUMN_WIDTH = 64
WEATHER_HERO_TEXT_GAP = 28
WEATHER_DAILY_TEXT_GAP = 18
WEATHER_HERO_ICON_SIZE = 90
WEATHER_DAILY_ICON_SIZE = 52
WEATHER_HERO_GAP = 16
WEATHER_DAILY_ROW_HEIGHT = 60
WEATHER_DAILY_ROW_GAP = 8

def init_display():
    return betterepd7in5.EPD(betterepd7in5.RaspberryPi())

def _load_bold_font(size):
    for path in FONT_PATH_BOLD_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.truetype(FONT_PATH, size)

def _wrap_text(text, font, max_width, max_lines=3):
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

def _draw_optically_centered_text(draw, cx, cy, label, font, fill):
    bbox = draw.textbbox((0, 0), label, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = cx - w / 2 - bbox[0]
    y = cy - h / 2 - bbox[1]
    draw.text((x, y), label, font=font, fill=fill)

def _fit_bold_font(draw, label, target_height):
    size = max(4, int(target_height))
    for _ in range(8):
        font = _load_bold_font(size)
        bbox = draw.textbbox((0, 0), label, font=font)
        height = bbox[3] - bbox[1]
        if height <= 0 or abs(height - target_height) < 1:
            break
        size = max(4, int(size * (target_height / height)))
    return font

def _fit_bold_font_by_width(draw, label, target_width, max_height=None):
    size = max(4, int(target_width))
    for _ in range(8):
        font = _load_bold_font(size)
        bbox = draw.textbbox((0, 0), label, font=font)
        width = bbox[2] - bbox[0]
        if width <= 0 or abs(width - target_width) < 1:
            break
        size = max(4, int(size * (target_width / width)))
    if max_height is not None:
        bbox = draw.textbbox((0, 0), label, font=font)
        height = bbox[3] - bbox[1]
        if height > max_height:
            size = max(4, int(size * (max_height / height)))
            font = _load_bold_font(size)
    return font

def _draw_line_bullet(draw, cx, cy, label, diameter):
    r = diameter / 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=0)
    font = _fit_bold_font(draw, label, diameter * 0.62)
    _draw_optically_centered_text(draw, cx, cy, label, font, fill=255)

def _draw_weather_hero(draw, x, y, today, font_l):
    line_h = font_l.size + 6
    lines = [
        f"{today['temp']}°F (feels {today['feels_like']}°F)",
        f"Precip: {today['precip_chance']}%",
        f"H:{today['high']}°  L:{today['low']}°",
    ]
    block_height = max(WEATHER_HERO_ICON_SIZE, len(lines) * line_h)
    center_x = x + WEATHER_ICON_COLUMN_WIDTH / 2
    center_y = y + block_height / 2
    draw_weather_icon(draw, center_x, center_y, WEATHER_HERO_ICON_SIZE, today["icon"])

    text_x = x + WEATHER_ICON_COLUMN_WIDTH + WEATHER_HERO_TEXT_GAP
    ty = y
    for line in lines:
        draw.text((text_x, ty), line, font=font_l, fill=0)
        ty += line_h

    return y + block_height

def _draw_weather_forecast_row(draw, x, y, day, font_l):
    row_height = WEATHER_DAILY_ROW_HEIGHT
    center_x = x + WEATHER_ICON_COLUMN_WIDTH / 2
    center_y = y + row_height / 2
    draw_weather_icon(draw, center_x, center_y, WEATHER_DAILY_ICON_SIZE, day["icon"])

    text_x = x + WEATHER_ICON_COLUMN_WIDTH + WEATHER_DAILY_TEXT_GAP
    label = f"{day['day']}   {day['high']}° / {day['low']}°"
    bbox = draw.textbbox((0, 0), label, font=font_l)
    text_y = center_y - (bbox[3] - bbox[1]) / 2 - bbox[1]
    draw.text((text_x, text_y), label, font=font_l, fill=0)

    return y + row_height + WEATHER_DAILY_ROW_GAP

def _draw_transit_group(draw, x, y, group, font_m, line_h):
    times = group["times"] or ["No data"]
    block_height = len(times) * line_h
    center_x = x + GROUP_LABEL_WIDTH / 2
    center_y = y + block_height / 2

    if group["kind"] == "bullet":
        diameter = block_height * BULLET_SIZE_RATIO
        _draw_line_bullet(draw, center_x, center_y, group["label"], diameter)
    else:
        font = _fit_bold_font_by_width(
            draw, group["label"], GROUP_LABEL_WIDTH - 10, max_height=block_height * 0.85
        )
        _draw_optically_centered_text(draw, center_x, center_y, group["label"], font, fill=0)

    times_x = x + GROUP_LABEL_WIDTH + GROUP_TIMES_GAP
    ty = y
    for line in times:
        draw.text((times_x, ty), line, font=font_m, fill=0)
        ty += line_h

    return y + block_height + GROUP_GAP

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


def _draw_right_header(draw, img, time_font, date_font):
    right_pad = 32
    top_y = 8
    time_string, date_string = current_date_time_string().split("\n")
    header_x = MID_X + right_pad
    draw.text((header_x, top_y), time_string, font=time_font, fill=0)
    draw.text((header_x, top_y + time_font.size + 2), date_string, font=date_font, fill=0)
    _paste_logo(img, top_y=top_y, right_aligned=True)
    return top_y + (Image.open(MTA_LOGO).height if MTA_LOGO.exists() else 60) + TOP_TRANSIT_BUFFER

def _draw_last_updated(draw, font_s, last_transit_update):
    text = minutes_ago_string(last_transit_update)
    draw.text((WIDTH - 8, HEIGHT - 8), text, font=font_s, fill=0, anchor="rb")

# Draw the entire screen with a full refresh
def draw_weather_and_transit_lines(epd, img, weather_data, transit_lines, outlook="", last_transit_update=None):
    img.paste(255, (0, 0, WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    font_s = ImageFont.truetype(FONT_PATH, FONT_S)
    font_m = ImageFont.truetype(FONT_PATH, FONT_M)
    font_l = ImageFont.truetype(FONT_PATH, FONT_L)
    font_xl = ImageFont.truetype(FONT_PATH, FONT_XL)

    # Center divider
    draw.line([(MID_X, 0), (MID_X, HEIGHT)], fill=0, width=1)

    # Left: Weather
    left_pad = 16
    y = 16
    if weather_data:
        y = _draw_weather_hero(draw, left_pad, y, weather_data["today"], font_l)
        y += WEATHER_HERO_GAP
        for day in weather_data["forecast"]:
            y = _draw_weather_forecast_row(draw, left_pad, y, day, font_l)

    # Left: Weather outlook (at bottom left)
    header_y = HEIGHT - 135
    draw.text((left_pad, header_y), "Today's Outlook:", font=font_m, fill=0)
    
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
    y = _draw_right_header(draw, img, font_xl, font_l)
    right_pad = 32

    line_h = font_m.size + 10
    for group in transit_lines:
        y = _draw_transit_group(draw, MID_X + right_pad, y, group, font_m, line_h)
        if y > HEIGHT - (font_s.size + 14):
            break

    _draw_last_updated(draw, font_s, last_transit_update)

    with epd.display_bilevel_full_refresh() as display:
        display(img)

# Draw only the right half of the display with a partial refresh, for updating transit info which changes often
def draw_right_half_only(epd, img, transit_lines, last_transit_update=None):
    draw = ImageDraw.Draw(img)
    font_s = ImageFont.truetype(FONT_PATH, FONT_S)
    font_m = ImageFont.truetype(FONT_PATH, FONT_M)
    
    # Clear right half (white)
    draw.rectangle([int(MID_X), 0, WIDTH, HEIGHT], fill=255)
    
    # Center divider
    draw.line([(MID_X, 0), (MID_X, HEIGHT)], fill=0, width=1)
    
    # Right: Timestamp, logo, and transit
    font_l = ImageFont.truetype(FONT_PATH, FONT_L)
    font_xl = ImageFont.truetype(FONT_PATH, FONT_XL)
    y = _draw_right_header(draw, img, font_xl, font_l)
    right_pad = 32

    line_h = font_m.size + 10
    for group in transit_lines:
        y = _draw_transit_group(draw, MID_X + right_pad, y, group, font_m, line_h)
        if y > HEIGHT - (font_s.size + 14):
            break

    _draw_last_updated(draw, font_s, last_transit_update)

    with epd.display_bilevel_partial_refresh() as display:
        display(img)
