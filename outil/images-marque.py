#!/usr/bin/env python3
"""Fabrique le favicon (le « ô » du logo sur fond Majorelle) et l'image de partage Open Graph.

Usage : python3 outil/images-marque.py
Entrées : img/cote-wordmark.svg, img/hero-dunes.jpg. Sorties : favicon.svg, favicon-32.png, apple-touch-icon.png, img/og-cote-maroc.jpg.
Le rendu PNG passe par Google Chrome en mode sans fenêtre ; Pillow fait les redimensionnements.
"""
import pathlib
import re
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
MAJORELLE = '#2B4DB8'

svg = (ROOT / 'img' / 'cote-wordmark.svg').read_text(encoding='utf-8')
corps = re.sub(r'<defs\b[^>]*>.*?</defs>', '', svg, flags=re.S)
chemins = re.findall(r'<path\b[^>]*>', corps)
assert len(chemins) == 6, f'6 glyphes attendus, {len(chemins)} trouvés'
# ordre des glyphes visibles : c, ô, t, é, accent du ô, accent du é
o_corps, o_accent = chemins[1], chemins[4]


def blanc(p):
    p = re.sub(r'\sclip-path="[^"]*"', '', p)
    p = re.sub(r'fill:#[0-9a-fA-F]{6}', 'fill:#ffffff', p)
    return p if p.endswith('/>') else p + '</path>'


# Le « ô » occupe x 109 → 203 et y 17.9 → 155.8 dans le repère du logo (ratio 94 : 138).
echelle = 66 / 138
largeur_glyphe = 94 * echelle
glyphe = f'<g transform="translate({(100 - largeur_glyphe) / 2:.2f},17) scale({echelle:.5f}) translate(-109,-17.9)">{blanc(o_corps)}{blanc(o_accent)}</g>'
favicon_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="20" fill="{MAJORELLE}"/>{glyphe}</svg>\n'
(ROOT / 'favicon.svg').write_text(favicon_svg, encoding='utf-8')


def rendu(html, largeur, hauteur, sortie):
    with tempfile.TemporaryDirectory() as d:
        page = pathlib.Path(d) / 'page.html'
        page.write_text(html, encoding='utf-8')
        r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--window-size={largeur},{hauteur}',
                            '--virtual-time-budget=8000', f'--screenshot={sortie}', page.as_uri()], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f'Chrome a échoué : {r.stderr[:300]}')


# Favicon PNG (icône carrée, coins arrondis déjà dans le SVG)
favicon_png = ROOT / 'favicon-512.png'
rendu(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:transparent}}svg{{display:block;width:512px;height:512px}}</style></head><body>{favicon_svg}</body></html>', 512, 512, favicon_png)
im = Image.open(favicon_png).convert('RGBA')
im.resize((180, 180), Image.LANCZOS).save(ROOT / 'apple-touch-icon.png', optimize=True)
im.resize((32, 32), Image.LANCZOS).save(ROOT / 'favicon-32.png', optimize=True)
favicon_png.unlink()

# Image Open Graph 1200 × 630 : dunes, voile sombre, logo blanc, accroche
hero = (ROOT / 'img' / 'hero-dunes.jpg').as_uri()
wordmark_inline = re.sub(r'<\?xml[^>]*\?>|<!--.*?-->', '', svg, flags=re.S)
wordmark_inline = re.sub(r'<svg\b[^>]*>', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="14.10 15.90 349.20 141.90" width="220" height="89" style="display:block">', wordmark_inline, count=1)
wordmark_inline = wordmark_inline.replace('fill:#ff4f58', 'fill:#ffffff').replace('fill="#ff4f58"', 'fill="#ffffff"')
og_html = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Gloock&family=Jost:wght@400;500&family=Outfit:wght@400&display=swap" rel="stylesheet">
<style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;font-family:Jost,sans-serif}}
.fond{{position:absolute;inset:0;background:url({hero}) center/cover}}
.voile{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(27,30,51,.25),rgba(27,30,51,.72))}}
.bloc{{position:absolute;left:80px;bottom:72px;color:#fff}}
.logo{{display:inline-flex;flex-direction:column;align-items:center;margin-bottom:28px}}
.cote{{width:220px;height:89px}}
.maroc{{display:flex;gap:6px;font-family:Outfit,sans-serif;font-size:33px;line-height:1;margin-top:4px}}
.maroc span:nth-child(1){{transform:rotate(-4deg)}}.maroc span:nth-child(2){{transform:translateY(-2px) rotate(3deg)}}.maroc span:nth-child(3){{transform:translateY(2px) rotate(-3deg)}}.maroc span:nth-child(4){{transform:translateY(-2px)}}.maroc span:nth-child(5){{transform:translateY(1px) rotate(4deg)}}
h1{{font-family:Gloock,serif;font-weight:400;font-size:64px;line-height:1.1;margin:0 0 14px;max-width:900px}}
p{{font-size:26px;margin:0;color:rgba(255,255,255,.88)}}
.badge{{position:absolute;top:56px;right:80px;font-family:Jost,sans-serif;font-size:20px;letter-spacing:.12em;text-transform:uppercase;color:#fff;border:2px solid rgba(255,255,255,.7);padding:10px 18px;border-radius:999px}}
</style></head><body>
<div class="fond"></div><div class="voile"></div>
<div class="badge">cotemaroc.ch</div>
<div class="bloc">
  <div class="logo"><div class="cote">{wordmark_inline}</div><div class="maroc"><span>m</span><span>a</span><span>r</span><span>o</span><span>c</span></div></div>
  <h1>Le Maroc sur mesure, organisé depuis la Suisse</h1>
  <p>Circuits en petit groupe, en privé et sur mesure · une marque de Côté Voyages, Martigny</p>
</div>
</body></html>'''
og_png = ROOT / 'img' / 'og-cote-maroc.png'
rendu(og_html, 1200, 630, og_png)
Image.open(og_png).convert('RGB').save(ROOT / 'img' / 'og-cote-maroc.jpg', quality=86, optimize=True, progressive=True)
og_png.unlink()
print('favicon.svg, favicon-32.png, apple-touch-icon.png, img/og-cote-maroc.jpg : ok')
