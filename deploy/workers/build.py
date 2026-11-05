"""Copy what one version serves into this folder. Usage: python build.py before|after|resource RESOURCE_URL"""

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SKIP = shutil.ignore_patterns("__pycache__", "static", "holes.json", "DESIGN_NOTES.md", "make_assets.py")


def build(app: str, resource_url: str) -> None:
    for folder in ("legible_core", "demo_site", "demo_resource", "businesses"):
        shutil.rmtree(HERE / "src" / folder, ignore_errors=True)
        shutil.copytree(ROOT / folder, HERE / "src" / folder, ignore=SKIP)
    shutil.rmtree(HERE / "public", ignore_errors=True)
    # Workers serves these directly, because Starlette's file responses need threads.
    shutil.copytree(ROOT / "demo_site" / "static", HERE / "public" / "static")
    (HERE / "src" / "version.py").write_text(f"APP = {app!r}\nRESOURCE_URL = {resource_url!r}\n")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
