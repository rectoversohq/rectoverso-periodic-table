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
