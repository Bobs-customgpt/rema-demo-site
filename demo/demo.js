/* CustomGPT.ai agents for the ReMA demo site:
   1. floating chat bubble (chat.js)
   2. header search -> Search Generative Experience results card (sge.js) */
(function () {
  var cfg = window.DEMO_CONFIG || {};
  var params = new URLSearchParams(location.search);

  /* ---------- AI search (SGE) ---------- */
  var sge = { pid: cfg.sge_p_id || '', pkey: cfg.sge_p_key || '', div: cfg.sge_div_id || 'customgpt_chat' };
  var panel = document.getElementById('sgePanel');
  var desktop = document.getElementById('cgptSearch');
  var desktopForm = desktop ? desktop.querySelector('form') : null;
  // ReMA's own search field inside the phone/tablet menu
  var mobileForm = document.querySelector('.kb-search247_34ff9c-2b form');
  var seq = 0;
  var anchor = null;

  function visible(el) { if (!el) return false; var r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; }

  function place() {
    if (!panel || panel.hidden) return;
    var vw = document.documentElement.clientWidth;
    var w = Math.min(720, vw - 32);
    var left, top;
    if (anchor && visible(anchor)) {
      var r = anchor.getBoundingClientRect();
      left = Math.min(Math.max(16, r.right - w), vw - 16 - w);
      top = r.bottom + 12;
    } else {
      // phone/tablet: drop the card under the purple header pill
      var bar = document.querySelector('.wp-block-kadence-off-canvas-trigger');
      var head = bar ? bar.closest('.kadence-header-row-inner') || bar : null;
      var hr = head && visible(head) ? head.getBoundingClientRect() : { bottom: 90 };
      w = vw - 32; left = 16; top = hr.bottom + 14;
    }
    panel.style.width = w + 'px';
    panel.style.left = (left + window.scrollX) + 'px';
    panel.style.top = (top + window.scrollY) + 'px';
  }

  function close() {
    if (!panel) return;
    panel.hidden = true;
    if (desktop) desktop.classList.remove('is-open');
  }

  function run(q, from) {
    q = (q || '').trim();
    if (!q || !panel || !sge.pid || !sge.pkey) return;
    anchor = from || null;
    [desktopForm, mobileForm].forEach(function (f) { var i = f && f.querySelector('input'); if (i) i.value = q; });
    document.getElementById('sgeQuery').textContent = q;
    panel.hidden = false;
    if (desktop && anchor === desktopForm) desktop.classList.add('is-open');
    place();

    var host = document.getElementById(sge.div);
    var loading = document.getElementById('sgeLoading');
    host.innerHTML = '';
    loading.hidden = false;
    loading.innerHTML = '<span class="sge-panel__spinner"></span> Searching recycledmaterials.org&hellip;';
    // keep the query shareable in the URL (no reload)
    try { var u = new URL(location.href); u.searchParams.set('q', q); history.replaceState(null, '', u.toString()); } catch (e) {}

    // sge.js reads its options from its script tag and renders an iframe into div_id, so re-inject it per search
    var mine = ++seq;
    var prev = document.getElementById('sgeScript');
    if (prev) prev.remove();
    var s = document.createElement('script');
    s.id = 'sgeScript';
    s.src = 'https://cdn.customgpt.ai/js/sge.js?v=' + mine;
    s.defer = true;
    s.setAttribute('div_id', sge.div);
    s.setAttribute('p_id', sge.pid);
    s.setAttribute('p_key', sge.pkey);
    s.setAttribute('prompt', q);
    s.setAttribute('height', '100%');
    s.onerror = function () { if (mine === seq) loading.innerHTML = 'The AI search could not be loaded. Check your connection and try again.'; };
    document.body.appendChild(s);

    // hide the loading veil once the results iframe has loaded
    var obs = new MutationObserver(function () {
      var f = host.querySelector('iframe');
      if (!f) return;
      obs.disconnect();
      var done = function () { if (mine === seq) loading.hidden = true; };
      f.addEventListener('load', done);
      setTimeout(done, 6000);
    });
    obs.observe(host, { childList: true, subtree: true });
    setTimeout(function () {
      if (mine === seq && !host.querySelector('iframe')) loading.innerHTML = 'No response from the search agent yet. Try again or use the chat bubble.';
    }, 12000);
  }

  if (panel) {
    if (desktopForm) {
      desktopForm.addEventListener('submit', function (e) { e.preventDefault(); run(desktopForm.querySelector('input').value, desktopForm); });
      var reopen = function () {
        // reopen the last result when the same query is still in the box
        var hasResult = document.querySelector('#' + sge.div + ' iframe');
        if (panel.hidden && hasResult && this.value.trim() === document.getElementById('sgeQuery').textContent) {
          anchor = desktopForm; panel.hidden = false; desktop.classList.add('is-open'); place();
        }
      };
      desktopForm.querySelector('input').addEventListener('focus', reopen);
      desktopForm.querySelector('input').addEventListener('click', reopen);
    }
    if (mobileForm) {
      var badge = document.createElement('span');
      badge.className = 'cgpt-mobile-ai'; badge.textContent = 'AI'; badge.setAttribute('aria-hidden', 'true');
      var wrap = mobileForm.querySelector('.kb-search-input-wrapper');
      if (wrap) { wrap.style.position = 'relative'; wrap.appendChild(badge); }
      mobileForm.setAttribute('action', '#');
      mobileForm.addEventListener('submit', function (e) {
        e.preventDefault();
        var q = mobileForm.querySelector('input').value;
        var x = document.querySelector('.kb-off-canvas-close');
        if (x && visible(x)) x.click();
        setTimeout(function () { run(q, null); }, 250);
      });
    }
    document.getElementById('sgeClose').addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) close(); });
    document.addEventListener('click', function (e) {
      if (!panel.hidden && !panel.contains(e.target) && !e.target.closest('.cgpt-search, .kb-search')) close();
    });
    window.addEventListener('resize', place);

    var q0 = params.get('q') || params.get('s') || params.get('query') || params.get('search');
    if (q0) window.addEventListener('load', function () { run(q0, visible(desktopForm) ? desktopForm : null); });
  }

  /* ---------- floating chat ---------- */
  var pid = params.get('p_id') || cfg.p_id || '';
  var pkey = params.get('p_key') || cfg.p_key || '';
  if (!pid || !pkey) return;
  var c = document.createElement('script');
  c.src = 'https://cdn.customgpt.ai/js/chat.js';
  c.defer = true;
  c.onload = function () {
    if (window.CustomGPT && typeof window.CustomGPT.init === 'function') {
      window.CustomGPT.init({ p_id: pid, p_key: pkey });
    }
  };
  document.body.appendChild(c);
})();
