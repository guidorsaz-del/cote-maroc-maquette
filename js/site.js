// Menu mobile : un seul comportement, ouvrir et fermer la navigation.
(function () {
  var bouton = document.querySelector('.menu-bouton');
  var nav = document.getElementById('nav-principal');
  if (!bouton || !nav) { return; }

  function ouvrir(etat) {
    bouton.setAttribute('aria-expanded', etat ? 'true' : 'false');
    nav.classList.toggle('ouvert', etat);
    document.body.classList.toggle('menu-ouvert', etat);
    if (etat) { nav.querySelector('a').focus(); } else { bouton.focus(); }
  }

  bouton.addEventListener('click', function () {
    ouvrir(bouton.getAttribute('aria-expanded') !== 'true');
  });

  nav.addEventListener('click', function (e) {
    if (e.target.closest('a') && nav.classList.contains('ouvert')) { ouvrir(false); }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && nav.classList.contains('ouvert')) { ouvrir(false); }
  });

  var mq = window.matchMedia('(min-width: 900px)');
  mq.addEventListener('change', function (ev) { if (ev.matches) { ouvrir(false); } });
})();
