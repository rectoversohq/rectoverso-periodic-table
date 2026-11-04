"""rectoverso.json, the source's notes and the registered pictures agree (no Anki needed)."""

import hashlib
import json
import re
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from source_data import IDS, inputs  # noqa: E402


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
            for field in note["fields"].values():
                for picture in re.findall(r'<img\b[^>]*?\bsrc="([^"]+)"', field):
                    self.assertTrue(
                        (ROOT / "source/media" / picture).is_file(), picture
                    )
            self.assertNotEqual(deck["id"], types["occlusion"]["id"])

    def test_registered_pictures_match_the_record(self):
        record = json.loads((ROOT / "source/artwork.json").read_text())
        credits = {c["file"] for c in self.meta["imageCredits"]}
        self.assertEqual(credits, {a["file"] for a in record["assets"].values()})
        self.assertEqual(self.meta["pictures"], len(credits))
        for asset in record["assets"].values():
            data = (ROOT / "source/media" / asset["file"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), asset["sha256"])


if __name__ == "__main__":
    unittest.main()
