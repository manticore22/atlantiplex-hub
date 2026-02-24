# Flask Security Configuration Example
# Place in config/security.py

import os
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

class SecurityConfig:
    """Security configuration for Flask application"""
    
    # =====================
    # DEBUG & ENVIRONMENT
    # =====================
    DEBUG = False
    TESTING = False
    ENV = os.getenv('FLASK_ENV', 'production')
    
    # =====================
    # SECURITY
    # =====================
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGIN', 'https://atlantiplex.example.com').split(',')
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    CORS_EXPOSE_HEADERS = ['Content-Range', 'X-Content-Range', 'X-Total-Count']
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_MAX_AGE = 86400  # 24 hours
    
    # Session Configuration
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
    SESSION_COOKIE_NAME = '__Host-session'  # Secure naming convention
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_REFRESH_EACH_REQUEST = False
    
    # CSRF Protection
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit
    WTF_CSRF_SSL_STRICT = True
    
    # JWT Configuration
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_ALGORITHM_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Security Headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' https://api.stripe.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        ),
    }
    
    # Input Validation
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = False
    
    # =====================
    # DATABASE
    # =====================
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'echo': False,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10,
        }
    }
    
    # =====================
    # RATE LIMITING
    # =====================
    
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
    RATELIMIT_DEFAULT = "200/day;50/hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # =====================
    # LOGGING
    # =====================
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = '/app/logs/flask.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10
    
    # =====================
    # STRIPE (Payment Processing)
    # =====================
    
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    # =====================
    # API KEYS
    # =====================
    
    API_KEY_HEADER = 'X-API-Key'
    API_KEY_HASH = os.getenv('API_KEY_HASH')


# Production Configuration
class ProductionConfig(SecurityConfig):
    """Production environment configuration"""
    ENV = 'production'
    DEBUG = False
    TESTING = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False


# Development Configuration
class DevelopmentConfig(SecurityConfig):
    """Development environment configuration"""
    ENV = 'development'
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development


# Testing Configuration
class TestingConfig(SecurityConfig):
    """Testing environment configuration"""
    ENV = 'testing'
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
