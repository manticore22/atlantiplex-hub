/**
 * Command Centre Authentication Module
 * 
 * Verifies admin/CEO access for the Command Centre
 */

const jwt = require('jsonwebtoken');

// JWT Secret (should match the one used in main auth)
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

/**
 * Verify JWT token and check for Command Centre access
 * @param {string} token - JWT token
 * @returns {Promise<Object>} User object if authorized
 */
async function verifyCommandCentreAccess(token) {
  try {
    // Verify the token
    const decoded = jwt.verify(token, JWT_SECRET);
    
    // Check if user has admin privileges
    // This integrates with your existing auth system
    const allowedRoles = ['super_admin', 'org_owner', 'org_admin', 'manticore_controller'];
    
    if (!decoded.role || !allowedRoles.includes(decoded.role)) {
      console.log(`[CommandCentre] Access denied for role: ${decoded.role}`);
      return null;
    }
    
    return {
      id: decoded.sub || decoded.id,
      username: decoded.username || decoded.email,
      role: decoded.role,
      isAdmin: true,
      organizationId: decoded.organization_id || decoded.orgId
    };
  } catch (error) {
    console.error('[CommandCentre] Token verification failed:', error.message);
    return null;
  }
}

/**
 * Middleware for Express routes
 * Requires admin access
 */
function requireCommandCentreAccess(req, res, next) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ 
      error: 'Authentication required',
      message: 'Bearer token required'
    });
  }
  
  const token = authHeader.substring(7);
  
  verifyCommandCentreAccess(token)
    .then(user => {
      if (!user) {
        return res.status(403).json({ 
          error: 'Access denied',
          message: 'Insufficient permissions for Command Centre'
        });
      }
      
      req.user = user;
      next();
    })
    .catch(error => {
      console.error('[CommandCentre] Auth error:', error);
      res.status(500).json({ 
        error: 'Authentication error',
        message: 'Failed to verify access'
      });
    });
}

/**
 * Check if user role has command centre access
 * @param {string} role - User role
 * @returns {boolean}
 */
function hasCommandCentreAccess(role) {
  const allowedRoles = ['super_admin', 'org_owner', 'org_admin', 'manticore_controller'];
  return allowedRoles.includes(role);
}

module.exports = {
  verifyCommandCentreAccess,
  requireCommandCentreAccess,
  hasCommandCentreAccess
};