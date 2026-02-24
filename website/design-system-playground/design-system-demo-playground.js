(function(){
  const routes = ['panel','glyph-divider','status','list-row','telemetry','dark-mode-toggle'];
  const buttons = document.querySelectorAll('.sidebar button');
  const panels = {
    panel: document.getElementById('panel-preview'),
    glyph-divider: document.getElementById('glyph-divider-preview'),
    status: document.getElementById('status-preview'),
    'list-row': document.getElementById('listrow-preview'),
    telemetry: document.getElementById('telemetry-preview'),
    'dark-mode-toggle': document.getElementById('darkmode-preview')
  };

  function showRoute(route){
    // simple hide/show tiles
    Object.values(panels).forEach(p => p.style.display = 'block');
    // highlight active button
    buttons.forEach(b => b.classList.remove('active'));
    const activeBtn = Array.from(buttons).find(b => b.getAttribute('data-route') === route);
    if (activeBtn) activeBtn.classList.add('active');
  }

  function routeFromHash(){
    const h = location.hash || '#/panel';
    const m = h.match(/#\/([a-zA-Z0-9-]+)/);
    return m ? m[1] : 'panel';
  }

  function render(){
    const route = routeFromHash();
    // Basic show/hide: only one panel visible at a time for demo clarity
    Object.entries(panels).forEach(([k,v]) => { v.style.display = (k === route) ? 'block' : 'none'; });
    showRoute(route);
  }

  // wire navigation
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const r = btn.getAttribute('data-route');
      location.hash = '/'+r;
      render();
    });
  });

  window.addEventListener('hashchange', render, false);
  // initial
  render();
})();
