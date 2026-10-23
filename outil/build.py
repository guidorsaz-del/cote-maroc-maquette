#!/usr/bin/env python3
"""Génère le site statique Côté Maroc à partir du dossier src/.

Python 3 standard uniquement, aucune dépendance. Usage : python3 outil/build.py
Les pages HTML à la racine, dans circuits/, envies/ et destinations/ sont écrasées.
"""
import json
import pathlib
import re
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'


def lire_json(nom):
    return json.loads((SRC / nom).read_text(encoding='utf-8'))


SITE = lire_json('site.json')
VOYAGES = lire_json('voyages.json')
DESTINATIONS = lire_json('destinations.json')
ENVIES = lire_json('envies.json')
FAQ = lire_json('faq.json')
AVIS = lire_json('avis.json') if (SRC / 'avis.json').exists() else []
GABARIT = (SRC / 'gabarit' / 'base.html').read_text(encoding='utf-8')
VOYAGE_PAR_SLUG = {v['slug']: v for v in VOYAGES}
DESTINATION_PAR_SLUG = {d['slug']: d for d in DESTINATIONS}
ENVIE_PAR_SLUG = {e['slug']: e for e in ENVIES}
MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']


def echapper(texte):
    return (str(texte).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))


def lien_whatsapp(message=''):
    base = f"https://wa.me/{SITE['whatsapp']}"
    return base + ('?text=' + urllib.parse.quote(message) if message else '')


def prix_html(v):
    morceaux = []
    if v['prixPrefixe']:
        morceaux.append(v['prixPrefixe'])
    morceaux.append(f"<strong>{v['prixTexte']}</strong>")
    if v['prixSuffixe']:
        morceaux.append(v['prixSuffixe'])
    return ' '.join(morceaux)


def carte_voyage(v, prefix):
    jours = v['jours'] if v['jours'] else v['nuits'] + 1
    mois = ','.join(map(str, v['mois'])) if isinstance(v['mois'], list) else 'tous'
    data = f' data-type="{v["type"]}" data-jours="{jours}" data-budget="{v["prixBande"]}" data-mois="{mois}"'
    url = f"{prefix}circuits/{v['slug']}.html"
    return f'''        <article class="carte"{data}>
          <img src="{prefix}img/{v['image']}" alt="{echapper(v['alt'])}" loading="lazy">
          <div class="carte-corps">
            <span class="etiquette">{v['etiquette']}</span>
            <h3><a href="{url}">{v['titre']}</a></h3>
            <p>{v['resume']}</p>
            <div class="carte-meta"><span>{v['dureeTexte']} · {prix_html(v)}</span><a class="lien-fleche" href="{url}">Découvrir</a></div>
          </div>
        </article>'''


def carte_sur_mesure(prefix):
    return f'''        <article class="carte carte-sur-mesure" data-type="sur-mesure" data-jours="0" data-budget="demande" data-mois="tous">
          <div class="carte-corps">
            <span class="etiquette">Sur mesure</span>
            <h3>Votre voyage, de A à Z</h3>
            <p>Un itinéraire construit autour de vos envies, de vos dates et de votre budget, avec notre équipe au Maroc.</p>
            <div class="carte-meta"><span><strong>Prix sur demande</strong></span><a class="lien-fleche" href="{prefix}devis.html">Demander un devis</a></div>
          </div>
        </article>'''


def cartes(voyages, prefix, sur_mesure=False):
    blocs = [carte_voyage(v, prefix) for v in voyages]
    if sur_mesure:
        blocs.append(carte_sur_mesure(prefix))
    return '\n'.join(blocs)


def tuiles_envies(prefix, envies=None):
    envies = envies or ENVIES
    out = []
    for e in envies:
        out.append(f'''        <a class="envie" href="{prefix}envies/{e['slug']}.html"><img src="{prefix}img/{e['image']}" alt="{echapper(e['alt'])}" loading="lazy"><div class="envie-texte"><strong>{e['nom']}</strong><span>{e['accroche']}</span></div></a>''')
    return '\n'.join(out)


def tuiles_destinations(prefix, destinations=None):
    destinations = destinations or DESTINATIONS
    out = []
    for d in destinations:
        out.append(f'''        <a class="envie" href="{prefix}destinations/{d['slug']}.html"><img src="{prefix}img/{d['image']}" alt="{echapper(d['alt'])}" loading="lazy"><div class="envie-texte"><strong>{d['nom']}</strong><span>{d['accroche']}</span></div></a>''')
    return '\n'.join(out)


def faq_html(cle):
    items = FAQ[cle]
    blocs = []
    for it in items:
        blocs.append(f'''        <details class="faq-item">
          <summary>{it['q']}</summary>
          <p>{it['r']}</p>
        </details>''')
    return '\n'.join(blocs)


def faq_jsonld(cle):
    data = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [{'@type': 'Question', 'name': it['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': it['r']}} for it in FAQ[cle]],
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


def carte_geo(v):
    etapes = json.dumps(v['etapes'], ensure_ascii=False)
    return f'''        <div class="carte-voyage" id="carte" data-etapes='{etapes.replace("'", "&#39;")}' data-boucle="{'true' if v.get('boucle') else 'false'}" role="img" aria-label="Carte des étapes du voyage"></div>
        <p class="mentions">Carte indicative des étapes. Les tracés exacts dépendent des routes et du programme du jour.</p>'''


def carte_destinations():
    points = json.dumps([{'nom': d['nom'], 'lat': d['lat'], 'lng': d['lng']} for d in DESTINATIONS], ensure_ascii=False)
    return f'''        <div class="carte-voyage" id="carte" data-etapes='{points.replace("'", "&#39;")}' data-boucle="false" data-ligne="false" data-direction="top" role="img" aria-label="Carte des destinations"></div>'''


def etoiles_html(note_texte):
    note = float(str(note_texte).replace(',', '.'))
    pleines = int(round(note))
    return '<span class="etoiles" aria-hidden="true">' + '★' * pleines + '☆' * (5 - pleines) + '</span>'


def note_google_pied():
    n = SITE.get('noteGoogle')
    if not n:
        return ''
    return f'        <p class="pied-note">{etoiles_html(n["note"])} Côté Voyages est notée <strong>{n["note"]} / {n["sur"]}</strong> sur Google ({n["avis"]} avis). <a href="{SITE["avisGoogleUrl"]}">Voir les avis</a></p>'


def bande_note_google():
    n = SITE.get('noteGoogle')
    if not n:
        return ''
    return f'''      <section class="section" id="avis" aria-labelledby="titre-note">
        <div class="bande-note">
          <div class="bande-note-chiffre">{n["note"]}<small>/ {n["sur"]}</small></div>
          <div>
            {etoiles_html(n["note"])}
            <h2 id="titre-note">La note Google de Côté Voyages, notre agence</h2>
            <p>{n["avis"]} voyageurs ont laissé un avis sur la fiche Google de Côté Voyages, à Martigny. Côté Maroc est jeune : ses premiers avis viendront de ses premiers voyageurs, et nous les publierons ici tels quels.</p>
            <a class="lien-fleche" href="{SITE["avisGoogleUrl"]}">Lire les avis sur Google</a>
          </div>
        </div>
      </section>'''


def avis_html():
    """Avis Google de Côté Voyages qui parlent du Maroc. Tant que src/avis.json est vide, seule la note moyenne est affichée."""
    if not AVIS:
        return bande_note_google()
    blocs = []
    for a in AVIS:
        etoiles = '★' * int(a.get('note', 5)) + '☆' * (5 - int(a.get('note', 5)))
        blocs.append(f'''          <blockquote>
            <div class="etoiles" aria-label="{a.get('note', 5)} étoiles sur 5">{etoiles}</div>
            <p>{a['texte']}</p>
            <footer>{a['auteur']}, avis Google{(' · ' + a['date']) if a.get('date') else ''}</footer>
          </blockquote>''')
    return f'''      <section class="section" id="avis" aria-labelledby="titre-avis">
        <div class="entete-section">
          <span class="etiquette">Ils sont partis avec nous</span>
          <h2 id="titre-avis">Avis Google de voyageurs revenus du Maroc</h2>
          <p class="sous-titre">Des avis publiés sur la fiche Google de Côté Voyages, notre agence à Martigny. Nous ne rédigeons jamais d'avis nous-mêmes.</p>
        </div>
        <div class="avis">
{chr(10).join(blocs)}
        </div>
        <p class="mentions"><a href="{SITE['avisGoogleUrl']}">Voir tous les avis sur Google</a></p>
      </section>'''


def carte_point(d):
    etapes = json.dumps([{'nom': d['nom'], 'lat': d['lat'], 'lng': d['lng']}], ensure_ascii=False)
    return f'''<div class="carte-voyage carte-destination" id="carte" data-etapes='{etapes.replace("'", "&#39;")}' data-boucle="false" data-zoom="8" role="img" aria-label="Carte de situation"></div>'''


def partage(titre, prefix):
    return f'''        <div class="partage">
          <span class="etiquette">Partager</span>
          <div class="groupe-boutons">
            <button type="button" class="btn btn-secondaire btn-petit" data-partager data-titre="{echapper(titre)}">Envoyer à un proche</button>
            <a class="btn btn-secondaire btn-petit" href="mailto:?subject={urllib.parse.quote(titre)}&amp;body={urllib.parse.quote(titre + ' : ')}" data-partager-mail>Par e-mail</a>
            <button type="button" class="btn btn-secondaire btn-petit" data-imprimer>Imprimer la fiche</button>
          </div>
        </div>'''


def compte_a_rebours():
    return '''        <div class="compte-a-rebours" data-cible="2027-08-02T00:00:00+01:00" aria-live="polite">
          <div><strong data-jours>…</strong><span>jours</span></div>
          <div><strong data-heures>…</strong><span>heures</span></div>
          <div><strong data-minutes>…</strong><span>minutes</span></div>
          <p>avant l'éclipse totale du 2 août 2027</p>
        </div>'''


def bloc_calendly(prefix):
    url = SITE.get('calendlyUrl', '')
    if url:
        return f'''        <div class="calendly-bloc" id="calendly" data-url="{url}">
          <p class="mentions">Le calendrier se charge ci-dessous. S'il ne s'affiche pas, <a href="{url}">ouvrez-le dans un nouvel onglet</a>.</p>
        </div>'''
    return f'''        <div class="calendly-bloc calendly-attente" id="calendly" data-url="">
          <p><strong>Prise de rendez-vous en ligne</strong></p>
          <p>Le calendrier de Sandra sera relié ici. En attendant, écrivez-nous sur WhatsApp ou par e-mail pour convenir d'un moment.</p>
          <div class="groupe-boutons">
            <a class="btn btn-principal" href="{lien_whatsapp('Bonjour, je souhaite prendre rendez-vous pour parler de mon projet de voyage au Maroc.')}">Proposer un créneau sur WhatsApp</a>
            <a class="btn btn-secondaire" href="mailto:{SITE['email']}?subject=Rendez-vous">Par e-mail</a>
          </div>
        </div>'''


def liste_voyages_lies(slugs, prefix, titre='Les voyages qui correspondent'):
    voyages = [VOYAGE_PAR_SLUG[s] for s in slugs if s in VOYAGE_PAR_SLUG]
    if not voyages:
        return ''
    return f'''      <section class="section" aria-labelledby="titre-voyages-lies">
        <div class="entete-section">
          <span class="etiquette">Nos voyages</span>
          <h2 id="titre-voyages-lies">{titre}</h2>
        </div>
        <div class="grille-cartes grille-cartes-3">
{cartes(voyages, prefix)}
        </div>
      </section>'''


def remplacer_marqueurs(main, prefix, contexte):
    """Remplace les marqueurs <!-- xxx --> des fragments par les blocs générés."""
    extra_head = []

    def rempl(m):
        cle = m.group(1).strip()
        if cle == 'cartes:phares':
            return cartes([v for v in VOYAGES if v.get('phare')], prefix)
        if cle == 'cartes:toutes':
            return cartes(VOYAGES, prefix, sur_mesure=True)
        if cle == 'envies:apercu':
            return tuiles_envies(prefix)
        if cle == 'destinations:apercu':
            return tuiles_destinations(prefix)
        if cle.startswith('faq:'):
            extra_head.append(faq_jsonld(cle.split(':', 1)[1]))
            return faq_html(cle.split(':', 1)[1])
        if cle == 'carte:destinations':
            contexte['leaflet'] = True
            return carte_destinations()
        if cle.startswith('carte:'):
            contexte['leaflet'] = True
            return carte_geo(VOYAGE_PAR_SLUG[cle.split(':', 1)[1]])
        if cle == 'avis':
            return avis_html()
        if cle == 'partage':
            return partage(contexte.get('titre_partage', SITE['nom']), prefix)
        if cle == 'compte-a-rebours':
            return compte_a_rebours()
        if cle == 'calendly':
            contexte['calendly'] = True
            return bloc_calendly(prefix)
        return m.group(0)

    main = re.sub(r'<!--\s*([a-z\-:]+)\s*-->', rempl, main)
    return main, '\n'.join(extra_head)


def nav_html(prefix, page_path):
    lignes = []
    for item in SITE['nav']:
        courant = ' aria-current="page"' if item['href'] == page_path else ''
        lignes.append(f'        <li><a href="{prefix}{item["href"]}"{courant}>{item["libelle"]}</a></li>')
    return '\n'.join(lignes)


def pied_pages_html(prefix):
    return '\n'.join(f'          <li><a href="{prefix}{p["href"]}">{p["libelle"]}</a></li>' for p in SITE['piedPages'])


def ecrire_page(chemin, titre, description, main, body_class='', whatsapp='', titre_partage=None, nav_path=None):
    chemin = pathlib.Path(chemin)
    profondeur = len(chemin.parts) - 1
    prefix = '../' * profondeur
    contexte = {'titre_partage': titre_partage or titre}
    main, head_faq = remplacer_marqueurs(main, prefix, contexte)
    head_extra = [head_faq] if head_faq else []
    scripts_extra = []
    if contexte.get('leaflet'):
        head_extra.append('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">')
        scripts_extra.append('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>')
        scripts_extra.append(f'<script>window.initialiserCartes && window.initialiserCartes();</script>')
    message_wa = whatsapp or 'Bonjour, je souhaite des renseignements sur un voyage au Maroc.'
    body_data = f' data-webhook="{SITE["webhookDevis"]}" data-wa="{echapper(message_wa)}"'
    page = (GABARIT
            .replace('{{TITLE}}', echapper(titre))
            .replace('{{DESCRIPTION}}', echapper(description))
            .replace('{{PREFIX}}', prefix)
            .replace('{{HEAD_EXTRA}}', '\n'.join(head_extra))
            .replace('{{BODY_CLASS}}', body_class)
            .replace('{{BODY_DATA}}', body_data)
            .replace('{{NAV}}', nav_html(prefix, nav_path or str(chemin).replace('\\', '/')))
            .replace('{{MAIN}}', main)
            .replace('{{WA_LIEN}}', lien_whatsapp(message_wa))
            .replace('{{WA_LIEN_SIMPLE}}', lien_whatsapp())
            .replace('{{WA_AFFICHE}}', SITE['whatsappAffiche'])
            .replace('{{EMAIL}}', SITE['email'])
            .replace('{{PIED_PAGES}}', pied_pages_html(prefix))
            .replace('{{NOTE_GOOGLE}}', note_google_pied())
            .replace('{{SCRIPTS_EXTRA}}', '\n'.join(scripts_extra)))
    sortie = ROOT / chemin
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(page, encoding='utf-8')
    return sortie


def lire_fragment(chemin):
    """Un fragment commence par <!-- meta {...} --> puis le contenu de <main>."""
    texte = (SRC / 'pages' / chemin).read_text(encoding='utf-8')
    m = re.match(r'\s*<!--\s*meta\s*(\{.*?\})\s*-->\s*', texte, re.S)
    if not m:
        raise SystemExit(f'fragment sans bloc meta : {chemin}')
    meta = json.loads(m.group(1))
    return meta, texte[m.end():]


def construire_fragments():
    pages = []
    for frag in sorted((SRC / 'pages').rglob('*.html')):
        rel = frag.relative_to(SRC / 'pages')
        meta, main = lire_fragment(rel)
        nav_path = meta.get('nav', str(rel).replace('\\', '/'))
        ecrire_page(str(rel), meta['title'], meta['description'], main,
                    body_class=meta.get('bodyClass', ''), whatsapp=meta.get('whatsapp', ''),
                    titre_partage=meta.get('titrePartage'), nav_path=nav_path)
        pages.append(str(rel))
    return pages


def page_envie(e):
    prefix = '../'
    destinations = [DESTINATION_PAR_SLUG[s] for s in e['destinations'] if s in DESTINATION_PAR_SLUG]
    textes = '\n'.join(f'        <p>{t}</p>' for t in e['textes'])
    main = f'''  <section class="banniere banniere-fiche" aria-labelledby="titre-envie">
    <img src="{prefix}img/{e['image']}" alt="{echapper(e['alt'])}" fetchpriority="high">
    <div class="conteneur">
      <nav class="fil-ariane" aria-label="Fil d'Ariane"><ol><li><a href="{prefix}index.html">Accueil</a></li><li><a href="{prefix}envies/index.html">Envies</a></li><li><span>{e['nom']}</span></li></ol></nav>
      <span class="etiquette">Envie</span>
      <h1 id="titre-envie">{e['nom']}</h1>
      <p class="sous-titre">{e['accroche']}.</p>
    </div>
  </section>
  <div class="conteneur">
    <section class="section texte-long" aria-labelledby="titre-texte">
      <h2 id="titre-texte" class="sr-only">Présentation</h2>
{textes}
      <p class="pour-qui"><strong>Pour qui ?</strong> {e['pourQui']}</p>
    </section>
{liste_voyages_lies(e['voyages'], prefix)}
    <section class="section section-sable section-bord" aria-labelledby="titre-destinations-liees">
      <div class="entete-section">
        <span class="etiquette">Destinations</span>
        <h2 id="titre-destinations-liees">Les lieux de cette envie</h2>
      </div>
      <div class="grille-envies">
{tuiles_destinations(prefix, destinations)}
      </div>
    </section>
    <section class="section" aria-labelledby="titre-cta-envie">
      <h2 id="titre-cta-envie">On en parle ?</h2>
      <p class="sous-titre">Dites-nous vos dates et vos envies, Sandra vous répond sous 24 h.</p>
      <div class="groupe-boutons">
        <a class="btn btn-principal" href="{prefix}devis.html?envie={e['slug']}">Demander un devis</a>
        <a class="btn btn-secondaire" href="{lien_whatsapp('Bonjour, je m intéresse à un voyage au Maroc, envie : ' + e['nom'] + '.')}">Parler à un spécialiste</a>
      </div>
    </section>
  </div>'''
    ecrire_page(f"envies/{e['slug']}.html", f"{e['nom']} · Envies · Côté Maroc", f"{e['accroche']}. Les voyages et les lieux au Maroc qui correspondent à cette envie, organisés depuis la Suisse.",
                main, whatsapp=f"Bonjour, je m'intéresse à un voyage au Maroc, envie : {e['nom']}.", nav_path='envies/index.html')


def page_destination(d):
    prefix = '../'
    voyages = [v['slug'] for v in VOYAGES if d['slug'] in v['destinations']]
    textes = '\n'.join(f'        <p>{t}</p>' for t in d['textes'])
    a_voir = '\n'.join(f'            <li><svg class="icone" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/></svg><span>{x}</span></li>' for x in d['aVoir'])
    vols = f'<p class="mentions">{d["vols"]}</p>' if d.get('vols') else ''
    main = f'''  <section class="banniere banniere-fiche" aria-labelledby="titre-destination">
    <img src="{prefix}img/{d['image']}" alt="{echapper(d['alt'])}" fetchpriority="high">
    <div class="conteneur">
      <nav class="fil-ariane" aria-label="Fil d'Ariane"><ol><li><a href="{prefix}index.html">Accueil</a></li><li><a href="{prefix}destinations/index.html">Destinations</a></li><li><span>{d['nom']}</span></li></ol></nav>
      <span class="etiquette">Destination</span>
      <h1 id="titre-destination">{d['nom']}</h1>
      <p class="sous-titre">{d['accroche']}.</p>
    </div>
  </section>
  <div class="conteneur fiche-grille">
    <div class="fiche-principal">
      <section class="texte-long" aria-labelledby="titre-texte">
        <h2 id="titre-texte" class="sr-only">Présentation</h2>
{textes}
        {vols}
      </section>
      <section aria-labelledby="titre-a-voir">
        <span class="etiquette">À voir</span>
        <h2 id="titre-a-voir">Ce qu'on ne manque pas</h2>
        <ul class="points-forts">
{a_voir}
        </ul>
      </section>
    </div>
    <aside class="fiche-aside">
      <div class="en-bref">
        <span class="etiquette">Situation</span>
        {carte_point(d)}
        <a class="btn btn-principal" href="{prefix}devis.html?etape={urllib.parse.quote(d['nom'])}">Demander un devis</a>
      </div>
    </aside>
  </div>
  <div class="conteneur">
{liste_voyages_lies(voyages, prefix, 'Nos voyages qui passent par ' + d['nom'])}
  </div>'''
    page = ecrire_page(f"destinations/{d['slug']}.html", f"{d['nom']} · Destinations · Côté Maroc", f"{d['nom']}, {d['accroche'].lower()}. Ce qu'on y voit et les voyages Côté Maroc qui y passent.",
                       main, whatsapp=f"Bonjour, je m'intéresse à un voyage au Maroc passant par {d['nom']}.", nav_path='destinations/index.html')
    # la carte de situation a besoin de Leaflet : on force son chargement
    texte = page.read_text(encoding='utf-8')
    if 'leaflet.js' not in texte:
        texte = texte.replace('</head>', '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">\n</head>')
        texte = texte.replace('</body>', '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>\n<script>window.initialiserCartes && window.initialiserCartes();</script>\n</body>')
        page.write_text(texte, encoding='utf-8')


def main():
    pages = construire_fragments()
    for e in ENVIES:
        page_envie(e)
    for d in DESTINATIONS:
        page_destination(d)
    print(f'{len(pages)} pages depuis les fragments, {len(ENVIES)} envies, {len(DESTINATIONS)} destinations.')


if __name__ == '__main__':
    main()
