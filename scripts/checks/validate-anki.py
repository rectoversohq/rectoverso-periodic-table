#!/usr/bin/env python3
"""Check packages in native Anki, one by one: the interface RectoVerso's gallery check calls.

    python scripts/checks/validate-anki.py --output DIR PACKAGE [PACKAGE ...]

Each package's sidecar (`.rectoverso.json` beside it) gives its card count. Every package gets the
checks that hold for any copy of the deck: the count, unique GUIDs, every card rendering a question
and an answer that adds to it, no RectoVerso Occlusion record shown, no missing media, a real study
answer kept through a repeat import and through export/reimport, with fields and media exact.
RectoVerso's gallery check also runs it on RectoVerso's own Anki export of the deck, whose note types
are its own; the checks that read this deck's note types (the occlusion note's 118 cards, the lit
cell, the name → symbol front) run only where they are present. `validate_source.py` is the source's
complete check (editor, updates, prior candidates).
"""

import argparse
import hashlib
import html
import json
import re
import sys
import tempfile
from pathlib import Path
from anki.collection import Collection, ExportAnkiPackageOptions
from anki.import_export_pb2 import ImportAnkiPackageOptions, ImportAnkiPackageRequest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from source_data import ELEMENT_KINDS, FIELD, IDS  # noqa: E402 — sibling source module.


def import_package(col, path):
    col.import_anki_package(
        ImportAnkiPackageRequest(
            package_path=str(path.resolve()),
            options=ImportAnkiPackageOptions(
                with_scheduling=True,
                merge_notetypes=True,
                update_notes=1,
                update_notetypes=1,
            ),
        )
    )
    col.models._clear_cache()


def visible(page):
    page = re.sub(r"<(style|script)[^>]*>.*?</\1>", "", page, flags=re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", page)).split())


def state(card):
    return (card.id, card.nid, card.type, card.queue, card.due, card.reps, card.ivl)


def own_checks(col, card, note, q, a, kinds):
    """This deck's own note types, where the package still has them."""
    mid = note.mid
    for lang, ids in IDS.items():
        if mid == ids["model"]:
            kinds["occlusion"] = kinds.get("occlusion", 0) + 1
            if "cloze" not in q or "cloze-highlight" not in a:
                raise ValueError("An occlusion card lost its native mask")
            return
        if mid == ELEMENT_KINDS["name-symbol"][lang]["model"]:
            kinds["name-symbol"] = kinds.get("name-symbol", 0) + 1
            if re.search(
                r"(?<![A-Za-z])" + re.escape(note["Symbol"]) + r"(?![a-z])",
                visible(q).replace(html.unescape(note["Name"]), ""),
            ):
                raise ValueError("A name → symbol front shows its symbol")
            return
        if mid == ELEMENT_KINDS["symbol-name"][lang]["model"]:
            kinds["symbol-name"] = kinds.get("symbol-name", 0) + 1
            if html.unescape(note["Name"]) in visible(q) or 'class="rv-lit"' not in q:
                raise ValueError("A symbol → name front shows its name or no lit cell")
            return


def check(package, output):
    meta = json.loads(package.with_suffix(".rectoverso.json").read_text())
    count = meta["cards"]
    with tempfile.TemporaryDirectory(prefix="native-anki-", dir=output) as temporary:
        root = Path(temporary)
        (root / "a").mkdir()
        (root / "b").mkdir()
        col = Collection(str(root / "a/collection.anki2"))
        try:
            import_package(col, package)
            ids = col.find_cards("")
            if len(ids) != count:
                raise ValueError(f"{len(ids)} cards, the sidecar says {count}")
            guids = {col.get_note(nid).guid for nid in col.find_notes("")}
            if len(guids) != col.note_count():
                raise ValueError("Duplicate note identities")
            kinds = {}
            for cid in ids:
                card = col.get_card(cid)
                note = card.note()
                q, a = card.question(), card.answer()
                if not visible(q) and "<img" not in q:
                    raise ValueError("Empty question")
                if not (visible(a) or "<img" in a) or a.strip() == q.strip():
                    raise ValueError("The answer shows nothing beyond the question")
                if "RV-OCCLUSION-1" in q + a or (
                    FIELD in note.keys() and note[FIELD] and note[FIELD] in q + a
                ):
                    raise ValueError(
                        "The RectoVerso Occlusion record is shown on a card"
                    )
                own_checks(col, card, note, q, a, kinds)
            media = col.media.check()
            if media.missing:
                raise ValueError("Missing media: " + str(list(media.missing)))
            card = col.get_card(min(ids))
            col.decks.select(card.did)
            studied = col.sched.getCard()
            if studied is None:
                raise ValueError("No card offered for study")
            col.sched.answerCard(studied, 3)
            before = state(col.get_card(studied.id))
            import_package(col, package)
            if state(col.get_card(studied.id)) != before:
                raise ValueError("A repeat import changed studied progress")
            notes = {
                col.get_note(nid).guid: tuple(col.get_note(nid).fields)
                for nid in col.find_notes("")
            }
            col.export_anki_package(
                out_path=str(root / "roundtrip.apkg"),
                options=ExportAnkiPackageOptions(with_scheduling=True, with_media=True),
                limit=None,
            )
            media_hashes = {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in Path(col.media.dir()).iterdir()
                if p.is_file()
            }
        finally:
            col.close()
        other = Collection(str(root / "b/collection.anki2"))
        try:
            import_package(other, root / "roundtrip.apkg")
            actual = {
                other.get_note(nid).guid: tuple(other.get_note(nid).fields)
                for nid in other.find_notes("")
            }
            if (
                actual != notes
                or other.card_count() != count
                or other.media.check().missing
            ):
                raise ValueError("Export/reimport changed notes, cards or media")
            actual_media = {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in Path(other.media.dir()).iterdir()
                if p.is_file()
            }
            if actual_media != media_hashes:
                raise ValueError("Media bytes changed through export")
            if state(other.get_card(before[0])) != before:
                raise ValueError("Export/reimport lost study state")
        finally:
            other.close()
    result = {
        "package": package.name,
        "cards": count,
        "notes": len(guids),
        "renderedSides": count * 2,
        "missingMedia": 0,
        "deckNoteTypeCards": kinds,
        "realStudyPreserved": True,
        "exportReimportFieldsAndMediaExact": True,
        "nativeDesktopVisualReview": "separate gate",
    }
    print(json.dumps(result), flush=True)
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("packages", type=Path, nargs="+")
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    results = [check(x, a.output) for x in a.packages]
    (a.output / "anki-validation.json").write_text(json.dumps(results, indent=2) + "\n")
