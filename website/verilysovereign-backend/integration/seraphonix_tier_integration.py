#!/usr/bin/env python3
"""
Atlantiplex Studio - Seraphonix Tier Integration
This module enforces tier-based access limits in Atlantiplex Studio
"""

import os
import requests
import logging
from functools import wraps
from flask import request, jsonify, g

logger = logging.getLogger(__name__)

# Seraphonix API Configuration
SERAPHONIX_API_URL = os.environ.get('SERAPHONIX_API_URL', 'http://seraphonix-api:3000')

# Tier limits configuration
TIER_LIMITS = {
    'free': {
        'max_guests': 2,
        'max_hours': 16,
        'resolution': '720p',
        'max_bitrate': 4500,
        'multistream': False,
        'ai_tools': False,
        'white_label': False,
        'scene_presets': 3,
    },
    'ascendant': {
        'max_guests': 6,
        'max_hours': 70,
        'resolution': '1080p',
        'max_bitrate': 8000,
        'multistream': True,
        'destinations': 2,
        'ai_tools': True,
        'white_label': False,
        'scene_presets': 10,
    },
    'covenant': {
        'max_guests': 6,
        'max_hours': 999,
        'resolution': '1080p',
        'max_bitrate': 10000,
        'multistream': True,
        'destinations': 3,
        'ai_tools': True,
        'white_label': False,
        'scene_presets': 20,
    },
    'infinite': {
        'max_guests': 8,
        'max_hours': 999,
        'resolution': '4k',
        'max_bitrate': 25000,
        'multistream': True,
        'destinations': 2,
        'ai_tools': True,
        'white_label': True,
        'scene_presets': 999,
    }
}


def get_user_tier_from_token(token):
    """Get user's subscription tier from Seraphonix API"""
    try:
        response = requests.get(
            f'{SERAPHONIX_API_URL}/api/auth/me',
            headers={'Authorization': f'Bearer {token}'},
            timeout=5
        )
        if response.ok:
            # Now get subscription
            sub_response = requests.get(
                f'{SERAPHONIX_API_URL}/api/user/subscription',
                headers={'Authorization': f'Bearer {token}'},
                timeout=5
            )
            if sub_response.ok:
                data = sub_response.json()
                return data.get('tier', 'free')
        return 'free'
    except Exception as e:
        logger.error(f"Failed to get user tier: {e}")
        return 'free'


def get_user_usage_from_token(token):
    """Get user's streaming hours usage from Seraphonix API"""
    try:
        response = requests.get(
            f'{SERAPHONIX_API_URL}/api/user/usage',
            headers={'Authorization': f'Bearer {token}'},
            timeout=5
        )
        if response.ok:
            return response.json()
        return {'hoursUsed': 0, 'hoursLimit': 16, 'tier': 'free'}
    except Exception as e:
        logger.error(f"Failed to get user usage: {e}")
        return {'hoursUsed': 0, 'hoursLimit': 16, 'tier': 'free'}


def get_tier_limits(tier):
    """Get the limits for a specific tier"""
    return TIER_LIMITS.get(tier, TIER_LIMITS['free'])


def require_tier_feature(feature):
    """Decorator to enforce tier-based feature access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token from header
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            token = auth_header.replace('Bearer ', '')
            tier = get_user_tier_from_token(token)
            limits = get_tier_limits(tier)
            
            # Check if feature is available
            if not limits.get(feature, False):
                return jsonify({
                    'error': f'Feature not available on {tier.upper()} tier',
                    'tier': tier,
                    'required': feature
                }), 403
            
            # Store tier info in request context
            g.user_tier = tier
            g.tier_limits = limits
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_guest_limit(tier, current_guests):
    """Check if user can add more guests"""
    limits = get_tier_limits(tier)
    return current_guests < limits['max_guests']


def check_streaming_hours(tier, hours_used):
    """Check if user has streaming hours remaining"""
    limits = get_tier_limits(tier)
    return hours_used < limits['max_hours']


def get_resolution_limit(tier):
    """Get maximum resolution for tier"""
    limits = get_tier_limits(tier)
    return limits['resolution']


# Flask extension for easy integration
class SeraphonixTierManager:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        
        @app.before_request
        def load_tier_info():
            """Load tier info for authenticated requests"""
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '')
                g.user_tier = get_user_tier_from_token(token)
                g.tier_limits = get_tier_limits(g.user_tier)
                g.user_usage = get_user_usage_from_token(token)
            else:
                g.user_tier = 'free'
                g.tier_limits = get_tier_limits('free')
                g.user_usage = {'hoursUsed': 0, 'hoursLimit': 16, 'tier': 'free'}
        
        @app.route('/api/tier-info')
        def tier_info():
            """Get current user's tier information"""
            return jsonify({
                'tier': g.user_tier,
                'limits': g.tier_limits,
                'usage': g.user_usage
            })


# Example usage in Atlantiplex app.py:
"""
from seraphonix_tier_integration import SeraphonixTierManager

# Initialize tier manager
tier_manager = SeraphonixTierManager(app)

# Use decorator to protect routes
@app.route('/api/start-stream')
@require_tier_feature('multistream')
def start_stream():
    # Your stream starting logic
    pass
"""
