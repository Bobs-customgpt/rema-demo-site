/* Loads the CustomGPT.ai floating chat agent for the ReMA demo site. */
(function () {
  var cfg = window.DEMO_CONFIG || {};
  var params = new URLSearchParams(location.search);
  var pid = params.get('p_id') || cfg.p_id || '';
  var pkey = params.get('p_key') || cfg.p_key || '';
  if (!pid || !pkey) return;

  var s = document.createElement('script');
  s.src = 'https://cdn.customgpt.ai/js/chat.js';
  s.defer = true;
  s.onload = function () {
    if (window.CustomGPT && typeof window.CustomGPT.init === 'function') {
      window.CustomGPT.init({ p_id: pid, p_key: pkey });
    }
  };
  document.body.appendChild(s);
})();
