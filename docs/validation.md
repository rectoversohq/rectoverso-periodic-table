# Local candidate validation — 2026-11-01

This records the source candidate, not a published release. The tested packages are `candidate-7`, Anki **26.09.3**, with four shared **3840 × 2400** PNGs. English and French each contain one native image-occlusion note and 118 cards.

| Check | Observed result |
| --- | --- |
| Factual source and identity tests | 4 passed: 118 unique symbols/positions, periods, detached group convention, both translations and provenance. |
| Artwork registration | Light and dark: exhaustive comparison found zero changed pixels outside the 118 symbol rectangles. All four images have identical dimensions. |
| Font | Qt explicitly loads `/System/Library/Fonts/SFNS.ttf`; `QFontInfo` resolves `.SF NS`, and `QRawFont` family/style plus the font-file SHA-256 are recorded in `artwork.json`. No font file is redistributed. |
| Native import | Both languages: 118 distinct card ordinals; expected note/model identities, masks, metadata hashes, answers and localized facts. Combined collection: 236 distinct cards, 2 notes. |
| Native editor API | Changed and restored Header, preserving masks and optional preparation. This is an API check, not a claim about manual desktop editing. |
| Media | Four exact media hashes; zero missing and zero unused files in each normal package. |
| Native schedule / export | Answered one card per language, exported with scheduling, reimported: full checked card state and one review-log entry preserved. |
| Source update | Independently rebuilt packages, with Anki's Always-update setting, replaced deliberately outdated Comments while preserving the studied card and review log. |
| Optional field removed | All 118 native questions/answers still render. No missing media. Only the two clean PNGs become unused, as expected; both ordinary theme images remain referenced. |
| Real bundled Anki reviewer | **944 / 944 passed**: 118 ordinals × 2 sides × 2 languages × 2 themes. Checks selected ordinal, actual target mask alpha, theme image, exactly one correct answer name, no front answer name and no optional metadata leak. 64 representative screenshots retained. |
| Manual visual review | Original/clean overview pair and native answer samples inspected. Name and compact facts are above the figure and visible immediately. |
| Fresh source clone | Code revision `9162376`: `git clone --no-local`, 4 tests, lint/format, regenerated SVGs unchanged, two independent package builds and the strengthened native backend checks all passed. Four raster hashes, preparation hashes and IDs matched candidate-7. All 472 generated EN/FR front/back HTML files were byte-identical to the full reviewer run's inputs. |
| Full Anki desktop editor | **Unverified.** An isolated SSD profile was launched with the installed `ANKI_SINGLE_INSTANCE_KEY` override. The available UI tool bound to the pre-existing user's Anki process instead; no UI actions were taken. Only the owned test process was stopped. The user's pending import and collection were untouched. |
| RectoVerso / physical devices | Separate app-format task; not claimed by this source repository. |
| Hosted source CI | The workflow runs on the source-review branch and PR. See [source review](review.md) and its linked checks for current results. |

The source checker, backend and web reviewer are separate checks. A native reviewer pass does not stand in for a complete manual Anki editor session or a hardware review.

## Native mask appearance

Ordinary Anki uses its native image and mask renderer. Inactive symbols are covered with neutral masks; active masks use the source's restrained accent. This differs from RectoVerso's registered clean plate, which preserves every cell color. The installed renderer supports a literal per-shape fill, but one literal cannot match both authored theme colors. This candidate keeps native behavior instead of replacing rendering or changing edited mask geometry. The source uses no text-occlusion annotations that would leak symbols on questions.

## Candidate packages

| Package | Bytes | SHA-256 |
| --- | ---: | --- |
| `Periodic-table-en.apkg` | 1,014,178 | `4505282f252978be1a94ca80b387fb223226490980d5289bde89c181b2ca2f67` |
| `Tableau-periodique-fr.apkg` | 1,014,251 | `635671a16d3724fb96cff0aade12230ad07ad552e6662f87d1bb4deb4d0a04fc` |

Local evidence root (outside source Git): `/Volumes/SSD/RectoVerso/raw/periodic-table-619-20261101/`.

- `build/candidate-7/`: packages and per-language sidecars.
- `build/artwork-2x/`: four PNGs, font identity, exact hashes and geometry.
- `evidence/anki-final/report.json`: strengthened editor/update/optional-field checks; isolated collections and all backend fronts/backs sit alongside it.
- `review/native-full-7/render-report.json`: complete reviewer results.
- `review/native-full-7/en-light-026-answer.png`: Iron answer sample.
- `review/native-full-7/fr-dark-117-answer.png`: Tennesse answer sample.
- `evidence/anki-fresh/report.json`, `evidence/fresh-artwork.log`, `evidence/fresh-build.json`, `evidence/fresh-rebuild.json`: fresh-clone checks. `fresh-source/` contains the isolated checkout; `fresh-build/` contains its rebuilds.

Rebuilds may differ in timestamp-dependent archive bytes. Compare validated media, fields and stable identities; each generated sidecar describes its own package.

## Source-review CI regression checks

Headless runs use software canvas rendering. The reviewer waits for its exact document and Anki’s drawing-complete callback, then checks the original assertions once; a rendered wrong answer or transparent mask still fails. CI runs all 944 pages plus a 64-page delayed-navigation regression. The [source-review record](review.md) preserves the initial GPU and asynchronous-navigation failures and their controls. These harness changes do not alter card content or native Anki rendering.

## Corrected source-review package candidate

The answer caption now waits for its active target to be parsed. A controlled parser pause reproduced missing names, and the same native-renderer control passes with this correction. Artwork, preparation and stable identities are unchanged; both packages were rebuilt. Full source/native-backend, 944-page reviewer and 64-page delayed-navigation/parser checks pass. Default **If Newer** imports from candidate-7 apply the caption script and preserve all 118 card IDs plus studied scheduling and one review-log entry in each language. This prior candidate was local, not a released version.

| Package | Bytes | SHA-256 |
| --- | ---: | --- |
| `Periodic-table-en.apkg` | 1,014,320 | `2ef37152d99fc795f5ef9853990fb01c2e06e588cd3651b170a9272d152be6c8` |
| `Tableau-periodique-fr.apkg` | 1,014,351 | `0965222794fd54b3567a5762e30b1eb867bf7bdb8351934a3a5917c12c553071` |

Evidence is in the source-push packet’s `working-ci-caption/`, `caption-default-upgrade/` and `parser-regression-green/`; hosted checks retain their own generated reports. The earlier candidate-7 table remains historical evidence.
