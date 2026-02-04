"""
SaaS Database Schema for Multi-Tenant Atlantiplex Lightning Studio
Enterprise-grade database schema with organization isolation and RBAC
"""

import sqlite3
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class SaaSDatabaseManager:
    """Multi-tenant SaaS database management"""
    
    def __init__(self, db_path: str = "saas_atlantiplex.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Initialize complete SaaS database schema"""
        cursor = self.connection.cursor()
        
        # Organizations table (tenants)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                domain TEXT NOT NULL,
                subdomain TEXT UNIQUE NOT NULL,
                subscription_tier TEXT NOT NULL DEFAULT 'free',
                subscription_status TEXT NOT NULL DEFAULT 'trial',
                tenant_status TEXT NOT NULL DEFAULT 'active',
                settings TEXT,
                resource_limits TEXT,
                billing_email TEXT NOT NULL,
                stripe_customer_id TEXT,
                trial_ends_at DATETIME,
                cancelled_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Teams table (departments/sub-organizations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                parent_team_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                resource_limits TEXT,
                permissions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_team_id) REFERENCES teams(id) ON DELETE CASCADE
            )
        """)
        
        # Enhanced users table with tenant support
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                organization_id TEXT,
                team_id TEXT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                avatar_url TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT FALSE,
                last_login DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
                FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
            )
        """)
        
        # Team members table (many-to-many relationship)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                organization_id TEXT NOT NULL,
                role TEXT NOT NULL,
                permissions TEXT,
                invited_by TEXT,
                invited_at DATETIME,
                joined_at DATETIME,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
                UNIQUE (user_id, team_id)
            )
        """)
        
        # Organization subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organization_subscriptions (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                stripe_subscription_id TEXT,
                stripe_price_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL DEFAULT 'usd',
                billing_interval TEXT NOT NULL DEFAULT 'month',
                status TEXT NOT NULL,
                current_period_start DATETIME,
                current_period_end DATETIME,
                cancel_at_period_end BOOLEAN DEFAULT FALSE,
                trial_end DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
            )
        """)
        
        # Organization usage tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organization_usage (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                unit TEXT NOT NULL,
                period_start DATETIME NOT NULL,
                period_end DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
            )
        """)
        
        # Organization invoices
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organization_invoices (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                stripe_invoice_id TEXT,
                invoice_number TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL DEFAULT 'usd',
                status TEXT NOT NULL,
                due_date DATETIME,
                paid_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
            )
        """)
        
        # Audit logs for compliance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                organization_id TEXT,
                user_id TEXT,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # API keys for organizations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organization_api_keys (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                name TEXT NOT NULL,
                key_hash TEXT NOT NULL,
                permissions TEXT,
                last_used DATETIME,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
            )
        """)
        
        # Organization settings (white-label, branding, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organization_settings (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                setting_key TEXT NOT NULL,
                setting_value TEXT,
                setting_type TEXT NOT NULL DEFAULT 'string',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
                UNIQUE (organization_id, setting_key)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_domain ON organizations(subdomain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_users ON users(organization_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_org ON teams(organization_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_members ON team_members(organization_id, user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_org ON organization_usage(organization_id, period_start)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_org ON audit_logs(organization_id, created_at)")
        
        self.connection.commit()
        print("OK: SaaS Multi-Tenant Database Schema Initialized")
    
    def create_organization(self, org_data: Dict[str, Any]) -> str:
        """Create new organization/tenant"""
        cursor = self.connection.cursor()
        org_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO organizations 
            (id, name, domain, subdomain, subscription_tier, subscription_status, 
             tenant_status, settings, resource_limits, billing_email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            org_id, org_data['name'], org_data['domain'], org_data['subdomain'],
            org_data.get('subscription_tier', 'free'), 'trial', 'active',
            json.dumps(org_data.get('settings', {})), json.dumps(org_data.get('resource_limits', {})),
            org_data['billing_email'], datetime.now(), datetime.now()
        ))
        
        self.connection.commit()
        return org_id
    
    def get_organization_by_subdomain(self, subdomain: str) -> Optional[Dict[str, Any]]:
        """Get organization by subdomain for tenant routing"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM organizations WHERE subdomain = ? AND tenant_status = 'active'
        """, (subdomain,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_organizations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all organizations for user"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT o.* FROM organizations o
            INNER JOIN team_members tm ON o.id = tm.organization_id
            WHERE tm.user_id = ? AND tm.is_active = TRUE AND o.tenant_status = 'active'
        """, (user_id,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def create_team(self, team_data: Dict[str, Any]) -> str:
        """Create new team"""
        cursor = self.connection.cursor()
        team_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO teams (id, organization_id, parent_team_id, name, description, 
                           resource_limits, permissions, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            team_id, team_data['organization_id'], team_data.get('parent_team_id'),
            team_data['name'], team_data.get('description', ''),
            json.dumps(team_data.get('resource_limits', {})),
            json.dumps(team_data.get('permissions', {})), datetime.now(), datetime.now()
        ))
        
        self.connection.commit()
        return team_id
    
    def add_team_member(self, member_data: Dict[str, Any]) -> str:
        """Add user to team"""
        cursor = self.connection.cursor()
        member_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO team_members (id, user_id, team_id, organization_id, role, 
                                   permissions, invited_by, invited_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            member_id, member_data['user_id'], member_data['team_id'],
            member_data['organization_id'], member_data['role'],
            json.dumps(member_data.get('permissions', [])), member_data.get('invited_by'),
            datetime.now(), True
        ))
        
        self.connection.commit()
        return member_id
    
    def get_organization_usage(self, organization_id: str, period_start: datetime, 
                          period_end: datetime) -> List[Dict[str, Any]]:
        """Get usage metrics for organization"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM organization_usage 
            WHERE organization_id = ? AND period_start >= ? AND period_end <= ?
            ORDER BY metric_name, period_start
        """, (organization_id, period_start, period_end))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def log_audit_event(self, organization_id: str, user_id: str, action: str,
                      resource_type: str = None, resource_id: str = None,
                      ip_address: str = None, user_agent: str = None,
                      success: bool = True, error_message: str = None):
        """Log audit event for compliance"""
        cursor = self.connection.cursor()
        audit_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO audit_logs (id, organization_id, user_id, action, resource_type, 
                                 resource_id, ip_address, user_agent, success, 
                                 error_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            audit_id, organization_id, user_id, action, resource_type,
            resource_id, ip_address, user_agent, success, error_message, datetime.now()
        ))
        
        self.connection.commit()
        return audit_id
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()