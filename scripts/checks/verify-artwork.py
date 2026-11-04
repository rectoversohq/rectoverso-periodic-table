#!/usr/bin/env python3
"""Check a fresh render against the pinned artwork record, source/artwork.json.

    python scripts/artwork.py --font /System/Library/Fonts/SFNS.ttf --out DIR
    python scripts/checks/verify-artwork.py --render DIR

The render must have the record's geometry: regions, cells, canvas, picture names and sizes
(`scripts/artwork.py` has already proved, pixel by pixel, that each clean picture differs only inside
the symbol regions). Drawn with the pinned font, the pinned Qt and the offscreen platform, its four
pictures must also be the pinned ones, byte for byte: what every release build renders. Drawn with
another font (the hosted runner's), the pictures are reported, not required.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--render", type=Path, required=True)
    a = p.parse_args()
    pinned = json.loads((ROOT / "source/artwork.json").read_text())
    fresh = json.loads((a.render / "artwork.json").read_text())
    for key in ("regions", "canvas"):
        assert fresh[key] == pinned[key], f"The render's {key} differ from the record's"
    shape = lambda r: {  # noqa: E731
        k: (v["file"], v["width"], v["height"]) for k, v in r["assets"].items()
    }
    assert shape(fresh) == shape(pinned), "The render's pictures differ in name or size"
    assert not list(ROOT.glob("source/**/*.png")), "Pictures stay outside source Git"
    pinned_font = fresh["fontSHA256"] == pinned["fontSHA256"]
    matches = {
        v["file"]: v["sha256"] == pinned["assets"][k]["sha256"]
        for k, v in fresh["assets"].items()
    }
    if pinned_font:
        assert fresh["renderer"] == pinned["renderer"], (
            f"The pinned font, another renderer: {fresh['renderer']} ≠ {pinned['renderer']}"
        )
        assert all(matches.values()), (
            f"The pinned font and renderer drew other pictures: {matches}"
        )
    print(
        json.dumps(
            {
                "geometryMatches": True,
                "pinnedFont": pinned_font,
                "renderer": fresh.get("renderer"),
                "picturesMatchThePin": matches,
                "picturesRequired": pinned_font,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
