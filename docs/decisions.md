# Decisions

## 2026-11-04 — Release decisions

The owner settled the questions raised before the first release (0.1.0-rc.1):

- **SF Pro stays.** The drawing keeps macOS's SF Pro, rendered into the pictures; the font file is never distributed. In the owner's words: "We'll use another font if Apple complains." There is no licensing hold on the release.
- **Pictures are rendered, not committed.** The four pictures stay out of Git, as this repository's rule says. Builds are reproducible because the renderer and the font are pinned: `source/artwork.json` records the font's SHA-256, Qt and PyQt's versions and the offscreen platform, and each picture's SHA-256; `scripts/build.py` renders the pictures and refuses any other bytes. Two builds from clean clones give identical pictures.
- **GUIDs keep their form.** `rvPTenV1001`, `rvPTenN079`, `rvPTenL079`: RectoVerso's gallery check accepts the compact form (`guidForm`), and the sample stays Au, `rvPTenV1001/79`.
- **French headers:** « Quel est son symbole ? » and « Quel est cet élément ? » take a narrow no-break space (U+202F) before the question mark, the French of RectoVerso's `docs/app/languages.md`; `contentModifiedAt` moves forward with them.
- **Gallery copy approved,** in English and French: the headline "Every element's symbol, name and place in the table." and the description in `rectoverso.json`.

Release: 0.1.0-rc.1, a prerelease, once CI is green on the final head from the branch and a clean clone and RectoVerso's gallery check accepts the deck. This publication-only change sets its status and download instructions, without changing notes, identities or pictures.

## Décisions du 4 novembre 2026, en français

SF Pro est conservée (« Nous changerons de police si Apple se plaint », le propriétaire) ; les images sont dessinées à chaque construction avec une police et un moteur de rendu fixés, jamais versées dans Git ; les identifiants GUID gardent leur forme compacte ; les titres français prennent une espace fine insécable avant « ? » ; l’accroche et la description sont approuvées.

## 2026-11-05 — GUIDs in RectoVerso's layout

The owner reversed the 2026-11-04 decision to keep the compact GUIDs ([simonpinkas/RectoVerso#746](https://github.com/simonpinkas/RectoVerso/issues/746)): every gallery deck's GUIDs read the same way, the deck's prefix, the language, then the note (RectoVerso's `agents/decks.md`).

- **Prefix:** `rv-periodic-table` (`guidPrefix`); `guidForm` is gone.
- **Notes,** in each language: `rv-periodic-table-en-table` (the occlusion note, one card a symbol), `rv-periodic-table-en-079-name` (the lit cell, asking the element's name; 0.1.0-rc.1's `rvPTenL079`) and `rv-periodic-table-en-079-symbol` (the name, asking its symbol; `rvPTenN079`), by atomic number; `-fr-` alike. The sample stays Au: `rv-periodic-table-en-table/79`, `rv-periodic-table-fr-table/79`.
- **Released as 0.2.0-rc.1.** Progress studied on 0.1.0-rc.1 doesn't carry over: its notes come back as new ones. Every other identity (deck, note types, fields, templates, note and card rows) and every card's content is unchanged; `contentModifiedAt` moves forward with the new notes.

## Décisions du 5 novembre 2026, en français

Le propriétaire revient sur les GUID compacts : comme dans tous les paquets de la galerie, chaque GUID est le préfixe `rv-periodic-table`, la langue, puis la note (`rv-periodic-table-fr-table`, `rv-periodic-table-fr-079-name`, `rv-periodic-table-fr-079-symbol`) ; `guidForm` disparaît. Publiée en 0.2.0-rc.1, la nouvelle version ne reprend pas la progression étudiée sur la 0.1.0-rc.1 : ses notes arrivent comme nouvelles. Les autres identifiants et le contenu des cartes ne changent pas.


## 2026-11-06 — One complete AGENTS.md for every agent, by kind of work

The owner: a single `AGENTS.md`, read by any agent (Codex, Claude Code or another) and complete on its own, organized around the three kinds of work done here: deck authoring (the content), contract honoring (what RectoVerso's gallery and Anki read: rectoverso.json, identities, packages, versions and releases) and cover making (the gallery's pictures: the specification, the names, the masters, renderer and check). It restates RectoVerso's `agents/decks.md`, the Library page's deck contract and cover specification and its French, with this repository's own rules; where they disagree, RectoVerso's pages win and this file is corrected. The `CLAUDE.md` first proposed here, importing RectoVerso's page, isn't kept.

## 2026-11-06 — 1.0.0, the first release learners get

The owner (2026-11-06): the deck's first release in RectoVerso's Deck gallery is 1.0.0, after the owner's review, its tag and release on the owner's go. It has the same cards as the last prerelease, 0.2.0-rc.1: version, tag and release address move to 1.0.0 in `rectoverso.json`, the READMEs and the review page, and `status` says `release`. No `whatsNew` (nothing changed for a learner since 0.2.0-rc.1) and no gallery covers yet (the app shows placeholders until the deck's own). `contentModifiedAt` stays.
