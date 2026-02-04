"""
Database Schema for Payment Integration and Subscription Management
SQLite schema with migration support for Atlantiplex Matrix Studio
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for Matrix Studio with payment integration"""
    
    def __init__(self, db_path: str = "matrix_studio.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Database connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with all required tables"""
        logger.info("Initializing database schema...")
        
        with self.get_connection() as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Subscriptions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    tier TEXT NOT NULL DEFAULT 'free',
                    stripe_customer_id TEXT,
                    stripe_subscription_id TEXT,
                    status TEXT DEFAULT 'active',
                    current_period_start TIMESTAMP,
                    current_period_end TIMESTAMP,
                    cancel_at_period_end BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Payments table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subscription_id INTEGER,
                    stripe_payment_intent_id TEXT,
                    amount_cents INTEGER NOT NULL,
                    currency TEXT DEFAULT 'usd',
                    status TEXT NOT NULL,
                    payment_method TEXT,
                    description TEXT,
                    metadata TEXT, -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions (id) ON DELETE SET NULL
                )
            """)
            
            # Usage tracking table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    usage_type TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    description TEXT,
                    session_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Feature access logs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feature_access (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    feature_path TEXT NOT NULL,
                    access_granted BOOLEAN NOT NULL,
                    tier TEXT,
                    reason TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Guest sessions (enhanced for subscription limits)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS guest_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    host_user_id INTEGER NOT NULL,
                    guest_name TEXT,
                    guest_email TEXT,
                    invite_code TEXT UNIQUE NOT NULL,
                    session_id TEXT,
                    status TEXT DEFAULT 'pending',
                    tier_allowed BOOLEAN DEFAULT 1,
                    max_duration_hours INTEGER DEFAULT 2,
                    actual_duration_minutes INTEGER,
                    joined_at TIMESTAMP,
                    left_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (host_user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Streaming sessions (with quality limits)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS streaming_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT,
                    platform TEXT,
                    quality TEXT DEFAULT 'SD',
                    max_duration_hours INTEGER DEFAULT 2,
                    actual_duration_minutes INTEGER,
                    viewer_count INTEGER DEFAULT 0,
                    bandwidth_used_mb INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'preparing',
                    stream_key TEXT,
                    thumbnail_url TEXT,
                    metadata TEXT, -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    ended_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Invoices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subscription_id INTEGER,
                    stripe_invoice_id TEXT,
                    amount_cents INTEGER NOT NULL,
                    currency TEXT DEFAULT 'usd',
                    status TEXT NOT NULL,
                    due_date TIMESTAMP,
                    paid_at TIMESTAMP,
                    invoice_url TEXT,
                    pdf_url TEXT,
                    line_items TEXT, -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions (id) ON DELETE SET NULL
                )
            """)
            
            # Webhook events
            conn.execute("""
                CREATE TABLE IF NOT EXISTS webhook_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stripe_event_id TEXT UNIQUE NOT NULL,
                    event_type TEXT NOT NULL,
                    processed BOOLEAN DEFAULT 0,
                    payload TEXT, -- JSON
                    processing_error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer_id ON subscriptions(stripe_customer_id)",
                "CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status)",
                "CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)",
                "CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_usage_tracking_created_at ON usage_tracking(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_guest_sessions_host_user_id ON guest_sessions(host_user_id)",
                "CREATE INDEX IF NOT EXISTS idx_guest_sessions_invite_code ON guest_sessions(invite_code)",
                "CREATE INDEX IF NOT EXISTS idx_streaming_sessions_user_id ON streaming_sessions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_streaming_sessions_status ON streaming_sessions(status)",
                "CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_webhook_events_stripe_event_id ON webhook_events(stripe_event_id)",
                "CREATE INDEX IF NOT EXISTS idx_webhook_events_processed ON webhook_events(processed)"
            ]
            
            for index_sql in indexes:
                conn.execute(index_sql)
        
        # Create default admin user
        self.create_default_admin()
        
        logger.info("Database initialized successfully")
    
    def create_default_admin(self):
        """Create default admin user with bypass credentials"""
        with self.get_connection() as conn:
            # Check if admin already exists
            cursor = conn.execute("SELECT id FROM users WHERE username = ?", ("manticore",))
            if cursor.fetchone():
                return
            
            # Insert admin user (password will be handled by auth system)
            conn.execute("""
                INSERT INTO users (username, email, role, is_active) 
                VALUES (?, ?, ?, ?)
            """, ("manticore", "admin@verilysovereign.org", "super_admin", 1))
            
            # Create admin subscription (unlimited)
            cursor = conn.execute("SELECT id FROM users WHERE username = ?", ("manticore",))
            admin_id = cursor.fetchone()['id']
            
            conn.execute("""
                INSERT INTO subscriptions (user_id, tier, status, cancel_at_period_end) 
                VALUES (?, ?, ?, ?)
            """, (admin_id, "admin_unlimited", "active", 0))
            
            logger.info("Default admin user created")
    
    # User management methods
    def create_user(self, username: str, email: str, password_hash: str, role: str = "user") -> Optional[int]:
        """Create new user"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO users (username, email, password_hash, role) 
                VALUES (?, ?, ?, ?)
            """, (username, email, password_hash, role))
            user_id = cursor.lastrowid
            
            # Create default subscription
            conn.execute("""
                INSERT INTO subscriptions (user_id, tier, status) 
                VALUES (?, ?, ?)
            """, (user_id, "free", "active"))
            
            return user_id
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_subscription(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's current subscription"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM subscriptions 
                WHERE user_id = ? AND status = 'active' 
                ORDER BY created_at DESC LIMIT 1
            """, (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_subscription(self, user_id: int, tier: str, stripe_subscription_id: str = None) -> bool:
        """Update user subscription"""
        with self.get_connection() as conn:
            # Update existing subscription or create new one
            cursor = conn.execute("""
                SELECT id FROM subscriptions 
                WHERE user_id = ? AND status = 'active'
            """, (user_id,))
            
            existing = cursor.fetchone()
            
            if existing:
                conn.execute("""
                    UPDATE subscriptions 
                    SET tier = ?, stripe_subscription_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (tier, stripe_subscription_id, existing['id']))
            else:
                conn.execute("""
                    INSERT INTO subscriptions (user_id, tier, stripe_subscription_id, status)
                    VALUES (?, ?, ?, ?)
                """, (user_id, tier, stripe_subscription_id, "active"))
            
            return True
    
    def record_payment(self, user_id: int, amount_cents: int, status: str, 
                      stripe_payment_intent_id: Optional[str] = None, subscription_id: Optional[int] = None,
                      description: Optional[str] = None, metadata: Optional[Dict] = None) -> Optional[int]:
        """Record payment transaction"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO payments (
                    user_id, subscription_id, stripe_payment_intent_id, 
                    amount_cents, status, description, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, subscription_id, stripe_payment_intent_id,
                amount_cents, status, description, 
                json.dumps(metadata) if metadata else None
            ))
            return cursor.lastrowid
    
    def track_usage(self, user_id: int, usage_type: str, amount: int, 
                   description: Optional[str] = None, session_id: Optional[str] = None) -> Optional[int]:
        """Track user usage"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO usage_tracking (user_id, usage_type, amount, description, session_id)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, usage_type, amount, description, session_id))
            return cursor.lastrowid
    
    def get_daily_usage(self, user_id: int, usage_type: str) -> int:
        """Get user's daily usage for specific type"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COALESCE(SUM(amount), 0) as total
                FROM usage_tracking 
                WHERE user_id = ? AND usage_type = ? 
                AND DATE(created_at) = DATE('now')
            """, (user_id, usage_type))
            result = cursor.fetchone()
            return result['total'] if result else 0
    
    def log_feature_access(self, user_id: int, feature_path: str, access_granted: bool,
                          tier: str, reason: Optional[str] = None, ip_address: Optional[str] = None) -> Optional[int]:
        """Log feature access attempt"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO feature_access (
                    user_id, feature_path, access_granted, tier, reason, ip_address
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, feature_path, access_granted, tier, reason, ip_address))
            return cursor.lastrowid
    
    def create_guest_session(self, host_user_id: int, guest_name: str, 
                           max_duration_hours: int = 2) -> Optional[str]:
        """Create guest session with invite code"""
        import secrets
        invite_code = secrets.token_urlsafe(12)
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO guest_sessions (
                    host_user_id, guest_name, invite_code, max_duration_hours, tier_allowed
                ) VALUES (?, ?, ?, ?, ?)
            """, (host_user_id, guest_name, invite_code, max_duration_hours, 1))
            
            return invite_code
    
    def get_active_guest_sessions(self, host_user_id: int) -> List[Dict[str, Any]]:
        """Get active guest sessions for user"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM guest_sessions 
                WHERE host_user_id = ? AND status IN ('pending', 'active')
                ORDER BY created_at DESC
            """, (host_user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def record_webhook_event(self, stripe_event_id: str, event_type: str, 
                            payload: Dict) -> Optional[int]:
        """Record Stripe webhook event"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO webhook_events (stripe_event_id, event_type, payload)
                VALUES (?, ?, ?)
            """, (stripe_event_id, event_type, json.dumps(payload)))
            return cursor.lastrowid
    
    def mark_webhook_processed(self, stripe_event_id: str, processing_error: Optional[str] = None):
        """Mark webhook event as processed"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE webhook_events 
                SET processed = 1, processed_at = CURRENT_TIMESTAMP, processing_error = ?
                WHERE stripe_event_id = ?
            """, (processing_error, stripe_event_id))
    
    def get_subscription_metrics(self) -> Dict[str, Any]:
        """Get subscription metrics for dashboard"""
        with self.get_connection() as conn:
            # Total users by tier
            cursor = conn.execute("""
                SELECT s.tier, COUNT(*) as count
                FROM subscriptions s
                WHERE s.status = 'active'
                GROUP BY s.tier
            """)
            tier_distribution = {row['tier']: row['count'] for row in cursor.fetchall()}
            
            # Monthly revenue (simplified)
            cursor = conn.execute("""
                SELECT COALESCE(SUM(amount_cents) / 100, 0) as revenue
                FROM payments p
                JOIN subscriptions s ON p.subscription_id = s.id
                WHERE p.status = 'completed' 
                AND DATE(p.created_at) >= DATE('now', '-30 days')
            """)
            revenue_result = cursor.fetchone()
            monthly_revenue = revenue_result['revenue'] if revenue_result else 0
            
            # Active subscriptions
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM subscriptions
                WHERE status = 'active' AND tier != 'free'
            """)
            active_paid = cursor.fetchone()['count']
            
            return {
                'tier_distribution': tier_distribution,
                'monthly_revenue': monthly_revenue,
                'active_paid_subscriptions': active_paid,
                'total_users': sum(tier_distribution.values())
            }