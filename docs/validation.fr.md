# Validation locale — 1er novembre 2026

Candidat local, sans publication. Anki **26.09.3** ; quatre images partagées de **3840 × 2400** pixels. Chaque langue contient une note d'occlusion native et **118 cartes**. Les chemins, sommes SHA-256 et résultats détaillés figurent dans le [rapport de validation](validation.md).

- **4 tests de source réussis** : symboles et positions uniques, périodes, convention des séries détachées, traductions et provenance.
- Images originales et nettoyées : **aucun pixel modifié hors des 118 rectangles de symboles**, dans les deux thèmes. Police SF Pro chargée explicitement depuis macOS ; identité Qt et empreinte du fichier enregistrées, police non redistribuée.
- Importation native : 118 cartes par langue, **236 cartes distinctes et 2 notes** ensemble ; quatre médias exacts, aucun manquant ou inutilisé.
- L'API d'édition native modifie puis restaure l'en-tête sans perdre la préparation facultative.
- Une réponse étudiée par langue conserve son état et son historique après exportation, réimportation et véritable remplacement de contenu par une reconstruction indépendante.
- Après suppression du champ facultatif de préparation, les 118 questions et réponses Anki restent utilisables. Seules les deux images nettoyées deviennent inutilisées.
- Moteur de révision livré avec Anki : **944 pages sur 944 réussies** — chaque ordinal, recto/verso, français/anglais, clair/sombre. Les contrôles vérifient le masque actif, l'image du thème, le nom exact au verso et l'absence de fuite de réponse ou de métadonnées au recto. 64 captures représentatives conservées.
- Paires d'images et exemples de réponses inspectés visuellement. Le nom et les faits compacts précèdent la grande figure.
- Clone indépendant de la révision de code `9162376` : tests, style, régénération des SVG, deux reconstructions et contrôles natifs renforcés réussis. Images, préparation et identités identiques au candidat ; les 472 rectos/versos HTML sont identiques octet par octet aux entrées du contrôle complet de 944 pages.

**L'édition manuelle complète dans Anki Desktop reste non vérifiée.** Une instance isolée sur SSD a été lancée avec la variable native `ANKI_SINGLE_INSTANCE_KEY`, mais l'outil d'interface sélectionnait l'instance personnelle déjà ouverte. Aucune action d'interface n'a été effectuée ; seul le processus de test a été arrêté. La collection personnelle et son importation en attente sont restées intactes.

Anki conserve ses masques natifs neutres. RectoVerso peut utiliser les images nettoyées enregistrées qui conservent les couleurs des cellules. Une couleur native par forme est possible, mais une valeur unique ne correspond pas aux deux palettes ; aucun moteur de masque de remplacement n'a été ajouté.

Le workflow de CI s’exécute sur la branche et la pull request de revue ; ses résultats courants sont liés dans la [revue des sources](review.md). Les contrôles propres à RectoVerso et aux appareils physiques relèvent de la tâche applicative séparée. Aucun paquet ni aucune release n’est publié.

## Contrôles de la CI de revue

Sans affichage, le canevas est rendu sans GPU. Le vérificateur attend le document exact et le rappel de fin de dessin d’Anki, puis applique ses assertions intactes : une réponse incorrecte ou un masque transparent reste un échec. La CI vérifie 944 pages et 64 pages supplémentaires avec navigation volontairement retardée. La [revue des sources](review.md) conserve les échecs initiaux et leurs contrôles. Aucun contenu de carte ni moteur de rendu Anki n’est modifié.

## Candidat de revue corrigé

Le nom et les faits attendent maintenant que la cible active soit présente dans le document. Une pause contrôlée de l’analyse HTML reproduisait leur absence ; le même contrôle réussit après correction. Les deux paquets ont été reconstruits, sans modifier les données, illustrations, régions ni identités. Les nouvelles empreintes figurent dans le [rapport anglais](validation.md) et le manifeste. L’importation normale **Si plus récent** depuis le candidat local précédent applique le script en conservant les 118 identifiants et la progression étudiée dans chaque langue. Ce contrôle ne prétend pas à une migration depuis une version publiée.


## Candidat : dégagement du numéro atomique — 2026-11-02

L’[issue source #3](https://github.com/rectoversohq/rectoverso-periodic-table/issues/3), liée à l’[app #622](https://github.com/simonpinkas/RectoVerso/issues/622), corrige l’espacement des cellules dessinées. L’ancien masque de 70 × 48 était trop proche du numéro : les 118 numéros, dans les deux thèmes, rencontraient la lentille et son contour inchangés. Il ne s’agissait pas d’un défaut de caméra ou de recalage. Des cellules plus hautes et une région de 70 × 40 contenant tout le symbole réservent une bande au numéro. Typographie, données et identités restent intactes. Les quatre PNG recalés mesurent désormais **3840 × 2960**.

| Contrôle | Résultat observé |
| --- | --- |
| Régression source | Cinq tests réussis. L’encre raster SF Pro des 118 numéros dans les deux thèmes garde au moins **11,432 unités source** au-delà du contour noir ; l’ancienne source échoue aux 236 cas (minimum −16,560). |
| Masquage et recalage | Zéro pixel modifié hors des 118 régions entre chaque original et sa version nettoyée. Les symboles entiers, descendantes comprises, restent dans leur région ; la réponse originale est inchangée. |
| Backend Anki natif | Paquets bilingues, reconstructions indépendantes, édition native, retrait du champ optionnel, planification et export/réimport réussis. Quatre médias exacts par paquet neuf, aucun absent ou inutilisé. |
| Mise à jour des anciens candidats | Avec **Si plus récent**, candidate-7 puis le candidat à légende corrigée sont mis à jour dans les deux langues : 118 identités de cartes, note/modèle/GUID/champs, état étudié et journal conservés. Masques et empreintes actuels vérifiés, puis export/réimport avec planification réussi. |
| Régression des noms de médias | Le premier essai réutilisant les noms a échoué : Anki renommait les fichiers modifiés, mais le JSON base64 conservait les anciens noms. Les noms `-v2.png` corrigent ce problème. Les anciens médias inutilisés peuvent rester dans la collection ; aucun média utilisateur n’est supprimé. L’option répétable `--prior-packages` conserve ce contrôle. |
| Reviewer Anki intégré | **944/944** pages finales réussies : masque, ordinal, thème, nom correct et absence de réponse/métadonnées sur le recto. |
| Core de l’app réelle | `GalleryOcclusionDeckTests` réussit avec les paquets finaux : 236 réponses originales/noms localisés, quatre médias par langue, étude/sauvegarde/mise à jour et export/réimport Anki avec progrès conservés. |
| Revue native sur simulateurs | **72 captures Duo** : six postures, clair/anglais et sombre/français, Cn (112) masqué/partiel/révélé, entrée automatique et pincement réel. **20 captures téléphone 430pt** ajoutent H et Og. Captures natives avec géométrie conservée ; les 118 éléments sont couverts par les contrôles raster/backend, sans prétendre à 118 captures natives. |
| Limite du zoom manuel | La plus petite fenêtre en portrait fermé, réponse complète, mesure 76pt. À environ 2,1×, le numéro 112 peut passer sous la barre ou hors écran tout en restant dégagé de la lentille. Ces captures extrêmes sont conservées. Les captures utiles à 1,386× en réponse partielle et 0,8× en réponse complète restent lisibles ; les autres zooms sont proches de 2,1×. Aucun contrôle de caméra ou de barre n’est modifié. |
| Préservation | Sonde isolée sans App Group. PID Duo original 89437 et **6 434** empreintes de fichiers conservés ; sonde retirée, posture/thème/texte restaurés. Aucun paquet du téléphone physique modifié. |

Preuves locales : `/Volumes/SSD/RectoVerso/raw/periodic-clearance-20261102/`, notamment `artwork-v2/`, `packages-v2/`, `anki-final/report.json`, `reviewer-v2/render-report.json`, `app-roundtrip/`, `clearance-audit.json`, `phone/`, `duo/`, `duo-extreme-zoom/`, `preservation/` et `review/index.html` avec liens vers les captures complètes. Les essais aux coordonnées erronées sont archivés séparément. La PR source indique les résultats du clone neuf sur le commit exact et de la CI hébergée. L’édition manuelle complète dans Anki Desktop et les revues matérielle/accessibilité restent distinctes ; aucune publication n’est impliquée.

| Paquet | Octets | SHA-256 |
| --- | ---: | --- |
| `Periodic-table-en.apkg` | 1 016 539 | `96b73a0ab62a1dd0f6fb5822a9d13c4c226d71767ee88f10e25a1ff4a92db010` |
| `Tableau-periodique-fr.apkg` | 1 016 597 | `f13b2fed311c3cbddff5a82def1e3b0a1c4363dcf9d884bf77787046ac770111` |
