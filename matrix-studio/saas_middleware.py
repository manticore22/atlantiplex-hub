"""
SaaS Tenant Middleware for Multi-Tenant Atlantiplex Lightning Studio
Enterprise-grade tenant routing and context management
"""

import logging
from typing import Dict, Optional, Callable, Any
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenantContext:
    """Tenant context for multi-tenant requests"""
    
    def __init__(self):
        self.organization_id = None
        self.organization = None
        self.user_id = None
        self.user_role = None
        self.permissions = []
        self.subdomain = None
        self.domain = None

    def set_tenant(self, organization_id: str, organization: Dict[str, Any]):
        """Set current tenant context"""
        self.organization_id = organization_id
        self.organization = organization
        logger.info(f"🏢 Tenant context set: {organization.get('name', 'Unknown')} ({organization_id})")
    
    def clear_tenant(self):
        """Clear tenant context"""
        self.organization_id = None
        self.organization = None
        self.user_id = None
        self.user_role = None
        self.permissions = []
        logger.info("🧹 Tenant context cleared")

class TenantMiddleware:
    """Multi-tenant middleware for Flask applications"""
    
    def __init__(self, app, saas_db):
        self.app = app
        self.saas_db = saas_db
        self.current_context = TenantContext()
        
    def extract_tenant_from_request(self, request) -> Optional[str]:
        """Extract tenant identifier from request"""
        # Method 1: Subdomain
        host = request.headers.get('Host', request.host.split(':')[0])
        if host:
            parts = host.split('.')
            if len(parts) >= 2 and parts[0] != 'www' and parts[0] != 'app':
                return parts[0]
        
        # Method 2: Header
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            return tenant_id
            
        # Method 3: Custom header
        tenant_id = request.headers.get('X-Organization-ID')
        if tenant_id:
            return tenant_id
            
        return None
    
    def load_tenant_context(self, organization_id: str) -> bool:
        """Load tenant context from database"""
        try:
            from saas_database import SaaSDatabaseManager
            
            # Get organization by ID
            cursor = self.saas_db.connection.cursor()
            cursor.execute("""
                SELECT * FROM organizations 
                WHERE id = ? AND tenant_status = 'active'
            """, (organization_id,))
            
            row = cursor.fetchone()
            if row:
                org = dict(row)
                self.current_context.set_tenant(organization_id, org)
                return True
            else:
                logger.warning(f"⚠️ Organization not found: {organization_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error loading tenant context: {str(e)}")
            return False
    
    def __call__(self, environ, start_response):
        """WSGI middleware interface"""
        # Import Flask request
        try:
            from flask import request, g
            
            # Create request context
            with self.app.app_context():
                # Extract tenant from request
                tenant_id = self.extract_tenant_from_request(request)
                
                if tenant_id:
                    # Load tenant context
                    if self.load_tenant_context(tenant_id):
                        # Set tenant in Flask globals
                        g.tenant_id = tenant_id
                        g.organization = self.current_context.organization
                        g.tenant_context = self.current_context
                        logger.info(f"🏢 Tenant loaded: {tenant_id}")
                    else:
                        logger.warning(f"⚠️ Failed to load tenant: {tenant_id}")
                        g.tenant_id = None
                        g.organization = None
                        g.tenant_context = None
                else:
                    # Default/shared context
                    g.tenant_id = None
                    g.organization = None
                    g.tenant_context = self.current_context
                
                return start_response(environ)
                
        except Exception as e:
            logger.error(f"❌ Middleware error: {str(e)}")
            return start_response(environ)

def tenant_required(f: Callable) -> Callable:
    """Decorator to require tenant context"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import g, request, jsonify
        
        if not hasattr(g, 'tenant_id') or not g.tenant_id:
            logger.warning(f"⚠️ Tenant required for: {request.endpoint}")
            return jsonify({'error': 'Tenant context required'}), 400
        
        return f(*args, **kwargs)
    
    return decorated_function

def tenant_permission_required(permission: str) -> Callable:
    """Decorator to require specific tenant permission"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import g, request, jsonify
            
            if not hasattr(g, 'tenant_context') or not g.tenant_context:
                return jsonify({'error': 'Tenant context required'}), 401
                
            user_permissions = g.tenant_context.permissions
            if permission not in user_permissions:
                logger.warning(f"⚠️ Permission denied: {permission} for user")
                return jsonify({'error': f'Permission {permission} required'}), 403
                
            return f(*args, **kwargs)
        
        return decorator
    
    return decorator

def tenant_role_required(role: str) -> Callable:
    """Decorator to require specific tenant role"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import g, request, jsonify
            
            if not hasattr(g, 'tenant_context') or not g.tenant_context:
                return jsonify({'error': 'Tenant context required'}), 401
                
            user_role = g.tenant_context.user_role
            if user_role != role:
                logger.warning(f"⚠️ Role required: {role}, current: {user_role}")
                return jsonify({'error': f'Role {role} required'}), 403
                
            return f(*args, **kwargs)
        
        return decorator
    
    return decorator

def get_current_tenant() -> Optional[Dict[str, Any]]:
    """Get current tenant organization"""
    try:
        from flask import g
        return g.organization if hasattr(g, 'organization') else None
    except:
        return None

def get_tenant_setting(setting_key: str, default: Any = None) -> Any:
    """Get tenant-specific setting"""
    tenant = get_current_tenant()
    if not tenant:
        return default
        
    try:
        from saas_database import SaaSDatabaseManager
        
        db = SaaSDatabaseManager()
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT setting_value FROM organization_settings 
            WHERE organization_id = ? AND setting_key = ?
        """, (tenant['id'], setting_key))
        
        row = cursor.fetchone()
        if row:
            import json
            return json.loads(row['setting_value']) if row['setting_value'].startswith('{') else row['setting_value']
        
        return default
        
    except Exception as e:
        logger.error(f"❌ Error getting tenant setting: {str(e)}")
        return default

def check_tenant_permission(permission: str) -> bool:
    """Check if current user has tenant permission"""
    try:
        from flask import g
        
        if not hasattr(g, 'tenant_context') or not g.tenant_context:
            return False
            
        return permission in g.tenant_context.permissions
        
    except:
        return False

def get_tenant_resource_limit(resource: str, default: Any = None) -> Any:
    """Get tenant resource limit"""
    tenant = get_current_tenant()
    if not tenant:
        return default
        
    limits = tenant.get('resource_limits', {})
    if isinstance(limits, str):
        import json
        limits = json.loads(limits)
        
    return limits.get(resource, default)

def log_tenant_action(action: str, resource_type: str = None, resource_id: str = None,
                   success: bool = True, details: Dict[str, Any] = None):
    """Log action in tenant context"""
    try:
        from flask import g, request
        
        tenant_id = getattr(g, 'tenant_id', None)
        user_id = getattr(g, 'tenant_context', {}).user_id if hasattr(g, 'tenant_context') else None
        
        if tenant_id and user_id:
            from saas_database import SaaSDatabaseManager
            
            db = SaaSDatabaseManager()
            db.log_audit_event(
                organization_id=tenant_id,
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                success=success,
                error_message=details.get('error') if details else None
            )
            
    except Exception as e:
        logger.error(f"❌ Error logging tenant action: {str(e)}")