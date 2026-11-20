"""Generate smaller companion sheets for common actions. Requires Pillow."""

import argparse
from pathlib import Path

from PIL import Image


def create_scaled_sheet(path):
    with Image.open(path) as original:
        if original.size != (5120, 5400):
            raise ValueError(f"Unexpected sprite sheet dimensions: {path}")
        original = original.convert("RGBA")
        scaled = Image.new("RGBA", (3584, 3780))
        for row in range(15):
            for col in range(8):
                x, y = col * 640, row * 360
                frame = original.crop((x, y, x + 640, y + 360))
                scaled.paste(frame.resize((448, 252), Image.Resampling.LANCZOS), (col * 448, row * 252))
        output = path.with_suffix(".scaled.webp")
        scaled.save(output, lossless=True)
        print(f"{output.name}: {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheets", nargs="+", type=Path)
    for sheet in parser.parse_args().sheets:
        create_scaled_sheet(sheet)
