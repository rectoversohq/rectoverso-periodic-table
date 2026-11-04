# Source and maintenance

## Content

The deck asks three ways, per language: one native Anki image-occlusion note with 118 ordinals asks for the **symbol** at a position; 118 **symbol → name** notes show the whole drawing with one element’s cell lit (outlined, nothing masked) and ask its name; 118 **name → symbol** notes give the name as text and ask its symbol. After answering, the full localized name appears with atomic number, group and period.

The lit notes carry the drawing with every symbol and a CSS outline over the cell for Anki; their optional **RectoVerso Occlusion** record has `"mode": "lit"`, no Anki masks (`masksSHA256` of the empty string) and one region: the whole cell (88 × 124 source units), its `title` and `answer` the name, and a `position` (« period 4, group 8 »; « lanthanoid row, 1 of 15 » in the detached rows) that VoiceOver reads instead of the name. Each element note has one card and its own identities (`ELEMENT_KINDS` in `scripts/source_data.py`); the occlusion note’s are unchanged. Every name and symbol is checked against sources independent of Wikidata: PubChem for symbols and English names, French references for French names. Detached La–Lu and Ac–Lr entries omit group rather than asserting a disputed group-3 placement.

The English deck uses American **Aluminum** and **Cesium**. French uses **Lutétium** (the older **Lutécium** remains the upstream Wikidata label) and **Tennesse**. `source/provenance.json` records the source and exceptions. The symbol is identical in both languages.

The original 18-column drawing contains atomic numbers as position cues, symbols and group/period markers. It does not show element names. Categories are a pedagogical palette: alkali metals, alkaline-earth metals, transition metals, post-transition metals, metalloids, nonmetals, halogens, noble gases, lanthanoids and actinoids. For superheavy elements, the color follows the column convention; it does not assert experimentally established chemistry. Polonium is placed among post-transition metals. Color is not the only identifier: row, column and atomic number remain visible.

## Artwork

`scripts/artwork.py` defines the drawing and generates four original SVG masters in one 1920 × 1480 coordinate system. Each run writes those masters to `artwork/`, replacing the previous SVG files, and renders the same generated vectors as 3840 × 2960 sRGB PNGs using the supplied macOS SF Pro font. Edit the drawing in the Python generator; direct SVG edits are overwritten on the next run. The clean image omits only the 118 symbol rectangles; numbers, cell colors, corners, spacing and canvas are identical. The renderer exhaustively checks that every changed pixel lies inside a symbol region. Both themes have a flat continuous canvas.

`artwork.json` in the output folder records the four PNG hashes and dimensions, normalized region coordinates, cells, canvas RGB and resolved font identity. The same vectors draw different pixels with another font file or another Qt platform (the hosted runner's font, or a session with a window instead of `QT_QPA_PLATFORM=offscreen`), so the packages ship **registered** pictures: the four reviewed PNGs in `source/media` and their record, `source/artwork.json`, which RectoVerso's gallery also reads as the deck's pictures. They are the offscreen render of this revision on macOS 27.2 (font SHA-256 `44890958…`), the pictures already reviewed on the simulators and in Core. `scripts/checks/verify-artwork.py` checks them against the record and the clean-pixel rule, and compares a fresh render's geometry; a fresh render's pixels are reported, not required. A changed drawing is rendered, reviewed and registered under new file names. Packages and validation collections stay outside source Git.

## Anki and preparation

The builder retains Anki's native image-occlusion note kind and renderer. **Occlusion**, **Image**, **Header**, **Back Extra** and **Comments** remain ordinary native fields. The optional **RectoVerso Occlusion** field is not referenced by either template. It contains `RV-OCCLUSION-1:` followed by base64 canonical JSON and four media-preserving image references.

The JSON records version 1; original/clean light and dark asset names, SHA-256 and pixel dimensions; the exact raw Occlusion field SHA-256; `hideAll` mode; and 118 stable `label` regions. Each region has a 1-based ordinal, normalized rectangle, symbol answer, localized full-name title and compact detail. The canvas method is `flat-srgb-v1`, with exact light/dark RGB components. Metadata is capability-bound to exact artwork and masks, not to a filename alone.

Anki uses the original figure and its native masks. The back selects only its ordinal's facts from **Back Extra**; this remains functional without the optional field. Anki dark mode chooses the registered dark original. RectoVerso can use the validated clean pair and authored answer through its separate format implementation.

## Identity and updates

`IDS` in `scripts/source_data.py` is the authoritative identity table. The two languages have different deck, model, note, GUID, template, field and card identities. Card ordinals remain atomic-number minus one. Anki's add APIs require newly allocated rows, so the source builder assigns deterministic note/card rows after native creation; validators then exercise the generated package through Anki's importer and scheduler. Anki assigns local deck IDs when importing into another collection; stable package IDs and names do not imply that every user's database has the source deck ID.

A patch fixes content without changing identities. A minor version adds compatible content. A major version is required only if notes cannot carry over. Every note and the deck's note types carry `contentModifiedAt` from `rectoverso.json`: a content change moves it forward to the time of the change, never into the future, since Anki updates a note only when the package's modification second differs from the collection's (If Newer: only when it is later). Rebuild both languages and run `scripts/checks/validate_source.py` against an independently rebuilt package, and `scripts/checks/validate-rebuild.py` on each pair: no duplicates, lost review history or media changes are accepted. The source is reviewed in this repository; merge and package publication require owner approval. No package release exists. See [source review](review.md).

## Gallery layout

`rectoverso.json` is the deck's single description, in the layout of RectoVerso's gallery (its `docs/app/library.md`, "A deck's metadata"): identity and version, the title, subject, headline and description in both languages, the category, creator, license, sources, image credits, `proOnly`, the source files, and for each language its artifact id, title, card count, package and sample. `scripts/source_data.py` expands one language (`inputs(language)`: its metadata, notes, note types and deck) for RectoVerso's `scripts/gallery/decks.py`; `scripts/build.py --language <code> --out <package>` builds it and writes the sidecar, that metadata with the package's bytes and SHA-256. The sample is Au's card of the occlusion note, `rvPTenV1001/79` and `rvPTfrV1001/79` (Anki's ordinal 78). The GUIDs keep their candidate form (`rvPTenV1001`, `rvPTenN079`, `rvPTenL079`); the gallery's `<guidPrefix>-<language>-` rule doesn't fit them yet (see the source PR).

## Validation boundary

The backend check imports both language packages, exercises the native editor update API, checks every front/back, validates media and metadata, answers a card, exports and reimports its schedule, then applies an independently rebuilt package and checks that history survives. A combined collection must contain two notes and 236 distinct cards.

The bundled Anki reviewer check renders all 118 fronts and backs, both languages, both themes: 944 pages. It verifies the selected ordinal, actual target mask alpha, correct theme image, one correct answer name, and absence of optional metadata. Saved screenshots supplement these checks. This is Anki's real bundled web renderer in Qt, not a screenshot of the full desktop editor. A complete manual Anki desktop editing session and physical-device behavior are separate review gates.

## Atomic-number clearance

The cell keeps an atomic-number band above the symbol. Its height is 124 source units, its row pitch 132, and the symbol baseline 89; the number remains at baseline 21. The 70 × 40 symbol region begins at (9, 58) within the cell. SF Pro sizes and weights remain 14 for numbers and 36 semibold for symbols. All 118 symbols, including descenders, fit their regions.

The raster regression checks every number in both themes against RectoVerso's unchanged capsule geometry and black rim: at least 10 source units remain clear. The app's margin, centering, source registration and imported-deck behavior are unchanged. Native screenshots check opening and actual pinch zoom separately from this source-level test.

This artwork revision uses `-v2.png` media names. Changed artwork must receive new names: Anki may rename same-name media on update, while the optional preparation's base64 JSON keeps its original filename and hash. An update is checked with the ordinary **If Newer** policy, preserving card/note/model/field IDs, studied state and review history. `scripts/checks/validate_source.py --prior-packages OLD_PACKAGE_DIRECTORY` adds that check and a scheduled export/reimport; the option may be repeated. Earlier candidate media may remain unused in an existing Anki collection and are not deleted.
