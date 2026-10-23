# Maquette du site Côté Maroc, octobre 2026

Maquette v2 du futur site de Côté Maroc, marque de Côté Voyages (Martigny), tour-opérateur spécialiste du Maroc. Elle sert à valider l'organisation des pages, le ton et les fonctions avant le développement du site définitif.

## Pages

| Page | Contenu |
|---|---|
| `index.html` | Accueil : bannière, engagements, voyages phares, envies, éclipse 2027, comment ça marche, contact rapide |
| `voyages.html` | Les sept voyages et le sur mesure, avec filtres (formule, durée, budget, mois) |
| `circuits/*.html` | Les sept fiches voyage : programme jour par jour, carte des étapes, prestations, partage et impression |
| `envies/index.html` et `envies/*.html` | Sept envies, chacune avec ses voyages et ses lieux |
| `destinations/index.html` et `destinations/*.html` | Dix lieux, avec carte, ce qu'on y voit et les voyages qui y passent |
| `eclipse-2027.html` | Compte à rebours, comparatif des deux formules, questions fréquentes |
| `preparer-son-voyage.html` | Quand partir mois par mois, formalités, vols, monnaie, usages, questions fréquentes |
| `qui-sommes-nous.html` | Côté Voyages depuis 1995, Sandra, l'équipe au Maroc, méthode, engagements |
| `devis.html` | Demande de devis en quatre étapes, envoi réel vers n8n |
| `professionnels.html` | Présentation pour les tour-opérateurs et agences, conditions, formulaire |
| `contact.html` | WhatsApp, e-mail, rendez-vous Calendly intégré, formulaire court |
| `merci.html` | Confirmation après envoi |

## Comment ça marche

Le site est généré par `python3 outil/build.py` (Python 3 standard, aucune dépendance) à partir du dossier `src/` :

- `src/site.json` : coordonnées, navigation, adresse du webhook n8n, lien Calendly
- `src/voyages.json`, `src/destinations.json`, `src/envies.json`, `src/faq.json` : les données
- `src/avis.json` : avis Google de Côté Voyages qui parlent du Maroc (vide tant qu'ils ne sont pas fournis ; la section n'apparaît pas)
- `src/pages/**` : le contenu de chaque page (le `<main>`), avec un bloc `meta` en tête et des marqueurs `<!-- cartes:phares -->`, `<!-- faq:eclipse -->`, `<!-- carte:slug -->`, etc. remplacés à la génération
- `src/gabarit/base.html` : en-tête, navigation, bouton WhatsApp flottant, pied de page

Les fichiers HTML à la racine et dans `circuits/`, `envies/`, `destinations/` sont générés : on modifie `src/`, puis on relance la génération.

## Fonctions

- Demande de devis en quatre étapes avec validation, pré-remplissage depuis les fiches (`?voyage=`), les envies (`?envie=`) et les destinations (`?etape=`), envoi au webhook n8n « Côté Maroc, Demandes du site » qui enregistre dans la base Airtable « Côté Maroc », prévient Sandra par e-mail et envoie un accusé de réception au client. Champ anti-robot invisible.
- Bouton WhatsApp flottant avec message pré-rempli selon la page.
- Rendez-vous Calendly « Rendez-vous Côté Maroc » intégré sur la page Contact.
- Partage d'une fiche (partage natif du téléphone ou WhatsApp, e-mail) et feuille de style d'impression.
- Filtres sans rechargement sur la liste des voyages.
- Cartes des étapes (Leaflet + OpenStreetMap) sur chaque fiche et chaque destination.
- Comparatif et compte à rebours sur la page Éclipse 2027.
- Questions fréquentes balisées schema.org (FAQPage) sur Éclipse 2027 et Préparer son voyage.

## Technique

HTML, CSS et JavaScript sans framework. Polices Google Fonts : Gloock, Jost, JetBrains Mono, Outfit. Cartes : Leaflet 1.9.4 depuis unpkg et tuiles OpenStreetMap. Le mot « côté » du logo est extrait en vectoriel du logo officiel de Côté Voyages (`img/cote-wordmark.svg`). Pages en `noindex` tant que la maquette n'est pas le site définitif.

## Crédits photos

Photos libres de droits publiées sur Pexels. Merci aux photographes.

| Fichier | Photographe | Photo |
|---|---|---|
| `img/hero-dunes.jpg` | Fives TM | [pexels.com/photo/30099211](https://www.pexels.com/photo/mesmerizing-dunes-at-sunrise-in-merzouga-30099211/) |
| `img/marrakech-koutoubia.jpg` | Valentin Vesa | [pexels.com/photo/36595610](https://www.pexels.com/photo/sunset-at-koutoubia-mosque-in-marrakesh-36595610/) |
| `img/marrakech-souk.jpg` | Uiliam Nörnberg | [pexels.com/photo/22711555](https://www.pexels.com/photo/alley-in-market-in-marrakech-morocco-22711555/) |
| `img/jemaa-el-fna.jpg` | Mathias Dargnat | [pexels.com/photo/20895317](https://www.pexels.com/photo/bazaar-in-city-in-evening-20895317/) |
| `img/casablanca-hassan-ii.jpg` | Tom D'Arby | [pexels.com/photo/6587429](https://www.pexels.com/photo/famous-hassan-ii-mosque-in-morocco-6587429/) |
| `img/rabat-tour-hassan.jpg` | MAG Photography | [pexels.com/photo/29804296](https://www.pexels.com/photo/hassan-tower-at-dusk-in-rabat-morocco-29804296/) |
| `img/fes-medina.jpg` | Moussa Idrissi | [pexels.com/photo/30398390](https://www.pexels.com/photo/panoramic-view-of-fes-medina-from-rooftop-30398390/) |
| `img/chefchaouen.jpg` | Christophe RASCLE | [pexels.com/photo/18487344](https://www.pexels.com/photo/blue-building-in-an-old-town-18487344/) |
| `img/tanger.jpg` | AL  CREATION STUDIO | [pexels.com/photo/11344766](https://www.pexels.com/photo/white-buildings-and-ancient-walls-in-town-11344766/) |
| `img/merzouga-dunes.jpg` | Ed Duvico | [pexels.com/photo/29107889](https://www.pexels.com/photo/sunset-over-merzouga-sahara-desert-dunes-29107889/) |
| `img/caravane.jpg` | Sergey Pesterev | [pexels.com/photo/8357638](https://www.pexels.com/photo/a-camels-walking-on-the-desert-8357638/) |
| `img/chameaux-famille.jpg` | Zakaria HANIF | [pexels.com/photo/12214734](https://www.pexels.com/photo/people-riding-on-camels-on-a-desert-12214734/) |
| `img/ait-ben-haddou.jpg` | Fives TM | [pexels.com/photo/29976840](https://www.pexels.com/photo/scenic-view-of-ait-ben-haddou-morocco-29976840/) |
| `img/atlas-village.jpg` | pierre matile | [pexels.com/photo/37684085](https://www.pexels.com/photo/traditional-berber-village-in-the-atlas-mountains-37684085/) |
| `img/gorges-dades.jpg` | Marcia Salido | [pexels.com/photo/14145715](https://www.pexels.com/photo/dades-gorges-rock-formation-photo-14145715/) |
| `img/riad.jpg` | Philippe Lasry | [pexels.com/photo/38891222](https://www.pexels.com/photo/elegant-moroccan-courtyard-in-marrakesh-38891222/) |
| `img/eclipse.jpg` | Drew Dempsey | [pexels.com/photo/28946775](https://www.pexels.com/photo/captivating-solar-eclipse-in-space-28946775/) |
| `img/lac-atlas.jpg` | pierre matile | [pexels.com/photo/37700635](https://www.pexels.com/photo/scenic-view-of-ouarzazate-lake-in-morocco-37700635/) |
| `img/oasis-tinghir.jpg` | Cornelis Johannes (Kees) van Leeuwen | [pexels.com/photo/37441764](https://www.pexels.com/photo/panoramic-view-of-tinghir-oasis-and-village-37441764/) |
| `img/volubilis.jpg` | Christophe RASCLE | [pexels.com/photo/18767562](https://www.pexels.com/photo/ruins-of-volubilis-basilica-in-morocco-18767562/) |
| `img/villa-piscine.jpg` | Andrea Musto | [pexels.com/photo/27945034](https://www.pexels.com/photo/a-pool-in-a-courtyard-with-potted-plants-27945034/) |
| `img/hammam.jpg` | Max Vakhtbovych | [pexels.com/photo/7598373](https://www.pexels.com/photo/bathhouse-interior-with-a-sink-and-seats-7598373/) |
| `img/tanger-port.jpg` | Reda Faghloumi | [pexels.com/photo/13142301](https://www.pexels.com/photo/port-de-tangier-ville-in-morocco-13142301/) |
| `img/palmeraie-coucher.jpg` | YOUSSEF elbelghiti | [pexels.com/photo/16919234](https://www.pexels.com/photo/silhouette-of-palm-trees-at-sunset-16919234/) |
