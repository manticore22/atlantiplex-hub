"""
Simple Enhanced Matrix Studio - Working Version
Combines basic Matrix Studio with admin bypass and payment structure
"""

from flask import Flask, request, jsonify, g
import jwt
import hashlib
import logging
from datetime import datetime, timedelta
import sqlite3
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMatrixStudio:
    """Simple Matrix Studio with admin bypass"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'matrix-studio-secret-key'
        self.app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
        
        self.init_database()
        self.register_routes()
    
    def init_database(self):
        """Initialize simple database"""
        self.db_path = "matrix_studio_simple.db"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    tier TEXT DEFAULT 'free',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS guest_sessions (
                    id INTEGER PRIMARY KEY,
                    host_user_id INTEGER,
                    guest_name TEXT,
                    invite_code TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create admin user
            cursor = conn.execute("SELECT id FROM users WHERE username = ?", ("manticore",))
            if not cursor.fetchone():
                conn.execute(
                    "INSERT INTO users (username, password, role, tier) VALUES (?, ?, ?, ?)",
                    ("manticore", "patriot8812", "admin", "unlimited")
                )
            
            # Create demo user
            cursor = conn.execute("SELECT id FROM users WHERE username = ?", ("demo",))
            if not cursor.fetchone():
                conn.execute(
                    "INSERT INTO users (username, password, role, tier) VALUES (?, ?, ?, ?)",
                    ("demo", "demo123", "demo", "starter")
                )
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'tier': user[4]
                }
        return None
    
    def create_token(self, user):
        """Create JWT token"""
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'tier': user['tier'],
            'exp': datetime.utcnow() + timedelta(days=365),  # 1 year for admin
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload
        except:
            return None
    
    def register_routes(self):
        """Register all routes"""
        
        @self.app.route('/')
        def home():
            return jsonify({
                'message': 'Atlantiplex Matrix Studio - Enhanced',
                'version': '2.0.0',
                'login': {
                    'admin': {'username': 'manticore', 'password': 'patriot8812'},
                    'demo': {'username': 'demo', 'password': 'demo123'}
                },
                'api_endpoints': {
                    'login': '/api/auth/login',
                    'guests': '/api/guests',
                    'streaming': '/api/streaming',
                    'health': '/api/health'
                }
            })
        
        @self.app.route('/api/health')
        def health():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'features': {
                    'guest_management': True,
                    'streaming': True,
                    'admin_bypass': True,
                    'payments': False
                }
            })
        
        @self.app.route('/api/auth/login', methods=['POST'])
        def login():
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'error': 'Username and password required'}), 400
            
            user = self.verify_user(username, password)
            
            if user:
                token = self.create_token(user)
                return jsonify({
                    'success': True,
                    'token': token,
                    'user': user
                })
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
        
        @self.app.route('/api/auth/verify', methods=['POST'])
        def verify_token_endpoint():
            data = request.get_json()
            token = data.get('token')
            
            if not token:
                return jsonify({'error': 'Token required'}), 400
            
            payload = self.verify_token(token)
            
            if payload:
                return jsonify({
                    'success': True,
                    'valid': True,
                    'user': payload
                })
            else:
                return jsonify({'error': 'Invalid token'}), 401
        
        @self.app.route('/api/guests', methods=['GET', 'POST'])
        def manage_guests():
            # Get token from header
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'error': 'Token required'}), 401
            
            payload = self.verify_token(token)
            
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            user_id = payload['user_id']
            tier = payload['tier']
            
            if request.method == 'GET':
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT * FROM guest_sessions WHERE host_user_id = ?",
                        (user_id,)
                    )
                    guests = [
                        {
                            'id': row[0],
                            'guest_name': row[2],
                            'invite_code': row[3],
                            'created_at': row[4]
                        }
                        for row in cursor.fetchall()
                    ]
                    
                    return jsonify({
                        'success': True,
                        'guests': guests,
                        'tier': tier,
                        'limits': self.get_tier_limits(tier)
                    })
            
            elif request.method == 'POST':
                data = request.get_json()
                guest_name = data.get('guest_name')
                
                if not guest_name:
                    return jsonify({'error': 'Guest name required'}), 400
                
                # Check limits
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM guest_sessions WHERE host_user_id = ?",
                        (user_id,)
                    )
                    current_guests = cursor.fetchone()[0]
                    
                    max_guests = self.get_max_guests(tier)
                    
                    if current_guests >= max_guests:
                        return jsonify({
                            'error': 'Guest limit reached',
                            'current': current_guests,
                            'limit': max_guests,
                            'tier': tier
                        }), 402
                    
                    # Create guest session
                    import secrets
                    invite_code = secrets.token_urlsafe(8)
                    
                    conn.execute(
                        "INSERT INTO guest_sessions (host_user_id, guest_name, invite_code) VALUES (?, ?, ?)",
                        (user_id, guest_name, invite_code)
                    )
                    
                    return jsonify({
                        'success': True,
                        'guest': {
                            'guest_name': guest_name,
                            'invite_code': invite_code
                        }
                    })
        
        @self.app.route('/api/streaming', methods=['GET', 'POST'])
        def manage_streaming():
            # Get token from header
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'error': 'Token required'}), 401
            
            payload = self.verify_token(token)
            
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            tier = payload['tier']
            
            if request.method == 'POST':
                data = request.get_json()
                quality = data.get('quality', 'SD')
                
                # Check if quality is allowed for tier
                allowed_qualities = self.get_allowed_qualities(tier)
                
                if quality not in allowed_qualities:
                    return jsonify({
                        'error': f'Quality {quality} not available in {tier} tier',
                        'allowed_qualities': allowed_qualities,
                        'tier': tier
                    }), 402
                
                return jsonify({
                    'success': True,
                    'stream': {
                        'quality': quality,
                        'tier': tier,
                        'stream_key': f'stream_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
                    }
                })
            
            else:
                return jsonify({
                    'success': True,
                    'tier': tier,
                    'allowed_qualities': self.get_allowed_qualities(tier),
                    'max_duration_hours': self.get_max_duration(tier)
                })
        
        @self.app.route('/api/user/info')
        def user_info():
            # Get token from header
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'error': 'Token required'}), 401
            
            payload = self.verify_token(token)
            
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            return jsonify({
                'success': True,
                'user': {
                    'id': payload['user_id'],
                    'username': payload['username'],
                    'role': payload['role'],
                    'tier': payload['tier']
                },
                'features': self.get_tier_features(payload['tier'])
            })
    
    def get_tier_limits(self, tier):
        """Get tier limits"""
        limits = {
            'unlimited': {'max_guests': float('inf'), 'bandwidth': float('inf')},
            'enterprise': {'max_guests': 50, 'bandwidth': '2000GB'},
            'professional': {'max_guests': 10, 'bandwidth': '500GB'},
            'starter': {'max_guests': 3, 'bandwidth': '100GB'},
            'free': {'max_guests': 1, 'bandwidth': '10GB'}
        }
        return limits.get(tier, limits['free'])
    
    def get_max_guests(self, tier):
        """Get max guests for tier"""
        return self.get_tier_limits(tier)['max_guests']
    
    def get_allowed_qualities(self, tier):
        """Get allowed streaming qualities"""
        qualities = {
            'unlimited': ['SD', 'HD', 'Full HD', '4K', '8K'],
            'enterprise': ['SD', 'HD', 'Full HD', '4K'],
            'professional': ['SD', 'HD', 'Full HD'],
            'starter': ['SD', 'HD'],
            'free': ['SD']
        }
        return qualities.get(tier, qualities['free'])
    
    def get_max_duration(self, tier):
        """Get max streaming duration in hours"""
        durations = {
            'unlimited': float('inf'),
            'enterprise': 24,
            'professional': 8,
            'starter': 4,
            'free': 2
        }
        return durations.get(tier, 2)
    
    def get_tier_features(self, tier):
        """Get tier features"""
        features = {
            'unlimited': {
                'guest_management': True,
                'premium_scenes': True,
                'custom_scenes': True,
                'analytics': True,
                'api_access': True,
                'white_label': True,
                'admin_access': True
            },
            'enterprise': {
                'guest_management': True,
                'premium_scenes': True,
                'custom_scenes': True,
                'analytics': True,
                'api_access': True,
                'white_label': False,
                'admin_access': False
            },
            'professional': {
                'guest_management': True,
                'premium_scenes': True,
                'custom_scenes': False,
                'analytics': True,
                'api_access': False,
                'white_label': False,
                'admin_access': False
            },
            'starter': {
                'guest_management': True,
                'premium_scenes': False,
                'custom_scenes': False,
                'analytics': False,
                'api_access': False,
                'white_label': False,
                'admin_access': False
            },
            'free': {
                'guest_management': True,
                'premium_scenes': False,
                'custom_scenes': False,
                'analytics': False,
                'api_access': False,
                'white_label': False,
                'admin_access': False
            }
        }
        return features.get(tier, features['free'])
    
    def run(self):
        """Run the application"""
        logger.info("Starting Simple Enhanced Matrix Studio")
        logger.info("Admin Login: manticore / patriot8812")
        logger.info("Demo Login: demo / demo123")
        logger.info("Access: http://localhost:8081")
        
        self.app.run(host='0.0.0.0', port=8081, debug=False)

# Run the application
if __name__ == '__main__':
    app = SimpleMatrixStudio()
    app.run()