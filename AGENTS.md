# Periodic table: rules for agents

**Read `kit/AGENTS.md` first.** The deck kit ([rectoverso-deck-kit](https://github.com/rectoversohq/rectoverso-deck-kit), a submodule at `kit/`: `git submodule update --init kit`) holds what every deck follows: the deck contract, its check, and the rules for authoring, covers, languages, versions and releases. This file adds only this deck's own rules and checks.

## This deck
- **Periodic table** (« Tableau périodique »), `rectoversohq/rectoverso-periodic-table`, public. GUID prefix `rv-periodic-table`; languages English and French; license CC BY 4.0. Asks the 118 elements three ways: the symbol hidden in its cell (an image occlusion, one card a symbol), the symbol from the name, and the element whose cell is lit. Its build renders its pictures (`renderedPictures`).
- **Our own material here is CC BY 4.0, © Simon Pinkas** (never another name or a company).
- **The deck's own issues are in this repository;** the app's side of the deck (its pin, the catalog, the gallery) is an issue in simonpinkas/RectoVerso.

## This repository
- **Read first:** docs/source.md, before changing content, artwork, identities or the package format; docs/review.md records the reviewed snapshot, docs/validation.md the checks, docs/decisions.md the dated decisions. French versions beside them (`.fr.md`).
- **Where things are:** shared facts in source/elements.json, names in source/translations/, original SVGs in artwork/, the pinned artwork record in source/artwork.json (the rendered pictures stay out of Git: builds render them, scripts/artwork.py), tools in scripts/, checks in scripts/checks/, tests in tests/. Packages, caches and evidence go in an output folder outside the repository.
- **Before a commit, after a content or artwork change:** rebuild both languages; run the source tests, the Anki validators (validate_source.py, validate-anki.py, validate-rebuild.py) and the bundled-reviewer check; look at the light and dark originals and the clean pairs.

## This deck's content
- **Identities:** the atomic number is an element's stable identity; each language has its own ids. The GUIDs are `rv-periodic-table-<language>-…` since 0.2.0-rc.1 (the table's occlusion note, `-table`; by atomic number, `-079-name` and `-079-symbol`).
- **Facts:** a correction comes with its provenance. The detached series don't assert a group-3 convention; the color categories are a documented teaching convention.
- **Artwork:** no changed pixel outside the symbols' regions, and no answer metadata on a front.
- **Each note's header** (`Header`) is the question its card asks, in its language (« Quel est son symbole ? »): RectoVerso shows it as the card's line.

## This deck's checks
- `python3 kit/check.py --rectoverso`: the deck contract, as RectoVerso's gallery takes a deck, by the kit pinned here (`kit/docs/check.md` explains each refusal). The workflow runs it first.
- `scripts/checks/validate-anki.py` and `validate-rebuild.py`, the two every deck has (`kit/docs/getting-started.md`), and scripts/checks/verify-artwork.py and render_anki.py; tests in tests/ (test_source.py, test_metadata.py, test_artwork_clearance.py).
- Anki desktop's look and RectoVerso's own are separate checks: a rendering in Anki's backend isn't a visual approval.

## This deck's covers
- **Six masters:** three designs in light and dark, shared by English and French. See [Building gallery covers](docs/build.md) for their provenance and rebuild commands.
- **PNG** for drawn art (a JPEG only for a photograph); small files (they ship inside the app's download: aim under 400 KB).
- **Accurate:** whatever real place, flag, element, name or shape a cover shows is right, checked against the deck's own sources.
- **Masters** in artwork/covers/, SVG, named as their PNGs (`.svg`), with lettering outlined (or a pinned, embedded font) so every render is identical; no external resource.
- **scripts/covers.py** renders every master to its PNG at 2010 × 1340, called by scripts/build.py, into the build's output folder, never into the repository (nothing rendered is committed). Two independent builds give the same bytes.
- **scripts/checks/verify-covers.py,** run by the deck's CI, refuses a wrong size or name, a language without a light and a dark cover, a worded cover missing in a language, an ambiguous set, and anything but background in the top-trailing corner the gallery keeps for the language's pill (within 4 per channel of the corner's dominant color). Its tests in tests/.
- **A new or changed cover** is shown to the owner as rendered PNGs, light and dark, every language, before it's merged.

## The kit
- **Pinned at `kit/`, at a tag.** Moving it is a pull request of its own, with the check run again (`kit/docs/versioning.md`). Never edit a file under `kit/` from here.
- **A new field, value or form** is a change to the kit, made there first (`kit/CONTRIBUTING.md`): this deck never uses one alone.
