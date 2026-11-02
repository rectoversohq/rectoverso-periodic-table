# Tableau périodique

[English](README.md)

Un paquet original bilingue à occlusion d’image : **118 symboles**, puis le nom complet de l’élément et de courtes indications de numéro atomique, groupe et période après la réponse. Les versions française et anglaise sont deux paquets issus d’une même source. Le tableau à 18 colonnes possède des images originales et nettoyées parfaitement alignées, en clair et en sombre. Seules les zones des symboles sont retirées.

Version **0.1.0-rc.1**, **candidate locale à examiner**. Aucun dépôt, aucune version ni aucun paquet n’a été publié. Illustrations originales et paquet : © Simon Pinkas, **CC BY 4.0**. Données factuelles de Wikidata : **CC0**. Voir les [crédits](NOTICE.md), les [règles de source](docs/source.fr.md) et les [résultats des vérifications](docs/validation.fr.md).

## Construire et vérifier

Utiliser Python 3.13 ou 3.14, Anki 26.9.3 et Qt/PyQt 6.11.0 dans un environnement dédié avec `requirements.txt`. Le dessin utilise SF Pro, fourni par macOS ; le fichier de police n’est pas distribué. Les commandes complètes figurent dans le [README anglais](README.md#build-and-check). Elles acceptent des chemins explicites et placent les paquets, collections de test et captures hors du dépôt source.

Le générateur produit **Periodic-table-en.apkg** et **Tableau-periodique-fr.apkg**, leurs métadonnées, quatre PNG et leurs empreintes. Le vérificateur Anki importe les deux langues, contrôle les médias et le champ facultatif, modifie la note par l’API native, étudie une carte, exporte et réimporte son historique, puis applique un paquet reconstruit. Le vérificateur visuel utilise le moteur de révision livré avec la même version d’Anki : 118 rectos et versos, deux langues et deux thèmes, soit 944 pages. Une session graphique est nécessaire.

## Entretenir

Les faits communs sont dans `source/elements.json`, les noms dans `source/translations/`, les SVG originaux dans `artwork/`. Modifier le dessin dans `scripts/artwork.py`, puis régénérer les quatre SVG ensemble. Conserver les identifiants des notes et les numéros des éléments. Une langue a ses propres identifiants afin que les deux paquets puissent coexister sans perdre leur historique.

Les noms apparaissent après la réponse ; le symbole seul constitue la réponse demandée. Les séries détachées La–Lu et Ac–Lr n’affirment aucun numéro de groupe. **Lutétium** et **Tennesse** sont les graphies retenues. Les couleurs sont une convention pédagogique documentée, pas une affirmation sur les propriétés encore incertaines des éléments superlourds.

Toute publication attend la revue du propriétaire. Ce travail ne modifie ni l’application RectoVerso, ni son paquet d’exemple, ni la galerie.
