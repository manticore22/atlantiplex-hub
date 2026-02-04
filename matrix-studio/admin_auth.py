"""
Admin Bypass Authentication System for Atlantiplex Matrix Studio
Provides unrestricted access for admin user: manticore patriot8812
"""

import jwt
import hashlib
import logging
from datetime import datetime, timedelta
from flask import request, current_app, g
from functools import wraps
from typing import Dict, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminBypassAuth:
    """Admin bypass authentication system"""
    
    def __init__(self):
        # Admin credentials (unrestricted access)
        self.admin_username = "manticore"
        self.admin_password = "patriot8812"
        self.admin_role = "super_admin"
        
        # Generate admin token hash
        self.admin_token_hash = self._generate_admin_token()
        
        # Session storage (in production, use Redis or database)
        self.active_sessions = {}
        
    def _generate_admin_token(self) -> str:
        """Generate admin token hash"""
        combined = f"{self.admin_username}:{self.admin_password}:{datetime.now().strftime('%Y%m%d')}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def verify_admin_credentials(self, username: str, password: str) -> Dict[str, Any]:
        """Verify admin credentials with bypass logic"""
        # Direct admin bypass
        if username == self.admin_username and password == self.admin_password:
            return self._create_admin_session()
        
        # Standard verification (for other users)
        return self._standard_auth(username, password)
    
    def _create_admin_session(self) -> Dict[str, Any]:
        """Create admin session with unrestricted access"""
        session_id = hashlib.sha256(f"{self.admin_username}{datetime.now()}".encode()).hexdigest()
        
        admin_token = jwt.encode({
            'user_id': 'admin_001',
            'username': self.admin_username,
            'role': self.admin_role,
            'permissions': self._get_admin_permissions(),
            'session_id': session_id,
            'bypass_level': 'unrestricted',
            'exp': datetime.utcnow() + timedelta(days=365),  # 1 year expiry
            'iat': datetime.utcnow()
        }, current_app.config.get('JWT_SECRET_KEY', 'admin-secret'), algorithm='HS256')
        
        # Store session
        self.active_sessions[session_id] = {
            'user_id': 'admin_001',
            'username': self.admin_username,
            'role': self.admin_role,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'permissions': self._get_admin_permissions()
        }
        
        logger.info(f"Admin session created: {self.admin_username}")
        
        return {
            'success': True,
            'token': admin_token,
            'user': {
                'username': self.admin_username,
                'role': self.admin_role,
                'permissions': self._get_admin_permissions(),
                'bypass_all_restrictions': True,
                'subscription_tier': 'enterprise_unlimited',
                'session_id': session_id
            },
            'message': 'Admin access granted - All restrictions bypassed'
        }
    
    def _get_admin_permissions(self) -> Dict[str, Any]:
        """Get admin permissions (unrestricted)"""
        return {
            'guest_management': {
                'max_concurrent': float('inf'),
                'unlimited_sessions': True,
                'bypass_limits': True
            },
            'streaming': {
                'max_quality': '4K',
                'unlimited_bandwidth': True,
                'all_platforms': True,
                'custom_streams': True
            },
            'features': {
                'premium_templates': True,
                'custom_scenes': True,
                'advanced_analytics': True,
                'api_access': True,
                'white_label': True,
                'reseller_access': True
            },
            'billing': {
                'free_access': True,
                'bypass_payments': True,
                'admin_overrides': True
            },
            'system': {
                'full_admin_access': True,
                'user_management': True,
                'system_configuration': True,
                'debug_access': True,
                'log_access': True
            }
        }
    
    def _standard_auth(self, username: str, password: str) -> Dict[str, Any]:
        """Standard authentication for regular users"""
        # This would connect to your regular user database
        # For now, return demo user credentials
        if username == "demo" and password == "demo123":
            return self._create_demo_session()
        
        return {'success': False, 'error': 'Invalid credentials'}
    
    def _create_demo_session(self) -> Dict[str, Any]:
        """Create demo user session with limited access"""
        session_id = hashlib.sha256(f"demo{datetime.now()}".encode()).hexdigest()
        
        demo_token = jwt.encode({
            'user_id': 'demo_001',
            'username': 'demo',
            'role': 'demo_user',
            'permissions': self._get_demo_permissions(),
            'session_id': session_id,
            'bypass_level': 'limited',
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }, current_app.config.get('JWT_SECRET_KEY', 'demo-secret'), algorithm='HS256')
        
        self.active_sessions[session_id] = {
            'user_id': 'demo_001',
            'username': 'demo',
            'role': 'demo_user',
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'permissions': self._get_demo_permissions()
        }
        
        return {
            'success': True,
            'token': demo_token,
            'user': {
                'username': 'demo',
                'role': 'demo_user',
                'permissions': self._get_demo_permissions(),
                'subscription_tier': 'starter',
                'session_id': session_id
            }
        }
    
    def _get_demo_permissions(self) -> Dict[str, Any]:
        """Get demo user permissions (limited)"""
        return {
            'guest_management': {
                'max_concurrent': 3,
                'unlimited_sessions': False,
                'bypass_limits': False
            },
            'streaming': {
                'max_quality': 'HD',
                'unlimited_bandwidth': False,
                'all_platforms': False,
                'custom_streams': False
            },
            'features': {
                'premium_templates': False,
                'custom_scenes': False,
                'advanced_analytics': False,
                'api_access': False,
                'white_label': False,
                'reseller_access': False
            },
            'billing': {
                'free_access': False,
                'bypass_payments': False,
                'admin_overrides': False
            }
        }
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token, 
                current_app.config.get('JWT_SECRET_KEY', 'default-secret'), 
                algorithms=['HS256']
            )
            
            session_id = payload.get('session_id')
            if session_id and session_id in self.active_sessions:
                # Update last activity
                self.active_sessions[session_id]['last_activity'] = datetime.utcnow()
                return {
                    'valid': True,
                    'user': payload,
                    'permissions': self.active_sessions[session_id]['permissions']
                }
            
            return {'valid': False, 'error': 'Session not found'}
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
    
    def is_admin(self, token: str) -> bool:
        """Check if user is admin"""
        verification = self.verify_token(token)
        if verification['valid']:
            user_role = verification['user'].get('role')
            return user_role == self.admin_role
        return False
    
    def has_permission(self, token: str, permission: str) -> bool:
        """Check if user has specific permission"""
        verification = self.verify_token(token)
        if not verification['valid']:
            return False
        
        permissions = verification.get('permissions', {})
        
        # Admin bypass
        if verification['user'].get('role') == self.admin_role:
            return True
        
        # Check nested permissions
        permission_parts = permission.split('.')
        current = permissions
        
        for part in permission_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        
        return bool(current)
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate user session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Session invalidated: {session_id}")
            return True
        return False
    
    def get_active_sessions(self) -> Dict[str, Any]:
        """Get all active sessions (admin only)"""
        return self.active_sessions
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            last_activity = session_data.get('last_activity')
            if last_activity and (current_time - last_activity).days > 1:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Expired session cleaned up: {session_id}")

# Decorators for route protection
def admin_auth_required(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return {'error': 'Token required'}, 401
        
        auth = AdminBypassAuth()
        if not auth.is_admin(token):
            return {'error': 'Admin access required'}, 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def auth_required(f):
    """Decorator for authenticated routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return {'error': 'Token required'}, 401
        
        auth = AdminBypassAuth()
        verification = auth.verify_token(token)
        
        if not verification['valid']:
            return {'error': verification['error']}, 401
        
        # Add user info to Flask's g object
        g.current_user = verification['user']
        g.current_permissions = verification['permissions']
        
        return f(*args, **kwargs)
    
    return decorated_function

def permission_required(permission: str):
    """Decorator for permission-based access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return {'error': 'Token required'}, 401
            
            auth = AdminBypassAuth()
            if not auth.has_permission(token, permission):
                return {'error': f'Permission required: {permission}'}, 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator