"""rectoverso.json, the source's notes and the pinned artwork record agree (no Anki needed)."""

import json
import re
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from source_data import HEADERS, IDS, inputs  # noqa: E402


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.meta = json.loads((ROOT / "rectoverso.json").read_text())

    def test_every_shipped_language_has_the_gallery_fields(self):
        languages = set(self.meta["languages"])
        self.assertEqual(languages, set(IDS))
        for field in ("title", "subject", "headline", "description"):
            self.assertEqual(set(self.meta[field]), languages, field)
            self.assertTrue(all(v.strip() for v in self.meta[field].values()), field)
        for lang, artifact in self.meta["languages"].items():
            self.assertEqual(artifact["title"], self.meta["title"][lang])
            self.assertEqual(artifact["cards"], self.meta["cards"])
        self.assertEqual(self.meta["releaseTag"], "v" + self.meta["version"])
        self.assertTrue(
            self.meta["publication"]["release"].endswith("/" + self.meta["releaseTag"])
        )
        self.assertIs(self.meta["proOnly"], False)
        stamp = datetime.fromisoformat(
            self.meta["contentModifiedAt"].replace("Z", "+00:00")
        )
        self.assertLessEqual(stamp.timestamp(), datetime.now().timestamp())

    def test_french_typography(self):
        # The French of RectoVerso's docs/app/languages.md: a narrow no-break space before ; : ! ?
        for field in ("title", "subject", "headline", "description"):
            text = self.meta[field]["fr"]
            self.assertIsNone(re.search("(?<![\u202f\u00a0])[;:!?]", text), field)
            self.assertNotIn("'", text, field)

    def test_notes_make_the_declared_cards_and_name_the_sample(self):
        guids = set()
        for lang, artifact in self.meta["languages"].items():
            expanded, notes, types, deck = inputs(lang)
            self.assertEqual(sum(n.get("cards", 1) for n in notes), artifact["cards"])
            self.assertEqual(len(notes), self.meta["notes"])
            self.assertTrue(all(n["model"] in types for n in notes))
            ids = [n["guid"] for n in notes]
            self.assertEqual(len(set(ids)), len(ids))
            self.assertFalse(guids & set(ids))
            guids |= set(ids)
            self.assertEqual(expanded["sample"], artifact["sample"])
            self.assertEqual(expanded["package"], artifact["package"])
            guid, number = artifact["sample"].split("/")
            [note] = [n for n in notes if n["guid"] == guid]
            self.assertIn("{{c%s::" % number, note["fields"]["Occlusion"])
            credited = {c["file"] for c in self.meta["imageCredits"]}
            for field in note["fields"].values():
                for picture in re.findall(r'<img\b[^>]*?\bsrc="([^"]+)"', field):
                    self.assertIn(picture, credited)
            self.assertNotEqual(deck["id"], types["occlusion"]["id"])

    def test_guids_read_as_every_gallery_decks(self):
        # The prefix, the language, then the note (RectoVerso's agents/decks.md): the table, and
        # each element by its atomic number, then what its note asks.
        self.assertEqual(self.meta["guidPrefix"], "rv-periodic-table")
        self.assertNotIn("guidForm", self.meta)
        asks = {"name-symbol": "symbol", "symbol-name": "name"}
        for lang in self.meta["languages"]:
            _, notes, _, _ = inputs(lang)
            for note in notes:
                if note["model"] == "occlusion":
                    expected = f"rv-periodic-table-{lang}-table"
                else:
                    z, ask = note["atomicNumber"], asks[note["model"]]
                    expected = f"rv-periodic-table-{lang}-{z:03d}-{ask}"
                self.assertEqual(note["guid"], expected)
                self.assertRegex(note["guid"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            by_guid = {n["guid"]: n for n in notes}
            # Gold: its symbol asked from its name, its name asked from its lit cell.
            symbol = by_guid[f"rv-periodic-table-{lang}-079-symbol"]
            name = by_guid[f"rv-periodic-table-{lang}-079-name"]
            self.assertEqual(symbol["fields"]["Header"], HEADERS["name-symbol"][lang])
            self.assertEqual(name["fields"]["Header"], HEADERS["symbol-name"][lang])
            self.assertEqual(
                (symbol["model"], name["model"]), ("name-symbol", "symbol-name")
            )

    def test_pictures_are_pinned_and_rendered_not_committed(self):
        record = json.loads((ROOT / "source/artwork.json").read_text())
        credits = {c["file"]: c for c in self.meta["imageCredits"]}
        self.assertEqual(set(credits), {a["file"] for a in record["assets"].values()})
        self.assertEqual(self.meta["pictures"], len(credits))
        self.assertIs(self.meta["renderedPictures"], True)
        for credit in credits.values():
            self.assertTrue((ROOT / credit["original"]).is_file(), credit["original"])
        self.assertEqual(len(record["fontSHA256"]), 64)
        self.assertEqual(record["renderer"]["platform"], "offscreen")
        self.assertEqual(list(ROOT.glob("source/**/*.png")), [])

    def test_french_card_headers_have_their_narrow_space(self):
        from source_data import HEADERS, occlusion_note  # noqa: F401

        for kind in HEADERS.values():
            self.assertRegex(kind["fr"], "\u202f\\?$")


if __name__ == "__main__":
    unittest.main()
