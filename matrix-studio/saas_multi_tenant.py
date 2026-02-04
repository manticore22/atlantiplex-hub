"""
Multi-Tenant SaaS Architecture for Atlantiplex Lightning Studio
Enterprise-grade multi-tenant organization and tenant management
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TenantStatus(Enum):
    """Tenant organization status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"

class SubscriptionStatus(Enum):
    """Organization subscription status"""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    TRIAL = "trial"

class UserRole(Enum):
    """User roles within organizations"""
    ORG_OWNER = "org_owner"
    ORG_ADMIN = "org_admin" 
    TEAM_ADMIN = "team_admin"
    TEAM_MEMBER = "team_member"
    VIEWER = "viewer"

@dataclass
class Organization:
    """Multi-tenant organization model"""
    id: str
    name: str
    domain: str
    subdomain: str
    subscription_tier: str
    subscription_status: SubscriptionStatus
    tenant_status: TenantStatus
    settings: Dict[str, Any]
    resource_limits: Dict[str, Any]
    billing_email: str
    created_at: datetime
    updated_at: datetime
    trial_ends_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'subdomain': self.subdomain,
            'subscription_tier': self.subscription_tier,
            'subscription_status': self.subscription_status.value,
            'tenant_status': self.tenant_status.value,
            'settings': self.settings,
            'resource_limits': self.resource_limits,
            'billing_email': self.billing_email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'trial_ends_at': self.trial_ends_at.isoformat() if self.trial_ends_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None
        }

@dataclass 
class Team:
    """Team/Department model within organizations"""
    id: str
    organization_id: str
    parent_team_id: Optional[str]
    name: str
    description: str
    resource_limits: Dict[str, Any]
    permissions: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'parent_team_id': self.parent_team_id,
            'name': self.name,
            'description': self.description,
            'resource_limits': self.resource_limits,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class TeamMember:
    """Team member with role-based permissions"""
    id: str
    user_id: str
    team_id: str
    organization_id: str
    role: UserRole
    permissions: List[str]
    invited_by: Optional[str]
    invited_at: Optional[datetime]
    joined_at: Optional[datetime]
    last_active: datetime
    is_active: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'team_id': self.team_id,
            'organization_id': self.organization_id,
            'role': self.role.value,
            'permissions': self.permissions,
            'invited_by': self.invited_by,
            'invited_at': self.invited_at.isoformat() if self.invited_at else None,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_active': self.last_active.isoformat(),
            'is_active': self.is_active
        }

class MultiTenantManager:
    """Manages multi-tenant SaaS operations"""
    
    def __init__(self):
        self.organizations = {}
        self.teams = {}
        self.team_members = {}
        self.tenant_context = {}
        
    def create_organization(self, name: str, domain: str, subdomain: str, 
                        billing_email: str, subscription_tier: str = "free") -> Organization:
        """Create new tenant organization"""
        org_id = str(uuid.uuid4())
        org = Organization(
            id=org_id,
            name=name,
            domain=domain,
            subdomain=subdomain,
            subscription_tier=subscription_tier,
            subscription_status=SubscriptionStatus.TRIAL,
            tenant_status=TenantStatus.ACTIVE,
            settings=self._get_default_settings(subscription_tier),
            resource_limits=self._get_default_limits(subscription_tier),
            billing_email=billing_email,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            trial_ends_at=datetime.now() + timedelta(days=14)
        )
        
        self.organizations[org_id] = org
        logger.info(f"🏢 Created organization: {name} ({org_id})")
        return org
    
    def create_team(self, organization_id: str, name: str, description: str = "",
                   parent_team_id: Optional[str] = None) -> Team:
        """Create team within organization"""
        team_id = str(uuid.uuid4())
        
        # Get org limits
        org = self.organizations.get(organization_id)
        if not org:
            raise ValueError(f"Organization {organization_id} not found")
            
        team = Team(
            id=team_id,
            organization_id=organization_id,
            parent_team_id=parent_team_id,
            name=name,
            description=description,
            resource_limits=self._get_team_limits(org.subscription_tier),
            permissions=self._get_default_team_permissions(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.teams[team_id] = team
        logger.info(f"👥 Created team: {name} in organization {organization_id}")
        return team
    
    def add_team_member(self, organization_id: str, team_id: str, user_id: str, 
                       role: UserRole, invited_by: Optional[str] = None) -> TeamMember:
        """Add user to team with specified role"""
        member_id = str(uuid.uuid4())
        
        # Get permissions for role
        permissions = self._get_role_permissions(role)
        
        member = TeamMember(
            id=member_id,
            user_id=user_id,
            team_id=team_id,
            organization_id=organization_id,
            role=role,
            permissions=permissions,
            invited_by=invited_by,
            invited_at=datetime.now(),
            joined_at=None,
            last_active=datetime.now(),
            is_active=False
        )
        
        self.team_members[member_id] = member
        logger.info(f"👤 Added team member: {user_id} to team {team_id} as {role.value}")
        return member
    
    def get_organization_teams(self, organization_id: str) -> List[Team]:
        """Get all teams for organization"""
        return [team for team in self.teams.values() 
                if team.organization_id == organization_id]
    
    def get_user_organizations(self, user_id: str) -> List[Organization]:
        """Get all organizations for user"""
        user_memberships = [member for member in self.team_members.values() 
                          if member.user_id == user_id and member.is_active]
        
        org_ids = list(set([member.organization_id for member in user_memberships]))
        return [self.organizations[org_id] for org_id in org_ids if org_id in self.organizations]
    
    def get_user_permissions(self, user_id: str, organization_id: str) -> List[str]:
        """Get aggregated permissions for user in organization"""
        memberships = [member for member in self.team_members.values() 
                     if member.user_id == user_id and member.organization_id == organization_id and member.is_active]
        
        if not memberships:
            return []
            
        # Aggregate permissions from all memberships
        all_permissions = set()
        for member in memberships:
            all_permissions.update(member.permissions)
            
        return list(all_permissions)
    
    def _get_default_settings(self, subscription_tier: str) -> Dict[str, Any]:
        """Get default settings for subscription tier"""
        return {
            'branding': {
                'custom_logo': False,
                'custom_colors': False,
                'white_label': subscription_tier in ['enterprise']
            },
            'features': {
                'api_access': subscription_tier in ['professional', 'enterprise'],
                'advanced_analytics': subscription_tier in ['enterprise'],
                'custom_domains': subscription_tier in ['enterprise'],
                'sso_enabled': subscription_tier in ['enterprise']
            },
            'security': {
                'mfa_required': subscription_tier in ['enterprise'],
                'ip_whitelist': subscription_tier in ['enterprise'],
                'session_timeout': self._get_session_timeout(subscription_tier)
            }
        }
    
    def _get_default_limits(self, subscription_tier: str) -> Dict[str, Any]:
        """Get default resource limits for subscription tier"""
        limits_map = {
            'free': {
                'max_users': 5,
                'max_teams': 2,
                'max_concurrent_streams': 1,
                'bandwidth_gb_per_month': 50,
                'storage_gb': 5,
                'api_calls_per_day': 100
            },
            'starter': {
                'max_users': 20,
                'max_teams': 5,
                'max_concurrent_streams': 3,
                'bandwidth_gb_per_month': 500,
                'storage_gb': 50,
                'api_calls_per_day': 1000
            },
            'professional': {
                'max_users': 100,
                'max_teams': 20,
                'max_concurrent_streams': 10,
                'bandwidth_gb_per_month': 2000,
                'storage_gb': 500,
                'api_calls_per_day': 10000
            },
            'enterprise': {
                'max_users': float('inf'),
                'max_teams': float('inf'),
                'max_concurrent_streams': 50,
                'bandwidth_gb_per_month': float('inf'),
                'storage_gb': float('inf'),
                'api_calls_per_day': float('inf')
            }
        }
        
        return limits_map.get(subscription_tier, limits_map['free'])
    
    def _get_team_limits(self, subscription_tier: str) -> Dict[str, Any]:
        """Get team-specific resource limits"""
        org_limits = self._get_default_limits(subscription_tier)
        
        return {
            'max_members': org_limits.get('max_users', 5) // 2,
            'max_streams': org_limits.get('max_concurrent_streams', 1) // 2,
            'storage_gb': org_limits.get('storage_gb', 5) // 4,
            'can_create_subteams': subscription_tier in ['professional', 'enterprise']
        }
    
    def _get_default_team_permissions(self) -> Dict[str, bool]:
        """Get default permissions for teams"""
        return {
            'view_streams': True,
            'create_streams': True,
            'manage_guests': True,
            'view_analytics': True,
            'manage_team': False,
            'manage_billing': False,
            'manage_organization': False
        }
    
    def _get_role_permissions(self, role: UserRole) -> List[str]:
        """Get permissions for specific role"""
        role_permissions = {
            UserRole.VIEWER: [
                'view_streams', 'view_team', 'view_analytics'
            ],
            UserRole.TEAM_MEMBER: [
                'view_streams', 'create_streams', 'manage_guests', 
                'view_analytics', 'view_team'
            ],
            UserRole.TEAM_ADMIN: [
                'view_streams', 'create_streams', 'manage_guests',
                'view_analytics', 'view_team', 'manage_team',
                'invite_members', 'remove_members'
            ],
            UserRole.ORG_ADMIN: [
                'view_streams', 'create_streams', 'manage_guests',
                'view_analytics', 'view_team', 'manage_team',
                'invite_members', 'remove_members', 'manage_billing',
                'manage_organization_settings', 'manage_teams', 'view_billing'
            ],
            UserRole.ORG_OWNER: [
                'view_streams', 'create_streams', 'manage_guests',
                'view_analytics', 'view_team', 'manage_team',
                'invite_members', 'remove_members', 'manage_billing',
                'manage_organization_settings', 'manage_teams', 'view_billing',
                'delete_organization', 'upgrade_subscription', 'cancel_subscription'
            ]
        }
        
        return role_permissions.get(role, [])
    
    def _get_session_timeout(self, subscription_tier: str) -> int:
        """Get session timeout in hours for subscription tier"""
        timeouts = {
            'free': 2,
            'starter': 8,
            'professional': 24,
            'enterprise': 72
        }
        return timeouts.get(subscription_tier, 2)