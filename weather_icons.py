# Weather Icons by Erik Flowers (https://erikflowers.github.io/weather-icons/),
# font licensed under SIL OFL 1.1. Font asset committed at assets/weathericons-regular-webfont.ttf.
#
# This module is the only place that knows how weather icons are actually rendered. If the
# icon set is ever swapped out, only ICON_GLYPHS / _load_icon_font / draw_weather_icon need to
# change; display.py just calls draw_weather_icon() with an icon_key and doesn't know or care
# how the glyph is produced.
from pathlib import Path
from PIL import ImageFont

HERE = Path(__file__).resolve().parent
FONT_PATH = HERE / "assets" / "weathericons-regular-webfont.ttf"

# Codepoints from the project's weather-icons.css.
ICON_GLYPHS = {
    "clear": "\uf00d",
    "partly_cloudy": "\uf002",
    "cloudy": "\uf013",
    "fog": "\uf014",
    "drizzle": "\uf01c",
    "rain": "\uf019",
    "showers": "\uf01a",
    "snow": "\uf01b",
    "thunderstorm": "\uf01e",
}
DEFAULT_ICON = "cloudy"

_font_cache = {}

def _load_icon_font(size):
    size = int(size)
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(str(FONT_PATH), size)
    return _font_cache[size]

def draw_weather_icon(draw, cx, cy, size, icon_key):
    glyph = ICON_GLYPHS.get(icon_key, ICON_GLYPHS[DEFAULT_ICON])
    font = _load_icon_font(size * 0.85)
    bbox = draw.textbbox((0, 0), glyph, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = cx - w / 2 - bbox[0]
    y = cy - h / 2 - bbox[1]
    draw.text((x, y), glyph, font=font, fill=0)
