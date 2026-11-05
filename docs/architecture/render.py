"""Make the dark versions of the architecture diagrams: python docs/architecture/render.py

Each diagram is drawn by hand with the light palette. Run this after changing one.
"""

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DARK_COLOURS = {
    "#FEFEFE": "#0D1117", "#111111": "#FFFFFF",
    "#FFFFFF": "#1F1E18", "#33322E": "#ECEBE4", "#24231F": "#ECEBE4",
    "#FFF4EC": "#3A2418", "#C8501A": "#F0814A", "#3A2A20": "#FCE9DD",
    "#F1EEFF": "#2A2350", "#6A57C7": "#A99BF0", "#2C2360": "#EDEAFF",
    "#EAF3FF": "#14304D", "#2F6FB3": "#6FB0F0", "#16324F": "#E3F0FF",
    "#F6F5F1": "#2A2922", "#8A877E": "#A3A097",
    "#FFF9E6": "#3A2F10", "#A87A00": "#E0B45F", "#4A3700": "#FBEFCF",
}

for source in HERE.glob("*.svg"):
    if source.stem.endswith("-dark"):
        continue
    text = re.sub("|".join(DARK_COLOURS), lambda found: DARK_COLOURS[found.group(0)], source.read_text())
    (HERE / f"{source.stem}-dark.svg").write_text(text)
