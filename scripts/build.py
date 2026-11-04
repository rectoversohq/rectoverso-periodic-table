#!/usr/bin/env python3
"""Build the two language packages from source and registered artwork using native Anki IO."""

import argparse
import base64
import hashlib
import html
import json
from datetime import datetime
from pathlib import Path
from anki.collection import Collection, ExportAnkiPackageOptions
from anki.buildinfo import version as anki_version

ROOT = Path(__file__).resolve().parents[1]
FIELD = "RectoVerso Occlusion"
IDS = {
    "en": {
        "deck": 619101000001,
        "model": 619102000001,
        "note": 619103000001,
        "guid": "rvPTenV1001",
        "cardBase": 619104100000,
    },
    "fr": {
        "deck": 619101000002,
        "model": 619102000002,
        "note": 619103000002,
        "guid": "rvPTfrV1001",
        "cardBase": 619104200000,
    },
}
TITLES = {"en": "Periodic table", "fr": "Tableau périodique"}


def content_modified():
    """The reviewed content's time (rectoverso.json), in seconds: every note and note type carries it.

    Anki applies an update to a note only when the package's modification second differs from the
    collection's (If Newer: only when it is later). Stamping the build's wall-clock time made that
    second depend on when the build ran, so an edit made in the same second as a build was skipped.
    """
    stamp = json.loads((ROOT / "rectoverso.json").read_text())["contentModifiedAt"]
    return int(datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp())


# One note per element and language for each added card kind (#5). The occlusion note above
# keeps its identities; these never reuse its rows. Element z's note, card and GUID derive from z.
ELEMENT_KINDS = {
    "name-symbol": {
        "en": {
            "model": 619102000011,
            "template": 619106000011,
            "fieldBase": 619105001100,
            "noteBase": 619103101000,
            "cardBase": 619104110000,
            "guid": "rvPTenN",
        },
        "fr": {
            "model": 619102000012,
            "template": 619106000012,
            "fieldBase": 619105002100,
            "noteBase": 619103201000,
            "cardBase": 619104210000,
            "guid": "rvPTfrN",
        },
    },
    "symbol-name": {
        "en": {
            "model": 619102000021,
            "template": 619106000021,
            "fieldBase": 619105001200,
            "noteBase": 619103102000,
            "cardBase": 619104120000,
            "guid": "rvPTenL",
        },
        "fr": {
            "model": 619102000022,
            "template": 619106000022,
            "fieldBase": 619105002200,
            "noteBase": 619103202000,
            "cardBase": 619104220000,
            "guid": "rvPTfrL",
        },
    },
}
HEADERS = {
    "name-symbol": {"en": "What’s its symbol?", "fr": "Quel est son symbole ?"},
    "symbol-name": {"en": "Which element is this?", "fr": "Quel est cet élément ?"},
}
KIND_NAMES = {
    "name-symbol": {"en": "Name → Symbol", "fr": "Nom → Symbole"},
    "symbol-name": {"en": "Symbol → Name", "fr": "Symbole → Nom"},
}
CARD_CSS = """
.card {font-family: -apple-system, BlinkMacSystemFont, "SF Pro", sans-serif; background:#f7f5ef; color:#252820; font-size:18px; margin:20px; text-align:center;}
.card.nightMode {background:#181a18;color:#f3f2e9;}
.rv-header {font-size:16px;color:#62665c;margin-bottom:16px;}
.nightMode .rv-header {color:#a4aaa0;}
.rv-prompt {font-size:40px;font-weight:600;}
.rv-symbol {font-size:56px;font-weight:600;}
.rv-name {font-size:24px;font-weight:600;margin:16px 0 8px;}
.rv-detail {font-size:14px;line-height:1.5;}
.rv-figure {position:relative;margin:20px auto;max-width:1600px;}
.rv-figure img {display:block;width:100%;height:auto;}
.rv-figure .rv-dark {display:none;}
.nightMode .rv-figure .rv-light {display:none;}
.nightMode .rv-figure .rv-dark {display:block;}
.rv-lit {position:absolute;box-sizing:border-box;border:3px solid #dfb450;border-radius:6px;box-shadow:0 0 0 2px #25282066;}
.nightMode .rv-lit {border-color:#ffd25b;box-shadow:0 0 0 2px #f3f2e966;}
"""


def compact(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def detail(e, lang):
    if lang == "fr":
        return (
            f"Numéro atomique {e['atomicNumber']} · "
            + (f"Groupe {e['group']} · " if e["group"] else "")
            + f"Période {e['period']}"
        )
    return (
        f"Atomic number {e['atomicNumber']} · "
        + (f"Group {e['group']} · " if e["group"] else "")
        + f"Period {e['period']}"
    )


def element_model(col, kind, lang, fields, qfmt, afmt):
    ids = ELEMENT_KINDS[kind][lang]
    model = col.models.new(
        f"Periodic table · {KIND_NAMES[kind][lang]} · {lang.upper()}"
    )
    for name in fields:
        col.models.add_field(model, col.models.new_field(name))
    template = col.models.new_template(KIND_NAMES[kind][lang])
    template["qfmt"], template["afmt"] = qfmt, afmt
    col.models.add_template(model, template)
    model["css"] = CARD_CSS
    col.models.add(model)
    model = col.models.by_name(model["name"])
    old = model["id"]
    model["id"] = ids["model"]
    for i, field in enumerate(model["flds"]):
        field["id"] = ids["fieldBase"] + i
    model["tmpls"][0]["id"] = ids["template"]
    col.models.update(model)
    col.models.remove(old)
    return col.models.get(ids["model"])


def pin(col, note, kind, lang, z):
    """Give a just-added element note and its one card their deterministic source rows."""
    ids = ELEMENT_KINDS[kind][lang]
    nid, cid = ids["noteBase"] + z, ids["cardBase"] + z
    col.db.execute("update cards set nid=? where nid=?", nid, note.id)
    col.db.execute("update notes set id=? where id=?", nid, note.id)
    [card] = col.get_note(nid).cards()
    col.db.execute("update cards set id=? where id=?", cid, card.id)


def add_elements(col, lang, elements, names, artwork, deck_id):
    """Name → symbol (text) and symbol → name (the full drawing, the element's cell lit)."""
    assets = artwork["assets"]
    header = '<div class="rv-header">{{Header}}</div>'
    facts = '<div class="rv-detail">{{Details}}</div>'
    text = element_model(
        col,
        "name-symbol",
        lang,
        ["Name", "Symbol", "Header", "Details", "Comments"],
        header + '<div class="rv-prompt">{{Name}}</div>',
        '{{FrontSide}}<hr id="answer"><div class="rv-symbol">{{Symbol}}</div>' + facts,
    )
    figure = (
        '<div class="rv-figure"><img class="rv-light" src="'
        + assets["rv-periodic-light"]["file"]
        + '">'
        '<img class="rv-dark" src="'
        + assets["rv-periodic-dark"]["file"]
        + '" aria-hidden="true">'
        '<div class="rv-lit" style="{{Lit}}"></div></div>'
    )
    lit = element_model(
        col,
        "symbol-name",
        lang,
        ["Symbol", "Name", "Header", "Lit", "Details", FIELD, "Comments"],
        header + figure,
        header + '<div class="rv-name">{{Name}}</div>' + facts + figure,
    )
    comments = "Original artwork and deck © Simon Pinkas, CC BY 4.0. Names and symbols: Wikidata CC0, checked against PubChem and French references."
    for e, g in zip(elements, artwork["regions"]):
        z = e["atomicNumber"]
        assert g["atomicNumber"] == z
        name, symbol, details = names[str(z)], e["symbol"], detail(e, lang)
        note = col.new_note(text)
        note.guid = f"{ELEMENT_KINDS['name-symbol'][lang]['guid']}{z:03d}"
        note["Name"], note["Symbol"], note["Details"] = (
            html.escape(name),
            symbol,
            html.escape(details),
        )
        note["Header"], note["Comments"] = HEADERS["name-symbol"][lang], comments
        note.tags = ["rectoverso", "chemistry", "periodic-table", "name-symbol", lang]
        col.add_note(note, deck_id)
        pin(col, note, "name-symbol", lang, z)
        left, top, width, height = g["cell"]
        preparation = {
            "version": 1,
            "source": assets["rv-periodic-light"],
            "clean": assets["rv-periodic-light-clean"],
            "darkSource": assets["rv-periodic-dark"],
            "darkClean": assets["rv-periodic-dark-clean"],
            "masksSHA256": sha(b""),
            "mode": "lit",
            "regions": [
                {
                    "id": f"element-{z:03d}-cell",
                    "ordinal": 1,
                    "kind": "label",
                    "geometry": {
                        "kind": "rect",
                        "coordinates": [left, top, width, height],
                    },
                    "answer": name,
                    "title": name,
                    "detail": details,
                    "position": position(e, lang),
                }
            ],
            "canvas": artwork["canvas"],
        }
        note = col.new_note(lit)
        note.guid = f"{ELEMENT_KINDS['symbol-name'][lang]['guid']}{z:03d}"
        note["Symbol"], note["Name"], note["Details"] = (
            symbol,
            html.escape(name),
            html.escape(details),
        )
        note["Header"], note["Comments"] = HEADERS["symbol-name"][lang], comments
        note["Lit"] = (
            f"left:{left * 100:.4f}%;top:{top * 100:.4f}%;width:{width * 100:.4f}%;height:{height * 100:.4f}%"
        )
        note[FIELD] = (
            "RV-OCCLUSION-1:"
            + base64.b64encode(compact(preparation).encode()).decode()
            + "".join('<img src="' + a["file"] + '">' for a in assets.values())
        )
        note.tags = ["rectoverso", "chemistry", "periodic-table", "symbol-name", lang]
        col.add_note(note, deck_id)
        pin(col, note, "symbol-name", lang, z)


def position(e, lang):
    """What VoiceOver says for the lit cell: its place, never its name."""
    if e["group"]:
        return (
            f"période {e['period']}, groupe {e['group']}"
            if lang == "fr"
            else f"period {e['period']}, group {e['group']}"
        )
    # The detached rows: 15 cells each, from column 4 of the drawing.
    place = e["column"] - 3
    if lang == "fr":
        return f"ligne des {'lanthanoïdes' if e['row'] == 8 else 'actinoïdes'}, {place} sur 15"
    return f"{'lanthanoid' if e['row'] == 8 else 'actinoid'} row, {place} of 15"


def build(lang, art, out):
    elements = json.loads((ROOT / "source/elements.json").read_text())
    names = json.loads((ROOT / f"source/translations/{lang}.json").read_text())
    artwork = json.loads((art / "artwork.json").read_text())
    ids = IDS[lang]
    folder = out / lang
    folder.mkdir(parents=True, exist_ok=False)
    col = Collection(str(folder / "source.anki2"))
    col.add_image_occlusion_notetype()
    model = col.models.by_name("Image Occlusion")
    old_model = model["id"]
    model["id"] = ids["model"]
    model["name"] = "Periodic table · " + lang.upper()
    col.models.add_field(model, col.models.new_field(FIELD))
    model["css"] += """
.card {font-family: -apple-system, BlinkMacSystemFont, "SF Pro", sans-serif; background:#f7f5ef; color:#252820; font-size:18px; margin:20px;}
.card.nightMode {background:#181a18;color:#f3f2e9;}
#image-occlusion-container {margin:20px auto;max-width:1600px;}
#image-occlusion-canvas {--inactive-shape-color:#c4c6be;--active-shape-color:#dfb450;--inactive-shape-border:0px transparent;--active-shape-border:1px #252820;--highlight-shape-color:#ffffff00;--highlight-shape-border:1px #797e71;}
.nightMode #image-occlusion-canvas {--inactive-shape-color:#40463f;--active-shape-color:#8e7133;--active-shape-border:1px #f3f2e9;}
.rv-fact {margin:20px auto;max-width:720px;}
.rv-name {font-size:24px;font-weight:600;margin-bottom:8px;}
.rv-detail {font-size:14px;line-height:1.5;}
button {font:inherit;font-size:14px;padding:8px 16px;border-radius:18px;}
"""
    for key in ("qfmt", "afmt"):
        model["tmpls"][0][key] = model["tmpls"][0][key].replace(
            "try {",
            """try {
    const image = document.querySelector('#image-occlusion-container img');
    if (document.body.classList.contains('nightMode')) image.src = 'rv-periodic-dark-v2.png';""",
        )
    # The revealed name and compact facts lead the back, before the large figure.
    model["tmpls"][0]["afmt"] = model["tmpls"][0]["afmt"].replace(
        "{{#Header}}<div>{{Header}}</div>{{/Header}}",
        "{{#Back Extra}}<div>{{Back Extra}}</div>{{/Back Extra}}",
        1,
    )
    marker = "{{#Back Extra}}<div>{{Back Extra}}</div>{{/Back Extra}}"
    position = model["tmpls"][0]["afmt"].rfind(marker)
    model["tmpls"][0]["afmt"] = model["tmpls"][0]["afmt"][:position] + model["tmpls"][
        0
    ]["afmt"][position:].replace(marker, "", 1)
    if lang == "fr":
        model["tmpls"][0]["afmt"] = model["tmpls"][0]["afmt"].replace(
            "Toggle Masks", "Afficher les masques"
        )
    for i, field in enumerate(model["flds"]):
        field["id"] = 619105000000 + (1000 if lang == "en" else 2000) + i
    model["tmpls"][0]["id"] = 619106000000 + (1 if lang == "en" else 2)
    col.models.update(model)
    col.models.remove(old_model)
    deck = col.decks.get(1)
    deck["id"] = ids["deck"]
    deck["name"] = TITLES[lang]
    col.decks.update(deck)
    for asset in artwork["assets"].values():
        col.media.write_data(asset["file"], (art / asset["file"]).read_bytes())
    regions = []
    masks = []
    for e, g in zip(elements, artwork["regions"]):
        assert e["atomicNumber"] == g["atomicNumber"]
        z = e["atomicNumber"]
        coords = g["coordinates"]
        masks.append(
            "{{c"
            + str(z)
            + "::image-occlusion:rect:"
            + ":".join(
                k + "=" + format(v, ".17g")
                for k, v in zip(["left", "top", "width", "height"], coords)
            )
            + ":oi=1}}"
        )
        regions.append(
            {
                "id": f"element-{z:03d}-symbol",
                "ordinal": z,
                "kind": "label",
                "geometry": {"kind": "rect", "coordinates": coords},
                "answer": e["symbol"],
                "title": names[str(z)],
                "detail": detail(e, lang),
            }
        )
    masks = "".join(masks)
    assets = artwork["assets"]
    preparation = {
        "version": 1,
        "source": assets["rv-periodic-light"],
        "clean": assets["rv-periodic-light-clean"],
        "darkSource": assets["rv-periodic-dark"],
        "darkClean": assets["rv-periodic-dark-clean"],
        "masksSHA256": sha(masks.encode()),
        "mode": "hideAll",
        "regions": regions,
        "canvas": artwork["canvas"],
    }
    field = (
        "RV-OCCLUSION-1:"
        + base64.b64encode(compact(preparation).encode()).decode()
        + "".join('<img src="' + a["file"] + '">' for a in assets.values())
    )
    note = col.new_note(model)
    note.guid = ids["guid"]
    note["Occlusion"] = masks
    note["Image"] = (
        '<img src="rv-periodic-light-v2.png"><img src="rv-periodic-dark-v2.png" style="display:none" aria-hidden="true">'
    )
    note["Header"] = (
        "Which symbol belongs here?" if lang == "en" else "Quel symbole se trouve ici ?"
    )
    note[FIELD] = field
    extras = []
    for e in elements:
        z = e["atomicNumber"]
        extras.append(
            f'<section class="rv-fact" data-rv-ordinal="{z}" hidden><div class="rv-name">{html.escape(names[str(z)])}</div><div class="rv-detail">{html.escape(detail(e, lang))}</div></section>'
        )
    note["Back Extra"] = (
        "".join(extras)
        + """<script>(() => {
  const showFact = () => {
    const ordinal = document.querySelector('.cloze-highlight')?.dataset.ordinal;
    if (!ordinal) return;
    document.querySelectorAll('[data-rv-ordinal]').forEach(el => {
      if (el.dataset.rvOrdinal === ordinal) el.hidden = false;
      else el.remove();
    });
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showFact, {once: true});
  } else {
    showFact();
  }
})();</script>"""
    )
    note["Comments"] = (
        "Original artwork and deck © Simon Pinkas, CC BY 4.0. Element facts: Wikidata CC0, checked against IUPAC. "
        + (
            "Detached series have no asserted group number."
            if lang == "en"
            else "Aucun numéro de groupe n’est attribué aux séries détachées."
        )
    )
    note.tags = ["rectoverso", "chemistry", "periodic-table", lang]
    col.add_note(note, ids["deck"])
    # Anki's native add API allocates the row; assign deterministic source IDs after creation.
    col.db.execute("update cards set nid=? where nid=?", ids["note"], note.id)
    col.db.execute("update notes set id=? where id=?", ids["note"], note.id)
    note = col.get_note(ids["note"])
    for card in note.cards():
        col.db.execute(
            "update cards set id=? where id=?", ids["cardBase"] + card.ord + 1, card.id
        )
    cards = note.cards()
    assert len(cards) == 118
    assert {c.ord for c in cards} == set(range(118))
    add_elements(col, lang, elements, names, artwork, ids["deck"])
    assert col.card_count() == 3 * 118
    assert col.note_count() == 1 + 2 * 118
    modified = content_modified()
    models = [ids["model"]] + [kind[lang]["model"] for kind in ELEMENT_KINDS.values()]
    col.db.execute("update notes set mod=?", modified)
    col.db.execute(
        "update notetypes set mtime_secs=? where id in (?, ?, ?)", modified, *models
    )
    (folder / "preparation.json").write_text(
        json.dumps(preparation, ensure_ascii=False, indent=2) + "\n"
    )
    (folder / "occlusion.txt").write_text(masks)
    package = out / (
        ("Periodic-table" if lang == "en" else "Tableau-periodique")
        + "-"
        + lang
        + ".apkg"
    )
    col.export_anki_package(
        out_path=str(package),
        options=ExportAnkiPackageOptions(
            with_scheduling=False,
            with_media=True,
            with_deck_configs=False,
            legacy=False,
        ),
        limit=None,
    )
    media = col.media.check()
    assert not media.missing and not media.unused, (
        list(media.missing),
        list(media.unused),
    )
    col.close()
    metadata = {
        "id": "periodic-table",
        "language": lang,
        "title": TITLES[lang],
        "cards": 3 * 118,
        "notes": 1 + 2 * 118,
        "pictures": 4,
        "sounds": 0,
        "license": "CC-BY-4.0",
        "ankiVersion": anki_version,
        "identities": ids,
        "package": package.name,
        "bytes": package.stat().st_size,
        "sha256": sha(package.read_bytes()),
        "preparationSHA256": sha(compact(preparation).encode()),
    }
    (out / (package.stem + ".rectoverso.json")).write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    )
    return metadata


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artwork", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    assert anki_version == "26.09.3" or anki_version == "26.9.3", anki_version
    report = [build(lang, a.artwork, a.out) for lang in IDS]
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
