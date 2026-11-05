# Periodic table source

@~/Dev/RectoVerso/agents/decks.md

Above: the rules every RectoVerso gallery deck follows (`agents/decks.md` in RectoVerso, `~/Dev/RectoVerso` on the owner's Mac). Below: this repository's own.

- **Read first:** docs/source.md, before changing content, artwork, identities or the package format; docs/review.md records the reviewed snapshot.
- **Where things are:** shared facts in source/elements.json, names in source/translations/, original SVGs in artwork/, the pinned artwork record in source/artwork.json (the pictures stay out of Git: builds render them), tools in scripts/, checks in scripts/checks/. Packages, caches and evidence go in an output folder outside the repository.
- **Identities:** the atomic number is an element's stable identity; each language has its own ids. The GUIDs move to RectoVerso's layout, rv-periodic-table-… (simonpinkas/RectoVerso#746): until that release, the published compact form stays as it is.
- **Facts:** a correction comes with its provenance. The detached series don't assert a group-3 convention; the color categories are a documented teaching convention.
- **After a content or artwork change:** rebuild both languages; run the source tests, the Anki validators (validate_source.py, validate-anki.py, validate-rebuild.py) and the bundled-reviewer check; look at the light and dark originals and the clean pairs. No changed pixel outside the symbols' regions, and no answer metadata on a front.
