"""Render the architecture diagrams to light and dark images: python docs/architecture/render.py

The .mmd files and system-overview.svg are the sources, written with the light palette. Needs
Node.js. Set PUPPETEER_EXECUTABLE_PATH to use a Chrome you already have. Run it again after changing
a diagram.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
DARK_COLOURS = {
    "#FFFFFF": "#1F1E18", "#33322E": "#ECEBE4", "#24231F": "#ECEBE4", "#55524A": "#C5C2B8",
    "#FFF4EC": "#3A2418", "#C8501A": "#F0814A", "#3A2A20": "#FCE9DD", "#FFFAF6": "#1E1510", "#8E3A12": "#F7B28C",
    "#F1EEFF": "#2A2350", "#6A57C7": "#A99BF0", "#2C2360": "#EDEAFF", "#FBFAFF": "#17142B", "#4A3BA0": "#C7BDF7",
    "#EAF3FF": "#14304D", "#2F6FB3": "#6FB0F0", "#16324F": "#E3F0FF", "#F5F9FF": "#0E1B2B", "#1F5288": "#A8D0F5",
    "#F6F5F1": "#2A2922", "#8A877E": "#A3A097", "#FBFAF7": "#191813",
    "#FFF9E6": "#3A2F10", "#A87A00": "#E0B45F", "#4A3700": "#FBEFCF",
    "rgb(255,250,246)": "rgb(30,21,16)", "rgb(245,249,255)": "rgb(14,27,43)", "rgb(251,250,247)": "rgb(25,24,19)",
}
THEMES = {
    "light": {
        "primaryColor": "#FFF4EC", "primaryBorderColor": "#C8501A", "primaryTextColor": "#24231F",
        "secondaryColor": "#F6F5F1", "tertiaryColor": "#FFFFFF", "lineColor": "#55524A", "textColor": "#24231F",
        "noteBkgColor": "#FFF9E6", "noteBorderColor": "#A87A00", "noteTextColor": "#4A3700",
        "actorBkg": "#FFF4EC", "actorBorder": "#C8501A", "actorTextColor": "#24231F", "actorLineColor": "#B9B6AC",
        "signalColor": "#33322E", "signalTextColor": "#24231F", "labelBoxBkgColor": "#F6F5F1", "labelBoxBorderColor": "#8A877E",
        "labelTextColor": "#24231F", "loopTextColor": "#24231F", "sequenceNumberColor": "#FFFFFF", "edgeLabelBackground": "#FFFFFF",
    },
    "dark": {
        "primaryColor": "#3A2418", "primaryBorderColor": "#F0814A", "primaryTextColor": "#ECEBE4",
        "secondaryColor": "#2A2922", "tertiaryColor": "#1F1E18", "lineColor": "#A3A097", "textColor": "#ECEBE4",
        "noteBkgColor": "#3A2F10", "noteBorderColor": "#E0B45F", "noteTextColor": "#FBEFCF",
        "actorBkg": "#3A2418", "actorBorder": "#F0814A", "actorTextColor": "#ECEBE4", "actorLineColor": "#55524A",
        "signalColor": "#ECEBE4", "signalTextColor": "#ECEBE4", "labelBoxBkgColor": "#2A2922", "labelBoxBorderColor": "#A3A097",
        "labelTextColor": "#ECEBE4", "loopTextColor": "#ECEBE4", "sequenceNumberColor": "#16150F", "edgeLabelBackground": "#0D1117",
    },
}


def render(source: Path, name: str) -> None:
    text = source.read_text()
    if name == "dark":
        for light, dark in DARK_COLOURS.items():
            text = text.replace(light, dark)
    config = {
        "theme": "base",
        "themeVariables": {**THEMES[name], "fontFamily": FONT, "fontSize": "15px"},
        "flowchart": {"curve": "basis", "nodeSpacing": 34, "rankSpacing": 58, "padding": 14},
        "sequence": {"mirrorActors": False, "messageMargin": 32, "boxMargin": 8, "width": 130, "actorMargin": 20, "noteMargin": 8, "messageFontSize": 16, "noteFontSize": 15, "actorFontSize": 16},
    }
    with tempfile.TemporaryDirectory() as folder:
        diagram, settings = Path(folder) / "diagram.mmd", Path(folder) / "config.json"
        diagram.write_text(text)
        settings.write_text(json.dumps(config))
        output = HERE / f"{source.stem}-{name}.png"
        env = {**os.environ, "PUPPETEER_SKIP_DOWNLOAD": os.environ.get("PUPPETEER_SKIP_DOWNLOAD", "")}
        command = ["npx", "--yes", "@mermaid-js/mermaid-cli@11.4.2", "-i", str(diagram), "-o", str(output), "-c", str(settings), "-b", "transparent", "-w", "1400", "-s", "2"]
        subprocess.run(command, check=True, env=env)


def render_svg() -> None:
    """The system overview is laid out by hand, so only its colours change."""
    text = (HERE / "system-overview.svg").read_text()
    for light, dark in DARK_COLOURS.items():
        text = text.replace(light, dark)
    (HERE / "system-overview-dark.svg").write_text(text)


if __name__ == "__main__":
    render_svg()
    for source in sorted(HERE.glob("*.mmd")):
        for theme in THEMES:
            render(source, theme)
