#!/usr/bin/env python3
"""Check that an independent rebuild is the same deck, and updates one in place with its progress.

    python scripts/checks/validate-rebuild.py FIRST.apkg SECOND.apkg OUTPUT.json

The two packages must hold the same notes (GUID, note id, note type, fields, tags, modification
time), cards (id, note, ordinal), note types (name, fields, templates, CSS, modification time),
deck ids and media bytes; archive bytes may differ. Importing the second over the first, with a
card in review, keeps every card id and that card's progress. Needs Python 3.14 (compression.zstd).
"""

import argparse
from compression import zstd
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import zipfile
from anki.collection import Collection
from anki.import_export_pb2 import ImportAnkiPackageRequest


def import_package(collection, package):
    collection.import_anki_package(
        ImportAnkiPackageRequest(package_path=str(package.resolve()))
    )
    collection.models._clear_cache()


def inspect(package, folder):
    """The package's own rows, read from its database rather than after an import."""
    folder.mkdir()
    with zipfile.ZipFile(package) as archive:
        database = folder / "source.sqlite"
        database.write_bytes(zstd.decompress(archive.read("collection.anki21b")))
        media = sorted(
            hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist()
            if name.isdigit()
        )
    connection = sqlite3.connect(database)
    connection.create_collation(
        "unicase", lambda x, y: (x.lower() > y.lower()) - (x.lower() < y.lower())
    )
    try:
        rows = lambda query: [tuple(r) for r in connection.execute(query)]  # noqa: E731
        types = [r[0] for r in rows("select distinct mid from notes")]
        listed = ",".join(map(str, types))
        return {
            "notes": rows(
                "select id, guid, mid, mod, tags, flds from notes order by id"
            ),
            "cards": rows("select id, nid, ord from cards order by id"),
            "decks": rows("select distinct did from cards order by did"),
            "noteTypes": rows(
                f"select id, name, mtime_secs, config from notetypes where id in ({listed}) order by id"
            ),
            "fields": rows(
                f"select ntid, ord, name, config from fields where ntid in ({listed}) order by ntid, ord"
            ),
            "templates": rows(
                f"select ntid, ord, name, config from templates where ntid in ({listed}) order by ntid, ord"
            ),
            "media": media,
        }
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="rebuild-", dir=args.output.parent
    ) as temporary:
        root = Path(temporary)
        before = inspect(args.first, root / "one")
        after = inspect(args.second, root / "two")
        differ = [key for key in before if before[key] != after[key]]
        if differ:
            raise ValueError("The rebuild differs in " + ", ".join(differ))
        (root / "upgrade").mkdir()
        collection = Collection(str(root / "upgrade" / "collection.anki2"))
        try:
            import_package(collection, args.first)
            ids = set(collection.find_cards(""))
            card = collection.get_card(min(ids))
            card.type = 2
            card.queue = 2
            card.ivl = 19
            card.due = 37
            card.reps = 6
            collection.update_card(card)
            expected = (
                card.id,
                card.nid,
                card.did,
                card.type,
                card.queue,
                card.ivl,
                card.due,
                card.reps,
            )
            import_package(collection, args.second)
            kept = collection.get_card(card.id)
            actual = (
                kept.id,
                kept.nid,
                kept.did,
                kept.type,
                kept.queue,
                kept.ivl,
                kept.due,
                kept.reps,
            )
            if actual != expected or set(collection.find_cards("")) != ids:
                raise ValueError(
                    "The rebuild duplicated cards or changed local identity or progress"
                )
        finally:
            collection.close()
    result = {
        "cards": len(before["cards"]),
        "notes": len(before["notes"]),
        "sourceContentAndIdentitiesExact": True,
        "noteTypesExact": True,
        "mediaExact": True,
        "inPlaceCardIDsAndProgressPreserved": True,
        "archiveBytesMayDiffer": True,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
