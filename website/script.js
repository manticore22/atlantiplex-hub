// Atlantiplex - Seraphonix Studios
// JavaScript for Interactivity

document.addEventListener('DOMContentLoaded', function() {
    createBubbles();
    initParallax();
});

/**
 * Generate animated bubbles rising from bottom
 */
function createBubbles() {
    const bubblesContainer = document.querySelector('.bubbles');
    if (!bubblesContainer) return;
    
    const bubbleCount = 25;
    
    for (let i = 0; i < bubbleCount; i++) {
        const bubble = document.createElement('div');
        bubble.classList.add('bubble');
        
        // Random properties
        const size = Math.random() * 30 + 10;
        const left = Math.random() * 100;
        const duration = Math.random() * 12 + 8;
        const delay = Math.random() * 10;
        const randomVal = Math.random();
        
        bubble.style.width = `${size}px`;
        bubble.style.height = `${size}px`;
        bubble.style.left = `${left}vw`;
        bubble.style.animationDuration = `${duration}s`;
        bubble.style.animationDelay = `${delay}s`;
        bubble.style.setProperty('--random', randomVal);
        
        bubblesContainer.appendChild(bubble);
    }
}

/**
 * Parallax scrolling effect for lore page
 */
function initParallax() {
    const parallaxSections = document.querySelectorAll('.parallax-section');
    
    if (parallaxSections.length === 0) return;
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        
        parallaxSections.forEach((section, index) => {
            const speed = 0.3 + (index * 0.1);
            const bg = section.querySelector('.parallax-bg');
            if (bg) {
                bg.style.transform = `translateY(${scrolled * speed}px)`;
            }
        });
    });
}

/**
 * Open contact modal
 */
function openModal() {
    const modal = document.getElementById('contact-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Focus first input for accessibility
        setTimeout(() => {
            const firstInput = modal.querySelector('input');
            if (firstInput) firstInput.focus();
        }, 100);
    }
}

/**
 * Close contact modal
 */
function closeModal(event) {
    // If called with event, check if it's the overlay click
    if (event && event.target !== event.currentTarget && !event.target.classList.contains('modal-close')) {
        return;
    }
    
    const modal = document.getElementById('contact-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

/**
 * Handle form submission
 */
function handleSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Get form values
    const name = formData.get('name');
    const email = formData.get('email');
    const message = formData.get('message');
    
    // Log to console (in production, send to backend)
    console.log('Form submitted:', { name, email, message });
    
    // Show success message
    alert(`🌊 Thank you, ${name}! Your message has been sent into the depths. We'll resurface with a reply soon!`);
    
    // Close modal and reset form
    closeModal();
    form.reset();
}

/**
 * Add to cart functionality
 */
function addToCart(productName, price) {
    // Create a bubble effect
    showAddToCartFeedback(productName);
    
    // Log cart action
    console.log(`Added to cart: ${productName} - $${price}`);
}

/**
 * Show visual feedback when adding to cart
 */
function showAddToCartFeedback(productName) {
    // Create floating notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, rgba(0, 31, 63, 0.95), rgba(0, 116, 217, 0.9));
        color: white;
        padding: 25px 40px;
        border-radius: 20px;
        z-index: 1000;
        text-align: center;
        animation: popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
        border: 2px solid rgba(127, 219, 255, 0.5);
    `;
    
    notification.innerHTML = `
        <div style="font-size: 3rem; margin-bottom: 10px;">🫧</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: var(--aqua);">Added to Cart!</div>
        <div style="margin-top: 5px; opacity: 0.9;">${productName}</div>
    `;
    
    document.body.appendChild(notification);
    
    // Add animation keyframes dynamically
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes popIn {
                0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
                70% { transform: translate(-50%, -50%) scale(1.1); }
                100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
            }
            @keyframes popOut {
                0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
                100% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Remove after delay
    setTimeout(() => {
        notification.style.animation = 'popOut 0.3s ease-in forwards';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 1500);
}

/**
 * Smooth scroll for navigation
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ESC key closes modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Add ripple effect to social orbs on click
document.querySelectorAll('.social-orb').forEach(orb => {
    orb.addEventListener('click', function(e) {
        // Ripple effect is handled by CSS animation
        console.log('Social link clicked:', this.getAttribute('aria-label'));
    });
});
