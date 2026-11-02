"""Keep source number ink clear of RectoVerso's unmodified lens geometry."""

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

from PyQt6.QtGui import QColor, QFontDatabase
from PyQt6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import artwork  # noqa: E402


class ArtworkClearanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        font = Path("/System/Library/Fonts/SFNS.ttf")
        if not font.exists():
            raise unittest.SkipTest("The authored SF Pro raster check requires macOS")
        assert QFontDatabase.addApplicationFont(str(font)) >= 0
        cls.elements = json.loads((ROOT / "source/elements.json").read_text())

    def test_every_atomic_number_clears_lens_and_ink_rim(self):
        # RectoVerso OcclusionLens production geometry: source-space
        # lengths normalized through the fitted figure (296 x 228.8 points).
        # Native app captures separately check the current renderer and zoom.
        unit = min(296 / 600, 228.8 / 585) / min(
            296 / artwork.WIDTH, 228.8 / artwork.HEIGHT
        )
        rim = (1.1 + 1.5 * 0.35) * unit
        failures = []
        with tempfile.TemporaryDirectory() as folder:
            for theme in artwork.THEMES:
                image = artwork.render(
                    artwork.svg(self.elements, theme, clean=True),
                    Path(folder) / (theme + ".png"),
                )
                ink = QColor(artwork.THEMES[theme]["ink"])
                for element in self.elements:
                    x, y, _, _ = artwork.rect(element)
                    rx, ry, rw, rh = artwork.region(element)
                    pad = 8 * unit + 0.02 * max(rw, rh)
                    width, height = rw + 2 * pad, rh + 2 * pad
                    cx, cy = rx + rw / 2, ry + rh / 2
                    radius = min(width, height) / 2
                    distances = []
                    for py in range(int((y + 3) * 2), int((y + 24) * 2)):
                        for px in range(int((x + 7) * 2), int((x + 45) * 2)):
                            pixel = image.pixelColor(px, py)
                            if (
                                max(
                                    abs(a - b)
                                    for a, b in zip(
                                        pixel.getRgb()[:3], ink.getRgb()[:3]
                                    )
                                )
                                > 40
                            ):
                                continue
                            qx = abs((px + 0.5) / 2 - cx) - width / 2 + radius
                            qy = abs((py + 0.5) / 2 - cy) - height / 2 + radius
                            distances.append(
                                math.hypot(max(qx, 0), max(qy, 0))
                                + min(max(qx, qy), 0)
                                - radius
                                - rim
                            )
                    self.assertTrue(distances, (theme, element["atomicNumber"]))
                    if min(distances) < 10:
                        failures.append(
                            (theme, element["atomicNumber"], round(min(distances), 2))
                        )
        self.assertEqual(
            failures, [], "Atomic number needs 10 source units beyond the ink rim"
        )


if __name__ == "__main__":
    unittest.main()
