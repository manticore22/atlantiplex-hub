// SERAPHONIX — Shop Client
// Handles product display and subscription management

// Product data (loaded from backend)
let products = [];

// Load products from API
async function loadProducts() {
    try {
        const res = await fetch('/api/products');
        if (res.ok) {
            products = await res.json();
            return products;
        }
    } catch (e) {
        console.error('Failed to load products:', e);
    }
    return [];
}

// Render products on homepage
async function renderProducts() {
    const grid = document.getElementById('modules-grid');
    if (!grid) return;

    const products = await loadProducts();
    
    grid.innerHTML = products.map(product => `
        <div class="module-card ${product.status}" data-product="${product.id}">
            <div class="module-icon">◇</div>
            <h3 class="module-title">${product.name}</h3>
            <p class="module-desc">${product.description}</p>
            <div class="module-status ${product.status}">${product.status.toUpperCase()}</div>
        </div>
    `).join('');

    // Add click handlers
    grid.querySelectorAll('.module-card').forEach(card => {
        card.addEventListener('click', () => {
            const productId = card.dataset.product;
            handleProductClick(productId);
        });
    });
}

// Handle product click
function handleProductClick(productId) {
    const product = products.find(p => p.id === productId);
    
    if (!product) return;

    if (product.status === 'coming-soon') {
        return; // Do nothing for coming soon
    }

    // Check authentication
    if (!window.SeraphonixAuth.isAuthenticated()) {
        window.location.href = '/login.html?redirect=' + encodeURIComponent('/?product=' + productId);
        return;
    }

    // Check subscription and redirect to product or membership
    window.SeraphonixAuth.checkSubscription().then(sub => {
        if (sub && sub.tier === product.requiredTier) {
            window.location.href = '/product/' + productId + '.html';
        } else {
            window.location.href = '/membership.html?product=' + productId;
        }
    });
}

// Create checkout session
async function createCheckoutSession(tier) {
    const token = window.SeraphonixAuth.getToken();
    
    const res = await fetch('/api/stripe/create-checkout-session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ tier })
    });

    const data = await res.json();
    
    if (data.url) {
        window.location.href = data.url;
    } else {
        alert('Error initiating checkout');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Only render products on homepage
    if (document.getElementById('modules-grid')) {
        await renderProducts();
    }
});

// Export
window.SeraphonixShop = {
    loadProducts,
    renderProducts,
    createCheckoutSession
};
