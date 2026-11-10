# Periodic table: rules for agents

This repository is one deck of RectoVerso's Deck gallery. Any agent working here (Codex, Claude Code or another) reads this whole file before anything else: it is complete on its own. Three kinds of work happen here: **deck authoring** (the content), **contract honoring** (what RectoVerso's gallery and Anki read of the deck) and **cover making** (the gallery's pictures). Find the kind you're doing and keep its rules, and the rules for every kind; work that crosses two kinds keeps both.

These rules restate, for this deck, RectoVerso's own pages: `agents/decks.md` (the rules every gallery deck follows), the Library page's "A deck's metadata" and "Covers" (`docs/app/library.md`) and the French of `docs/app/languages.md`, in the RectoVerso repository (`~/Dev/RectoVerso` on the owner's Mac; until RectoVerso 1.1 is merged, their gallery side is in the worktree `~/Dev/RectoVerso-worktrees/605-deck-gallery`). Where this file and those pages disagree, RectoVerso's pages win, and this file is corrected in the same change.

## This deck
- **Periodic table** (« Tableau périodique »), `rectoversohq/rectoverso-periodic-table`, public. GUID prefix `rv-periodic-table`; languages English and French; license CC BY 4.0. Asks the 118 elements three ways: the symbol hidden in its cell (an image occlusion, one card a symbol), the symbol from the name, and the element whose cell is lit. Its build renders its pictures (`renderedPictures`).

## For every kind of work

### The owner decides
- **The owner (Simon Pinkas) decides** coverage, names, conventions (borders, continents, a contested group), categories, the sample, the headline and description, the covers, the gallery's order and every release. Bring each choice with a recommendation, in chat; never settle it in the deck, and never call a habit found in the files a convention: only what's written here, in RectoVerso's pages or by the owner is one.
- **An agent starts only on an explicit go** ("go", "start it", "yes"); an answer that sharpens the scope isn't one.
- **Each decision gets a dated entry** in docs/decisions.md (the date, what was decided, by whom, and why). Earlier entries are history: never edit them.

### Git
- **A branch and a pull request for every change,** its checks green, merged by the owner or on the owner's go. Never push to main, force-push, rewrite pushed history, or bypass a check.
- **Commit only your own files, by name** (never `git add -A` or `git commit -a`). Never switch branches, stash or reset in a folder someone else is using.
- **A merge, a tag, a release, and RectoVerso's pin moved to it each wait for the owner's go,** given for that one step: a go for one isn't a go for the next.
- **The deck's own issues are in this repository;** the app's side of the deck (its pin, the catalog, the gallery) is an issue in simonpinkas/RectoVerso.

### Files and evidence
- **Packages, rendered pictures, caches and evidence stay out of Git,** in an output folder outside the checkout (the owner's external media drive), passed to every tool as an argument: no tool names a drive, a user or a path of its own. Keep failed evidence beside the rest.
- **Never invent a fact.** Every fact (a name, a capital, a border, a date, a value) is checked against an independent, citable source, recorded with the content. When sources disagree or a fact can't be verified, say so and bring it to the owner.
- **What can't be checked is said plainly,** with what it would take to check it.

### This repository
- **Read first:** docs/source.md, before changing content, artwork, identities or the package format; docs/review.md records the reviewed snapshot, docs/validation.md the checks, docs/decisions.md the dated decisions. French versions beside them (`.fr.md`).
- **Where things are:** shared facts in source/elements.json, names in source/translations/, original SVGs in artwork/, the pinned artwork record in source/artwork.json (the rendered pictures stay out of Git: builds render them, scripts/artwork.py), tools in scripts/, checks in scripts/checks/, tests in tests/. Packages, caches and evidence go in an output folder outside the repository.
- **Before a commit, after a content or artwork change:** rebuild both languages; run the source tests, the Anki validators (validate_source.py, validate-anki.py, validate-rebuild.py) and the bundled-reviewer check; look at the light and dark originals and the clean pairs.

## 1. Deck authoring: the content
The questions, answers, names, words and pictures the learner studies, in every language the deck ships.

### Content changes; identities don't
- **The content changes freely from one version to the next:** a question reworded, an answer fixed, a picture redrawn, notes added or retired.
- **What identifies the deck never changes** once a version has been published or studied (see Contract honoring): an existing exercise never becomes a different question. A new exercise gets a new note with a stable identity of its own.
- **A retired question keeps its note,** so its history stays; how it leaves the reviews is the owner's call.
- **New-card stages are an introduction order,** never a scheduler or an entitlement.

### Words
- **Every language the deck ships is complete:** title, subject, headline, description, what's new, every card, the notes and the docs a learner reads. Names, role qualifiers, source notes and docs agree across languages.
- **The headline and the description are the owner's copy:** a new one, or a change, goes to the owner first.
- **English is American English** (spelling and usage).
- **French is RectoVerso's French** (`docs/app/languages.md`): France's, for every French-speaking learner. Its terms (a deck is « un deck », never « jeu » or « paquet »), and its typography:
  - guillemets « » with a narrow no-break space (U+202F) inside: « Tardigrade »; quotes inside quotes “ ”;
  - a narrow no-break space (U+202F) before ; : ! ? and before % (« 40 % »), never an ordinary space and never none;
  - the typographic apostrophe ’ (« l’eau »), never the straight one;
  - the ellipsis as one character, …, with no space before it;
  - ordinals 1er, 1re, 2e (never « 2ème » or « 2nd »); capitals keep their accents (« État », « À »); an en dash, spaced, for a parenthesis.
- **Search metadata** (RectoVerso search v1, an optional field) is hidden from studying: only learner-facing names, values and aliases, in the card's language; never geometry, ids or license text.

### Sources, credits and licenses
- **Every source** the deck builds from has its name, version, https URL and license, recorded in rectoverso.json's `sources`.
- **Every picture** has its credit (file, source, creator and license) in `imageCredits`, and every asset its exact provenance, license and hash.
- **Our own material in a public deck is CC BY 4.0,** © Simon Pinkas (never another name or a company); a Pro deck's is under its own terms.

### This deck's content
- **Identities:** the atomic number is an element's stable identity; each language has its own ids. The GUIDs are `rv-periodic-table-<language>-…` since 0.2.0-rc.1 (the table's occlusion note, `-table`; by atomic number, `-079-name` and `-079-symbol`).
- **Facts:** a correction comes with its provenance. The detached series don't assert a group-3 convention; the color categories are a documented teaching convention.
- **Artwork:** no changed pixel outside the symbols' regions, and no answer metadata on a front.
- **Each note's header** (`Header`) is the question its card asks, in its language (« Quel est son symbole ? »): RectoVerso shows it as the card's line.

## 2. Contract honoring: what the app and Anki read
rectoverso.json, the deck's identities, its packages, its versions and its releases. RectoVerso's gallery check (`scripts/gallery/decks.py check` in RectoVerso) refuses a deck that breaks any of this; a deck isn't done until it passes.

### rectoverso.json
At the repository's root, the deck's single source of truth, released with its packages. RectoVerso's gallery check requires the fields below (all but those marked optional), and of the deck's file the gallery reads only these. A deck may keep keys of its own beside them (`status`, `roster`, counts such as `sounds`): the check and the app leave them aside, so a key of the deck's own never changes what the app shows; a new key the app should read is a change to the contract (below).
- **Identity and version:** `id` (the repository's name); `version`; `releaseTag` (`v` and the version: the tag RectoVerso pins); `guidPrefix` (every note's GUID starts with it, then the language); `identityBase` (the base of the note types' and decks' Anki ids, an integer); `contentModifiedAt` (ISO 8601, moved forward with each content change, never into the future); `publication`: the repository's URL (`remote`), the release's URL (`release`), `approved` (only an approved deck enters the catalog) and `visibility` (`public`, or `private` for a Pro deck).
- **In every shipped language,** each holding every language in `languages`, none empty: `title` (the plain title), `subject`, `headline` (one line) and `description` (short).
- **`languages`,** by code (`en`, `fr`): each language's artifact `id` (stable for good), its `title`, its `cards` (the count), its `sample` and its `package` (its file). The package is attached to the release with its sidecar (`<package>.rectoverso.json`) and listed in the release's SHA256SUMS.
- **`cards`:** the source's notes must make exactly the declared count. A note that makes several cards says how many; an image occlusion note counts its label groups; every other note counts as one. A language may use several note types, each with its own id, distinct across the deck's languages.
- **`sample`,** under each language: the one card the gallery opens as the deck's sample question. A note that makes one card is named by its GUID; one card of a cloze of several blanks or of an occlusion of several labels by `<GUID>/<cloze number>`. Every picture or sound its fields name is one of the deck's files. The sample is the owner's choice.
- **`whatsNew`** (optional): this version's notes, in one or more of the shipped languages, none empty.
- **`categories`:** one or more of `geography`, `history`, `languages`, `sciences`, `mathematics`, `medicine`, `arts`, `music`, each once; the first places the deck in the gallery's sections. Categories are the owner's.
- **Whole deck:** `creator`; `license` (CC BY 4.0 for ours, a `LicenseRef-` identifier for a Pro deck's own terms); `sources` (each with name, version, https URL and license); `pictures` and `imageCredits` (each picture a file of the pictures folder, or, for a deck that renders its pictures, `"renderedPictures": true` with each credit's `original`, the vector in this repository the build renders it from); `proOnly` (true only for a Pro deck, from its private repository); `sourceFiles` (the source paths the deck builds from).
- **`covers`** (optional, see Cover making): per language, `{"light": [<files>], "dark": [<files>]}`, each list non-empty, in the order shown; a deck that has covers has both lists in every shipped language.

### Identities
- **Never changed once a version has been published or studied:** each note's GUID, the ids of its note types, fields, templates and deck, and each language's package id. An update recognizes the new version's notes by them and keeps the learner's progress; a note whose GUID changed is a new card beside the old one, with the progress left on the old.
- **Every GUID reads the same way:** the deck's `guidPrefix`, then the language, then the note, in lowercase words and hyphens (`rv-flags-fr-npl-flag-place`). Never a form of the deck's own.
- **Each language is a package of its own,** with ids of its own: adding or changing one language never touches another's progress.

### Prerequisites
- **A course whose cards build on each other says so card by card** (RectoVerso #876): in each note's "RectoVerso" payload, two optional lists, `requires` and `introduces`, of the deck's own tokens (lowercase words and digits, hyphens between them). The app's **Lesson mode** holds a card back until the cards that introduce what it requires have been answered, right or wrong.
- **Only a card that teaches introduces;** a card requires everything it shows or asks that another card teaches, a figure's other visible items included. The source's own ordering data isn't the contract: what the package's payloads say is.
- **RectoVerso's gallery check refuses** a list that isn't one of tokens, each once; a token no card of the same language's package introduces; a card that could never come (it waits for itself, or two cards wait for each other); and a deck's order that asks before it teaches.
- **This deck declares none:** its cards stand alone, and it studies as any deck.

### The contract is RectoVerso's
- **A new field, value or form** is a change to RectoVerso's contract, made there first, at once in every place that reads it (the gallery check, the app's catalog reader and its frozen fixture, the catalog writer, the Library page, a dated decision). A deck never uses one alone: what only the check knows, the app can't read.

### Tools
- `scripts/source_data.py` expands each language's metadata, notes, note types and deck for RectoVerso's check.
- `scripts/build.py --language <code> --out <package>` builds one language's package (a deck that renders its pictures also takes `--artwork <folder>`).
- `scripts/checks/validate-anki.py` and `scripts/checks/validate-rebuild.py` check a package in Anki and a rebuild's identities.

### Versions and releases
- **Every content change is a new version:** a patch fixes, a minor adds, a major only when notes can't carry over (before 1.0, a minor). `contentModifiedAt` moves forward; `whatsNew` is written in every language the deck ships.
- **The first release learners get is 1.0.0;** release candidates before it are `-rc.<n>`.
- **A release attaches** each language's package and its sidecar, and the covers, all listed in its SHA256SUMS (written by RectoVerso's `decks.py sums <release folder>`, and held to it by `--check`).
- **Before the owner sees a candidate:** this deck's own checks; RectoVerso's gallery check on the built packages; Anki's (each package opens with its cards and media, and an update over the previous version keeps every review, with no duplicates); and, in RectoVerso, the deck added from the gallery on the simulators. Checks pass; the owner decides: a green check publishes nothing.
- **Retiring the deck or a language** starts in RectoVerso's catalog, before any asset pack goes; the owner decides it.

### This deck's checks
- The checks above, and scripts/checks/verify-artwork.py and render_anki.py; tests in tests/ (test_source.py, test_metadata.py, test_artwork_clearance.py).
- Anki desktop's look and RectoVerso's own are separate checks: a rendering in Anki's backend isn't a visual approval.

## 3. Cover making: the gallery's pictures
The pictures the gallery shows for this deck: in the featured box, a row's thumbnail, the deck's carousel and tabletop's tiles. Their design is the owner's; this work is their masters, their build and their checks.

### The specification
- **3:2, exactly 2010 × 1340 px** (the widest crop the app shows is 669 pt at @3x).
- **The safe area:** the subject and any words entirely inside the middle 78 % of the width and 66 % of the height (x 221–1789, y 228–1112): every place crops around the middle, the smallest being a row's thumbnail, 126 pt wide.
- **The clear corner:** the top-trailing 20 % × 25 % (x ≥ 1608, y ≤ 335) carries the app's language pill: background only.
- **Never the deck's title** (the app sets it beside the cover). Other words are allowed, in each shipped language.
- **Light and dark:** one or more covers for each appearance, in the order the app shows them; one picture may serve both.
- **PNG** for drawn art (a JPEG only for a photograph); small files (they ship inside the app's download: aim under 400 KB).
- **Accurate:** whatever real place, flag, element, name or shape a cover shows is right, checked against the deck's own sources.

### Names
`<guidPrefix>[-<language>]-cover[-<light|dark>]-<n>.png` (`.jpg` for a photograph), lowercase words and hyphens, `n` from 1 in the order shown.
- **The language** only on a cover with words: one file per shipped language, the same `n` (`<prefix>-en-cover-2.png`, `<prefix>-fr-cover-2.png`). Without words, one file every language lists (`<prefix>-cover-1.png`).
- **The appearance** only on a cover made for light or dark mode. Without one, the same file is listed under both `light` and `dark`.
- **Never ambiguous:** one `n` is never both with and without a language, nor both with and without an appearance in one language. The deck's prefix keeps every deck's covers apart in the app, which holds them all in one folder by name.

### Masters, build and checks
- **Masters** in artwork/covers/, SVG, named as their PNGs (`.svg`), with lettering outlined (or a pinned, embedded font) so every render is identical; no external resource.
- **scripts/covers.py** renders every master to its PNG at 2010 × 1340, called by scripts/build.py, into the build's output folder, never into the repository (nothing rendered is committed). Two independent builds give the same bytes.
- **scripts/checks/verify-covers.py,** run by the deck's CI, refuses a wrong size or name, a language without a light and a dark cover, a worded cover missing in a language, an ambiguous set, and anything but background in the clear corner (within 4 per channel of the corner's dominant color). Its tests in tests/.
- **A new or changed cover** is shown to the owner as rendered PNGs, light and dark, every language, before it's merged.
- **Listed at release:** rectoverso.json's `covers` lists them per language and appearance, and the release attaches them with the packages; they reach the app with the deck's next release, never before.

### This deck's covers
- **Six masters:** three designs in light and dark, shared by English and French. See [Building gallery covers](docs/build.md) for their provenance and rebuild commands.
