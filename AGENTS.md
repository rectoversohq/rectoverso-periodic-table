# Periodic table source

This repository owns one multilingual deck. Read `docs/source.md` before changing content, artwork, identities or the package format.

- Preserve published note GUIDs, deck/model IDs, field IDs and element ordinals. Atomic number is the stable region identity. A language has separate identities.
- Keep shared facts in `source/elements.json`, names in `source/translations/`, original SVGs in `artwork/`, tools in `scripts/`, and checks in `scripts/checks/`. Put packages, caches and evidence in an explicit output directory outside this repository.
- After a content or artwork change, rebuild both languages and run the source tests, Anki validator and bundled-reviewer check. Inspect light/dark originals and clean pairs. Require zero changed pixels outside symbol regions and no answer metadata on a front.
- Add factual corrections with provenance. The detached series do not assert a group-3 convention. Color categories are a documented teaching convention.
- Keep English and French documentation together. New release publication, remote creation and changes to the parent app need the owner's explicit go. Current work is local only.
