(function(){
  const routes = ['overview','playground','docs','a11y'];
  const btns = document.querySelectorAll('.gateway .sidebar .nav-btn');
  const sections = {
    overview: document.getElementById('overview'),
    playground: document.getElementById('playground'),
    docs: document.getElementById('docs'),
    a11y: document.getElementById('a11y')
  };
  function show(route){
    routes.forEach(r => {
      const sec = sections[r];
      if (sec) sec.style.display = (r === route) ? 'block' : 'none';
    });
    btns.forEach(b => b.classList.toggle('active', b.getAttribute('data-route') === route));
  }

  function initPlayground(){
    const grid = document.getElementById('playground-grid');
    if (!grid) return;
    // Lightweight component explorer similar to before, but here as HTML blocks
    const addSection = (title, content) => {
      const wrap = document.createElement('div');
      wrap.className = 'panel';
      const h = document.createElement('h2'); h.textContent = title; h.style.fontSize = '1rem';
      const p = document.createElement('p'); p.textContent = content;
      wrap.appendChild(h); wrap.appendChild(p);
      grid.appendChild(wrap);
    };
    grid.innerHTML = '';
    addSection('Panel', 'A glassy, glass-like panel surface.');
    addSection('Glyph Divider', 'Decorative Atlantean glyphs divider.');
    addSection('Status Badges', 'Ok, Info, and Warn badges.');
    addSection('List Row', 'Row with primary, secondary, and trailing content.');
    addSection('Telemetry', 'Inline chart placeholder.');
  }

  // wire navigation
  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      const route = btn.getAttribute('data-route');
      location.hash = '/'+route;
      show(route);
    });
  });

  window.addEventListener('hashchange', () => {
    const h = location.hash.replace('#/','') || 'overview';
    show(h);
  }, false);

  // initial
  const initial = location.hash.replace('#/','') || 'overview';
  show(initial);
  initPlayground();
})();
