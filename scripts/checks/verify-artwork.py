#!/usr/bin/env python3
"""Check the registered artwork, and a fresh render against it.

    python scripts/checks/verify-artwork.py [--render DIR]

The four registered pictures in source/media match source/artwork.json (SHA-256, size), and each
clean picture differs from its original only inside the 118 symbol regions. `--render DIR` (a
`scripts/artwork.py` output folder) must have the registered geometry: regions, cells, canvas,
picture names and sizes. Its pixels depend on the font file and the Qt platform that drew them, so
they are compared and reported, not required: the registered pictures are what the packages ship.
"""

import argparse
import hashlib
import json
from pathlib import Path
from PyQt6.QtGui import QImage

ROOT = Path(__file__).resolve().parents[2]
SCALE = 2


def pixels(path):
    image = QImage(str(path)).convertToFormat(QImage.Format.Format_RGB32)
    bits = image.constBits()
    bits.setsize(image.sizeInBytes())
    return image.width(), image.height(), image.bytesPerLine(), bytes(bits)


def changed_outside(original, clean, regions):
    """Pixels that differ between the pair outside every symbol region (in picture pixels)."""
    w, h, stride, a = pixels(original)
    w2, h2, stride2, b = pixels(clean)
    assert (w, h, stride) == (w2, h2, stride2)
    boxes = [[v * SCALE for v in r["pixels"]] for r in regions]
    outside, inside = 0, 0
    for y in range(h):
        row_a, row_b = (
            a[y * stride : y * stride + w * 4],
            b[y * stride : y * stride + w * 4],
        )
        if row_a == row_b:
            continue
        spans = sorted((x, x + bw) for x, by, bw, bh in boxes if by <= y < by + bh)
        for x in range(w):
            if row_a[x * 4 : x * 4 + 4] != row_b[x * 4 : x * 4 + 4]:
                if any(start <= x < end for start, end in spans):
                    inside += 1
                else:
                    outside += 1
    return outside, inside


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--render", type=Path)
    a = p.parse_args()
    record = json.loads((ROOT / "source/artwork.json").read_text())
    media = ROOT / "source/media"
    report = {"pictures": {}}
    for key, asset in record["assets"].items():
        path = media / asset["file"]
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == asset["sha256"], asset["file"]
        image = QImage(str(path))
        assert (image.width(), image.height()) == (asset["width"], asset["height"]), (
            asset["file"]
        )
        report["pictures"][asset["file"]] = asset["sha256"]
    assert sorted(
        p.name for p in media.iterdir() if not p.name.startswith(".")
    ) == sorted(a["file"] for a in record["assets"].values()), (
        "source/media holds exactly the registered pictures"
    )
    for theme in ("light", "dark"):
        outside, inside = changed_outside(
            media / record["assets"][f"rv-periodic-{theme}"]["file"],
            media / record["assets"][f"rv-periodic-{theme}-clean"]["file"],
            record["regions"],
        )
        assert outside == 0 and inside > 118, (theme, outside, inside)
        report[theme + "CleanPixelsChanged"] = {
            "outsideSymbolRegions": outside,
            "inside": inside,
        }
    if a.render:
        fresh = json.loads((a.render / "artwork.json").read_text())
        for key in ("regions", "canvas"):
            assert fresh[key] == record[key], (
                f"The fresh render's {key} differ from the registered"
            )
        assert {
            k: (v["file"], v["width"], v["height"]) for k, v in fresh["assets"].items()
        } == {
            k: (v["file"], v["width"], v["height"]) for k, v in record["assets"].items()
        }, "The fresh render's pictures differ in name or size"
        report["freshRender"] = {
            "geometryMatches": True,
            "fontMatches": fresh["fontSHA256"] == record["fontSHA256"],
            "picturesMatch": {
                v["file"]: v["sha256"] == record["assets"][k]["sha256"]
                for k, v in fresh["assets"].items()
            },
        }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
