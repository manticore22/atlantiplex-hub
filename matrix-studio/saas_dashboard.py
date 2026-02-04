"""
SaaS Dashboard Components for Atlantiplex Lightning Studio
Enterprise admin dashboard with organization management, analytics, and billing
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SaaSDashboard:
    """Multi-tenant SaaS dashboard management"""
    
    def __init__(self, saas_db):
        self.saas_db = saas_db
    
    def get_dashboard_stats(self, organization_id: str) -> Dict[str, Any]:
        """Get dashboard statistics for organization"""
        cursor = self.saas_db.connection.cursor()
        
        # Organization info
        cursor.execute("""
            SELECT * FROM organizations WHERE id = ?
        """, (organization_id,))
        org = dict(cursor.fetchone())
        
        # User count
        cursor.execute("""
            SELECT COUNT(DISTINCT tm.user_id) as user_count
            FROM team_members tm
            WHERE tm.organization_id = ? AND tm.is_active = TRUE
        """, (organization_id,))
        user_count = cursor.fetchone()['user_count']
        
        # Team count
        cursor.execute("""
            SELECT COUNT(*) as team_count FROM teams WHERE organization_id = ?
        """, (organization_id,))
        team_count = cursor.fetchone()['team_count']
        
        # Active streams (placeholder - would connect to actual streaming data)
        active_streams = 0  # This would come from streaming system
        
        # Usage metrics
        cursor.execute("""
            SELECT metric_name, SUM(metric_value) as total
            FROM organization_usage 
            WHERE organization_id = ? AND period_start >= date('now', '-30 days')
            GROUP BY metric_name
        """, (organization_id,))
        usage_data = {row['metric_name']: row['total'] for row in cursor.fetchall()}
        
        return {
            'organization': org,
            'stats': {
                'users': user_count,
                'teams': team_count,
                'active_streams': active_streams,
                'storage_used_gb': usage_data.get('storage_gb', 0),
                'bandwidth_used_gb': usage_data.get('bandwidth_gb', 0),
                'api_calls': usage_data.get('api_calls', 0),
                'stream_hours': usage_data.get('stream_hours', 0)
            }
        }
    
    def get_organization_management_data(self, organization_id: str) -> Dict[str, Any]:
        """Get organization management data"""
        cursor = self.saas_db.connection.cursor()
        
        # Organization details
        cursor.execute("""
            SELECT * FROM organizations WHERE id = ?
        """, (organization_id,))
        org = dict(cursor.fetchone())
        
        # Teams hierarchy
        cursor.execute("""
            SELECT t.*, tm.role as creator_role, u.email as creator_email
            FROM teams t
            LEFT JOIN team_members tm ON t.id = tm.user_id AND tm.role = 'team_admin'
            LEFT JOIN users u ON tm.user_id = u.id
            WHERE t.organization_id = ?
            ORDER BY t.created_at
        """, (organization_id,))
        teams = []
        for row in cursor.fetchall():
            team = dict(row)
            team['member_count'] = self._get_team_member_count(team['id'])
            teams.append(team)
        
        # Team members
        cursor.execute("""
            SELECT tm.*, u.email, u.first_name, u.last_name, t.name as team_name
            FROM team_members tm
            JOIN users u ON tm.user_id = u.id
            JOIN teams t ON tm.team_id = t.id
            WHERE tm.organization_id = ? AND tm.is_active = TRUE
            ORDER BY tm.role DESC, tm.joined_at
        """, (organization_id,))
        members = []
        for row in cursor.fetchall():
            member = dict(row)
            members.append(member)
        
        return {
            'organization': org,
            'teams': teams,
            'members': members
        }
    
    def get_billing_dashboard_data(self, organization_id: str) -> Dict[str, Any]:
        """Get billing dashboard data"""
        cursor = self.saas_db.connection.cursor()
        
        # Current subscription
        cursor.execute("""
            SELECT os.*, o.name as organization_name
            FROM organization_subscriptions os
            JOIN organizations o ON os.organization_id = o.id
            WHERE os.organization_id = ?
            ORDER BY os.created_at DESC
            LIMIT 1
        """, (organization_id,))
        subscription = dict(cursor.fetchone()) if cursor.fetchone() else None
        
        # Recent invoices
        cursor.execute("""
            SELECT * FROM organization_invoices 
            WHERE organization_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (organization_id,))
        invoices = [dict(row) for row in cursor.fetchall()]
        
        # Usage-based billing calculation
        usage_cost = self._calculate_usage_based_billing(organization_id)
        
        return {
            'subscription': subscription,
            'invoices': invoices,
            'usage_cost': usage_cost,
            'next_billing_date': self._get_next_billing_date(subscription) if subscription else None
        }
    
    def get_analytics_dashboard_data(self, organization_id: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics dashboard data"""
        cursor = self.saas_db.connection.cursor()
        start_date = datetime.now() - timedelta(days=days)
        
        # Usage trends
        cursor.execute("""
            SELECT DATE(period_start) as date, metric_name, metric_value
            FROM organization_usage 
            WHERE organization_id = ? AND period_start >= ?
            ORDER BY period_start, metric_name
        """, (organization_id, start_date))
        
        usage_data = {}
        for row in cursor.fetchall():
            date = row['date']
            if date not in usage_data:
                usage_data[date] = {}
            usage_data[date][row['metric_name']] = row['metric_value']
        
        # Top users by usage
        cursor.execute("""
            SELECT u.email, COUNT(*) as actions
            FROM audit_logs al
            JOIN users u ON al.user_id = u.id
            WHERE al.organization_id = ? AND al.success = TRUE 
            AND al.created_at >= ?
            GROUP BY u.id
            ORDER BY actions DESC
            LIMIT 10
        """, (organization_id, start_date))
        top_users = [dict(row) for row in cursor.fetchall()]
        
        # Feature usage
        cursor.execute("""
            SELECT action, COUNT(*) as usage_count
            FROM audit_logs
            WHERE organization_id = ? AND created_at >= ?
            GROUP BY action
            ORDER BY usage_count DESC
        """, (organization_id, start_date))
        feature_usage = [dict(row) for row in cursor.fetchall()]
        
        return {
            'usage_trends': usage_data,
            'top_users': top_users,
            'feature_usage': feature_usage,
            'period_days': days
        }
    
    def _get_team_member_count(self, team_id: str) -> int:
        """Get member count for team"""
        cursor = self.saas_db.connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count FROM team_members WHERE team_id = ? AND is_active = TRUE
        """, (team_id,))
        return cursor.fetchone()['count']
    
    def _calculate_usage_based_billing(self, organization_id: str) -> Dict[str, Any]:
        """Calculate usage-based billing costs"""
        # This is a simplified calculation - in production would use actual usage rates
        cursor = self.saas_db.connection.cursor()
        cursor.execute("""
            SELECT metric_name, SUM(metric_value) as total_usage
            FROM organization_usage 
            WHERE organization_id = ? AND period_start >= date('now', '-30 days')
            GROUP BY metric_name
        """, (organization_id,))
        
        usage_metrics = {row['metric_name']: row['total_usage'] for row in cursor.fetchall()}
        
        # Simplified pricing model (would be configurable in production)
        pricing = {
            'storage_gb_per_month': 0.10,  # $0.10 per GB
            'bandwidth_gb_per_month': 0.05,  # $0.05 per GB
            'api_calls_per_day': 0.001,  # $0.001 per API call
            'stream_hours': 0.50,  # $0.50 per hour
        }
        
        total_cost = 0
        cost_breakdown = {}
        
        for metric, usage in usage_metrics.items():
            if metric in pricing:
                metric_cost = usage * pricing[metric]
                cost_breakdown[metric] = {
                    'usage': usage,
                    'rate': pricing[metric],
                    'cost': metric_cost
                }
                total_cost += metric_cost
        
        return {
            'total_cost': total_cost,
            'cost_breakdown': cost_breakdown,
            'currency': 'USD'
        }
    
    def _get_next_billing_date(self, subscription: Dict[str, Any]) -> Optional[datetime]:
        """Get next billing date for subscription"""
        if not subscription:
            return None
            
        try:
            if subscription['current_period_end']:
                # Parse the period end date
                return datetime.fromisoformat(subscription['current_period_end'])
            else:
                # Default to monthly cycle
                return datetime.now().replace(day=1) + timedelta(days=30)
        except:
            return None
    
    def generate_super_admin_overview(self) -> Dict[str, Any]:
        """Generate super admin overview of all organizations"""
        cursor = self.saas_db.connection.cursor()
        
        # Overall stats
        cursor.execute("SELECT COUNT(*) as count FROM organizations WHERE tenant_status = 'active'")
        active_orgs = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM organizations WHERE tenant_status = 'trial'")
        trial_orgs = cursor.fetchone()['count']
        
        # Subscription distribution
        cursor.execute("""
            SELECT subscription_tier, COUNT(*) as count
            FROM organizations 
            WHERE tenant_status = 'active'
            GROUP BY subscription_tier
        """)
        subscription_distribution = {row['subscription_tier']: row['count'] for row in cursor.fetchall()}
        
        # Revenue (simplified)
        cursor.execute("""
            SELECT os.amount, os.currency
            FROM organization_subscriptions os
            JOIN organizations o ON os.organization_id = o.id
            WHERE o.tenant_status = 'active' AND os.status = 'active'
        """)
        revenue_data = cursor.fetchall()
        monthly_revenue = sum(row['amount'] / 100 for row in revenue_data) if revenue_data else 0
        
        # Recent organizations
        cursor.execute("""
            SELECT id, name, subdomain, created_at, subscription_tier
            FROM organizations
            ORDER BY created_at DESC
            LIMIT 10
        """)
        recent_orgs = [dict(row) for row in cursor.fetchall()]
        
        return {
            'overview': {
                'active_organizations': active_orgs,
                'trial_organizations': trial_orgs,
                'monthly_revenue': monthly_revenue,
                'subscription_distribution': subscription_distribution
            },
            'recent_organizations': recent_orgs
        }