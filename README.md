# Periodic table

[Français](README.fr.md)

An original, bilingual deck of the 118 elements, three cards each: the table with a symbol masked (**which symbol belongs here?**), the table with an element’s cell lit (**which element is this?**), and an element’s name (**what’s its symbol?**). The full element name and compact atomic-number, group and period facts follow each answer. English and French are separate packages built from one source. The 18-column figure has registered light/dark original and clean pairs; only symbol regions are removed.

This is a **source review candidate**, version **0.1.0-rc.1**. The source is available for review; no package release is published. Original artwork and deck: © Simon Pinkas, **CC BY 4.0**. Factual Wikidata records: **CC0**. See [credits](NOTICE.md), [source and identity rules](docs/source.md), and [validation](docs/validation.md).

## Get the source

The complete candidate is reviewed in [source issue #1](https://github.com/rectoversohq/rectoverso-periodic-table/issues/1). The default branch is a landing page until the source PR is merged. Clone the review branch to run the commands below:

```sh
git clone --branch codex/1-source-candidate https://github.com/rectoversohq/rectoverso-periodic-table.git
cd rectoverso-periodic-table
```

See [source review and validation status](docs/review.md).

## Build and check

Use Python 3.14, Anki 26.9.3, and Qt/PyQt 6.11.0. The drawing uses the macOS-provided SF Pro font; its file is never bundled. Install `requirements.txt` in a dedicated environment. Anki's bundled Python/Qt environment can also run the artwork and reviewer checks, while its matching Python backend builds packages.

Choose an output directory outside this source repository. The builder makes one language's package from the source and the registered pictures in `source/media`, and refuses to overwrite a package.

```sh
export DECK_OUT=/path/to/new-output-directory
python -m unittest discover -s tests
python scripts/checks/verify-artwork.py
for lang in en fr; do
  file=$(python -c "import json, sys; print(json.load(open('rectoverso.json'))['languages'][sys.argv[1]]['package']['file'])" "$lang")
  python scripts/build.py --language "$lang" --out "$DECK_OUT/packages/$file"
  python scripts/build.py --language "$lang" --out "$DECK_OUT/rebuild/$file"
  python scripts/checks/validate-rebuild.py "$DECK_OUT/packages/$file" "$DECK_OUT/rebuild/$file" "$DECK_OUT/rebuild-$lang.json"
done
python scripts/checks/validate_source.py --packages "$DECK_OUT/packages" \
  --update-packages "$DECK_OUT/rebuild" --out "$DECK_OUT/anki-check"
python scripts/checks/validate-anki.py --output "$DECK_OUT/anki-packages" "$DECK_OUT"/packages/*.apkg
python scripts/checks/render_anki.py --evidence "$DECK_OUT/anki-check" \
  --web /Applications/Anki.app/Contents/Resources/app_packages/_aqt/data/web \
  --out "$DECK_OUT/render-check"
```

`--web` must point to the **same Anki version's** installed reviewer assets. The render check uses a Qt window. In a graphical session, run it normally; for headless CI set `QT_QPA_PLATFORM=offscreen` and `QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu` so canvas masks use software rendering. `--sample` checks eight representative elements before the full 944-page pass. Adding `--document-delay-ms 300 --parser-delay-ms 300` exercises slow navigation and HTML parsing without changing the expected card result. For an installed `aqt` distribution, its `_aqt/data/web` directory is equivalent.

Outputs: `Periodic-table-en.apkg`, `Tableau-periodique-fr.apkg`, each package's sidecar (`.rectoverso.json`: the language's metadata from `rectoverso.json` with the package's bytes and SHA-256), backend reports and native-reviewer captures. `validate_source.py` is the source's complete Anki check (editor, updates, scheduling); `validate-anki.py` and `validate-rebuild.py` are the per-package checks RectoVerso's gallery runs. Every note and note type carries `contentModifiedAt`, so two builds hold the same notes; the archive bytes may still differ. Use the sidecar belonging to the actual package.

## Gallery metadata

`rectoverso.json` follows RectoVerso's gallery layout ([simonpinkas/RectoVerso#690](https://github.com/simonpinkas/RectoVerso/issues/690)): the deck's title, subject, headline and description in English and French, its category (`sciences`), creator, license, sources, image credits, and for each language its package and its **sample** question, the gold cell Au (`rvPTenV1001/79`, `rvPTfrV1001/79`). `scripts/source_data.py` expands one language's metadata and notes for RectoVerso's `scripts/gallery/decks.py`. The headline and description are drafts for the owner's review.

## Update

Edit shared facts in `source/elements.json` and names in `source/translations/`. Preserve region ordinals and all language identities. A content change moves `contentModifiedAt` in `rectoverso.json` forward to the time of the change (never into the future): Anki updates a note only when the package's modification time differs from the collection's. Rebuild both packages, check them against an independently rebuilt update, inspect both themes and clean pairs, and review any content change before publication. The current scope does not modify RectoVerso, its sample deck or the gallery.

The original SVG masters are generated from `scripts/artwork.py`; edit the drawing there and regenerate all four together (`--font /System/Library/Fonts/SFNS.ttf --out "$DECK_OUT/artwork"`, with `QT_QPA_PLATFORM=offscreen`). It renders them at 3840 × 2960, with the actual resolved font family and font digest recorded. The pixels depend on the font file and the Qt platform that draw them, so the packages ship the **registered** pictures: the four PNGs in `source/media` and their record, `source/artwork.json`. A changed drawing is reviewed, then registered under new file names (`-v3.png`). `scripts/checks/verify-artwork.py` checks the registered pictures against their record, rejects any clean-image pixel change outside the 118 symbol regions, and with `--render` compares a fresh render's geometry. The optional **RectoVerso Occlusion** field binds exact masks and media; Anki's ordinary question and answer remain usable without it.
