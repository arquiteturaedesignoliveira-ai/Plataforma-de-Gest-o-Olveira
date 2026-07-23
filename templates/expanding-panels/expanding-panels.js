/* ==========================================================================
   Expanding Panels — helpers opcionais
   --------------------------------------------------------------------------
   O CSS sozinho já entrega o componente. Este arquivo oferece duas formas
   convenientes de gerar o markup:

   1) expandingPanels(items, opts)  -> string HTML
      Ideal para apps que montam a UI por template string (ex.: Sistema
      Oliveira, que faz el.innerHTML = ...). Basta concatenar o retorno.

   2) <expanding-panels>  (Custom Element, light DOM)
      Drop-in para qualquer site/app. Configure via atributo `items` (JSON)
      ou via <script type="application/json"> filho. Injeta o CSS uma vez.

   `items` é uma lista de objetos:
     { title, desc, img, href, ariaLabel, arrow }
       title     (obrigatório) texto do título
       desc      texto que aparece no hover/foco
       img       URL da imagem de fundo (qualquer valor CSS de background-image)
       href      se presente, o card vira <a href>; senão vira <button>
       ariaLabel rótulo acessível (padrão: title)
       arrow     mostra a seta circular (padrão: true)
   ========================================================================== */
(function (root) {
  "use strict";

  var ARROW =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<circle cx="12" cy="12" r="9"/><path d="M9 12h6M13 9l3 3-3 3"/></svg>';

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  /** Gera o HTML de um único card. */
  function cardHTML(item) {
    var tag = item.href ? "a" : "button";
    var attrs = 'class="xp-card"';
    if (item.img) attrs += ' style="--xp-img:url(&quot;' + esc(item.img) + '&quot;)"';
    if (item.href) attrs += ' href="' + esc(item.href) + '"';
    else attrs += ' type="button"';
    attrs += ' aria-label="' + esc(item.ariaLabel || item.title) + '"';

    var arrow = item.arrow === false ? "" : ARROW;
    var desc = item.desc
      ? '<span class="xp-desc">' + esc(item.desc) + "</span>"
      : "";

    return (
      "<" + tag + " " + attrs + ">" +
        '<span class="xp-body">' +
          '<span class="xp-title">' + esc(item.title) + arrow + "</span>" +
          desc +
        "</span>" +
      "</" + tag + ">"
    );
  }

  /**
   * Gera o HTML completo do grupo de painéis.
   * @param {Array} items
   * @param {Object} [opts] { theme:'warm'|'', className, style }
   * @returns {string}
   */
  function expandingPanels(items, opts) {
    opts = opts || {};
    var cls = "xp-cards";
    if (opts.theme) cls += " xp--" + opts.theme;
    if (opts.className) cls += " " + opts.className;
    var style = opts.style ? ' style="' + esc(opts.style) + '"' : "";
    return (
      '<div class="' + cls + '"' + style + ">" +
      (items || []).map(cardHTML).join("") +
      "</div>"
    );
  }

  /* ---- injeta a folha de estilo uma vez (usado pelo Custom Element) ---- */
  var STYLE_ID = "xp-styles";
  function ensureStyles(href) {
    if (document.getElementById(STYLE_ID)) return;
    var link = document.createElement("link");
    link.id = STYLE_ID;
    link.rel = "stylesheet";
    // resolve o CSS ao lado deste script, salvo se `href` for informado
    link.href = href || cssHref();
    document.head.appendChild(link);
  }
  function cssHref() {
    try {
      var s = document.currentScript ||
        document.querySelector('script[src*="expanding-panels.js"]');
      if (s && s.src) return s.src.replace(/expanding-panels\.js.*$/, "expanding-panels.css");
    } catch (e) {}
    return "expanding-panels.css";
  }

  /* ---- Custom Element <expanding-panels> (light DOM, adota o tema do host) ---- */
  if (typeof HTMLElement !== "undefined" && "customElements" in (root || {})) {
    var XP = function () { return Reflect.construct(HTMLElement, [], XP); };
    XP.prototype = Object.create(HTMLElement.prototype);
    XP.prototype.constructor = XP;

    XP.prototype.connectedCallback = function () {
      if (this.getAttribute("no-style") === null) ensureStyles(this.getAttribute("css"));
      var items = this._readItems();
      if (items) {
        this.innerHTML = expandingPanels(items, { theme: this.getAttribute("theme") });
      }
      // se já vier com markup .xp-cards pronto, apenas garante o CSS.
    };

    XP.prototype._readItems = function () {
      var raw = this.getAttribute("items");
      if (!raw) {
        var s = this.querySelector('script[type="application/json"]');
        raw = s && s.textContent;
      }
      if (!raw) return null;
      try { return JSON.parse(raw); }
      catch (e) { console.warn("<expanding-panels> items JSON inválido:", e); return null; }
    };

    if (!customElements.get("expanding-panels")) {
      try { customElements.define("expanding-panels", XP); } catch (e) {}
    }
  }

  /* ---- exports ---- */
  var api = { expandingPanels: expandingPanels, cardHTML: cardHTML, ensureStyles: ensureStyles };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) { root.expandingPanels = expandingPanels; root.ExpandingPanels = api; }
})(typeof window !== "undefined" ? window : this);
