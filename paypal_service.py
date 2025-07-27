import os
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ..models.payment import Payment, Subscription, PricingPlan

class PayPalService:
    """Service for PayPal payment processing"""
    
    def __init__(self):
        # PayPal configuration
        self.client_id = os.getenv('PAYPAL_CLIENT_ID', 'demo_client_id')
        self.client_secret = os.getenv('PAYPAL_CLIENT_SECRET', 'demo_client_secret')
        self.sandbox = os.getenv('PAYPAL_SANDBOX', 'true').lower() == 'true'
        
        # PayPal API URLs
        if self.sandbox:
            self.base_url = 'https://api.sandbox.paypal.com'
            self.checkout_url = 'https://www.sandbox.paypal.com/checkoutnow'
        else:
            self.base_url = 'https://api.paypal.com'
            self.checkout_url = 'https://www.paypal.com/checkoutnow'
        
        self.payments_file = "payments.json"
        self.subscriptions_file = "subscriptions.json"
        self._access_token = None
        self._token_expires_at = None
    
    def _get_access_token(self) -> str:
        """Get PayPal access token"""
        # Check if token is still valid
        if (self._access_token and self._token_expires_at and 
            datetime.now() < self._token_expires_at):
            return self._access_token
        
        # Request new token
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        data = 'grant_type=client_credentials'
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret)
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self._access_token
            
        except requests.RequestException as e:
            # For demo purposes, return a mock token
            self._access_token = "demo_access_token"
            self._token_expires_at = datetime.now() + timedelta(hours=1)
            return self._access_token
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to PayPal API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._get_access_token()}',
            'PayPal-Request-Id': str(int(datetime.now().timestamp()))
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            # For demo purposes, return mock responses
            return self._get_mock_response(endpoint, method, data)
    
    def _get_mock_response(self, endpoint: str, method: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate mock responses for demo purposes"""
        if '/v2/checkout/orders' in endpoint and method == 'POST':
            return {
                'id': f'demo_order_{int(datetime.now().timestamp())}',
                'status': 'CREATED',
                'links': [
                    {
                        'href': f'{self.checkout_url}?token=demo_token',
                        'rel': 'approve',
                        'method': 'GET'
                    }
                ]
            }
        elif '/v2/checkout/orders' in endpoint and method == 'GET':
            return {
                'id': endpoint.split('/')[-1],
                'status': 'APPROVED',
                'payer': {
                    'payer_id': 'demo_payer_id',
                    'email_address': 'demo@example.com'
                },
                'purchase_units': [
                    {
                        'amount': {
                            'currency_code': 'USD',
                            'value': '29.00'
                        }
                    }
                ]
            }
        elif '/v1/billing/subscriptions' in endpoint and method == 'POST':
            return {
                'id': f'demo_subscription_{int(datetime.now().timestamp())}',
                'status': 'APPROVAL_PENDING',
                'links': [
                    {
                        'href': f'{self.checkout_url}?subscription_id=demo_sub',
                        'rel': 'approve',
                        'method': 'GET'
                    }
                ]
            }
        else:
            return {'status': 'success', 'id': 'demo_id'}
    
    def create_payment(self, amount: float, currency: str, plan_type: str, 
                      billing_cycle: str, return_url: str, cancel_url: str) -> Dict[str, Any]:
        """Create a PayPal payment"""
        order_data = {
            'intent': 'CAPTURE',
            'purchase_units': [
                {
                    'amount': {
                        'currency_code': currency,
                        'value': str(amount)
                    },
                    'description': f'{plan_type.title()} Plan - {billing_cycle.title()} Billing'
                }
            ],
            'application_context': {
                'return_url': return_url,
                'cancel_url': cancel_url,
                'brand_name': 'SEO Analyzer Pro',
                'landing_page': 'BILLING',
                'user_action': 'PAY_NOW'
            }
        }
        
        response = self._make_request('POST', '/v2/checkout/orders', order_data)
        
        # Store payment record
        payment = Payment()
        payment.paypal_payment_id = response['id']
        payment.amount = amount
        payment.currency = currency
        payment.plan_type = plan_type
        payment.billing_cycle = billing_cycle
        payment.status = 'pending'
        payment.created_at = datetime.now()
        
        self._save_payment(payment)
        
        # Extract approval URL
        approval_url = None
        for link in response.get('links', []):
            if link.get('rel') == 'approve':
                approval_url = link.get('href')
                break
        
        return {
            'payment_id': response['id'],
            'approval_url': approval_url,
            'status': response.get('status', 'CREATED')
        }
    
    def execute_payment(self, payment_id: str, payer_id: str) -> Dict[str, Any]:
        """Execute/capture a PayPal payment"""
        # Capture the order
        response = self._make_request('POST', f'/v2/checkout/orders/{payment_id}/capture')
        
        # Update payment record
        payment = self._get_payment_by_paypal_id(payment_id)
        if payment:
            payment.paypal_payer_id = payer_id
            payment.status = 'completed' if response.get('status') == 'COMPLETED' else 'failed'
            payment.updated_at = datetime.now()
            self._save_payment(payment)
        
        return {
            'payment_id': payment_id,
            'status': response.get('status', 'COMPLETED'),
            'capture_id': response.get('purchase_units', [{}])[0].get('payments', {}).get('captures', [{}])[0].get('id')
        }
    
    def create_subscription(self, plan_type: str, billing_cycle: str, 
                          return_url: str, cancel_url: str) -> Dict[str, Any]:
        """Create a PayPal subscription"""
        plan = PricingPlan.get_plan(plan_type)
        if not plan:
            raise ValueError(f"Invalid plan type: {plan_type}")
        
        amount = PricingPlan.get_price(plan_type, billing_cycle)
        
        subscription_data = {
            'plan_id': f'demo_plan_{plan_type}_{billing_cycle}',
            'subscriber': {
                'email_address': 'demo@example.com'
            },
            'application_context': {
                'return_url': return_url,
                'cancel_url': cancel_url,
                'brand_name': 'SEO Analyzer Pro',
                'user_action': 'SUBSCRIBE_NOW'
            }
        }
        
        response = self._make_request('POST', '/v1/billing/subscriptions', subscription_data)
        
        # Store subscription record
        subscription = Subscription()
        subscription.paypal_subscription_id = response['id']
        subscription.plan_type = plan_type
        subscription.billing_cycle = billing_cycle
        subscription.amount = amount
        subscription.status = 'pending'
        subscription.created_at = datetime.now()
        
        if billing_cycle == 'monthly':
            subscription.next_billing_date = datetime.now() + timedelta(days=30)
        else:
            subscription.next_billing_date = datetime.now() + timedelta(days=365)
        
        self._save_subscription(subscription)
        
        # Extract approval URL
        approval_url = None
        for link in response.get('links', []):
            if link.get('rel') == 'approve':
                approval_url = link.get('href')
                break
        
        return {
            'subscription_id': response['id'],
            'approval_url': approval_url,
            'status': response.get('status', 'APPROVAL_PENDING')
        }
    
    def cancel_subscription(self, subscription_id: str, reason: str = 'User requested cancellation') -> Dict[str, Any]:
        """Cancel a PayPal subscription"""
        cancel_data = {
            'reason': reason
        }
        
        response = self._make_request('POST', f'/v1/billing/subscriptions/{subscription_id}/cancel', cancel_data)
        
        # Update subscription record
        subscription = self._get_subscription_by_paypal_id(subscription_id)
        if subscription:
            subscription.status = 'cancelled'
            subscription.cancelled_at = datetime.now()
            subscription.updated_at = datetime.now()
            self._save_subscription(subscription)
        
        return {
            'subscription_id': subscription_id,
            'status': 'cancelled'
        }
    
    def get_payment_details(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment details from PayPal"""
        response = self._make_request('GET', f'/v2/checkout/orders/{payment_id}')
        return response
    
    def get_subscription_details(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details from PayPal"""
        response = self._make_request('GET', f'/v1/billing/subscriptions/{subscription_id}')
        return response
    
    def _load_payments(self) -> Dict[str, Any]:
        """Load payments from file"""
        if not os.path.exists(self.payments_file):
            return {}
        
        try:
            with open(self.payments_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_payments(self, payments: Dict[str, Any]):
        """Save payments to file"""
        with open(self.payments_file, 'w') as f:
            json.dump(payments, f, indent=2, default=str)
    
    def _save_payment(self, payment: Payment):
        """Save a single payment"""
        payments = self._load_payments()
        
        if not payment.id:
            payment.id = max([int(k) for k in payments.keys()] + [0]) + 1
        
        payments[str(payment.id)] = payment.to_dict()
        self._save_payments(payments)
    
    def _get_payment_by_paypal_id(self, paypal_id: str) -> Optional[Payment]:
        """Get payment by PayPal ID"""
        payments = self._load_payments()
        
        for payment_data in payments.values():
            if payment_data.get('paypal_payment_id') == paypal_id:
                return Payment.from_dict(payment_data)
        
        return None
    
    def _load_subscriptions(self) -> Dict[str, Any]:
        """Load subscriptions from file"""
        if not os.path.exists(self.subscriptions_file):
            return {}
        
        try:
            with open(self.subscriptions_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_subscriptions(self, subscriptions: Dict[str, Any]):
        """Save subscriptions to file"""
        with open(self.subscriptions_file, 'w') as f:
            json.dump(subscriptions, f, indent=2, default=str)
    
    def _save_subscription(self, subscription: Subscription):
        """Save a single subscription"""
        subscriptions = self._load_subscriptions()
        
        if not subscription.id:
            subscription.id = max([int(k) for k in subscriptions.keys()] + [0]) + 1
        
        subscriptions[str(subscription.id)] = subscription.to_dict()
        self._save_subscriptions(subscriptions)
    
    def _get_subscription_by_paypal_id(self, paypal_id: str) -> Optional[Subscription]:
        """Get subscription by PayPal ID"""
        subscriptions = self._load_subscriptions()
        
        for subscription_data in subscriptions.values():
            if subscription_data.get('paypal_subscription_id') == paypal_id:
                return Subscription.from_dict(subscription_data)
        
        return None
    
    def get_user_payments(self, user_id: int) -> List[Payment]:
        """Get all payments for a user"""
        payments = self._load_payments()
        user_payments = []
        
        for payment_data in payments.values():
            if payment_data.get('user_id') == user_id:
                user_payments.append(Payment.from_dict(payment_data))
        
        return sorted(user_payments, key=lambda x: x.created_at or datetime.min, reverse=True)
    
    def get_user_subscriptions(self, user_id: int) -> List[Subscription]:
        """Get all subscriptions for a user"""
        subscriptions = self._load_subscriptions()
        user_subscriptions = []
        
        for subscription_data in subscriptions.values():
            if subscription_data.get('user_id') == user_id:
                user_subscriptions.append(Subscription.from_dict(subscription_data))
        
        return sorted(user_subscriptions, key=lambda x: x.created_at or datetime.min, reverse=True)

