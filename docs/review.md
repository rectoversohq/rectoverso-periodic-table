# Source review

## Current publication

The candidate for [1.0.0](https://github.com/rectoversohq/rectoverso-periodic-table/releases/tag/v1.0.0), the first release learners get in RectoVerso's Deck gallery, awaits the owner's review, its tag and release on the owner's go; it has the same cards as the last prerelease, [0.2.0-rc.1](https://github.com/rectoversohq/rectoverso-periodic-table/releases/tag/v0.2.0-rc.1), which published both languages' packages, their sidecars and `SHA256SUMS`, built from a clean clone of the tagged source with the pinned renderer and font. It replaces [0.1.0-rc.1](https://github.com/rectoversohq/rectoverso-periodic-table/releases/tag/v0.1.0-rc.1) with the same cards under GUIDs in RectoVerso's layout, so its notes are new ones ([decisions](decisions.md)). Earlier sections below are the review's history.

La candidate à la [1.0.0](https://github.com/rectoversohq/rectoverso-periodic-table/releases/tag/v1.0.0), première version de la Galerie de decks de RectoVerso, attend la revue du propriétaire, son étiquette et sa publication son feu vert ; elle reprend les cartes de la dernière préversion, [0.2.0-rc.1](https://github.com/rectoversohq/rectoverso-periodic-table/releases/tag/v0.2.0-rc.1), qui publie les paquets des deux langues, leurs métadonnées et `SHA256SUMS`, construits à partir d’un clone propre des sources étiquetées. Elle remplace la 0.1.0-rc.1 : les mêmes cartes, sous des GUID au format de RectoVerso, donc de nouvelles notes.

The owner approved creating this repository and pushing this candidate for source review. The [source issue](https://github.com/rectoversohq/rectoverso-periodic-table/issues/1) tracks the first PR against a README-only main branch. Merges, version tags and package releases remain separate owner decisions. The source is public; no packaged deck release is published.

## Provenance of this branch

The initial source commit is an exact Git-tree snapshot of the previously tested local candidate `4665e527c32770eeeb036827e971a904b9efa2b7` (tree `b1a485dfe20bb5d6a1a2600a1528e23040337eb8`). Its original local branch and history remain intact. The following setup commit updates repository/build instructions and the Periodic table check name/action pins plus full CC BY 4.0 license text; it does not change learning content, images, identities, templates or package-generation code. Source history was inspected for packaged decks, font binaries, credentials and inappropriate private content before pushing. Build output and evidence stay outside source Git.

The manifest describes the current reviewed source package candidate; it does not announce a release. Regenerated archives may have different timestamp-dependent bytes. Use the sidecars from the actual build.

## Checks and next steps

- [Anki packages](https://github.com/rectoversohq/rectoverso-periodic-table/actions) runs from this branch and its PR. Inspect the actual check result at the PR head; this page does not infer success from workflow presence.
- Local source/native-backend and independent clean-clone checks are recorded with the source PR. [Validation](validation.md) distinguishes backend, bundled reviewer, manual desktop and app evidence.
- Native Anki desktop review remains a release gate. Existing app integration evidence is tracked in [the app task](https://github.com/simonpinkas/RectoVerso/issues/619).
- Require a PR, resolved conversations and the exact **Anki packages** check for main; branch protection is a repository setting, not part of the source files.
- After editorial/native approval, obtain the owner’s go for a versioned bilingual package release.
- The app will pin one multilingual source submodule to an approved tag. Source CI itself neither starts Xcode Cloud nor deploys an Apple asset pack.

## Headless reviewer environment

The existing mask-alpha assertions caught a real CI-environment failure: offscreen Qt reported lost GPU contexts and left question canvases transparent. A representative 64-page run failed 31 questions. Changing only `QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu` produced 64/64 passing pages. CI uses this software canvas path, while retaining every mask, ordinal, theme and answer-leak assertion. Full and clean-clone runs are recorded with the PR; no card or renderer code changed.

## Hosted document readiness

The first hosted reviewer run passed 942 of 944 pages. Its two failures sampled an unfinished 300 × 150 canvas or the preceding question while expecting the answer. A controlled 300 ms document delay reproduced the navigation race: 1/64 passed before the fix, 64/64 after it. The harness now identifies its exact document and observes Anki’s supported `onDidDrawShapes` callback before checking pixels and text. It does not replace Anki’s drawing or wait for failed assertions to become true. An intentionally transparent target still fails the mask-alpha gate.

CI also runs `--sample --document-delay-ms 300` after the full reviewer. These are checker changes only; source artwork, card templates, package-generation code and identities are unchanged. The previous failed hosted reports remain attached to their runs.

## Caption initialization correction

A later hosted run reached the correct document and completed drawing but still missed one element caption. The answer’s early zero-delay timer could run before the browser had parsed the later active-mask element, then remove every fact. A parser-blocking resource reproduced the missing-caption result. The builder now selects the fact after DOM parsing, or immediately when the document is already ready. It never deletes facts without finding the active ordinal.

This is a narrow answer-script change. Facts, artwork, geometry, prepared asset hashes and all card/note identities stay unchanged. Source CI rebuilds both language artifacts and runs all 944 pages plus delayed navigation and parsing. Default **If Newer** import from the earlier local candidate updates this script in both languages while preserving all 118 card IDs and the studied schedule/review log. This is a tested local-candidate transition, not a published-release upgrade claim.

The manifest’s package hashes now identify the corrected local candidate; generated archives from subsequent runs can differ by timestamp. The source PR links the current hosted check and retained initial failures.

## En français

Le propriétaire a autorisé le dépôt et l’envoi des sources pour revue. Le premier commit de sources reproduit exactement l’arbre du candidat testé indiqué ci-dessus ; son historique local d’origine est conservé. Les modifications de mise en place concernent la documentation et la présentation de la licence ainsi que la configuration du contrôle CI, sans changer les cartes, médias, identités ni générateurs. Vérifier le résultat réel d’**Anki packages** sur la pull request. La revue Anki Desktop, l’approbation éditoriale et la publication restent des étapes distinctes. Aucun paquet n’est publié à ce stade.


## Atomic-number clearance review

[Issue #3](https://github.com/rectoversohq/rectoverso-periodic-table/issues/3) is a source-only follow-up stacked on `codex/1-source-candidate`, linked to [app #619](https://github.com/simonpinkas/RectoVerso/issues/619) and [#622](https://github.com/simonpinkas/RectoVerso/issues/622). It separates the number band from the full-symbol region in taller authored cells, preserves the typography and all identities, and versions changed PNG names to make ordinary Anki updates safe. The failing raster and media-upgrade controls, all-element checks, native app captures and explicit extreme-manual-zoom limit are recorded in [validation](validation.md#atomic-number-clearance-candidate--2026-11-02). This branch changes no app lens, camera, imported-deck behavior or physical-phone deck. A source review push is authorized; merging, tagging, publication and installation remain separate decisions.

L’[issue #3](https://github.com/rectoversohq/rectoverso-periodic-table/issues/3) est une correction source empilée sur `codex/1-source-candidate`, liée aux issues app #619 et #622. Elle sépare la bande du numéro de la région du symbole entier dans des cellules plus hautes, conserve typographie et identités, et versionne les noms PNG pour sécuriser les mises à jour Anki ordinaires. La [validation française](validation.fr.md) décrit les contrôles en échec puis corrigés, la revue native et la limite explicite du zoom manuel extrême. Aucun code de lentille/caméra, comportement de paquet importé ou paquet du téléphone physique n’est modifié. L’envoi pour revue source est autorisé ; fusion, tag, publication et installation restent des décisions distinctes.

## Gallery layout

[Source issue #5](https://github.com/rectoversohq/rectoverso-periodic-table/issues/5)'s PR also brings the deck to RectoVerso's gallery layout ([simonpinkas/RectoVerso#690](https://github.com/simonpinkas/RectoVerso/issues/690), step 3). `rectoverso.json` gains the gallery's fields (headline and description; category `sciences`; creator; sources; each language's sample, Au); `scripts/source_data.py` expands a language for RectoVerso's check; `scripts/build.py` builds one language with its sidecar; `validate-anki.py` and `validate-rebuild.py` are the per-package checks the gallery calls, and the complete source check is now `validate_source.py`. The pictures stay out of Git: the font, the renderer and the four pictures' hashes are pinned in `source/artwork.json`, and each build renders them and refuses any other bytes. Notes, fields, templates, identities and media are unchanged, checked package against package with the previous builder; the two element note types lose a random suffix the previous builder added to their names.

La pull request de l’[issue #5](https://github.com/rectoversohq/rectoverso-periodic-table/issues/5) aligne aussi le paquet sur la structure de la galerie de RectoVerso (#690, étape 3) : nouveaux champs de `rectoverso.json` (accroche et description, catégorie, auteur, sources, question exemple de chaque langue), `scripts/source_data.py`, une construction par langue avec ses métadonnées, les contrôles par paquet de la galerie, et les quatre images, dessinées par chaque construction avec une police et un moteur de rendu fixés. Notes, champs, modèles, identités et médias sont inchangés.
