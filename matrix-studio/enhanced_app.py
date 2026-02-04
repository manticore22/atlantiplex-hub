"""
Enhanced Main Application with Payment Integration
Combines Matrix Studio with Stripe payments and admin bypass
"""

from flask import Flask, request, jsonify
import logging
import os
from datetime import datetime

# Import payment integration modules
from admin_auth import AdminBypassAuth, auth_required, admin_auth_required
from stripe_payments import StripePaymentManager
from subscription_manager import TierManager, SubscriptionTier
from database_payments import DatabaseManager
from payment_api import register_payment_routes

# Import existing Matrix Studio components
# from app import MatrixStudioApp  # Your existing main app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMatrixStudio:
    """Enhanced Matrix Studio with payment integration"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_config()
        self.init_managers()
        self.register_routes()
    
    def setup_config(self):
        """Setup Flask configuration"""
        self.app.config.update({
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'matrix-studio-secret-key'),
            'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key'),
            'STRIPE_SECRET_KEY': os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...'),
            'STRIPE_WEBHOOK_SECRET': os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_...'),
            'DATABASE_URL': os.environ.get('DATABASE_URL', 'sqlite:///matrix_studio.db'),
            'HOST': os.environ.get('HOST', '0.0.0.0'),
            'PORT': int(os.environ.get('PORT', 8081))
        })
    
    def init_managers(self):
        """Initialize all managers"""
        with self.app.app_context():
            self.auth_manager = AdminBypassAuth()
            self.payment_manager = StripePaymentManager()
            self.tier_manager = TierManager()
            self.db_manager = DatabaseManager()
            
            # Store managers in app context for route access
            self.app.config['auth_manager'] = self.auth_manager
            self.app.config['payment_manager'] = self.payment_manager
            self.app.config['tier_manager'] = self.tier_manager
            self.app.config['db_manager'] = self.db_manager
    
    def register_routes(self):
        """Register all routes"""
        # Register payment routes
        register_payment_routes(self.app)
        
        # Register existing Matrix Studio routes
        self.register_matrix_routes()
        
        # Health check
        @self.app.route('/api/health')
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '2.0.0',
                'features': {
                    'payments': self.payment_manager.stripe_available,
                    'admin_bypass': True,
                    'subscriptions': True
                }
            })
        
        # Landing page with payment info
        @self.app.route('/')
        def landing():
            return jsonify({
                'message': 'Atlantiplex Matrix Studio - Enhanced with Payments',
                'features': [
                    'Professional broadcasting studio',
                    'Guest management',
                    'Multi-platform streaming',
                    'Subscription-based pricing',
                    'Admin bypass access',
                    'Payment processing via Stripe'
                ],
                'login': {
                    'admin': {'username': 'manticore', 'note': 'Unlimited access - patriot8812'},
                    'demo': {'username': 'demo', 'password': 'demo123'}
                },
                'api_endpoints': {
                    'auth': '/api/auth/login',
                    'subscriptions': '/api/subscriptions/tiers',
                    'payments': '/api/payments/checkout',
                    'health': '/api/health'
                }
            })
    
    def register_matrix_routes(self):
        """Register existing Matrix Studio routes with payment integration"""
        
        @self.app.route('/api/guests', methods=['GET', 'POST'])
        @auth_required
        def manage_guests():
            """Manage guests with subscription limits"""
            user_id = request.environ.get('current_user_id')
            tier = self.tier_manager.get_user_tier(user_id)
            
            # Check guest limits
            if request.method == 'POST':
                current_guests = len(self.db_manager.get_active_guest_sessions(int(user_id) if user_id.isdigit() else 1))
                max_guests = self.tier_manager.tier_configs[tier]['features']['guest_management']['max_concurrent']
                
                if current_guests >= max_guests:
                    return jsonify({
                        'error': 'Guest limit reached',
                        'current': current_guests,
                        'limit': max_guests,
                        'upgrade_required': True
                    }), 402  # Payment Required
            
            # Process guest request
            return jsonify({
                'message': 'Guest management',
                'tier': tier.value,
                'max_guests': self.tier_manager.tier_configs[tier]['features']['guest_management']['max_concurrent']
            })
        
        @self.app.route('/api/streaming/start', methods=['POST'])
        @auth_required
        def start_streaming():
            """Start streaming with quality limits"""
            user_id = request.environ.get('current_user_id')
            tier = self.tier_manager.get_user_tier(user_id)
            
            data = request.get_json() or {}
            requested_quality = data.get('quality', 'SD')
            max_quality = self.tier_manager.tier_configs[tier]['features']['streaming']['max_quality']
            
            # Quality validation
            quality_hierarchy = ['SD', 'HD', 'Full HD', '4K', '4K+']
            if quality_hierarchy.index(requested_quality) > quality_hierarchy.index(max_quality):
                return jsonify({
                    'error': f'Quality {requested_quality} not available in {tier.value} tier',
                    'max_quality': max_quality,
                    'upgrade_required': True
                }), 402
            
            return jsonify({
                'message': 'Streaming started',
                'quality': requested_quality,
                'tier': tier.value
            })
        
        @self.app.route('/api/scenes', methods=['GET', 'POST'])
        @auth_required
        def manage_scenes():
            """Manage scenes with feature limits"""
            user_id = request.environ.get('current_user_id')
            tier = self.tier_manager.get_user_tier(user_id)
            
            tier_config = self.tier_manager.tier_configs[tier]
            features = tier_config['features']
            
            return jsonify({
                'available_features': {
                    'basic_scenes': features.get('basic_scenes', False),
                    'premium_scenes': features.get('premium_scenes', False),
                    'custom_scenes': features.get('custom_scenes', False)
                },
                'tier': tier.value,
                'upgrade_options': self.tier_manager.get_upgrade_options(user_id)
            })
    
    def run(self):
        """Run the enhanced application"""
        logger.info("Starting Enhanced Matrix Studio with Payment Integration")
        logger.info("Admin bypass enabled - Login: manticore / patriot8812")
        logger.info("Demo login - Login: demo / demo123")
        
        self.app.run(
            host=self.app.config['HOST'],
            port=self.app.config['PORT'],
            debug=os.environ.get('DEBUG', 'False').lower() == 'true'
        )

# Standalone execution
if __name__ == '__main__':
    app = EnhancedMatrixStudio()
    app.run()