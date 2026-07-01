(function () {
  'use strict';

  var CONSENT_KEY = 'cookie_consent';
  // Replace with your GA4 Measurement ID (e.g. 'G-ABC1234567')
  var GA_ID = 'G-XXXXXXXXXX';

  function getCookie(name) {
    var m = document.cookie.match('(?:^|;\\s*)' + name + '=([^;]*)');
    return m ? decodeURIComponent(m[1]) : null;
  }

  function setCookie(name, value, days) {
    var expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = name + '=' + encodeURIComponent(value) +
      '; expires=' + expires + '; path=/; SameSite=Lax';
  }

  function loadGA() {
    if (!GA_ID || GA_ID === 'G-XXXXXXXXXX') return;
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', GA_ID);
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
  }

  function hideBanner() {
    var el = document.getElementById('cookie-banner');
    if (!el) return;
    el.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
    el.style.transform = 'translateY(100%)';
    el.style.opacity = '0';
    setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 320);
  }

  window.__cookieAcceptAll = function () {
    setCookie(CONSENT_KEY, 'all', 365);
    loadGA();
    hideBanner();
  };

  window.__cookieEssential = function () {
    setCookie(CONSENT_KEY, 'essential', 365);
    hideBanner();
  };

  // Apply existing consent on every page load
  var existing = getCookie(CONSENT_KEY);
  if (existing === 'all') { loadGA(); }
  if (existing) return;

  // Determine relative prefix (works on GitHub Pages subpath and custom domain)
  var _inSubdir = /\/(articulos|categorias)\//.test(window.location.pathname);
  var _cookiesHref = (_inSubdir ? '../' : '') + 'cookies.html';

  // No stored consent — show banner
  var banner = document.createElement('div');
  banner.id = 'cookie-banner';
  banner.setAttribute('role', 'dialog');
  banner.setAttribute('aria-label', 'Aviso de cookies');
  banner.innerHTML =
    '<div class="cookie-banner-inner">' +
      '<p>🍪 Usamos cookies de analítica (Google Analytics) para mejorar el sitio. ' +
      '<a href="' + _cookiesHref + '">Política de cookies</a>.</p>' +
      '<div class="cookie-banner-btns">' +
        '<button class="cookie-btn cookie-btn-secondary" onclick="__cookieEssential()">Solo técnicas</button>' +
        '<button class="cookie-btn cookie-btn-primary" onclick="__cookieAcceptAll()">Aceptar todas</button>' +
      '</div>' +
    '</div>';
  document.body.appendChild(banner);

  // Newsletter / email form — show success state on submit
  function initForms() {
    document.querySelectorAll('.newsletter-form, .email-form').forEach(function (form) {
      if (form.dataset.nlInit) return;
      form.dataset.nlInit = '1';
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var input = form.querySelector('input[type="email"]');
        var btn = form.querySelector('button[type="submit"]');
        if (btn) {
          btn.textContent = '✓ ¡Apuntado!';
          btn.disabled = true;
          btn.style.background = '#10b981';
          btn.style.backgroundImage = 'none';
        }
        if (input) input.disabled = true;
        // TODO: Add your newsletter provider embed code here
        // Mailchimp: https://mailchimp.com/help/add-a-signup-form-to-your-website/
        // Brevo:     https://www.brevo.com/features/signup-forms/
        // ConvertKit: https://developers.kit.com/docs/subscriber-forms
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initForms);
  } else {
    initForms();
  }

}());
