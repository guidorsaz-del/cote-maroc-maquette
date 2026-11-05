# cotemaroc.ch

Site de Côté Maroc, marque de Côté Voyages (Martigny), tour-opérateur spécialiste du Maroc. En ligne sur https://cotemaroc.ch depuis le 5 novembre 2026.

## Hébergement et mise en ligne

- Le site est servi par GitHub Pages depuis la branche `main` de ce dépôt. Chaque `git push` sur `main` met le site à jour en une à deux minutes.
- Le domaine `cotemaroc.ch` est chez Hostinger ; ses enregistrements A/AAAA pointent vers GitHub Pages et `www` est un CNAME vers `guidorsaz-del.github.io`. Le fichier `CNAME` à la racine lie le dépôt au domaine.
- HTTPS est fourni par GitHub Pages (certificat automatique).

## Pages

| Page | Contenu |
|---|---|
| `index.html` | Accueil : bannière, engagements, voyages phares, envies, éclipse 2027, comment ça marche, note Google, contact rapide |
| `voyages.html` | Les sept voyages et le sur mesure, avec filtres (formule, durée, budget, mois) |
| `circuits/*.html` | Les sept fiches voyage : programme jour par jour, carte des étapes, prestations, partage et impression |
| `envies/index.html` et `envies/*.html` | Sept envies, chacune avec ses voyages et ses lieux |
| `destinations/index.html` et `destinations/*.html` | Dix lieux, avec carte, ce qu'on y voit et les voyages qui y passent |
| `eclipse-2027.html` | Compte à rebours, comparatif des deux formules, questions fréquentes |
| `preparer-son-voyage.html` | Quand partir mois par mois, formalités, vols, monnaie, usages, questions fréquentes |
| `qui-sommes-nous.html` | Côté Voyages depuis 1995, Sandra, l'équipe au Maroc, méthode, engagements |
| `devis.html` | Demande de devis en quatre étapes, envoyée à n8n |
| `professionnels.html` | Présentation pour les tour-opérateurs et agences, conditions, formulaire |
| `contact.html` | WhatsApp, e-mail, rendez-vous Calendly intégré, formulaire court |
| `merci.html`, `credits.html`, `404.html` | Confirmation après envoi, crédits photos et cartes, page introuvable |

## Comment modifier le site

Le site est généré par `python3 outil/build.py` (Python 3 standard, aucune dépendance) à partir du dossier `src/` :

- `src/site.json` : adresse du site, coordonnées, navigation, note Google, adresse du webhook n8n, lien Calendly
- `src/voyages.json`, `src/destinations.json`, `src/envies.json`, `src/faq.json`, `src/credits.json` : les données
- `src/avis.json` : avis Google qui parlent du Maroc (vide pour l'instant ; la section affiche la note moyenne tant qu'il n'y en a pas)
- `src/pages/**` : le contenu de chaque page (le `<main>`), avec un bloc `meta` en tête et des marqueurs `<!-- cartes:phares -->`, `<!-- faq:eclipse -->`, `<!-- carte:slug -->`, etc. remplacés à la génération
- `src/gabarit/base.html` : en-tête, navigation, bouton WhatsApp flottant, pied de page

Les fichiers HTML à la racine et dans `circuits/`, `envies/`, `destinations/`, ainsi que `sitemap.xml` et `robots.txt`, sont générés : on modifie `src/`, on relance `python3 outil/build.py`, on vérifie en local (`python3 -m http.server 8765`), puis `git push`.

`python3 outil/images-marque.py` refabrique le favicon et l'image de partage à partir du logo.

## Fonctions

- Demande de devis en quatre étapes, pré-remplie depuis les fiches (`?voyage=`), les envies (`?envie=`) et les destinations (`?etape=`), envoyée au webhook n8n « Côté Maroc, Demandes du site » qui enregistre dans la base Airtable « Côté Maroc », puis prévient Sandra par e-mail et envoie un accusé de réception au client. Si l'envoi échoue, le visiteur reçoit un lien e-mail pré-rempli et un lien WhatsApp ; rien n'est perdu.
- Bouton WhatsApp flottant avec message pré-rempli selon la page.
- Rendez-vous Calendly « Rendez-vous Côté Maroc » intégré sur la page Contact.
- Partage d'une fiche (partage natif du téléphone ou WhatsApp, e-mail) et feuille de style d'impression.
- Filtres sans rechargement sur la liste des voyages.
- Cartes des étapes (Leaflet + OpenStreetMap) sur chaque fiche et chaque destination.
- Comparatif et compte à rebours sur la page Éclipse 2027.
- Référencement : canonical, Open Graph, questions fréquentes balisées schema.org, fiche TravelAgency sur l'accueil, sitemap et robots.txt.

## Technique

HTML, CSS et JavaScript sans framework. Polices Google Fonts : Gloock, Jost, JetBrains Mono, Outfit. Cartes : Leaflet 1.9.4 depuis unpkg et tuiles OpenStreetMap. Le mot « côté » du logo est extrait en vectoriel du logo officiel de Côté Voyages (`img/cote-wordmark.svg`).

## Crédits photos

Photos libres de droits publiées sur Pexels, listées sur la page `credits.html` du site et dans `src/credits.json`.
