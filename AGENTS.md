# Periodic table source

This repository owns one multilingual deck. Read `docs/source.md` before changing content, artwork, identities or the package format.

- Preserve published note GUIDs, deck/model IDs, field IDs and element ordinals. Atomic number is the stable region identity. A language has separate identities.
- Keep shared facts in `source/elements.json`, names in `source/translations/`, original SVGs in `artwork/`, the pinned artwork record in `source/artwork.json` (pictures stay out of Git: builds render them), tools in `scripts/`, and checks in `scripts/checks/`. Put packages, caches and evidence in an explicit output directory outside this repository.
- `rectoverso.json` follows RectoVerso's gallery layout; a content change moves its `contentModifiedAt` forward (never into the future). Headlines and descriptions are the owner's copy.
- After a content or artwork change, rebuild both languages and run the source tests, the Anki validators (`validate_source.py`, `validate-anki.py`, `validate-rebuild.py`) and the bundled-reviewer check. Inspect light/dark originals and clean pairs. Require zero changed pixels outside symbol regions and no answer metadata on a front.
- Add factual corrections with provenance. The detached series do not assert a group-3 convention. Color categories are a documented teaching convention.
- Keep English and French documentation together. Work on a codex/ source branch linked to a source issue. The owner approved this source-review push; merges, tags, releases and parent-app changes require their own go. Read docs/review.md for the reviewed snapshot and current gates.
