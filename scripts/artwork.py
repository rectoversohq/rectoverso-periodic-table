#!/usr/bin/env python3
"""Draw the original table pair; the pictures stay outside source Git, pinned by their record."""

import argparse
import hashlib
import json
import os
from pathlib import Path
from xml.sax.saxutils import escape
from PyQt6.QtCore import PYQT_VERSION_STR, QByteArray, qVersion
from PyQt6.QtGui import (
    QColor,
    QColorSpace,
    QFont,
    QFontDatabase,
    QFontInfo,
    QGuiApplication,
    QImage,
    QPainter,
    QRawFont,
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1920, 1480
SCALE = 2
X, Y, PITCH, ROW_PITCH, CELL_W, CELL_H = 100, 126, 96, 132, 88, 124
# Original pedagogical color scheme. Hue families remain registered in each pair.
PALETTE = {
    "alkali": ["#e9b8ad", "#603b37"],
    "alkaline-earth": ["#e8cf9b", "#5a492b"],
    "transition": ["#cedce5", "#334956"],
    "post-transition": ["#bbd3cc", "#354f47"],
    "metalloid": ["#d1dbad", "#485231"],
    "nonmetal": ["#a9d5cb", "#28574d"],
    "halogen": ["#c3c9e6", "#3d4261"],
    "noble-gas": ["#dbc4df", "#543b59"],
    "lanthanoid": ["#d6c6b5", "#504235"],
    "actinoid": ["#dcbebf", "#593d40"],
}
THEMES = {
    "light": {"canvas": "#f7f5ef", "ink": "#252820", "muted": "#62665c"},
    "dark": {"canvas": "#181a18", "ink": "#f3f2e9", "muted": "#a4aaa0"},
}


def rect(element):
    x = X + (element["column"] - 1) * PITCH
    row = element["row"]
    y = Y + (row - 1) * ROW_PITCH + (36 if row >= 8 else 0)
    return x, y, CELL_W, CELL_H


def region(element):
    # Keep the full symbol, including descenders, below the separate number band.
    # Its clearance is checked against the native lens, without moving that lens.
    x, y, _, _ = rect(element)
    return [x + 9, y + 58, 70, 40]


def svg(elements, theme, clean=False):
    p = THEMES[theme]
    idx = int(theme == "dark")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{p["canvas"]}"/>',
        '<g font-family=".SF NS">',
    ]

    def text(x, y, value, size=16, color=None, anchor="middle", weight=400):
        parts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color or p["muted"]}">{escape(str(value))}</text>'
        )

    for group in range(1, 19):
        text(X + (group - 1) * PITCH + CELL_W / 2, 94, group)
    for row in range(1, 8):
        text(55, Y + (row - 1) * ROW_PITCH + CELL_H / 2 + 9, row)
    for row, period in [(8, 6), (9, 7)]:
        text(X + 2 * PITCH + CELL_W / 2, Y + (row - 1) * ROW_PITCH + CELL_H - 1, period)
    for period, span in [(6, "57–71"), (7, "89–103")]:
        x = X + 2 * PITCH
        y = Y + (period - 1) * ROW_PITCH
        parts.append(
            f'<rect x="{x}" y="{y}" width="{CELL_W}" height="{CELL_H}" rx="4" fill="none" stroke="{p["muted"]}" stroke-opacity="0.4"/>'
        )
        text(x + CELL_W / 2, y + CELL_H / 2 + 7, span, 15)
    for e in elements:
        x, y, w, h = rect(e)
        fill = PALETTE[e["family"]][idx]
        parts.append(
            f'<rect id="cell-{e["atomicNumber"]}" x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}"/>'
        )
        text(x + 10, y + 21, e["atomicNumber"], 14, p["ink"], "start")
        if not clean:
            text(x + w / 2, y + 89, e["symbol"], 36, p["ink"], "middle", 600)
    parts.append("</g></svg>")
    return "\n".join(parts) + "\n"


def render(vector, path):
    image = QImage(WIDTH * SCALE, HEIGHT * SCALE, QImage.Format.Format_RGB32)
    image.setColorSpace(QColorSpace(QColorSpace.NamedColorSpace.SRgb))
    image.fill(QColor("white"))
    painter = QPainter(image)
    QSvgRenderer(QByteArray(vector.encode())).render(painter)
    painter.end()
    assert image.save(str(path), "PNG")
    return image


# The pinned renderer: Qt's offscreen platform draws text the same way on every run of one Mac; a
# window-system platform (cocoa) draws it differently. The font is pinned by its SHA-256 in
# source/artwork.json, and so are the pictures it gives.
PLATFORM = "offscreen"


def render_artwork(font_path, out, write_vectors=True, check_clean=True):
    """Draw the four pictures into `out` and return their record (what artwork.json holds).

    With `write_vectors`, the SVG masters in artwork/ are written too (scripts/artwork.py); a build
    renders without touching the checkout. `check_clean` proves, pixel by pixel, that each clean
    picture differs only inside the symbol regions; a build that matches the pinned pictures' hashes
    can skip it, since the pinned pictures passed it.
    """
    os.environ["QT_QPA_PLATFORM"] = PLATFORM
    out.mkdir(parents=True, exist_ok=True)
    _app = QApplication.instance() or QApplication([])  # Alive while Qt renders.
    font_id = QFontDatabase.addApplicationFont(str(font_path))
    assert font_id >= 0, "Font did not load"
    font = QFont(".SF NS")
    font.setPixelSize(36)
    info = QFontInfo(font)
    rawfont = QRawFont.fromFont(font)
    assert info.family() == ".SF NS", info.family()
    assert QGuiApplication.platformName() == PLATFORM, QGuiApplication.platformName()
    elements = json.loads((ROOT / "source/elements.json").read_text())
    assets = {}
    for theme in THEMES:
        images = {}
        for clean in (False, True):
            name = "rv-periodic-" + theme + ("-clean" if clean else "")
            vector = svg(elements, theme, clean)
            if write_vectors:
                (ROOT / "artwork" / f"{name}.svg").write_text(vector)
            filename = f"{name}-v2.png"
            images[clean] = render(vector, out / filename)
            assets[name] = {
                "file": filename,
                "sha256": hashlib.sha256((out / filename).read_bytes()).hexdigest(),
                "width": WIDTH * SCALE,
                "height": HEIGHT * SCALE,
            }
        if not check_clean:
            continue
        # Prove the clean image differs only inside the 118 symbol rectangles.
        changed = 0
        boxes = [[v * SCALE for v in region(e)] for e in elements]
        for y in range(HEIGHT * SCALE):
            for x in range(WIDTH * SCALE):
                if images[False].pixel(x, y) != images[True].pixel(x, y):
                    assert any(
                        rx <= x < rx + rw and ry <= y < ry + rh
                        for rx, ry, rw, rh in boxes
                    ), (theme, x, y)
                    changed += 1
        assert changed > 118
    record = {
        "assets": assets,
        "canvas": {
            "method": "flat-srgb-v1",
            "light": [247 / 255, 245 / 255, 239 / 255],
            "dark": [24 / 255, 26 / 255, 24 / 255],
        },
        "fontFamily": rawfont.familyName(),
        "fontStyle": rawfont.styleName(),
        "fontSHA256": hashlib.sha256(Path(font_path).read_bytes()).hexdigest(),
        "renderer": {"qt": qVersion(), "pyqt": PYQT_VERSION_STR, "platform": PLATFORM},
        "regions": [
            {
                "atomicNumber": e["atomicNumber"],
                "pixels": region(e),
                "coordinates": [
                    region(e)[0] / WIDTH,
                    region(e)[1] / HEIGHT,
                    region(e)[2] / WIDTH,
                    region(e)[3] / HEIGHT,
                ],
                # The whole cell, which a symbol → name card lights (#5).
                "cell": [
                    rect(e)[0] / WIDTH,
                    rect(e)[1] / HEIGHT,
                    rect(e)[2] / WIDTH,
                    rect(e)[3] / HEIGHT,
                ],
            }
            for e in elements
        ],
    }
    (out / "artwork.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--out", type=Path, required=True)
    a.add_argument("--font", type=Path, required=True)
    args = a.parse_args()
    record = render_artwork(args.font, args.out)
    print(
        json.dumps(
            {
                "images": 4,
                "registeredSymbolRegions": len(record["regions"]),
                "size": [WIDTH * SCALE, HEIGHT * SCALE],
                "fontFamily": record["fontFamily"],
                "renderer": record["renderer"],
                "outsideRegionPixelsChanged": 0,
                "out": str(args.out),
            }
        )
    )


if __name__ == "__main__":
    main()
