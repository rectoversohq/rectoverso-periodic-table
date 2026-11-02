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
| Hosted source CI | Workflow supplied; no remote exists and no hosted run is claimed. |

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
