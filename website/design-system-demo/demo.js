(function(){
  const toggle = document.getElementById('themeToggle');
  const root = document.documentElement;

  function applyTheme(next){
    root.setAttribute('data-ds-theme', next);
  }

  // Initialize from localStorage if present
  const saved = localStorage.getItem('ds-theme');
  const initial = saved || 'deep';
  applyTheme(initial === 'deep' ? 'deep' : 'glow');

  if (toggle) {
    toggle.addEventListener('click', () => {
      const current = root.getAttribute('data-ds-theme') || 'deep';
      const next = current === 'deep' ? 'glow' : 'deep';
      applyTheme(next);
      localStorage.setItem('ds-theme', next);
    });
  }
})();
