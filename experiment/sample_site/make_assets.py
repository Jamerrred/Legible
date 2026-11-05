"""Draw the price board and the service-area map. Run: uv run python -m sample_site.make_assets"""

from __future__ import annotations

from pathlib import Path

from business_core.business import load_facts
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "static" / "img"
FONT_DIR = "/System/Library/Fonts/Supplemental/"
NAVY = (22, 62, 92)
TEAL = (31, 122, 140)
INK = (35, 40, 45)
STRIPE = (236, 243, 246)
SIZES = ["small", "midsize", "large", "oversized"]

CLASS_KEY = [
    ("Class A", "Coupes, hatchbacks, compact cars (Civic, Corolla, Mini Cooper, Mazda3)"),
    ("Class B", "Sedans, crossovers, 2-row SUVs (Camry, Model 3, Model Y, CR-V, Outback)"),
    ("Class C", "3-row SUVs, minivans, compact vans, standard pickups"),
    ("", "(Highlander, Tahoe, Odyssey, Transit Connect, Tacoma, F-150, Ram 1500)"),
    ("Class D", "Full-size cargo and passenger vans, extended SUVs, heavy-duty pickups"),
    ("", "(Transit, Sprinter, ProMaster, Express, Suburban, F-250, Ram 2500)"),
]


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_DIR + ("Arial Bold.ttf" if bold else "Arial.ttf"), size)


def price_board() -> None:
    model = load_facts("sunrise")["pricing_model"]
    image = Image.new("RGB", (1100, 1130), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1100, 100), fill=NAVY)
    draw.text((550, 50), "Packages & Prices", font=font(46, True), fill="white", anchor="mm")
    columns = [530, 670, 810, 950]

    def header(y: int, title: str) -> int:
        draw.rectangle((40, y, 1060, y + 48), fill=TEAL)
        draw.text((58, y + 24), title, font=font(25, True), fill="white", anchor="lm")
        for x, label in zip(columns, ["Class A", "Class B", "Class C", "Class D"], strict=True):
            draw.text((x, y + 24), label, font=font(23, True), fill="white", anchor="mm")
        return y + 48

    y = header(125, "Package")
    for index, service in enumerate(model["services"].values()):
        if index % 2:
            draw.rectangle((40, y, 1060, y + 54), fill=STRIPE)
        draw.text((58, y + 27), service["marketing_name"], font=font(27, True), fill=INK, anchor="lm")
        for x, size in zip(columns, SIZES, strict=True):
            draw.text((x, y + 27), f"${service['prices'][size]}", font=font(27), fill=INK, anchor="mm")
        y += 54

    y = header(y + 30, "Add-ons")
    for index, addon in enumerate(model["addons"].values()):
        if index % 2:
            draw.rectangle((40, y, 1060, y + 50), fill=STRIPE)
        draw.text((58, y + 25), addon["label"].split(",")[0], font=font(24), fill=INK, anchor="lm")
        if "prices" in addon:
            for x, size in zip(columns, SIZES, strict=True):
                draw.text((x, y + 25), f"${addon['prices'][size]}", font=font(24), fill=INK, anchor="mm")
        elif "range" in addon:
            low, high = addon["range"]["low"], addon["range"]["high"]
            draw.text((740, y + 25), f"${low} (1 hour ozone) or ${high} (2 hour ozone)", font=font(24), fill=INK, anchor="mm")
        else:
            draw.text((740, y + 25), f"${addon['flat']} per pair, any size", font=font(24), fill=INK, anchor="mm")
        y += 50

    y += 30
    draw.text((40, y), "What class is my vehicle?", font=font(27, True), fill=NAVY)
    y += 42
    for label, text in CLASS_KEY:
        draw.text((40, y), label, font=font(21, True), fill=INK)
        draw.text((140, y), text, font=font(21), fill=INK)
        y += 32
    image = image.crop((0, 0, 1100, y + 20))
    image.save(OUT / "packages.png")


def area_map() -> None:
    water, land = (205, 226, 238), (238, 233, 220)
    home, further = (31, 122, 140), (150, 203, 208)
    image = Image.new("RGB", (900, 620), water)
    draw = ImageDraw.Draw(image)
    # Land first, then the shaded regions we go to.
    draw.polygon([(150, 0), (430, 0), (445, 120), (365, 195), (300, 190), (215, 110)], fill=land)
    draw.polygon([(250, 232), (395, 222), (440, 430), (525, 620), (290, 620), (240, 400)], fill=land)
    draw.polygon([(560, 0), (900, 0), (900, 620), (705, 620), (610, 420), (570, 250)], fill=land)
    draw.polygon([(255, 120), (430, 95), (445, 120), (365, 195), (300, 190)], fill=further)
    draw.polygon([(245, 330), (408, 320), (440, 430), (432, 480), (268, 480), (240, 400)], fill=further)
    draw.polygon([(565, 150), (770, 140), (790, 390), (605, 400), (570, 250)], fill=further)
    draw.polygon([(250, 232), (395, 222), (408, 320), (245, 330)], fill=home)
    draw.ellipse((470, 205, 500, 240), fill=further, outline=TEAL)
    draw.text((327, 276), "San Francisco", font=font(21, True), fill="white", anchor="mm")
    draw.text((340, 405), "Peninsula", font=font(26, True), fill=NAVY, anchor="mm")
    draw.text((340, 150), "Marin", font=font(26, True), fill=NAVY, anchor="mm")
    draw.text((680, 270), "East Bay", font=font(26, True), fill=NAVY, anchor="mm")
    draw.text((485, 192), "Treasure Island", font=font(20, True), fill=NAVY, anchor="mm")
    image.save(OUT / "area.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    price_board()
    area_map()
