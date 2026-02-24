// Interactive shop: fetch prices and support free/paid paths
(async function(){
  const grid = document.getElementById('shop-grid');
  const emailInput = document.getElementById('customer-email');
  const checkoutBtn = document.getElementById('checkout-btn');
  const freeBtn = document.getElementById('free-btn');

  function renderPrices(prices){
    grid.innerHTML = '';
    prices.forEach(p => {
      const card = document.createElement('div');
      card.style.padding = '12px';
      card.style.borderRadius = '8px';
      card.style.border = '1px solid rgba(128,210,255,.25)';
      const title = document.createElement('div'); title.style.fontWeight = '600'; title.style.marginBottom='6px'; title.textContent = p.name;
      const desc = document.createElement('div'); desc.style.color = '#cdeaf6'; desc.style.fontSize = '0.92rem'; desc.style.marginBottom = '6px'; desc.textContent = p.description;
      const price = document.createElement('div'); price.style.fontFamily = 'Monospace'; price.style.fontSize = '0.9rem'; price.style.marginBottom = '6px';
      price.textContent = p.free ? 'Free' : '$' + (p.price/100).toFixed(2) + (p.interval ? ' / ' + p.interval : '');
      const cbWrap = document.createElement('label'); cbWrap.style.display = 'block';
      const cb = document.createElement('input'); cb.type = 'checkbox'; cb.dataset.priceid = p.priceId; cb.dataset.free = p.free ? 'true' : 'false'; cbWrap.appendChild(cb); cbWrap.appendChild(document.createTextNode(' Select'));
      card.appendChild(title); card.appendChild(desc); card.appendChild(price); card.appendChild(cbWrap);
      grid.appendChild(card);
    });
  }

  async function loadPrices(){
    try {
      const r = await fetch('/prices');
      if (!r.ok) return [];
      return await r.json();
    } catch (e) {
      return [];
    }
  }

  const prices = await loadPrices();
  if (prices.length) renderPrices(prices);

  checkoutBtn?.addEventListener('click', async () => {
    if (!emailInput) return;
    const email = emailInput.value;
    const selected = Array.from(grid.querySelectorAll('input[type="checkbox"]:checked')).map(i => i.dataset.priceid).filter(id => id);
    if (!selected.length) return alert('Select at least one item.');
    const resp = await fetch('/create-checkout-session', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ priceIds: selected, customer_email: email })
    });
    const data = await resp.json();
    if (data.url) window.location = data.url;
    else if (data.free) window.location = '/account?email=' + encodeURIComponent(email);
    else alert('Checkout initiation failed');
  });

  freeBtn?.addEventListener('click', async () => {
    if (!emailInput) return;
    const email = emailInput.value;
    const freeSelected = Array.from(grid.querySelectorAll('input[type="checkbox"][data-free="true"]:checked')).map(i => i.dataset.priceid);
    if (!freeSelected.length) return alert('Select a free item to activate access.');
    const resp = await fetch('/create-checkout-session', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ priceIds: freeSelected, customer_email: email })
    });
    const data = await resp.json();
    if (data.free) window.location = '/account?email=' + encodeURIComponent(email); else if (data.url) window.location = data.url; else alert('Failed to activate access');
  });
})();
