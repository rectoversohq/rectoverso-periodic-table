#!/usr/bin/env python3
"""Exercise native Anki import, editor update, schedules, media and roundtrips."""

import argparse
import base64
import hashlib
import json
import re
import sys
from pathlib import Path
from anki.collection import Collection, ExportAnkiPackageOptions
from anki.import_export_pb2 import ImportAnkiPackageOptions, ImportAnkiPackageRequest
from anki.buildinfo import version

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build import FIELD, IDS, detail  # noqa: E402 — sibling source module, not installed.


def digest(data):
    return hashlib.sha256(data).hexdigest()


def imported(col, path, scheduling=True, always_update=False):
    return col.import_anki_package(
        ImportAnkiPackageRequest(
            package_path=str(path),
            options=ImportAnkiPackageOptions(
                with_scheduling=scheduling,
                with_deck_configs=False,
                merge_notetypes=True,
                update_notes=1 if always_update else 0,
            ),
        )
    )


def note_for(col, lang):
    return col.get_note(
        col.db.scalar("select id from notes where guid=?", IDS[lang]["guid"])
    )


def state(card):
    return {
        k: getattr(card, k)
        for k in (
            "id",
            "nid",
            "ord",
            "type",
            "queue",
            "reps",
            "lapses",
            "due",
            "ivl",
            "factor",
        )
    }


def validate(col, lang, expected=None):
    note = note_for(col, lang)
    cards = note.cards()
    assert len(cards) == 118
    assert {c.ord for c in cards} == set(range(118))
    assert note.mid == IDS[lang]["model"]
    assert note.id == IDS[lang]["note"]
    value = note[FIELD]
    encoded = value.split(":", 1)[1].split("<", 1)[0]
    data = json.loads(base64.b64decode(encoded))
    assert data["version"] == 1
    assert data["mode"] == "hideAll"
    assert digest(note["Occlusion"].encode()) == data["masksSHA256"]
    assert len(data["regions"]) == 118
    assert len({r["id"] for r in data["regions"]}) == 118
    elements = json.loads((ROOT / "source/elements.json").read_text())
    names = json.loads((ROOT / f"source/translations/{lang}.json").read_text())
    shapes = re.findall(
        r"\{\{c(\d+)::image-occlusion:rect:left=([^:]+):top=([^:]+):width=([^:]+):height=([^:]+):oi=1\}\}",
        note["Occlusion"],
    )
    assert len(shapes) == 118
    for e, r, s in zip(elements, data["regions"], shapes):
        z = e["atomicNumber"]
        assert r["ordinal"] == int(s[0]) == z
        assert r["kind"] == "label"
        assert r["answer"] == e["symbol"]
        assert r["title"] == names[str(z)]
        assert r["detail"] == detail(e, lang)
        assert r["geometry"]["kind"] == "rect"
        assert r["geometry"]["coordinates"] == list(map(float, s[1:]))
        assert all(0 <= v <= 1 for v in r["geometry"]["coordinates"])
    assets = {}
    for key in ("source", "clean", "darkSource", "darkClean"):
        a = data[key]
        blob = (Path(col.media.dir()) / a["file"]).read_bytes()
        assert digest(blob) == a["sha256"]
        assert a["width"] == 3840 and a["height"] == 2400
        assert blob[:8] == b"\x89PNG\r\n\x1a\n"
        assert int.from_bytes(blob[16:20], "big") == 3840
        assert int.from_bytes(blob[20:24], "big") == 2400
        assets[a["file"]] = digest(blob)
    media = col.media.check()
    assert not media.missing and not media.unused
    for c in cards:
        q, a = c.question(), c.answer()
        assert q.strip() and a.strip()
        assert "RV-OCCLUSION-1" not in q + a
        assert FIELD not in q + a
        assert "rv-name" not in q.split("</style>")[-1]
        assert "cloze" in q and "cloze-highlight" in a
    if expected:
        assert value == expected["field"] and assets == expected["assets"]
    return {"field": value, "assets": assets, "cards": cards, "note": note}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--packages", type=Path, required=True)
    p.add_argument("--update-packages", type=Path)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    results = []
    packages = {lang: next(a.packages.glob("*-" + lang + ".apkg")) for lang in IDS}
    for lang, package in packages.items():
        folder = a.out / lang
        folder.mkdir()
        col = Collection(str(folder / "source.anki2"))
        imported(col, package)
        before = validate(col, lang)
        note = before["note"]
        original_header = note["Header"]
        edited_header = original_header + " — editor check"
        col.update_image_occlusion_note(
            note_id=note.id,
            occlusions=note["Occlusion"],
            header=edited_header,
            back_extra=note["Back Extra"],
            tags=note.tags,
        )
        assert note_for(col, lang)["Header"] == edited_header
        validate(col, lang, before)
        col.update_image_occlusion_note(
            note_id=note.id,
            occlusions=note["Occlusion"],
            header=original_header,
            back_extra=note["Back Extra"],
            tags=note.tags,
        )
        assert note_for(col, lang)["Header"] == original_header
        # Preserve the source's complete backend-rendered cards for the bundled reviewer check.
        for card in before["cards"]:
            for side, body in [
                ("question", card.question()),
                ("answer", card.answer()),
            ]:
                (folder / f"{card.ord + 1:03d}-{side}.html").write_text(body)
        col.decks.select(before["cards"][0].did)
        card = col.sched.getCard()
        assert card
        col.sched.answerCard(card, 3)
        studied = state(col.get_card(card.id))
        assert studied["reps"] == 1
        package2 = folder / "studied.apkg"
        col.export_anki_package(
            out_path=str(package2),
            options=ExportAnkiPackageOptions(
                with_scheduling=True,
                with_media=True,
                with_deck_configs=False,
                legacy=False,
            ),
            limit=None,
        )
        col.close()
        again = Collection(str(folder / "reimport.anki2"))
        imported(again, package2)
        validate(again, lang, before)
        assert state(again.get_card(studied["id"])) == studied
        assert again.db.scalar("select count(*) from revlog") == 1
        update = next((a.update_packages or a.packages).glob("*-" + lang + ".apkg"))
        updated_note = note_for(again, lang)
        original_comments = updated_note["Comments"]
        updated_note["Comments"] = "Outdated fixture: replaced by the source update"
        again.update_note(updated_note)
        imported(again, update, False, always_update=True)
        assert note_for(again, lang)["Comments"] == original_comments
        validate(again, lang, before)
        assert state(again.get_card(studied["id"])) == studied
        assert again.db.scalar("select count(*) from revlog") == 1
        again.export_anki_package(
            out_path=str(folder / "reexport.apkg"),
            options=ExportAnkiPackageOptions(
                with_scheduling=True,
                with_media=True,
                with_deck_configs=False,
                legacy=False,
            ),
            limit=None,
        )
        again.close()
        # The optional preparation field must not be required for native Anki cards.
        ordinary = Collection(str(folder / "without-preparation.anki2"))
        imported(ordinary, package)
        model = ordinary.models.get(IDS[lang]["model"])
        field = next(f for f in model["flds"] if f["name"] == FIELD)
        ordinary.models.remove_field(model, field)
        ordinary.models.save(model)
        ordinary_note = note_for(ordinary, lang)
        assert FIELD not in ordinary_note.keys()
        assert len(ordinary_note.cards()) == 118
        for ordinary_card in ordinary_note.cards():
            assert "cloze" in ordinary_card.question()
            assert "cloze-highlight" in ordinary_card.answer()
            assert "rv-name" in ordinary_card.answer()
        media_without = ordinary.media.check()
        assert not media_without.missing
        assert set(media_without.unused) == {
            "rv-periodic-light-clean.png",
            "rv-periodic-dark-clean.png",
        }
        ordinary.close()
        results.append(
            {
                "language": lang,
                "cards": 118,
                "ordinals": 118,
                "missingMedia": 0,
                "unusedMedia": 0,
                "editorPreservesOptionalField": True,
                "editorChangedAndRestoredHeader": True,
                "sourceUpdateActuallyReplacedContent": True,
                "nativeCardsWorkWithoutPreparationField": True,
                "roundtripPreservesMediaAndMetadata": True,
                "studyStatePreserved": True,
                "rebuiltPackageUpdatePreservesSchedule": True,
                "reviewLogRows": 1,
                "frontMetadataLeak": False,
            }
        )
    combined = Collection(str(a.out / "both.anki2"))
    for lang, package in packages.items():
        imported(combined, package)
        validate(combined, lang)
    assert combined.card_count() == 236
    assert combined.note_count() == 2
    assert len({c.id for lang in IDS for c in note_for(combined, lang).cards()}) == 236
    combined.close()
    report = {
        "ankiVersion": version,
        "languages": results,
        "combinedCards": 236,
        "combinedNotes": 2,
    }
    (a.out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
