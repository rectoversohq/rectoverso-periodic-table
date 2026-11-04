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
from build import ELEMENT_KINDS, FIELD, HEADERS, IDS, detail, position  # noqa: E402 — sibling source module, not installed.


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


def validate(col, lang, expected=None, allowed_unused=()):
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
        assert a["width"] == 3840 and a["height"] == 2960
        assert blob[:8] == b"\x89PNG\r\n\x1a\n"
        assert int.from_bytes(blob[16:20], "big") == 3840
        assert int.from_bytes(blob[20:24], "big") == 2960
        assets[a["file"]] = digest(blob)
    media = col.media.check()
    assert not media.missing and set(media.unused) <= set(allowed_unused)
    for c in cards:
        q, a = c.question(), c.answer()
        assert q.strip() and a.strip()
        assert "RV-OCCLUSION-1" not in q + a
        assert FIELD not in q + a
        assert "rv-name" not in q.split("</style>")[-1]
        assert "cloze" in q and "cloze-highlight" in a
    if expected:
        assert value == expected["field"] and assets == expected["assets"]
    validate_elements(col, lang, elements, names, data)
    return {"field": value, "assets": assets, "cards": cards, "note": note}


def text_of(page):
    page = re.sub(r"<(style|script)[^>]*>.*?</\1>", "", page, flags=re.S)
    return " ".join(re.sub(r"<[^>]+>", " ", page).split())


def validate_elements(col, lang, elements, names, occlusion):
    """Each element's name → symbol and lit symbol → name notes (#5)."""
    for e, symbol_region in zip(elements, occlusion["regions"]):
        z, name, symbol = e["atomicNumber"], names[str(e["atomicNumber"])], e["symbol"]
        for kind in ("name-symbol", "symbol-name"):
            ids = ELEMENT_KINDS[kind][lang]
            note = col.get_note(
                col.db.scalar(
                    "select id from notes where guid=?", f"{ids['guid']}{z:03d}"
                )
            )
            assert (note.id, note.mid) == (ids["noteBase"] + z, ids["model"])
            [card] = note.cards()
            assert (card.id, card.ord) == (ids["cardBase"] + z, 0)
            assert [f["id"] for f in col.models.get(note.mid)["flds"]] == [
                ids["fieldBase"] + i for i in range(len(note.keys()))
            ]
            assert note["Header"] == HEADERS[kind][lang]
            q, a = text_of(card.question()), text_of(card.answer())
            assert "RV-OCCLUSION-1" not in card.question() + card.answer()
            if kind == "name-symbol":
                assert q == f"{HEADERS[kind][lang]} {name}", q
                assert symbol in a.split() and detail(e, lang) in a
            else:
                # The front shows the drawing and the lit frame, never the answer.
                assert q == HEADERS[kind][lang], q
                assert name in a and detail(e, lang) in a
                data = json.loads(
                    base64.b64decode(note[FIELD].split(":", 1)[1].split("<", 1)[0])
                )
                assert data["version"] == 1 and data["mode"] == "lit"
                assert (
                    data["masksSHA256"] == digest(b"")
                    and "Occlusion" not in note.keys()
                )
                for key in ("source", "clean", "darkSource", "darkClean", "canvas"):
                    assert data[key] == occlusion[key]
                [r] = data["regions"]
                assert (r["id"], r["ordinal"], r["kind"]) == (
                    f"element-{z:03d}-cell",
                    1,
                    "label",
                )
                assert r["answer"] == r["title"] == name and r["detail"] == detail(
                    e, lang
                )
                assert r["position"] == position(e, lang) and name not in r["position"]
                # The cell, independently of the artwork record: the symbol region sits at (9, 58)
                # in an 88 × 124 cell of the 1920 × 1480 drawing.
                left, top, _, _ = symbol_region["geometry"]["coordinates"]
                cell = [left - 9 / 1920, top - 58 / 1480, 88 / 1920, 124 / 1480]
                assert all(
                    abs(x - y) < 1e-9
                    for x, y in zip(r["geometry"]["coordinates"], cell)
                )
                lit = dict(part.split(":") for part in note["Lit"].split(";"))
                assert all(
                    abs(float(lit[k].rstrip("%")) / 100 - v) < 1e-6
                    for k, v in zip(("left", "top", "width", "height"), cell)
                )


def validate_prior_update(previous, packages, folder):
    """Default If Newer update; exact prepared media must survive name conflicts."""
    folder.mkdir()
    results = []
    for lang in IDS:
        target = folder / lang
        target.mkdir()
        col = Collection(str(target / "prior.anki2"))
        imported(col, next(previous.glob("*-" + lang + ".apkg")))
        note = note_for(col, lang)
        identity = (note.id, note.mid, note.guid)
        card_ids = [(card.id, card.nid, card.ord) for card in note.cards()]
        field_ids = [field["id"] for field in col.models.get(note.mid)["flds"]]
        old_assets = {path.name for path in Path(col.media.dir()).iterdir()}
        col.decks.select(note.cards()[0].did)
        card = col.sched.getCard()
        col.sched.answerCard(card, 3)
        studied = state(col.get_card(card.id))
        reviews = col.db.all("select * from revlog")
        imported(col, packages[lang], scheduling=False)
        result = validate(col, lang, allowed_unused=old_assets)
        note = result["note"]
        assert (note.id, note.mid, note.guid) == identity
        assert [(card.id, card.nid, card.ord) for card in note.cards()] == card_ids
        assert [field["id"] for field in col.models.get(note.mid)["flds"]] == field_ids
        assert state(col.get_card(card.id)) == studied
        assert col.db.all("select * from revlog") == reviews
        # Assert current content, not just valid old data after a skipped update.
        expected = Collection(str(target / "expected.anki2"))
        imported(expected, packages[lang])
        assert note[FIELD] == note_for(expected, lang)[FIELD]
        assert note["Occlusion"] == note_for(expected, lang)["Occlusion"]
        expected.close()
        exported = target / "studied.apkg"
        col.export_anki_package(
            out_path=str(exported),
            options=ExportAnkiPackageOptions(
                with_scheduling=True,
                with_media=True,
                with_deck_configs=False,
                legacy=False,
            ),
            limit=None,
        )
        col.close()
        again = Collection(str(target / "roundtrip.anki2"))
        imported(again, exported)
        validate(again, lang)
        assert state(again.get_card(card.id)) == studied
        assert again.db.all("select * from revlog") == reviews
        again.close()
        results.append(
            {
                "language": lang,
                "cardIDsPreserved": len(card_ids),
                "defaultIfNewer": True,
                "preparedHashesAndMasksCurrent": True,
                "noteModelFieldIDsPreserved": True,
                "studiedStateAndReviewLogPreserved": True,
                "exportReimport": True,
            }
        )
    return {"source": str(previous), "languages": results}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--packages", type=Path, required=True)
    p.add_argument("--update-packages", type=Path)
    p.add_argument("--prior-packages", type=Path, action="append", default=[])
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
        # Every note type that carries the optional field loses it, the lit notes' too.
        for mid in (IDS[lang]["model"], ELEMENT_KINDS["symbol-name"][lang]["model"]):
            model = ordinary.models.get(mid)
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
            "rv-periodic-light-clean-v2.png",
            "rv-periodic-dark-clean-v2.png",
        }
        ordinary.close()
        results.append(
            {
                "language": lang,
                "cards": 3 * 118,
                "ordinals": 118,
                "elementNotes": 2 * 118,
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
    assert combined.card_count() == 2 * 3 * 118
    assert combined.note_count() == 2 * (1 + 2 * 118)
    assert len({c.id for lang in IDS for c in note_for(combined, lang).cards()}) == 236
    assert len(set(combined.db.list("select id from cards"))) == 2 * 3 * 118
    combined.close()
    report = {
        "ankiVersion": version,
        "languages": results,
        "combinedCards": 2 * 3 * 118,
        "combinedNotes": 2 * (1 + 2 * 118),
        "priorUpdates": [
            validate_prior_update(prior, packages, a.out / f"prior-{index}")
            for index, prior in enumerate(a.prior_packages)
        ],
    }
    (a.out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
