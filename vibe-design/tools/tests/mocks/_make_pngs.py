"""generate mock PNGs for palette compliance tests:
- compliant: dominant color #1A73E8 (matches mock spec primary)
- violation: dominant color #FF00AA (way off any spec hex)
"""
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPLIANT = ROOT / "compliant"
VIOLATION = ROOT / "violation"


def make_png(path: Path, fill: tuple[int, int, int]) -> None:
    img = Image.new("RGB", (256, 256), fill)
    img.save(path)


make_png(COMPLIANT / "artifact.png", (0x1A, 0x73, 0xE8))
make_png(VIOLATION / "artifact.png", (0xFF, 0x00, 0xAA))
print("wrote", COMPLIANT / "artifact.png", "and", VIOLATION / "artifact.png")
