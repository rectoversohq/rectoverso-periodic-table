"""Compose one language's notes from the shared facts, its names and the pinned artwork record.

`inputs(language)` is the interface RectoVerso's gallery check reads (its `scripts/gallery/decks.py`):
the language's expanded metadata, its notes (GUID, note type, fields, cards), its note types and its
deck. `scripts/build.py` turns the same notes into the Anki package.
"""

import base64
import hashlib
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD = "RectoVerso Occlusion"
# The pinned artwork record: the font, the renderer, the four pictures' hashes and sizes, the
# regions, cells and canvas. The pictures themselves are rendered by each build (scripts/build.py).
ARTWORK = ROOT / "source/artwork.json"
# Every note's GUID is the deck's prefix, the language, then the note, in lowercase words and
# hyphens (RectoVerso's agents/decks.md): rv-periodic-table-en-table, rv-periodic-table-en-079-name.
IDS = {
    "en": {
        "deck": 619101000001,
        "model": 619102000001,
        "note": 619103000001,
        "guid": "rv-periodic-table-en-table",
        "cardBase": 619104100000,
    },
    "fr": {
        "deck": 619101000002,
        "model": 619102000002,
        "note": 619103000002,
        "guid": "rv-periodic-table-fr-table",
        "cardBase": 619104200000,
    },
}
TITLES = {"en": "Periodic table", "fr": "Tableau périodique"}
# One note per element and language for each added card kind (#5). The occlusion note above
# keeps its identities; these never reuse its rows. Element z's note, card and GUID derive from z:
# its GUID names the element by its atomic number, then what the note asks (element_guid).
ELEMENT_KINDS = {
    "name-symbol": {
        "en": {
            "model": 619102000011,
            "template": 619106000011,
            "fieldBase": 619105001100,
            "noteBase": 619103101000,
            "cardBase": 619104110000,
            "guid": "rv-periodic-table-en-{z:03d}-symbol",
        },
        "fr": {
            "model": 619102000012,
            "template": 619106000012,
            "fieldBase": 619105002100,
            "noteBase": 619103201000,
            "cardBase": 619104210000,
            "guid": "rv-periodic-table-fr-{z:03d}-symbol",
        },
    },
    "symbol-name": {
        "en": {
            "model": 619102000021,
            "template": 619106000021,
            "fieldBase": 619105001200,
            "noteBase": 619103102000,
            "cardBase": 619104120000,
            "guid": "rv-periodic-table-en-{z:03d}-name",
        },
        "fr": {
            "model": 619102000022,
            "template": 619106000022,
            "fieldBase": 619105002200,
            "noteBase": 619103202000,
            "cardBase": 619104220000,
            "guid": "rv-periodic-table-fr-{z:03d}-name",
        },
    },
}
HEADERS = {
    "name-symbol": {"en": "What’s its symbol?", "fr": "Quel est son symbole\u202f?"},
    "symbol-name": {
        "en": "Which element is this?",
        "fr": "Quel est cet élément\u202f?",
    },
}
KIND_NAMES = {
    "name-symbol": {"en": "Name → Symbol", "fr": "Nom → Symbole"},
    "symbol-name": {"en": "Symbol → Name", "fr": "Symbole → Nom"},
}


def read(path):
    return json.loads((ROOT / path).read_text())


def content_modified():
    """The reviewed content's time (rectoverso.json), in seconds: every note and note type carries it.

    Anki applies an update to a note only when the package's modification second differs from the
    collection's (If Newer: only when it is later). Stamping the build's wall-clock time made that
    second depend on when the build ran, so an edit made in the same second as a build was skipped.
    """
    stamp = read("rectoverso.json")["contentModifiedAt"]
    return int(datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp())


def element_guid(kind, lang, z):
    """Element z's note of this kind: rv-periodic-table-en-079-symbol asks gold's symbol."""
    return ELEMENT_KINDS[kind][lang]["guid"].format(z=z)


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


def artwork(record=ARTWORK):
    """The artwork record: the four pictures' files and hashes, regions, cells, canvas, font, renderer."""
    return json.loads(Path(record).read_text())


def occlusion_note(lang, elements, names, art):
    """The image-occlusion note: one card per symbol, its name and facts after the answer."""
    regions = []
    masks = []
    for e, g in zip(elements, art["regions"]):
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
    assets = art["assets"]
    preparation = {
        "version": 1,
        "source": assets["rv-periodic-light"],
        "clean": assets["rv-periodic-light-clean"],
        "darkSource": assets["rv-periodic-dark"],
        "darkClean": assets["rv-periodic-dark-clean"],
        "masksSHA256": sha(masks.encode()),
        "mode": "hideAll",
        "regions": regions,
        "canvas": art["canvas"],
    }
    extras = []
    for e in elements:
        z = e["atomicNumber"]
        extras.append(
            f'<section class="rv-fact" data-rv-ordinal="{z}" hidden><div class="rv-name">{html.escape(names[str(z)])}</div><div class="rv-detail">{html.escape(detail(e, lang))}</div></section>'
        )
    fields = {
        "Occlusion": masks,
        "Image": '<img src="rv-periodic-light-v2.png"><img src="rv-periodic-dark-v2.png" style="display:none" aria-hidden="true">',
        "Header": "Which symbol belongs here?"
        if lang == "en"
        else "Quel symbole se trouve ici\u00a0?",
        FIELD: "RV-OCCLUSION-1:"
        + base64.b64encode(compact(preparation).encode()).decode()
        + "".join('<img src="' + a["file"] + '">' for a in assets.values()),
        "Back Extra": "".join(extras)
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
})();</script>""",
        "Comments": "Original artwork and deck © Simon Pinkas, CC BY 4.0. Element facts: Wikidata CC0, checked against IUPAC. "
        + (
            "Detached series have no asserted group number."
            if lang == "en"
            else "Aucun numéro de groupe n’est attribué aux séries détachées."
        ),
    }
    return {
        "guid": IDS[lang]["guid"],
        "model": "occlusion",
        "fields": fields,
        "tags": ["rectoverso", "chemistry", "periodic-table", lang],
        "cards": len(elements),
    }


def element_notes(lang, elements, names, art):
    """Name → symbol (text) and symbol → name (the full drawing, the element's cell lit)."""
    assets = art["assets"]
    comments = "Original artwork and deck © Simon Pinkas, CC BY 4.0. Names and symbols: Wikidata CC0, checked against PubChem and French references."
    notes = []
    for e, g in zip(elements, art["regions"]):
        z = e["atomicNumber"]
        assert g["atomicNumber"] == z
        name, symbol, details = names[str(z)], e["symbol"], detail(e, lang)
        notes.append(
            {
                "guid": element_guid("name-symbol", lang, z),
                "model": "name-symbol",
                "atomicNumber": z,
                "fields": {
                    "Name": html.escape(name),
                    "Symbol": symbol,
                    "Header": HEADERS["name-symbol"][lang],
                    "Details": html.escape(details),
                    "Comments": comments,
                },
                "tags": [
                    "rectoverso",
                    "chemistry",
                    "periodic-table",
                    "name-symbol",
                    lang,
                ],
            }
        )
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
            "canvas": art["canvas"],
        }
        notes.append(
            {
                "guid": element_guid("symbol-name", lang, z),
                "model": "symbol-name",
                "atomicNumber": z,
                "fields": {
                    "Symbol": symbol,
                    "Name": html.escape(name),
                    "Header": HEADERS["symbol-name"][lang],
                    "Lit": f"left:{left * 100:.4f}%;top:{top * 100:.4f}%;width:{width * 100:.4f}%;height:{height * 100:.4f}%",
                    "Details": html.escape(details),
                    FIELD: "RV-OCCLUSION-1:"
                    + base64.b64encode(compact(preparation).encode()).decode()
                    + "".join('<img src="' + a["file"] + '">' for a in assets.values()),
                    "Comments": comments,
                },
                "tags": [
                    "rectoverso",
                    "chemistry",
                    "periodic-table",
                    "symbol-name",
                    lang,
                ],
            }
        )
    return notes


def inputs(language, record=ARTWORK):
    """One language: (expanded metadata, notes, note types, deck), from the source alone."""
    meta = read("rectoverso.json")
    artifact = meta["languages"][language]
    elements = read("source/elements.json")
    names = read(f"source/translations/{language}.json")
    art = artwork(record)
    notes = [occlusion_note(language, elements, names, art)] + element_notes(
        language, elements, names, art
    )
    types = {"occlusion": {"id": IDS[language]["model"]}} | {
        kind: {"id": ids[language]["model"]} for kind, ids in ELEMENT_KINDS.items()
    }
    deck = {"id": IDS[language]["deck"], "name": TITLES[language]}
    expanded = dict(meta)
    expanded.pop("languages")
    expanded.update(
        id=artifact["id"],
        deckID=meta["id"],
        language=language,
        package=artifact["package"],
        sample=artifact["sample"],
    )
    return expanded, notes, types, deck
