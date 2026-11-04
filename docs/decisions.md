# Decisions

## 2026-11-04 — Release decisions

The owner settled the questions raised before the first release (0.1.0-rc.1):

- **SF Pro stays.** The drawing keeps macOS's SF Pro, rendered into the pictures; the font file is never distributed. In the owner's words: "We'll use another font if Apple complains." There is no licensing hold on the release.
- **Pictures are rendered, not committed.** The four pictures stay out of Git, as this repository's rule says. Builds are reproducible because the renderer and the font are pinned: `source/artwork.json` records the font's SHA-256, Qt and PyQt's versions and the offscreen platform, and each picture's SHA-256; `scripts/build.py` renders the pictures and refuses any other bytes. Two builds from clean clones give identical pictures.
- **GUIDs keep their form.** `rvPTenV1001`, `rvPTenN079`, `rvPTenL079`: RectoVerso's gallery check accepts the compact form (`guidForm`), and the sample stays Au, `rvPTenV1001/79`.
- **French headers:** « Quel est son symbole ? » and « Quel est cet élément ? » take a narrow no-break space (U+202F) before the question mark, the French of RectoVerso's `docs/app/languages.md`; `contentModifiedAt` moves forward with them.
- **Gallery copy approved,** in English and French: the headline "Every element's symbol, name and place in the table." and the description in `rectoverso.json`.

Release: 0.1.0-rc.1, a prerelease, once CI is green on the final head from the branch and a clean clone and RectoVerso's gallery check accepts the deck.

## Décisions du 4 novembre 2026, en français

SF Pro est conservée (« Nous changerons de police si Apple se plaint », le propriétaire) ; les images sont dessinées à chaque construction avec une police et un moteur de rendu fixés, jamais versées dans Git ; les identifiants GUID gardent leur forme compacte ; les titres français prennent une espace fine insécable avant « ? » ; l’accroche et la description sont approuvées.
