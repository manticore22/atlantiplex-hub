// Tiny enhancement script for the brand site
document.addEventListener('DOMContentLoaded', () => {
  // Simple active-nav highlighting on scroll
  const sections = Array.from(document.querySelectorAll('section[id]'));
  const navLinks = Array.from(document.querySelectorAll('.main-nav a'));
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      const id = e.target.id;
      const link = document.querySelector('.main-nav a[href="#'+id+'"]');
      if (e.isIntersecting) {
        navLinks.forEach(l => l.classList.remove('active'));
        if (link) link.classList.add('active');
      }
    });
  }, { rootMargin: '-40% 0px -50% 0px', threshold: 0.01 });
  sections.forEach(s => observer.observe(s));
});
