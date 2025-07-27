from datetime import datetime
from typing import Optional, Dict, Any
import json

class Payment:
    """Payment model for tracking transactions"""
    
    def __init__(self):
        self.id: Optional[int] = None
        self.user_id: Optional[int] = None
        self.paypal_payment_id: str = ""
        self.paypal_payer_id: str = ""
        self.amount: float = 0.0
        self.currency: str = "USD"
        self.plan_type: str = ""  # starter, professional, enterprise
        self.billing_cycle: str = ""  # monthly, annual
        self.status: str = "pending"  # pending, completed, failed, cancelled, refunded
        self.payment_method: str = "paypal"
        self.description: str = ""
        self.metadata: Dict[str, Any] = {}
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        self.expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'paypal_payment_id': self.paypal_payment_id,
            'paypal_payer_id': self.paypal_payer_id,
            'amount': self.amount,
            'currency': self.currency,
            'plan_type': self.plan_type,
            'billing_cycle': self.billing_cycle,
            'status': self.status,
            'payment_method': self.payment_method,
            'description': self.description,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Payment':
        """Create instance from dictionary"""
        payment = cls()
        payment.id = data.get('id')
        payment.user_id = data.get('user_id')
        payment.paypal_payment_id = data.get('paypal_payment_id', '')
        payment.paypal_payer_id = data.get('paypal_payer_id', '')
        payment.amount = data.get('amount', 0.0)
        payment.currency = data.get('currency', 'USD')
        payment.plan_type = data.get('plan_type', '')
        payment.billing_cycle = data.get('billing_cycle', '')
        payment.status = data.get('status', 'pending')
        payment.payment_method = data.get('payment_method', 'paypal')
        payment.description = data.get('description', '')
        payment.metadata = data.get('metadata', {})
        
        if data.get('created_at'):
            payment.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            payment.updated_at = datetime.fromisoformat(data['updated_at'])
        if data.get('expires_at'):
            payment.expires_at = datetime.fromisoformat(data['expires_at'])
            
        return payment

class Subscription:
    """Subscription model for recurring payments"""
    
    def __init__(self):
        self.id: Optional[int] = None
        self.user_id: Optional[int] = None
        self.paypal_subscription_id: str = ""
        self.plan_type: str = ""  # starter, professional, enterprise
        self.billing_cycle: str = ""  # monthly, annual
        self.status: str = "active"  # active, cancelled, expired, suspended
        self.amount: float = 0.0
        self.currency: str = "USD"
        self.next_billing_date: Optional[datetime] = None
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        self.cancelled_at: Optional[datetime] = None
        self.expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'paypal_subscription_id': self.paypal_subscription_id,
            'plan_type': self.plan_type,
            'billing_cycle': self.billing_cycle,
            'status': self.status,
            'amount': self.amount,
            'currency': self.currency,
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subscription':
        """Create instance from dictionary"""
        subscription = cls()
        subscription.id = data.get('id')
        subscription.user_id = data.get('user_id')
        subscription.paypal_subscription_id = data.get('paypal_subscription_id', '')
        subscription.plan_type = data.get('plan_type', '')
        subscription.billing_cycle = data.get('billing_cycle', '')
        subscription.status = data.get('status', 'active')
        subscription.amount = data.get('amount', 0.0)
        subscription.currency = data.get('currency', 'USD')
        
        if data.get('next_billing_date'):
            subscription.next_billing_date = datetime.fromisoformat(data['next_billing_date'])
        if data.get('created_at'):
            subscription.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            subscription.updated_at = datetime.fromisoformat(data['updated_at'])
        if data.get('cancelled_at'):
            subscription.cancelled_at = datetime.fromisoformat(data['cancelled_at'])
        if data.get('expires_at'):
            subscription.expires_at = datetime.fromisoformat(data['expires_at'])
            
        return subscription

class PricingPlan:
    """Pricing plan configuration"""
    
    PLANS = {
        'starter': {
            'name': 'Starter',
            'description': 'Perfect for small businesses and freelancers',
            'monthly_price': 29,
            'annual_price': 290,
            'features': [
                '10 SEO audits per month',
                'Basic backlink monitoring',
                'Social media analysis',
                'Security scanning',
                'Email support',
                'PDF reports'
            ],
            'limits': {
                'audits_per_month': 10,
                'backlink_checks': 100,
                'reports_per_month': 10
            }
        },
        'professional': {
            'name': 'Professional',
            'description': 'Ideal for agencies and growing businesses',
            'monthly_price': 79,
            'annual_price': 790,
            'features': [
                '50 SEO audits per month',
                'Advanced backlink monitoring',
                'Competitor analysis',
                'White-label reports',
                'Priority support',
                'API access',
                'Custom branding',
                'Team collaboration'
            ],
            'limits': {
                'audits_per_month': 50,
                'backlink_checks': 1000,
                'reports_per_month': 50,
                'team_members': 5
            }
        },
        'enterprise': {
            'name': 'Enterprise',
            'description': 'For large organizations with custom needs',
            'monthly_price': 199,
            'annual_price': 1990,
            'features': [
                'Unlimited SEO audits',
                'Advanced competitor tracking',
                'Custom integrations',
                'Dedicated account manager',
                'SLA guarantee',
                'Custom reporting',
                'Advanced analytics',
                'Phone support'
            ],
            'limits': {
                'audits_per_month': -1,  # Unlimited
                'backlink_checks': -1,   # Unlimited
                'reports_per_month': -1, # Unlimited
                'team_members': -1       # Unlimited
            }
        }
    }
    
    @classmethod
    def get_plan(cls, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan configuration by ID"""
        return cls.PLANS.get(plan_id)
    
    @classmethod
    def list_plans(cls) -> Dict[str, Dict[str, Any]]:
        """List all available plans"""
        return cls.PLANS
    
    @classmethod
    def get_price(cls, plan_id: str, billing_cycle: str) -> float:
        """Get price for a specific plan and billing cycle"""
        plan = cls.get_plan(plan_id)
        if not plan:
            return 0.0
        
        if billing_cycle == 'annual':
            return plan['annual_price']
        else:
            return plan['monthly_price']
    
    @classmethod
    def calculate_savings(cls, plan_id: str) -> float:
        """Calculate annual savings compared to monthly billing"""
        plan = cls.get_plan(plan_id)
        if not plan:
            return 0.0
        
        monthly_cost = plan['monthly_price'] * 12
        annual_cost = plan['annual_price']
        return monthly_cost - annual_cost

