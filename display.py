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
        f = font_m  # Use same font size for all weather lines
        draw.text((left_pad, y), line, font=f, fill=0)
        y += (f.size + 4)
        if y > HEIGHT - 80:  # Leave room for fact at bottom
            break
    
    # Left: Daily fact (at bottom left)
    # Fact of the day header (bold with larger font)
    header_y = HEIGHT - 135
    draw.text((left_pad, header_y), "Fact of the day:", font=font_m, fill=0)
    
    fact_y = header_y + font_m.size + 6
    # Wrap fact text to fit left column width (max 5 lines)
    left_col_width = int(MID_X - left_pad * 2)
    wrapped_fact = _wrap_text(daily_fact, font_s, left_col_width, max_lines=5)
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

def draw_right_half_only(epd, full_img, transit_lines):
    """
    Update only the right half (transit info) with partial refresh.
    Creates a cropped 400x480 image, renders transit content, then partial-updates display.
    """
    # Create a 400x480 image for the right half
    right_img = Image.new("1", (400, 480), 255)  # white background
    draw = ImageDraw.Draw(right_img)
    
    font_s = ImageFont.truetype(FONT_PATH, FONT_S)
    font_m = ImageFont.truetype(FONT_PATH, FONT_M)
    
    # Center divider (left edge of this cropped image)
    draw.line([(0, 0), (0, 480)], fill=0, width=1)
    
    # Right: Transit with logo
    # Need to paste logo into the cropped image
    if MTA_LOGO.exists():
        logo = Image.open(MTA_LOGO).convert("RGBA")
        alpha = logo.split()[-1]
        mask = alpha.point(lambda a: 255 if a > 0 else 0)
        # Logo x position: centered in the 400px right half, accounting for logo width
        x = (400 - logo.width) // 2
        right_img.paste(logo, (x, 8), mask)
    
    right_pad = 32
    y = 8 + (Image.open(MTA_LOGO).height if MTA_LOGO.exists() else 60) + 10

    line_h = font_m.size + 6
    for line in transit_lines:
        draw.text((right_pad, y), line, font=font_m, fill=0)
        y += line_h
        if y > 480 - (font_s.size + 14):
            break

    # Bottom-right: Footer (last updated)
    stamp = current_date_time_string()
    draw.text((400 - 8, 480 - 10), stamp, font=font_s, fill=0, anchor="rb")
    
    # Get buffer from cropped image and partial refresh
    buf = epd.getbuffer(right_img)
    epd.display_Partial(buf, 400, 0, 800, 480)


def draw_right_half_only_debug(epd, full_img, transit_lines):
    """Debug version: draw simple test pattern to verify coordinates."""
    # Create a 400x480 image for the right half
    right_img = Image.new("1", (400, 480), 255)
    draw = ImageDraw.Draw(right_img)
    
    font_s = ImageFont.truetype(FONT_PATH, FONT_S)
    font_m = ImageFont.truetype(FONT_PATH, FONT_M)
    
    # Center divider (left edge)
    draw.line([(0, 0), (0, 480)], fill=0, width=1)
    
    # Draw vertical test lines to check coordinate mapping
    for y in range(0, 480, 50):
        draw.line([(10, y), (390, y)], fill=0, width=2)
    
    # Draw test text at known positions
    draw.text((32, 50), "TEST TOP", font=font_m, fill=0)
    draw.text((32, 150), "TEST MID", font=font_m, fill=0)
    draw.text((32, 250), "TEST BOT", font=font_m, fill=0)
    
    # Test footer
    draw.text((400 - 8, 480 - 10), "TEST FOOTER", font=font_s, fill=0, anchor="rb")
    
    # Get buffer from cropped image and partial refresh
    buf = epd.getbuffer(right_img)
    epd.display_Partial(buf, 400, 0, 800, 480)


def draw_left_half_only(epd, full_img, weather_lines, daily_fact=""):
    """
    Update only the left half (weather + fact) with partial refresh.
    Creates a cropped 400x480 image, renders weather content, then partial-updates display.
    """
    # Create a 400x480 image for the left half
    left_img = Image.new("1", (400, 480), 255)  # white background
    draw = ImageDraw.Draw(left_img)
    
    font_s = ImageFont.truetype(FONT_PATH, FONT_S)
    font_m = ImageFont.truetype(FONT_PATH, FONT_M)
    
    # Center divider (right edge of this cropped image)
    draw.line([(400, 0), (400, 480)], fill=0, width=1)
    
    # Left: Weather
    left_pad = 16
    y = 16
    for i, line in enumerate(weather_lines):
        f = font_m  # Use same font size for all weather lines
        draw.text((left_pad, y), line, font=f, fill=0)
        y += (f.size + 4)
        if y > 480 - 80:  # Leave room for fact at bottom
            break
    
    # Left: Daily fact (at bottom left)
    # Fact of the day header (bold with larger font)
    header_y = 480 - 135
    draw.text((left_pad, header_y), "Fact of the day:", font=font_m, fill=0)
    
    fact_y = header_y + font_m.size + 6
    # Wrap fact text to fit left column width (max 5 lines)
    left_col_width = 400 - left_pad * 2
    wrapped_fact = _wrap_text(daily_fact, font_s, left_col_width, max_lines=5)
    for line in wrapped_fact:
        draw.text((left_pad, fact_y), line, font=font_s, fill=0)
        fact_y += (font_s.size + 3)
        if fact_y > 480 - 15:
            break
    
    # Get buffer from cropped image and partial refresh
    buf = epd.getbuffer(left_img)
    epd.display_Partial(buf, 0, 0, 400, 480)

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

def test_partial_refresh(epd):
    """
    Sanity test for display_Partial():
    - Fill screen with white
    - Draw a small black box at known coordinates (100, 50) to (200, 150)
    - Call display_Partial with those exact coordinates
    - The black box should appear without distortion at that location
    """
    print("\n=== Testing display_Partial ===")
    
    # Create full 800x480 white image
    img = Image.new("1", (WIDTH, HEIGHT), 255)  # 255 = white
    draw = ImageDraw.Draw(img)
    
    # Draw small black box at (100, 50) to (200, 150)
    box_x_start, box_y_start = 100, 50
    box_x_end, box_y_end = 200, 150
    draw.rectangle([box_x_start, box_y_start, box_x_end, box_y_end], fill=0)  # 0 = black
    
    print(f"Drew black box: x={box_x_start}-{box_x_end}, y={box_y_start}-{box_y_end}")
    
    # Get full buffer
    buf = epd.getbuffer(img)
    
    # Try partial refresh
    print("Calling display_Partial...")
    try:
        epd.display_Partial(buf, box_x_start, box_y_start, box_x_end, box_y_end)
        print("✓ display_Partial() succeeded")
    except Exception as e:
        print(f"✗ display_Partial() failed: {e}")
        return
    
    # Now display full image to compare
    print("Displaying full image for comparison...")
    epd.display(buf)
