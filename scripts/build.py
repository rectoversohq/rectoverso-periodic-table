#!/usr/bin/env python3
"""Build one language's package from the source, rendering its pictures, with native Anki IO.

    python scripts/build.py --language en --out /outside/the/checkout/Periodic-table-en.apkg

renders the four pictures with the pinned renderer and font (`scripts/artwork.py`; macOS's
/System/Library/Fonts/SFNS.ttf, or `--font`), refuses them unless they match the pinned record,
source/artwork.json, byte for byte, then writes the package and, beside it, its sidecar
(`.rectoverso.json`): the language's metadata from `rectoverso.json` with the package's bytes and
SHA-256. `--artwork DIR` builds instead from a `scripts/artwork.py` output folder, unpinned: for a
check on a machine with another font (the hosted CI), never for a release.
Gallery cover PNGs are rendered separately beside the package.
"""

import argparse
import json
import tempfile
from pathlib import Path
from anki.collection import Collection, ExportAnkiPackageOptions
from anki.buildinfo import version as anki_version

from covers import render_covers
from source_data import (
    ARTWORK,
    ELEMENT_KINDS,
    FIELD,
    HEADERS,
    IDS,
    KIND_NAMES,
    TITLES,
    artwork,
    compact,
    content_modified,
    detail,
    element_guid,
    inputs,
    position,
    sha,
)

FONT = Path("/System/Library/Fonts/SFNS.ttf")

__all__ = [
    "ELEMENT_KINDS",
    "FIELD",
    "HEADERS",
    "IDS",
    "compact",
    "content_modified",
    "detail",
    "element_guid",
    "position",
    "sha",
]
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


def element_model(col, kind, lang, fields, qfmt, afmt):
    ids = ELEMENT_KINDS[kind][lang]
    title = f"Periodic table · {KIND_NAMES[kind][lang]} · {lang.upper()}"
    # Added under a provisional name, then given its id and its name: the model at its new id
    # must not share a name with the provisional one, or Anki adds a random suffix to it.
    model = col.models.new(title + " (building)")
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
    model["name"] = title
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


def add_note(col, model, source, deck_id):
    note = col.new_note(model)
    note.guid = source["guid"]
    for key, value in source["fields"].items():
        note[key] = value
    note.tags = source["tags"]
    col.add_note(note, deck_id)
    return note


def add_elements(col, lang, notes, art, deck_id):
    """Name → symbol (text) and symbol → name (the full drawing, the element's cell lit)."""
    assets = art["assets"]
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
    models = {"name-symbol": text, "symbol-name": lit}
    for source in notes:
        note = add_note(col, models[source["model"]], source, deck_id)
        pin(col, note, source["model"], lang, source["atomicNumber"])


def pinned_pictures(font, folder):
    """Render the pictures into `folder`; refuse them unless they are the pinned ones."""
    import artwork as renderer  # PyQt6: only a build that renders needs it.

    pinned = artwork(ARTWORK)
    rendered = renderer.render_artwork(
        font, folder, write_vectors=False, check_clean=False
    )
    if rendered["fontSHA256"] != pinned["fontSHA256"]:
        raise SystemExit(
            f"{font} is not the pinned font (SHA-256 {pinned['fontSHA256']}); "
            "build with --artwork from a render of your own, or pin a new font and pictures"
        )
    for key in ("assets", "renderer", "regions", "canvas"):
        if rendered[key] != pinned[key]:
            raise SystemExit(
                f"The rendered pictures' {key} differ from source/artwork.json's"
            )


def build(lang, out, art_dir=None, font=FONT):
    render_covers(out.parent)
    with tempfile.TemporaryDirectory(prefix="periodic-build-", dir=out.parent) as temp:
        if art_dir:
            record, pictures = art_dir / "artwork.json", art_dir
        else:
            record, pictures = ARTWORK, Path(temp) / "pictures"
            pinned_pictures(font, pictures)
        meta, notes, _, _ = inputs(lang, record)
        art = artwork(record)
        ids = IDS[lang]
        col = Collection(str(Path(temp) / "collection.anki2"))
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
        model["tmpls"][0]["afmt"] = model["tmpls"][0]["afmt"][:position] + model[
            "tmpls"
        ][0]["afmt"][position:].replace(marker, "", 1)
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
        for asset in art["assets"].values():
            col.media.write_data(asset["file"], (pictures / asset["file"]).read_bytes())
        [occlusion] = [n for n in notes if n["model"] == "occlusion"]
        note = add_note(col, model, occlusion, ids["deck"])
        # Anki's native add API allocates the row; assign deterministic source IDs after creation.
        col.db.execute("update cards set nid=? where nid=?", ids["note"], note.id)
        col.db.execute("update notes set id=? where id=?", ids["note"], note.id)
        note = col.get_note(ids["note"])
        for card in note.cards():
            col.db.execute(
                "update cards set id=? where id=?",
                ids["cardBase"] + card.ord + 1,
                card.id,
            )
        cards = note.cards()
        assert len(cards) == occlusion["cards"] == 118
        assert {c.ord for c in cards} == set(range(118))
        add_elements(
            col, lang, [n for n in notes if n["model"] != "occlusion"], art, ids["deck"]
        )
        assert col.card_count() == meta["cards"] == 3 * 118
        assert col.note_count() == len(notes) == 1 + 2 * 118
        modified = content_modified()
        models = [ids["model"]] + [
            kind[lang]["model"] for kind in ELEMENT_KINDS.values()
        ]
        col.db.execute("update notes set mod=?", modified)
        col.db.execute(
            "update notetypes set mtime_secs=? where id in (?, ?, ?)", modified, *models
        )
        col.export_anki_package(
            out_path=str(out),
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
    data = out.read_bytes()
    meta["package"] = meta["package"] | {"bytes": len(data), "sha256": sha(data)}
    out.with_suffix(".rectoverso.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n"
    )
    return {
        "language": lang,
        "cards": meta["cards"],
        "file": out.name,
        "bytes": len(data),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--language", required=True, choices=sorted(IDS))
    p.add_argument(
        "--out", type=Path, required=True, help="The package to write (.apkg)"
    )
    p.add_argument(
        "--artwork",
        type=Path,
        help="An unpinned scripts/artwork.py output folder (default: render the pinned pictures)",
    )
    p.add_argument("--font", type=Path, default=FONT, help="The pinned font file")
    a = p.parse_args()
    assert anki_version == "26.09.3" or anki_version == "26.9.3", anki_version
    if a.out.suffix != ".apkg" or a.out.exists():
        p.error("--out must be a new .apkg path")
    print(
        json.dumps(
            build(a.language, a.out.resolve(), a.artwork, a.font), ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
