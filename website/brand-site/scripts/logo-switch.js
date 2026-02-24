// Logo switcher: supports spiral, seraphonix, sovereign, atlantiplex
(function(){
  try {
    const url = new URL(window.location.href);
    const which = (url.searchParams.get('logo') || 'spiral').toLowerCase();
    const logos = ['logo-spiral', 'logo-seraphonix', 'logo-sovereign', 'logo-atlantiplex'];
    logos.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = (id === `logo-${which}`) ? 'block' : 'none';
    });
  } catch(e) {
    // ignore
  }
})();
