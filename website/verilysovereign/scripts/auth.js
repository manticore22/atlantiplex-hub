// SERAPHONIX — Auth Client
// Handles authentication state across the site

const AUTH_TOKEN_KEY = 'seraphonix_token';
const AUTH_USER_KEY = 'seraphonix_user';

// Check if user is authenticated
function isAuthenticated() {
    return !!localStorage.getItem(AUTH_TOKEN_KEY);
}

// Get current user
function getCurrentUser() {
    const userStr = localStorage.getItem(AUTH_USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
}

// Get auth token
function getToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

// Logout
function logout() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    window.location.href = '/';
}

// Update nav based on auth state
function updateNavAuth() {
    const navAuth = document.querySelector('.nav-auth');
    if (!navAuth) return;

    if (isAuthenticated()) {
        const user = getCurrentUser();
        navAuth.innerHTML = `
            <span class="user-greeting">${user?.email || 'OPERATIVE'}</span>
            <a href="#" class="nav-btn btn-logout" onclick="logout(); return false;">LOGOUT</a>
        `;
    }
}

// Protect page - redirect to login if not authenticated
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login.html?redirect=' + encodeURIComponent(window.location.pathname);
        return false;
    }
    return true;
}

// Check subscription status
async function checkSubscription() {
    const token = getToken();
    if (!token) return null;

    try {
        const res = await fetch('/api/user/subscription', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (res.ok) {
            return await res.json();
        }
    } catch (e) {
        console.error('Subscription check failed:', e);
    }
    return null;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateNavAuth();
});

// Export for use in other scripts
window.SeraphonixAuth = {
    isAuthenticated,
    getCurrentUser,
    getToken,
    logout,
    requireAuth,
    checkSubscription
};
