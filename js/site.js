// Côté Maroc, maquette v2. Vanilla JS, aucune dépendance sauf Leaflet (chargé seulement sur les pages avec carte).
(function () {
  'use strict';

  // ---------- Menu mobile ----------
  (function menu() {
    var bouton = document.querySelector('.menu-bouton');
    var nav = document.getElementById('nav-principal');
    if (!bouton || !nav) { return; }
    function ouvrir(etat) {
      bouton.setAttribute('aria-expanded', etat ? 'true' : 'false');
      nav.classList.toggle('ouvert', etat);
      document.body.classList.toggle('menu-ouvert', etat);
      if (etat) { nav.querySelector('a').focus(); } else { bouton.focus(); }
    }
    bouton.addEventListener('click', function () { ouvrir(bouton.getAttribute('aria-expanded') !== 'true'); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a') && nav.classList.contains('ouvert')) { ouvrir(false); } });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && nav.classList.contains('ouvert')) { ouvrir(false); } });
    window.matchMedia('(min-width: 900px)').addEventListener('change', function (ev) { if (ev.matches) { ouvrir(false); } });
  })();

  // ---------- Compte à rebours ----------
  (function compteARebours() {
    var el = document.querySelector('.compte-a-rebours');
    if (!el) { return; }
    var cible = new Date(el.getAttribute('data-cible')).getTime();
    function maj() {
      var d = Math.max(0, cible - Date.now());
      var jours = Math.floor(d / 86400000);
      var heures = Math.floor((d % 86400000) / 3600000);
      var minutes = Math.floor((d % 3600000) / 60000);
      el.querySelector('[data-jours]').textContent = jours;
      el.querySelector('[data-heures]').textContent = heures;
      el.querySelector('[data-minutes]').textContent = minutes;
    }
    maj();
    setInterval(maj, 30000);
  })();

  // ---------- Filtres de la liste des voyages ----------
  (function filtres() {
    var form = document.querySelector('.filtres');
    var grille = document.querySelector('.grille-cartes[data-filtrable]');
    if (!form || !grille) { return; }
    var cartes = Array.prototype.slice.call(grille.querySelectorAll('.carte'));
    var compte = form.querySelector('.filtres-compte');
    var etat = { type: '', jours: '', budget: '', mois: '' };

    function correspond(carte) {
      var type = carte.getAttribute('data-type');
      if (type === 'sur-mesure') { return true; }
      if (etat.type && type !== etat.type) { return false; }
      var jours = parseInt(carte.getAttribute('data-jours'), 10) || 0;
      if (etat.jours === 'court' && jours > 5) { return false; }
      if (etat.jours === 'moyen' && (jours < 6 || jours > 9)) { return false; }
      if (etat.jours === 'long' && jours < 10) { return false; }
      if (etat.budget && carte.getAttribute('data-budget') !== etat.budget) { return false; }
      if (etat.mois) {
        var mois = carte.getAttribute('data-mois');
        if (mois !== 'tous' && mois.split(',').indexOf(etat.mois) === -1) { return false; }
      }
      return true;
    }

    function appliquer() {
      var visibles = 0;
      cartes.forEach(function (c) {
        var ok = correspond(c);
        c.hidden = !ok;
        if (ok && c.getAttribute('data-type') !== 'sur-mesure') { visibles += 1; }
      });
      if (compte) {
        compte.textContent = visibles === 0 ? 'Aucun voyage ne correspond à ces critères. Le sur mesure, lui, correspond toujours.' : (visibles + (visibles > 1 ? ' voyages' : ' voyage') + ' correspond' + (visibles > 1 ? 'ent' : '') + ' à vos critères.');
      }
    }

    form.querySelectorAll('[data-filtre="type"]').forEach(function (puce) {
      puce.addEventListener('click', function () {
        etat.type = puce.getAttribute('data-valeur');
        form.querySelectorAll('[data-filtre="type"]').forEach(function (p) { p.setAttribute('aria-pressed', p === puce ? 'true' : 'false'); });
        appliquer();
      });
    });
    form.querySelectorAll('select[data-filtre]').forEach(function (sel) {
      sel.addEventListener('change', function () { etat[sel.getAttribute('data-filtre')] = sel.value; appliquer(); });
    });
    var reset = form.querySelector('[data-reinitialiser]');
    if (reset) {
      reset.addEventListener('click', function () {
        etat = { type: '', jours: '', budget: '', mois: '' };
        form.querySelectorAll('select[data-filtre]').forEach(function (s) { s.value = ''; });
        form.querySelectorAll('[data-filtre="type"]').forEach(function (p) { p.setAttribute('aria-pressed', p.getAttribute('data-valeur') === '' ? 'true' : 'false'); });
        appliquer();
      });
    }
    appliquer();
  })();

  // ---------- Partage et impression ----------
  (function partage() {
    document.querySelectorAll('[data-partager]').forEach(function (b) {
      b.addEventListener('click', function () {
        var titre = b.getAttribute('data-titre') || document.title;
        var url = location.href.split('#')[0];
        if (navigator.share) {
          navigator.share({ title: titre, text: titre, url: url }).catch(function () {});
        } else {
          window.open('https://wa.me/?text=' + encodeURIComponent(titre + ' ' + url), '_blank', 'noopener');
        }
      });
    });
    document.querySelectorAll('[data-partager-mail]').forEach(function (a) {
      a.setAttribute('href', a.getAttribute('href') + encodeURIComponent(location.href.split('#')[0]));
    });
    document.querySelectorAll('[data-imprimer]').forEach(function (b) {
      b.addEventListener('click', function () { window.print(); });
    });
  })();

  // ---------- Calendly ----------
  (function calendly() {
    var bloc = document.getElementById('calendly');
    if (!bloc) { return; }
    var url = bloc.getAttribute('data-url');
    if (!url) { return; }
    var lien = document.createElement('link');
    lien.rel = 'stylesheet'; lien.href = 'https://assets.calendly.com/assets/external/widget.css';
    document.head.appendChild(lien);
    var script = document.createElement('script');
    script.src = 'https://assets.calendly.com/assets/external/widget.js';
    script.async = true;
    script.onload = function () {
      var conteneur = document.createElement('div');
      conteneur.className = 'calendly-inline';
      bloc.insertBefore(conteneur, bloc.firstChild);
      window.Calendly.initInlineWidget({ url: url + (url.indexOf('?') === -1 ? '?' : '&') + 'hide_gdpr_banner=1&primary_color=2b4db8', parentElement: conteneur, resize: true });
    };
    document.body.appendChild(script);
  })();

  // ---------- Formulaires : envoi au webhook ----------
  function serialiser(form) {
    var donnees = {};
    var fd = new FormData(form);
    fd.forEach(function (valeur, cle) {
      if (donnees[cle] !== undefined) {
        if (!Array.isArray(donnees[cle])) { donnees[cle] = [donnees[cle]]; }
        donnees[cle].push(valeur);
      } else {
        donnees[cle] = valeur;
      }
    });
    donnees.page = location.href.split('#')[0];
    return donnees;
  }

  function envoyer(form, donnees, bouton, message) {
    var webhook = document.body.getAttribute('data-webhook');
    var texteInitial = bouton ? bouton.textContent : '';
    if (bouton) { bouton.disabled = true; bouton.textContent = 'Envoi en cours…'; }
    message.hidden = true;
    return fetch(webhook, { method: 'POST', mode: 'cors', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(donnees) })
      .then(function (r) { if (!r.ok) { throw new Error('http ' + r.status); } return r.json(); })
      .then(function () {
        var merci = form.getAttribute('data-merci') || 'merci.html';
        var params = new URLSearchParams();
        if (donnees.prenom) { params.set('prenom', donnees.prenom); }
        if (donnees.type) { params.set('type', donnees.type); }
        location.href = merci + (params.toString() ? '?' + params.toString() : '');
      })
      .catch(function () {
        if (bouton) { bouton.disabled = false; bouton.textContent = texteInitial; }
        message.hidden = false;
        var wa = 'https://wa.me/41798587217?text=' + encodeURIComponent('Bonjour, je n\'ai pas réussi à envoyer ma demande depuis le site. ' + (donnees.voyage ? 'Voyage : ' + donnees.voyage + '. ' : ''));
        message.innerHTML = 'L\'envoi n\'a pas abouti. Vous pouvez réessayer dans un instant, ou <a href="' + wa + '">nous écrire sur WhatsApp</a>. Rien n\'est perdu : vos réponses restent dans le formulaire.';
      });
  }

  (function formulairesSimples() {
    document.querySelectorAll('form[data-envoi]').forEach(function (form) {
      var message = form.querySelector('.message-envoi');
      if (!message) {
        message = document.createElement('p');
        message.className = 'message-envoi';
        message.hidden = true;
        form.appendChild(message);
      }
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!form.reportValidity()) { return; }
        var donnees = serialiser(form);
        donnees.type = form.getAttribute('data-envoi');
        envoyer(form, donnees, form.querySelector('[type="submit"]'), message);
      });
    });
  })();

  // ---------- Devis en étapes ----------
  (function devis() {
    var form = document.querySelector('form.etapes-devis');
    if (!form) { return; }
    var etapes = Array.prototype.slice.call(form.querySelectorAll('.bloc-etape'));
    var courante = 0;
    var progression = document.querySelector('.progression-devis');
    var message = form.querySelector('.message-envoi');

    // pré-remplissage depuis l'URL (?voyage=, ?envie=, ?etape=)
    var params = new URLSearchParams(location.search);
    var champVoyage = form.querySelector('[name="voyage"]');
    var chip = document.querySelector('.devis-contexte');
    var titres = {
      'sur-les-routes-du-maroc': 'Sur les routes du Maroc', 'villes-imperiales': 'Villes impériales millénaires', 'nord-sud': 'Du Nord au Sud',
      'eclipse-petit-groupe': 'Éclipse solaire et trésors impériaux, petit groupe', 'eclipse-prive': 'Éclipse solaire et trésors impériaux, en privé',
      'marrakech-prive': 'Marrakech privé', 'bien-etre-skoura': 'Bien-être dans la palmeraie de Skoura'
    };
    var envies = { 'desert-et-dunes': 'Désert et dunes', 'villes-imperiales': 'Villes impériales', 'marrakech': 'Marrakech', 'nord-et-chefchaouen': 'Nord et Chefchaouen', 'en-famille': 'En famille', 'voyage-de-noces': 'Voyage de noces', 'bien-etre': 'Bien-être', 'eclipse': 'Éclipse 2027' };
    if (params.get('voyage') && titres[params.get('voyage')]) {
      champVoyage.value = titres[params.get('voyage')];
      if (chip) { chip.hidden = false; chip.querySelector('span').textContent = titres[params.get('voyage')]; }
    }
    if (params.get('envie') && envies[params.get('envie')]) {
      var case_ = form.querySelector('input[name="envies"][value="' + envies[params.get('envie')] + '"]');
      if (case_) { case_.checked = true; }
    }
    if (params.get('etape')) {
      var etapesChamp = form.querySelector('[name="etapes"]');
      if (etapesChamp && !etapesChamp.value) { etapesChamp.value = params.get('etape'); }
      var radioOui = form.querySelector('input[name="a_des_etapes"][value="oui"]');
      if (radioOui) { radioOui.checked = true; }
    }

    function afficher(i) {
      courante = Math.max(0, Math.min(etapes.length - 1, i));
      etapes.forEach(function (bloc, k) { bloc.hidden = k !== courante; });
      if (progression) {
        progression.querySelectorAll('li').forEach(function (li, k) {
          li.classList.toggle('active', k === courante);
          li.classList.toggle('faite', k < courante);
          if (k === courante) { li.setAttribute('aria-current', 'step'); } else { li.removeAttribute('aria-current'); }
        });
      }
      if (courante > 0) { etapes[courante].scrollIntoView({ behavior: 'smooth', block: 'start' }); }
      var premier = etapes[courante].querySelector('input, select, textarea');
      if (premier && courante > 0) { premier.focus({ preventScroll: true }); }
    }

    function valider(i) {
      var champs = etapes[i].querySelectorAll('input, select, textarea');
      for (var k = 0; k < champs.length; k++) {
        if (!champs[k].checkValidity()) { champs[k].reportValidity(); return false; }
      }
      return true;
    }

    etapes.forEach(function (bloc, i) {
      var barre = document.createElement('div');
      barre.className = 'groupe-boutons etape-navigation';
      if (i > 0) {
        var prec = document.createElement('button');
        prec.type = 'button'; prec.className = 'btn btn-secondaire'; prec.textContent = 'Précédent';
        prec.addEventListener('click', function () { afficher(i - 1); });
        barre.appendChild(prec);
      }
      if (i < etapes.length - 1) {
        var suiv = document.createElement('button');
        suiv.type = 'button'; suiv.className = 'btn btn-principal'; suiv.textContent = 'Suivant';
        suiv.addEventListener('click', function () { if (valider(i)) { afficher(i + 1); } });
        barre.appendChild(suiv);
      } else {
        var env = document.createElement('button');
        env.type = 'submit'; env.className = 'btn btn-principal'; env.textContent = 'Envoyer ma demande';
        barre.appendChild(env);
      }
      bloc.appendChild(barre);
    });

    if (progression) {
      progression.querySelectorAll('li').forEach(function (li, k) {
        li.addEventListener('click', function () { if (k <= courante || valider(courante)) { afficher(k); } });
      });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!valider(courante)) { return; }
      var donnees = serialiser(form);
      donnees.type = 'voyageur';
      envoyer(form, donnees, form.querySelector('[type="submit"]'), message);
    });

    afficher(0);
  })();

  // ---------- Page merci : prénom ----------
  (function merci() {
    var el = document.querySelector('[data-prenom]');
    if (!el) { return; }
    var p = new URLSearchParams(location.search).get('prenom');
    if (p) { el.textContent = 'Merci ' + p + ','; }
  })();

  // ---------- Cartes Leaflet ----------
  window.initialiserCartes = function () {
    if (typeof L === 'undefined') { return; }
    document.querySelectorAll('.carte-voyage').forEach(function (el) {
      if (el.getAttribute('data-initialisee')) { return; }
      el.setAttribute('data-initialisee', '1');
      var etapes = JSON.parse(el.getAttribute('data-etapes') || '[]');
      if (!etapes.length) { return; }
      var carte = L.map(el, { scrollWheelZoom: false, zoomControl: true, attributionControl: true });
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' }).addTo(carte);
      var points = etapes.map(function (e) { return [e.lat, e.lng]; });
      if (points.length > 1 && el.getAttribute('data-ligne') !== 'false') {
        L.polyline(points, { color: '#D93640', weight: 3, opacity: .85, dashArray: '6 6' }).addTo(carte);
      }
      var deja = {};
      etapes.forEach(function (e, i) {
        var cle = e.lat + ',' + e.lng;
        var numero = deja[cle] ? deja[cle] + ' · ' + (i + 1) : String(i + 1);
        deja[cle] = numero;
        var numerote = etapes.length > 1 && el.getAttribute('data-ligne') !== 'false';
        var icone = L.divIcon({ className: 'marqueur-etape', html: '<span>' + (numerote ? (i + 1) : '') + '</span>', iconSize: [26, 26], iconAnchor: [13, 13] });
        var m = L.marker([e.lat, e.lng], { icon: icone, keyboard: false }).addTo(carte);
        m.bindTooltip(e.nom, { permanent: etapes.length <= 10, direction: el.getAttribute('data-direction') || 'right', offset: (el.getAttribute('data-direction') === 'top') ? [0, -14] : [14, 0], className: 'etiquette-etape' });
      });
      var zoom = parseInt(el.getAttribute('data-zoom'), 10);
      if (points.length === 1) {
        carte.setView(points[0], zoom || 9);
      } else {
        carte.fitBounds(L.latLngBounds(points), { padding: [28, 28] });
      }
    });
  };
  if (typeof L !== 'undefined') { window.initialiserCartes(); }
})();
