# Source review

The owner approved creating this repository and pushing this candidate for source review. The [source issue](https://github.com/rectoversohq/rectoverso-periodic-table/issues/1) tracks the first PR against a README-only main branch. Merges, version tags and package releases remain separate owner decisions. The source is public; no packaged deck release is published.

## Provenance of this branch

The initial source commit is an exact Git-tree snapshot of the previously tested local candidate `4665e527c32770eeeb036827e971a904b9efa2b7` (tree `b1a485dfe20bb5d6a1a2600a1528e23040337eb8`). Its original local branch and history remain intact. The following setup commit updates repository/build instructions and the Periodic table check name/action pins plus full CC BY 4.0 license text; it does not change learning content, images, identities, templates or package-generation code. Source history was inspected for packaged decks, font binaries, credentials and inappropriate private content before pushing. Build output and evidence stay outside source Git.

The manifest describes the frozen reviewed package candidate, including its recorded local status; it does not announce a release. Regenerated archives may have different timestamp-dependent bytes. Use the sidecars from the actual build.

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

## En français

Le propriétaire a autorisé le dépôt et l’envoi des sources pour revue. Le premier commit de sources reproduit exactement l’arbre du candidat testé indiqué ci-dessus ; son historique local d’origine est conservé. Les modifications de mise en place concernent la documentation et la présentation de la licence ainsi que la configuration du contrôle CI, sans changer les cartes, médias, identités ni générateurs. Vérifier le résultat réel d’**Anki packages** sur la pull request. La revue Anki Desktop, l’approbation éditoriale et la publication restent des étapes distinctes. Aucun paquet n’est publié à ce stade.
