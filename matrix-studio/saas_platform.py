"""
Atlantiplex Lightning Studio - Enterprise Multi-Tenant SaaS Platform
Complete SaaS transformation with organization management, billing, and security
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, g, render_template_string, redirect, url_for
from functools import wraps

# Import SaaS components
from saas_multi_tenant import MultiTenantManager, Organization, Team, TeamMember, UserRole, SubscriptionStatus
from saas_database import SaaSDatabaseManager
from saas_middleware import TenantMiddleware, tenant_required, tenant_permission_required, get_current_tenant
from saas_dashboard import SaaSDashboard
from stripe_payments import StripePaymentManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AtlantiplexSaaS:
    """Enterprise Multi-Tenant SaaS Platform"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.getenv('SECRET_KEY', 'saas-secret-key-change-in-production')
        
        # Configure app settings FIRST
        self.app.config.update({
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': True,
            'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,  # 50MB
            'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY', 'sk_test_demo_key'),
            'STRIPE_PUBLISHABLE_KEY': os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_demo_key'),
        })
        
        # Initialize components within app context
        with self.app.app_context():
            self.db = SaaSDatabaseManager()
            self.tenant_manager = MultiTenantManager()
            self.dashboard = SaaSDashboard(self.db)
            self.payment_manager = StripePaymentManager()
        
        # Configure tenant middleware
        self.tenant_middleware = TenantMiddleware(self.app, self.db)
        self.app.wsgi_app = self.tenant_middleware
        
        self._register_routes()
        self._register_error_handlers()
        
        logger.info("START: Atlantiplex SaaS Platform Initialized")
    
    def _register_routes(self):
        """Register all SaaS routes"""
        
        @self.app.route('/')
        def index():
            """Landing page"""
            if get_current_tenant():
                return redirect(url_for('dashboard'))
            return render_template_string('''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Atlantiplex Lightning Studio - Enterprise SaaS Platform</title>
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
                    <style>
                        body {
                            font-family: 'Inter', sans-serif;
                            background: linear-gradient(135deg, #0a0f1b 0%, #1a2942 50%, #0a0f1b 100%);
                            color: #eaf6ff;
                            margin: 0;
                            padding: 0;
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        }
                        .container {
                            text-align: center;
                            max-width: 600px;
                            padding: 40px;
                        }
                        .logo {
                            width: 120px;
                            height: 120px;
                            margin-bottom: 30px;
                            filter: drop-shadow(0 0 20px rgba(255, 235, 59, 0.3));
                        }
                        h1 {
                            font-size: 2.5rem;
                            font-weight: 700;
                            margin-bottom: 10px;
                            background: linear-gradient(135deg, #1e3c72, #2a5298);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            background-clip: text;
                            text-fill-color: transparent;
                        }
                        .subtitle {
                            font-size: 1.2rem;
                            color: #b8c5d6;
                            margin-bottom: 40px;
                        }
                        .auth-buttons {
                            display: flex;
                            gap: 20px;
                            justify-content: center;
                            flex-wrap: wrap;
                        }
                        .btn {
                            padding: 15px 30px;
                            border: none;
                            border-radius: 8px;
                            font-size: 1rem;
                            font-weight: 600;
                            cursor: pointer;
                            transition: all 0.3s ease;
                            text-decoration: none;
                            display: inline-block;
                        }
                        .btn-primary {
                            background: linear-gradient(135deg, #1e3c72, #2a5298);
                            color: white;
                            box-shadow: 0 4px 20px rgba(30, 60, 114, 0.4);
                        }
                        .btn-primary:hover {
                            transform: translateY(-2px);
                            box-shadow: 0 8px 30px rgba(30, 60, 114, 0.6);
                        }
                        .btn-secondary {
                            background: rgba(255, 255, 255, 0.1);
                            color: #eaf6ff;
                            border: 1px solid rgba(255, 255, 255, 0.2);
                        }
                        .btn-secondary:hover {
                            background: rgba(255, 255, 255, 0.2);
                            border-color: #ffeb3b;
                        }
                        .features {
                            text-align: left;
                            margin: 40px 0;
                            padding: 30px;
                            background: rgba(255, 255, 255, 0.05);
                            border-radius: 12px;
                            border: 1px solid rgba(255, 255, 255, 0.1);
                        }
                        .feature {
                            margin-bottom: 15px;
                        }
                        .feature-title {
                            font-weight: 600;
                            color: #ffeb3b;
                            margin-bottom: 5px;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <img src="/static/atlantiplex-lightning-logo.svg" alt="Atlantiplex Lightning Studio" class="logo">
                        <h1>Atlantiplex Lightning Studio</h1>
                        <p class="subtitle">Enterprise Multi-Tenant SaaS Platform</p>
                        
                        <div class="auth-buttons">
                            <a href="/login" class="btn btn-primary">Sign In</a>
                            <a href="/signup" class="btn btn-secondary">Create Organization</a>
                        </div>
                        
                        <div class="features">
                            <div class="feature">
                                <div class="feature-title">🏢 Multi-Tenant Architecture</div>
                                <div>Complete organization isolation with subdomain access</div>
                            </div>
                            <div class="feature">
                                <div class="feature-title">👥 Team Management</div>
                                <div>Hierarchical teams with role-based permissions</div>
                            </div>
                            <div class="feature">
                                <div class="feature-title">💰 Enterprise Billing</div>
                                <div>Usage-based billing with consolidated invoicing</div>
                            </div>
                            <div class="feature">
                                <div class="feature-title">📊 Advanced Analytics</div>
                                <div>Real-time usage metrics and organization insights</div>
                            </div>
                            <div class="feature">
                                <div class="feature-title">🔒 Enterprise Security</div>
                                <div>SSO, MFA, audit logging, compliance</div>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
            ''')
        
        @self.app.route('/dashboard')
        @tenant_required
        def dashboard():
            """Main dashboard for logged-in tenants"""
            org = get_current_tenant()
            if not org:
                return redirect(url_for('index'))
                
            dashboard_data = self.dashboard.get_dashboard_stats(org['id'])
            return render_template_string('''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{{ org.name }} - Dashboard</title>
                    <style>
                        body {
                            font-family: 'Inter', sans-serif;
                            background: linear-gradient(135deg, #0a0f1b 0%, #1a2942 50%, #0a0f1b 100%);
                            color: #eaf6ff;
                            margin: 0;
                            padding: 20px;
                        }
                        .header {
                            background: rgba(255, 255, 255, 0.05);
                            padding: 20px;
                            border-radius: 12px;
                            margin-bottom: 20px;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                        }
                        .org-name {
                            font-size: 1.5rem;
                            font-weight: 700;
                            color: #ffeb3b;
                        }
                        .stats-grid {
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                            gap: 20px;
                            margin-bottom: 20px;
                        }
                        .stat-card {
                            background: rgba(255, 255, 255, 0.05);
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            border-radius: 12px;
                            padding: 20px;
                            text-align: center;
                        }
                        .stat-number {
                            font-size: 2rem;
                            font-weight: 700;
                            color: #ffeb3b;
                            margin-bottom: 5px;
                        }
                        .stat-label {
                            color: #b8c5d6;
                            font-size: 0.9rem;
                        }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <div class="org-name">{{ org.name }}</div>
                        <div>{{ org.subdomain }}.atlantiplex.com</div>
                    </div>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{{ stats.users }}</div>
                            <div class="stat-label">Active Users</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{{ stats.teams }}</div>
                            <div class="stat-label">Teams</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{{ stats.active_streams }}</div>
                            <div class="stat-label">Active Streams</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{{ stats.storage_used_gb }}GB</div>
                            <div class="stat-label">Storage Used</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{{ stats.api_calls }}</div>
                            <div class="stat-label">API Calls</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{{ stats.stream_hours }}h</div>
                            <div class="stat-label">Stream Hours</div>
                        </div>
                    </div>
                </body>
                </html>
            ''', org=org, stats=dashboard_data['stats'])
        
        @self.app.route('/api/organizations', methods=['POST'])
        def create_organization():
            """Create new organization/tenant"""
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['name', 'domain', 'subdomain', 'billing_email']
                for field in required_fields:
                    if not data.get(field):
                        return jsonify({'error': f'{field} is required'}), 400
                
                # Check if subdomain is available
                existing = self.db.get_organization_by_subdomain(data['subdomain'])
                if existing:
                    return jsonify({'error': 'Subdomain already taken'}), 409
                
                # Create organization
                org_id = self.db.create_organization(data)
                
                # Create initial admin team
                team_data = {
                    'organization_id': org_id,
                    'name': 'Administrators',
                    'description': 'Organization administrators team'
                }
                team_id = self.db.create_team(team_data)
                
                # Add creating user as admin (would normally come from registration)
                # For demo, we'll create a placeholder admin user
                logger.info(f"🏢 Organization created: {data['name']} ({org_id})")
                
                return jsonify({
                    'organization_id': org_id,
                    'message': 'Organization created successfully',
                    'subdomain': f"{data['subdomain']}.atlantiplex.com"
                }), 201
                
            except Exception as e:
                logger.error(f"❌ Error creating organization: {str(e)}")
                return jsonify({'error': 'Failed to create organization'}), 500
        
        @self.app.route('/api/super-admin')
        def super_admin():
            """Super admin dashboard for managing all tenants"""
            try:
                if not request.args.get('admin_key') or request.args.get('admin_key') != 'super-admin-key':
                    return jsonify({'error': 'Unauthorized'}), 401
                
                overview = self.dashboard.generate_super_admin_overview()
                return jsonify(overview)
                
            except Exception as e:
                logger.error(f"❌ Super admin error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'Atlantiplex Lightning Studio SaaS',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0'
            })
    
    def _register_error_handlers(self):
        """Register error handlers"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Resource not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"❌ Internal server error: {str(error)}")
            return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.errorhandler(401)
        def unauthorized(error):
            return jsonify({'error': 'Unauthorized access'}), 401
        
        @self.app.errorhandler(403)
        def forbidden(error):
            return jsonify({'error': 'Access forbidden'}), 403
    
    def run(self, host='0.0.0.0', port=8080, debug=False):
        """Run the SaaS application"""
        logger.info(f"🚀 Starting Atlantiplex SaaS Platform on {host}:{port}")
        logger.info(f"🌐 Access: http://{host}:{port}")
        logger.info(f"🏢 Multi-tenant architecture enabled")
        logger.info(f"📊 SaaS dashboard available")
        logger.info(f"💰 Enterprise billing system active")
        logger.info(f"🔒 Security and compliance features enabled")
        logger.info("================================================")
        
        self.app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    # Environment configuration
    environment = os.getenv('FLASK_ENV', 'development')
    
    saas = AtlantiplexSaaS()
    
    if environment == 'production':
        saas.run(host='0.0.0.0', port=8080, debug=False)
    else:
        saas.run(host='127.0.0.1', port=8080, debug=True)