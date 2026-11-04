import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ElementSourceTests(unittest.TestCase):
    def setUp(self):
        self.elements = json.loads((ROOT / "source/elements.json").read_text())

    def test_complete_unique_table(self):
        self.assertEqual(
            [e["atomicNumber"] for e in self.elements], list(range(1, 119))
        )
        self.assertEqual(len({e["symbol"] for e in self.elements}), 118)
        self.assertEqual(len({(e["column"], e["row"]) for e in self.elements}), 118)
        self.assertTrue(
            all(1 <= e["column"] <= 18 and 1 <= e["row"] <= 9 for e in self.elements)
        )

    def test_detached_series_have_no_asserted_group(self):
        for e in self.elements:
            detached = 57 <= e["atomicNumber"] <= 71 or 89 <= e["atomicNumber"] <= 103
            self.assertEqual(e["group"] is None, detached)
            if not detached:
                self.assertEqual(e["group"], e["column"])
            self.assertEqual(
                e["period"],
                next(
                    p
                    for p, end in enumerate((2, 10, 18, 36, 54, 86, 118), 1)
                    if e["atomicNumber"] <= end
                ),
            )

    def test_both_translations_cover_every_element(self):
        for lang in ("en", "fr"):
            names = json.loads((ROOT / f"source/translations/{lang}.json").read_text())
            self.assertEqual(set(names), {str(z) for z in range(1, 119)})
            self.assertTrue(
                all(
                    v.strip() and not any(ord(c) < 32 for c in v)
                    for v in names.values()
                )
            )
        fr = json.loads((ROOT / "source/translations/fr.json").read_text())
        self.assertEqual(fr["117"], "Tennesse")
        self.assertEqual(fr["71"], "Lutétium")

    def test_cc0_provenance_and_selective_overrides(self):
        provenance = json.loads((ROOT / "source/provenance.json").read_text())
        self.assertEqual(provenance["license"], "CC0-1.0")
        self.assertEqual(len(provenance["rawSha256"]), 64)
        self.assertTrue(all(e["wikidata"].startswith("Q") for e in self.elements))


if __name__ == "__main__":
    unittest.main()
