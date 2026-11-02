# Periodic table

[Français](README.fr.md)

An original, bilingual image-occlusion deck: **118 symbols**, with the full element name and compact atomic-number, group and period facts after answering. English and French are separate packages built from one source. The 18-column figure has registered light/dark original and clean pairs; only symbol regions are removed.

This is a **source review candidate**, version **0.1.0-rc.1**. The source is available for review; no package release is published. Original artwork and deck: © Simon Pinkas, **CC BY 4.0**. Factual Wikidata records: **CC0**. See [credits](NOTICE.md), [source and identity rules](docs/source.md), and [validation](docs/validation.md).

## Get the source

The complete candidate is reviewed in [source issue #1](https://github.com/rectoversohq/rectoverso-periodic-table/issues/1). The default branch is a landing page until the source PR is merged. Clone the review branch to run the commands below:

```sh
git clone --branch codex/1-source-candidate https://github.com/rectoversohq/rectoverso-periodic-table.git
cd rectoverso-periodic-table
```

See [source review and validation status](docs/review.md).

## Build and check

Use Python 3.13 or 3.14, Anki 26.9.3, and Qt/PyQt 6.11.0. The drawing uses the macOS-provided SF Pro font; its file is never bundled. Install `requirements.txt` in a dedicated environment. Anki's bundled Python/Qt environment can also run the artwork and reviewer checks, while its matching Python backend builds packages.

Choose an output directory outside this source repository. Each run creates new collections and refuses to overwrite an existing language folder.

```sh
export DECK_OUT=/path/to/new-output-directory
python scripts/artwork.py --font /System/Library/Fonts/SFNS.ttf --out "$DECK_OUT/artwork"
python scripts/build.py --artwork "$DECK_OUT/artwork" --out "$DECK_OUT/packages"
python scripts/build.py --artwork "$DECK_OUT/artwork" --out "$DECK_OUT/rebuild"
python -m unittest discover -s tests
python scripts/checks/validate_anki.py --packages "$DECK_OUT/packages" \
  --update-packages "$DECK_OUT/rebuild" --out "$DECK_OUT/anki-check"
python scripts/checks/render_anki.py --evidence "$DECK_OUT/anki-check" \
  --web /Applications/Anki.app/Contents/Resources/app_packages/_aqt/data/web \
  --out "$DECK_OUT/render-check"
```

`--web` must point to the **same Anki version's** installed reviewer assets. The render check uses a Qt window. In a graphical session, run it normally; for headless CI set `QT_QPA_PLATFORM=offscreen` and `QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu` so canvas masks use software rendering. `--sample` checks eight representative elements before the full 944-page pass. Adding `--document-delay-ms 300 --parser-delay-ms 300` exercises slow navigation and HTML parsing without changing the expected card result. For an installed `aqt` distribution, its `_aqt/data/web` directory is equivalent.

Outputs: `Periodic-table-en.apkg`, `Tableau-periodique-fr.apkg`, each package's `.rectoverso.json`, four PNGs and their geometry/hash record, backend reports and native-reviewer captures. `rectoverso.json` in this repository describes the reviewed local candidate; rebuilding Anki archives may change their timestamp-dependent bytes and checksums. Compare validated content and identities, and use the sidecars belonging to the actual packages.

## Update

Edit shared facts in `source/elements.json` and names in `source/translations/`. Preserve region ordinals and all language identities. Rebuild both packages, check them against an independently rebuilt update, inspect both themes and clean pairs, and review any content change before publication. The current scope does not modify RectoVerso, its sample deck or the gallery.

The original SVG masters are generated from `scripts/artwork.py`; edit the drawing there and regenerate all four together. Builds render them at 3840 × 2960, with the actual resolved font family and font digest recorded. The source check rejects any clean-image pixel change outside the 118 symbol regions. The optional **RectoVerso Occlusion** field binds exact masks and media; Anki's ordinary question and answer remain usable without it.
