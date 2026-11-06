# Building gallery covers

Install the pinned dependencies in `requirements.txt`. To render the covers on their own:

```sh
python scripts/covers.py --output /outside/the/checkout/covers
python scripts/checks/verify-covers.py --output /outside/the/checkout/covers
```

The ordinary package build renders the same covers beside the package and its
sidecar. Each build writes six optimized 2010 × 1340 PNGs from the masters in
`artwork/covers/`. Keep generated files outside the checkout.

Use `rv-periodic-table[-<language>]-cover[-<light|dark>]-<n>.svg` for each
master and the same stem for its PNG. Use lowercase and number consecutively from 1 in
display order. Include a language only when the cover contains words, with a matching
master for every shipped language. Include an appearance only when the art
differs by appearance. The current designs use language-independent chemical
symbols and numbers, with separate light and dark art.

CI checks PNG names, dimensions, light and dark coverage, complete localized
sets, and conflicting language or appearance scopes. The language-pill corner
(`x ≥ 1608`, `y ≤ 335`) must stay within 4 per channel of its dominant color.
The check accepts `--compare DIR` to verify byte-identical PNGs across
independent builds. Actions attaches the six PNGs as `periodic-table-covers`.

## Artwork provenance

Compositions © Simon Pinkas, CC BY 4.0. Element positions, symbols and atomic
numbers use the [element roster](../source/elements.json) and the deck’s
[light](../artwork/rv-periodic-light.svg) and [dark](../artwork/rv-periodic-dark.svg)
table vectors. The three compositions show Au in focus, its symbol covered by a
smooth frosted lens, and the whole table. The system SF Pro lettering is
outlined from macOS’s `SFNS.ttf` (version `22.0d5e1`, SHA-256
`44890958f3e0b997028121ed7c7a789f3f5cce227c7a93ce8f86ec0db26da571`).
Builds need no installed font for the covers. The authoring font is Apple
software under its macOS license, separate from the compositions’ CC BY 4.0
license. See [Apple’s font information](https://developer.apple.com/fonts/).

| Approved master | SHA-256 |
|---|---|
| [rv-periodic-table-cover-dark-1.svg](../artwork/covers/rv-periodic-table-cover-dark-1.svg) | `8180e29b77158f75fc68ef6777b0f12215f550d456565fa86256a15750b301c0` |
| [rv-periodic-table-cover-dark-2.svg](../artwork/covers/rv-periodic-table-cover-dark-2.svg) | `c0f9bb34980e65de03e87b48819c727e2adeebee40b748e3be69f8c5a5db8711` |
| [rv-periodic-table-cover-dark-3.svg](../artwork/covers/rv-periodic-table-cover-dark-3.svg) | `cafb0c0a0b644e017a45f8aaa7287e9af27b2ac05137e17e1e7d3f249844079a` |
| [rv-periodic-table-cover-light-1.svg](../artwork/covers/rv-periodic-table-cover-light-1.svg) | `185c1c64812ad0539e0c1b8979ff3c2ffd4ebe4f25070325a881d66f66206fad` |
| [rv-periodic-table-cover-light-2.svg](../artwork/covers/rv-periodic-table-cover-light-2.svg) | `29d0393ef6085b6d31914628a786c8468c967d8cbe02b658d69635f07385a148` |
| [rv-periodic-table-cover-light-3.svg](../artwork/covers/rv-periodic-table-cover-light-3.svg) | `b6770f5b1958074b6a4c54cb936aaa220e5d42b51c7d7861f14e7c5f7c46a1ab` |

## En français

Installez les dépendances de `requirements.txt`. Lancez les deux commandes
ci-dessus avec un dossier de sortie hors du dépôt. La construction du deck
produit aussi les six PNG de 2010 × 1340 px à côté du paquet. Les noms des
masters suivent le format ci-dessus. Indiquez la langue uniquement si la
couverture contient du texte, et l’apparence uniquement si le dessin diffère
entre les modes clair et sombre. Les symboles chimiques et les numéros
atomiques sont communs aux deux langues.

Le contrôle vérifie les noms, les dimensions, la présence des deux apparences,
la couverture de chaque langue et le fond uni dans le coin réservé à la
pastille de langue. L’option `--compare DIR` vérifie que deux constructions
indépendantes produisent les mêmes octets. Le résultat Actions
`periodic-table-covers` contient les six PNG.
