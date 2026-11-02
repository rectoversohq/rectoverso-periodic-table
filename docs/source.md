# Source and maintenance

## Content

The deck asks for the **symbol**, not the name: 118 elements, one native Anki image-occlusion note with 118 ordinals per language. After answering, the full localized name appears with atomic number, group and period. Detached La–Lu and Ac–Lr entries omit group rather than asserting a disputed group-3 placement.

The English deck uses American **Aluminum** and **Cesium**. French uses **Lutétium** (the older **Lutécium** remains the upstream Wikidata label) and **Tennesse**. `source/provenance.json` records the source and exceptions. The symbol is identical in both languages.

The original 18-column drawing contains atomic numbers as position cues, symbols and group/period markers. It does not show element names. Categories are a pedagogical palette: alkali metals, alkaline-earth metals, transition metals, post-transition metals, metalloids, nonmetals, halogens, noble gases, lanthanoids and actinoids. For superheavy elements, the color follows the column convention; it does not assert experimentally established chemistry. Polonium is placed among post-transition metals. Color is not the only identifier: row, column and atomic number remain visible.

## Artwork

`scripts/artwork.py` defines the drawing and generates four original SVG masters in one 1920 × 1200 coordinate system. Each run writes those masters to `artwork/`, replacing the previous SVG files, and renders the same generated vectors as 3840 × 2400 sRGB PNGs using the supplied macOS SF Pro font. Edit the drawing in the Python generator; direct SVG edits are overwritten on the next run. The clean image omits only the 118 symbol rectangles; numbers, cell colors, corners, spacing and canvas are identical. The renderer exhaustively checks that every changed pixel lies inside a symbol region. Both themes have a flat continuous canvas.

`artwork.json` in the output folder records the four PNG hashes and dimensions, normalized region coordinates, canvas RGB and resolved font identity. Generated PNGs, packages and validation collections stay outside source Git.

## Anki and preparation

The builder retains Anki's native image-occlusion note kind and renderer. **Occlusion**, **Image**, **Header**, **Back Extra** and **Comments** remain ordinary native fields. The optional **RectoVerso Occlusion** field is not referenced by either template. It contains `RV-OCCLUSION-1:` followed by base64 canonical JSON and four media-preserving image references.

The JSON records version 1; original/clean light and dark asset names, SHA-256 and pixel dimensions; the exact raw Occlusion field SHA-256; `hideAll` mode; and 118 stable `label` regions. Each region has a 1-based ordinal, normalized rectangle, symbol answer, localized full-name title and compact detail. The canvas method is `flat-srgb-v1`, with exact light/dark RGB components. Metadata is capability-bound to exact artwork and masks, not to a filename alone.

Anki uses the original figure and its native masks. The back selects only its ordinal's facts from **Back Extra**; this remains functional without the optional field. Anki dark mode chooses the registered dark original. RectoVerso can use the validated clean pair and authored answer through its separate format implementation.

## Identity and updates

`IDS` in `scripts/build.py` is the authoritative identity table. The two languages have different deck, model, note, GUID, template, field and card identities. Card ordinals remain atomic-number minus one. Anki's add APIs require newly allocated rows, so the source builder assigns deterministic note/card rows after native creation; validators then exercise the generated package through Anki's importer and scheduler. Anki assigns local deck IDs when importing into another collection; stable package IDs and names do not imply that every user's database has the source deck ID.

A patch fixes content without changing identities. A minor version adds compatible content. A major version is required only if notes cannot carry over. Rebuild both languages and run `scripts/checks/validate_anki.py` against an independently rebuilt package: no duplicates, lost review history or media changes are accepted. Publish only after owner review; no source remote or release currently exists.

## Validation boundary

The backend check imports both language packages, exercises the native editor update API, checks every front/back, validates media and metadata, answers a card, exports and reimports its schedule, then applies an independently rebuilt package and checks that history survives. A combined collection must contain two notes and 236 distinct cards.

The bundled Anki reviewer check renders all 118 fronts and backs, both languages, both themes: 944 pages. It verifies the selected ordinal, actual target mask alpha, correct theme image, one correct answer name, and absence of optional metadata. Saved screenshots supplement these checks. This is Anki's real bundled web renderer in Qt, not a screenshot of the full desktop editor. A complete manual Anki desktop editing session and physical-device behavior are separate review gates.
