from waveshare_epd import epd7in5_V2 as epd7in5
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 800, 480

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SIZE = 17

def init_display():
    epd = epd7in5.EPD()
    epd.init()
    epd.Clear()
    return epd

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