// Lightweight static catalog with Stripe Payment Links (to be swapped with real Checkout later)
(function(){
  const products = [
    { id: 'rp-01', name: 'Telemetry Analysis Pack', price: 14900, url: 'https://buy.stripe.com/test_XXXXXXXXXXXXXXXX', description: 'Advanced telemetry data analysis for oceanic systems.' },
    { id: 'cr-01', name: 'Custom Robot Script', price: 8999, url: 'https://buy.stripe.com/test_XXXXXXXXXXXXXXXX', description: 'Tailored automation script for your submersible.' },
    { id: 'cs-01', name: 'Consultation Session', price: 19999, url: 'https://buy.stripe.com/test_XXXXXXXXXXXXXXXX', description: 'One-hour strategy consultation with our engineers.' },
  ];
  const grid = document.getElementById('shop-grid');
  if (!grid) return;
  products.forEach(p => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <h3>${p.name}</h3>
      <p style="color:#cdeaf6;">${p.description}</p>
      <p style="font-weight:600;">$${(p.price/100).toFixed(2)}</p>
      <a href="${p.url}" target="_blank" class="buy">Buy</a>
    `;
    grid.appendChild(card);
  });
})();
