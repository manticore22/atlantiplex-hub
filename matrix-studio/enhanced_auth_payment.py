"""
Enhanced Payment & Authentication System for Atlantiplex Lightning Studio
Integrates Stripe, PayPal, OAuth (Google), Phone Auth, and 2FA
"""

import json
import logging
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from flask import current_app, request, jsonify
from typing import Dict, List, Optional, Any
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPaymentManager:
    """Enhanced payment manager supporting Stripe, PayPal, and more"""
    
    def __init__(self):
        self.stripe_available = False
        self.paypal_available = False
        self.stripe = None
        self.paypal = None
        
        # Initialize Stripe
        try:
            import stripe
            self.stripe = stripe
            stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
            self.stripe_available = True
            logger.info("✅ Stripe initialized")
        except ImportError:
            logger.warning("⚠️ Stripe library not installed")
        
        # Initialize PayPal
        self.paypal_client_id = current_app.config.get('PAYPAL_CLIENT_ID')
        self.paypal_client_secret = current_app.config.get('PAYPAL_CLIENT_SECRET')
        self.paypal_mode = current_app.config.get('PAYPAL_MODE', 'sandbox')  # or 'live'
        if self.paypal_client_id and self.paypal_client_secret:
            self.paypal_available = True
            logger.info("✅ PayPal configured")
    
    # ==================== STRIPE CARD PAYMENTS ====================
    
    def create_stripe_payment_intent(self, amount: int, currency: str = 'usd', 
                                   customer_id: str = None, metadata: dict = None) -> Dict:
        """Create a Stripe PaymentIntent for one-time charges"""
        if not self.stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
        except Exception as e:
            logger.error(f"Stripe PaymentIntent error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def confirm_stripe_payment(self, payment_intent_id: str, payment_method_id: str) -> Dict:
        """Confirm a Stripe payment with payment method"""
        if not self.stripe_available:
            return {'success': False, 'error': 'Stripe not available'}
        
        try:
            intent = self.stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method_id
            )
            
            return {
                'success': True,
                'status': intent.status,
                'payment_intent_id': intent.id
            }
        except Exception as e:
            logger.error(f"Stripe confirm error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ==================== PAYPAL PAYMENTS ====================
    
    def get_paypal_access_token(self) -> Optional[str]:
        """Get PayPal OAuth access token"""
        if not self.paypal_available:
            return None
        
        base_url = "https://api-m.sandbox.paypal.com" if self.paypal_mode == 'sandbox' else "https://api-m.paypal.com"
        
        try:
            response = requests.post(
                f"{base_url}/v1/oauth2/token",
                headers={"Accept": "application/json", "Accept-Language": "en_US"},
                auth=(self.paypal_client_id, self.paypal_client_secret),
                data={"grant_type": "client_credentials"}
            )
            
            if response.status_code == 200:
                return response.json()['access_token']
            else:
                logger.error(f"PayPal auth error: {response.text}")
                return None
        except Exception as e:
            logger.error(f"PayPal token error: {str(e)}")
            return None
    
    def create_paypal_order(self, amount: float, currency: str = 'USD', 
                          description: str = '', return_url: str = '', 
                          cancel_url: str = '') -> Dict:
        """Create a PayPal order for payment"""
        if not self.paypal_available:
            return {'success': False, 'error': 'PayPal not configured'}
        
        access_token = self.get_paypal_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to authenticate with PayPal'}
        
        base_url = "https://api-m.sandbox.paypal.com" if self.paypal_mode == 'sandbox' else "https://api-m.paypal.com"
        
        try:
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}"
                    },
                    "description": description
                }],
                "application_context": {
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                    "brand_name": "Atlantiplex Lightning Studio",
                    "landing_page": "BILLING",
                    "user_action": "PAY_NOW"
                }
            }
            
            response = requests.post(
                f"{base_url}/v2/checkout/orders",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                },
                json=order_data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'order_id': result['id'],
                    'approval_url': next((link['href'] for link in result['links'] if link['rel'] == 'approve'), None)
                }
            else:
                logger.error(f"PayPal order error: {response.text}")
                return {'success': False, 'error': 'Failed to create PayPal order'}
                
        except Exception as e:
            logger.error(f"PayPal create order error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def capture_paypal_order(self, order_id: str) -> Dict:
        """Capture/complete a PayPal order"""
        if not self.paypal_available:
            return {'success': False, 'error': 'PayPal not configured'}
        
        access_token = self.get_paypal_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to authenticate with PayPal'}
        
        base_url = "https://api-m.sandbox.paypal.com" if self.paypal_mode == 'sandbox' else "https://api-m.paypal.com"
        
        try:
            response = requests.post(
                f"{base_url}/v2/checkout/orders/{order_id}/capture",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'status': result['status'],
                    'capture_id': result['purchase_units'][0]['payments']['captures'][0]['id']
                }
            else:
                logger.error(f"PayPal capture error: {response.text}")
                return {'success': False, 'error': 'Failed to capture payment'}
                
        except Exception as e:
            logger.error(f"PayPal capture error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_paypal_subscription(self, plan_id: str, subscriber_email: str, 
                                 return_url: str, cancel_url: str) -> Dict:
        """Create a PayPal subscription"""
        if not self.paypal_available:
            return {'success': False, 'error': 'PayPal not configured'}
        
        access_token = self.get_paypal_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to authenticate with PayPal'}
        
        base_url = "https://api-m.sandbox.paypal.com" if self.paypal_mode == 'sandbox' else "https://api-m.paypal.com"
        
        try:
            subscription_data = {
                "plan_id": plan_id,
                "subscriber": {
                    "email_address": subscriber_email
                },
                "application_context": {
                    "brand_name": "Atlantiplex Lightning Studio",
                    "locale": "en-US",
                    "shipping_preference": "NO_SHIPPING",
                    "user_action": "SUBSCRIBE_NOW",
                    "payment_method": {
                        "payer_selected": "PAYPAL",
                        "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
                    },
                    "return_url": return_url,
                    "cancel_url": cancel_url
                }
            }
            
            response = requests.post(
                f"{base_url}/v1/billing/subscriptions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                },
                json=subscription_data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'subscription_id': result['id'],
                    'approval_url': next((link['href'] for link in result['links'] if link['rel'] == 'approve'), None),
                    'status': result['status']
                }
            else:
                logger.error(f"PayPal subscription error: {response.text}")
                return {'success': False, 'error': 'Failed to create subscription'}
                
        except Exception as e:
            logger.error(f"PayPal subscription error: {str(e)}")
            return {'success': False, 'error': str(e)}


class AuthenticationManager:
    """Enhanced authentication with OAuth, Phone, and 2FA"""
    
    def __init__(self):
        self.google_client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        self.google_client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        self.twilio_sid = current_app.config.get('TWILIO_SID')
        self.twilio_token = current_app.config.get('TWILIO_TOKEN')
        self.twilio_phone = current_app.config.get('TWILIO_PHONE')
        
        # In-memory storage for verification codes (use Redis in production)
        self.phone_verifications = {}
        self.oauth_states = {}
    
    # ==================== EMAIL/PASSWORD AUTH ====================
    
    def register_with_email(self, email: str, password: str, phone: str = None) -> Dict:
        """Register new user with email and password"""
        from werkzeug.security import generate_password_hash
        
        try:
            # Check if email already exists
            if self._email_exists(email):
                return {'success': False, 'error': 'Email already registered'}
            
            # Hash password
            password_hash = generate_password_hash(password)
            
            # Create user
            user_id = self._create_user({
                'email': email,
                'password_hash': password_hash,
                'phone': phone,
                'auth_method': 'email',
                'created_at': datetime.now().isoformat(),
                'email_verified': False,
                'phone_verified': False,
                'two_factor_enabled': False
            })
            
            # Send verification email
            self._send_verification_email(email, user_id)
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'Registration successful. Please verify your email.'
            }
            
        except Exception as e:
            logger.error(f"Email registration error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def login_with_email(self, email: str, password: str, two_factor_code: str = None) -> Dict:
        """Login with email and password, optionally with 2FA"""
        from werkzeug.security import check_password_hash
        
        try:
            user = self._get_user_by_email(email)
            if not user:
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Verify password
            if not check_password_hash(user['password_hash'], password):
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Check if 2FA is enabled
            if user.get('two_factor_enabled'):
                if not two_factor_code:
                    return {
                        'success': False, 
                        'error': '2FA required',
                        'two_factor_required': True
                    }
                
                if not self._verify_totp(user['two_factor_secret'], two_factor_code):
                    return {'success': False, 'error': 'Invalid 2FA code'}
            
            # Generate JWT token
            token = self._generate_jwt(user['id'])
            
            return {
                'success': True,
                'token': token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'phone': user.get('phone'),
                    'two_factor_enabled': user.get('two_factor_enabled', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Email login error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ==================== PHONE/SMS AUTH ====================
    
    def send_phone_verification(self, phone_number: str) -> Dict:
        """Send SMS verification code"""
        if not self.twilio_sid or not self.twilio_token:
            return {'success': False, 'error': 'SMS service not configured'}
        
        try:
            from twilio.rest import Client
            
            # Generate 6-digit code
            import random
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Store code with expiration (10 minutes)
            self.phone_verifications[phone_number] = {
                'code': code,
                'expires': datetime.now() + timedelta(minutes=10)
            }
            
            # Send SMS
            client = Client(self.twilio_sid, self.twilio_token)
            message = client.messages.create(
                body=f"Your Atlantiplex verification code is: {code}",
                from_=self.twilio_phone,
                to=phone_number
            )
            
            return {
                'success': True,
                'message': 'Verification code sent',
                'sid': message.sid
            }
            
        except Exception as e:
            logger.error(f"SMS send error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def verify_phone_code(self, phone_number: str, code: str) -> Dict:
        """Verify phone SMS code"""
        try:
            verification = self.phone_verifications.get(phone_number)
            
            if not verification:
                return {'success': False, 'error': 'No verification pending'}
            
            if datetime.now() > verification['expires']:
                del self.phone_verifications[phone_number]
                return {'success': False, 'error': 'Verification code expired'}
            
            if verification['code'] != code:
                return {'success': False, 'error': 'Invalid verification code'}
            
            # Code verified - clean up
            del self.phone_verifications[phone_number]
            
            return {'success': True, 'message': 'Phone verified successfully'}
            
        except Exception as e:
            logger.error(f"Phone verification error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def register_with_phone(self, phone_number: str, code: str, password: str) -> Dict:
        """Complete registration with phone verification"""
        # Verify the code first
        verify_result = self.verify_phone_code(phone_number, code)
        if not verify_result['success']:
            return verify_result
        
        try:
            from werkzeug.security import generate_password_hash
            
            # Check if phone already registered
            if self._phone_exists(phone_number):
                return {'success': False, 'error': 'Phone number already registered'}
            
            # Create user
            password_hash = generate_password_hash(password)
            user_id = self._create_user({
                'phone': phone_number,
                'password_hash': password_hash,
                'auth_method': 'phone',
                'phone_verified': True,
                'created_at': datetime.now().isoformat(),
                'two_factor_enabled': False
            })
            
            # Generate token
            token = self._generate_jwt(user_id)
            
            return {
                'success': True,
                'token': token,
                'user_id': user_id,
                'message': 'Registration successful'
            }
            
        except Exception as e:
            logger.error(f"Phone registration error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ==================== GOOGLE OAUTH ====================
    
    def get_google_auth_url(self, redirect_uri: str) -> Dict:
        """Get Google OAuth authorization URL"""
        if not self.google_client_id:
            return {'success': False, 'error': 'Google OAuth not configured'}
        
        try:
            import secrets
            state = secrets.token_urlsafe(32)
            self.oauth_states[state] = {
                'created_at': datetime.now(),
                'redirect_uri': redirect_uri
            }
            
            auth_url = (
                "https://accounts.google.com/o/oauth2/v2/auth?"
                f"client_id={self.google_client_id}&"
                f"redirect_uri={redirect_uri}&"
                "response_type=code&"
                "scope=openid%20email%20profile&"
                f"state={state}&"
                "access_type=offline&"
                "prompt=consent"
            )
            
            return {
                'success': True,
                'auth_url': auth_url,
                'state': state
            }
            
        except Exception as e:
            logger.error(f"Google auth URL error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_google_callback(self, code: str, state: str) -> Dict:
        """Handle Google OAuth callback"""
        if not self.google_client_id or not self.google_client_secret:
            return {'success': False, 'error': 'Google OAuth not configured'}
        
        # Verify state
        if state not in self.oauth_states:
            return {'success': False, 'error': 'Invalid state parameter'}
        
        try:
            # Exchange code for tokens
            token_data = {
                'code': code,
                'client_id': self.google_client_id,
                'client_secret': self.google_client_secret,
                'redirect_uri': self.oauth_states[state]['redirect_uri'],
                'grant_type': 'authorization_code'
            }
            
            token_response = requests.post(
                'https://oauth2.googleapis.com/token',
                data=token_data
            )
            
            if token_response.status_code != 200:
                return {'success': False, 'error': 'Failed to get access token'}
            
            tokens = token_response.json()
            
            # Get user info
            userinfo_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f"Bearer {tokens['access_token']}"}
            )
            
            if userinfo_response.status_code != 200:
                return {'success': False, 'error': 'Failed to get user info'}
            
            google_user = userinfo_response.json()
            
            # Check if user exists
            user = self._get_user_by_email(google_user['email'])
            
            if user:
                # Existing user - log them in
                token = self._generate_jwt(user['id'])
                return {
                    'success': True,
                    'token': token,
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'name': google_user.get('name'),
                        'picture': google_user.get('picture'),
                        'auth_method': 'google'
                    },
                    'new_user': False
                }
            else:
                # New user - create account
                user_id = self._create_user({
                    'email': google_user['email'],
                    'name': google_user.get('name'),
                    'picture': google_user.get('picture'),
                    'auth_method': 'google',
                    'google_id': google_user['id'],
                    'email_verified': True,
                    'created_at': datetime.now().isoformat(),
                    'two_factor_enabled': False
                })
                
                token = self._generate_jwt(user_id)
                
                return {
                    'success': True,
                    'token': token,
                    'user': {
                        'id': user_id,
                        'email': google_user['email'],
                        'name': google_user.get('name'),
                        'picture': google_user.get('picture'),
                        'auth_method': 'google'
                    },
                    'new_user': True
                }
            
        except Exception as e:
            logger.error(f"Google callback error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ==================== 2FA / AUTHENTICATOR ====================
    
    def setup_two_factor(self, user_id: str) -> Dict:
        """Setup 2FA for user - returns QR code"""
        try:
            # Generate secret
            secret = pyotp.random_base32()
            
            # Get user email
            user = self._get_user_by_id(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Create TOTP provisioning URI
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=user['email'],
                issuer_name="Atlantiplex Lightning Studio"
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Temporarily store secret (user must confirm)
            self._store_pending_2fa_secret(user_id, secret)
            
            return {
                'success': True,
                'secret': secret,  # Show this as backup
                'qr_code': f"data:image/png;base64,{qr_base64}",
                'manual_entry_key': secret,
                'message': 'Scan QR code with authenticator app, then verify with a code'
            }
            
        except Exception as e:
            logger.error(f"2FA setup error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def verify_and_enable_two_factor(self, user_id: str, code: str) -> Dict:
        """Verify 2FA code and enable 2FA"""
        try:
            # Get pending secret
            secret = self._get_pending_2fa_secret(user_id)
            if not secret:
                return {'success': False, 'error': '2FA setup not initiated'}
            
            # Verify code
            totp = pyotp.TOTP(secret)
            if not totp.verify(code, valid_window=1):
                return {'success': False, 'error': 'Invalid verification code'}
            
            # Enable 2FA
            self._enable_two_factor(user_id, secret)
            
            # Generate backup codes
            backup_codes = self._generate_backup_codes(user_id)
            
            return {
                'success': True,
                'message': '2FA enabled successfully',
                'backup_codes': backup_codes,
                'warning': 'Save these backup codes securely!'
            }
            
        except Exception as e:
            logger.error(f"2FA verification error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def disable_two_factor(self, user_id: str, password: str, code: str = None) -> Dict:
        """Disable 2FA for user"""
        try:
            user = self._get_user_by_id(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Verify password
            from werkzeug.security import check_password_hash
            if not check_password_hash(user['password_hash'], password):
                return {'success': False, 'error': 'Invalid password'}
            
            # If 2FA is enabled, verify the code
            if user.get('two_factor_enabled') and code:
                if not self._verify_totp(user['two_factor_secret'], code):
                    return {'success': False, 'error': 'Invalid 2FA code'}
            
            # Disable 2FA
            self._disable_two_factor(user_id)
            
            return {
                'success': True,
                'message': '2FA disabled successfully'
            }
            
        except Exception as e:
            logger.error(f"2FA disable error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _verify_totp(self, secret: str, code: str) -> bool:
        """Verify TOTP code"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=1)
        except:
            return False
    
    def _generate_backup_codes(self, user_id: str) -> List[str]:
        """Generate single-use backup codes"""
        import secrets
        codes = [''.join([str(secrets.randbelow(10)) for _ in range(8)]) for _ in range(10)]
        # Store hashed codes (implementation depends on your DB)
        return codes
    
    # ==================== HELPER METHODS (DB) ====================
    
    def _email_exists(self, email: str) -> bool:
        """Check if email exists"""
        # Implement with your database
        return False
    
    def _phone_exists(self, phone: str) -> bool:
        """Check if phone exists"""
        # Implement with your database
        return False
    
    def _get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        # Implement with your database
        return None
    
    def _get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        # Implement with your database
        return None
    
    def _create_user(self, user_data: Dict) -> str:
        """Create new user, return user_id"""
        # Implement with your database
        import uuid
        return str(uuid.uuid4())
    
    def _generate_jwt(self, user_id: str) -> str:
        """Generate JWT token"""
        import jwt
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    def _send_verification_email(self, email: str, user_id: str):
        """Send verification email"""
        # Implement with your email service
        pass
    
    def _store_pending_2fa_secret(self, user_id: str, secret: str):
        """Temporarily store 2FA secret"""
        # Implement with your cache/database
        pass
    
    def _get_pending_2fa_secret(self, user_id: str) -> Optional[str]:
        """Get pending 2FA secret"""
        # Implement with your cache/database
        return None
    
    def _enable_two_factor(self, user_id: str, secret: str):
        """Enable 2FA for user"""
        # Implement with your database
        pass
    
    def _disable_two_factor(self, user_id: str):
        """Disable 2FA for user"""
        # Implement with your database
        pass


# Export managers
enhanced_payment_manager = None
auth_manager = None

def init_payment_and_auth(app):
    """Initialize payment and auth managers"""
    global enhanced_payment_manager, auth_manager
    with app.app_context():
        enhanced_payment_manager = EnhancedPaymentManager()
        auth_manager = AuthenticationManager()
        logger.info("✅ Enhanced Payment & Auth managers initialized")