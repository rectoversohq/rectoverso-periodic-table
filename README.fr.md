# Tableau périodique

[English](README.md)

Un paquet original bilingue des 118 éléments, trois cartes chacun : le tableau avec un symbole masqué (**quel symbole se trouve ici ?**), le tableau avec la case d’un élément éclairée (**quel est cet élément ?**) et le nom d’un élément (**quel est son symbole ?**). Le nom complet de l’élément et de courtes indications de numéro atomique, groupe et période suivent chaque réponse. Les versions française et anglaise sont deux paquets issus d’une même source. Le tableau à 18 colonnes possède des images originales et nettoyées parfaitement alignées, en clair et en sombre. Seules les zones des symboles sont retirées.

**Version 1.0.0,** les mêmes cartes que la dernière préversion, 0.2.0-rc.1. [Télécharger les paquets Anki français et anglais](https://github.com/rectoversohq/rectoverso-periodic-table/releases/tag/v1.0.0). Les GUID de ses notes ont changé depuis la 0.1.0-rc.1 : la progression étudiée sur la 0.1.0-rc.1 n’est pas reprise, et ses cartes arrivent comme nouvelles dans le même profil Anki. Illustrations originales et paquet : © Simon Pinkas, **CC BY 4.0**. Données factuelles de Wikidata : **CC0**. Voir les [crédits](NOTICE.md), les [règles de source](docs/source.fr.md) et les [résultats des vérifications](docs/validation.fr.md).

## Obtenir les sources

Cloner les sources étiquetées pour reproduire cette préversion :

```sh
git clone --branch v1.0.0 https://github.com/rectoversohq/rectoverso-periodic-table.git
cd rectoverso-periodic-table
```

La [revue des sources](docs/review.md) précise l’état des contrôles et les étapes restantes.

## Construire et vérifier

Utiliser Python 3.14, Anki 26.9.3 et Qt/PyQt 6.11.0 dans un environnement dédié avec `requirements.txt`. Le dessin utilise SF Pro, fourni par macOS ; le fichier de police n’est pas distribué. Les commandes complètes figurent dans le [README anglais](README.md#build-and-check). Elles acceptent des chemins explicites et placent les paquets, collections de test et captures hors du dépôt source.

Le générateur produit une langue à la fois, **Periodic-table-en.apkg** ou **Tableau-periodique-fr.apkg**, avec ses métadonnées (`.rectoverso.json`), à partir des sources, en dessinant ses quatre images avec le moteur de rendu et la police fixés. Le vérificateur Anki importe les deux langues, contrôle les médias et le champ facultatif, modifie la note par l’API native, étudie une carte, exporte et réimporte son historique, puis applique un paquet reconstruit. Le vérificateur visuel utilise le moteur de révision livré avec la même version d’Anki : 118 rectos et versos, deux langues et deux thèmes, soit 944 pages. Dans une session graphique, l’exécution est directe. En CI sans affichage, définir `QT_QPA_PLATFORM=offscreen` et `QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu` pour dessiner les masques sans contexte GPU. Le contrôle `--sample --document-delay-ms 300 --parser-delay-ms 300` vérifie aussi une navigation et une analyse HTML volontairement lentes, avec les mêmes résultats attendus.

## Entretenir

Les faits communs sont dans `source/elements.json`, les noms dans `source/translations/`, les SVG originaux dans `artwork/`, la description fixée des images dans `source/artwork.json`. Modifier le dessin dans `scripts/artwork.py`, puis régénérer les quatre SVG ensemble. Les pixels dépendant de la police et de Qt, `source/artwork.json` fixe l’empreinte de la police, le moteur de rendu et l’empreinte de chaque image ; les images restent hors de Git, chaque construction les dessine et refuse une image différente. Un nouveau dessin est revu puis fixé sous de nouveaux noms de fichiers. Un changement de contenu avance `contentModifiedAt` dans `rectoverso.json` jusqu’au moment du changement (jamais dans le futur) : Anki ne met une note à jour que si sa date de modification diffère de celle de la collection. Conserver les identifiants des notes et les numéros des éléments. Une langue a ses propres identifiants afin que les deux paquets puissent coexister sans perdre leur historique.

Les noms apparaissent après la réponse ; le symbole seul constitue la réponse demandée. Les séries détachées La–Lu et Ac–Lr n’affirment aucun numéro de groupe. **Lutétium** et **Tennesse** sont les graphies retenues. Les couleurs sont une convention pédagogique documentée, pas une affirmation sur les propriétés encore incertaines des éléments superlourds.

`rectoverso.json` suit la structure de la galerie de RectoVerso : titre, sujet, accroche et description en anglais et en français, catégorie, auteur, licence, sources, crédits des images et, pour chaque langue, son paquet et sa **question exemple**, la case de l’or (Au).

Toute publication attend la revue du propriétaire. Ce travail ne modifie ni l’application RectoVerso, ni son paquet d’exemple, ni la galerie.
