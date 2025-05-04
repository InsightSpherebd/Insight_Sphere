import os
import requests
import stripe
import logging
import json
from flask import current_app, url_for
from datetime import datetime
from urllib.parse import urlencode
from models import Payment

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class PaymentService:
    @staticmethod
    def create_payment_session(user_id, course_id, payment_method='stripe'):
        """
        Create a payment session based on the selected payment method
        
        Args:
            user_id: User ID
            course_id: Course ID
            payment_method: Payment method (stripe, sslcommerz, manual)
            
        Returns:
            Checkout session URL if successful, None otherwise
        """
        from app import db
        from models import User, Course
        
        try:
            # Get user and course
            user = User.query.get(user_id)
            course = Course.query.get(course_id)
            
            if not user or not course:
                return None
                
            # Check if payment method is supported for this course
            if payment_method == 'stripe' and not course.allow_cards:
                return None
            elif payment_method == 'sslcommerz' and not (course.allow_bkash or course.allow_nagad or course.allow_rocket):
                return None
            
            # Based on the payment method, create the appropriate session
            if payment_method == 'stripe':
                return PaymentService.create_stripe_session(user_id, course_id, course.fee, 'bdt')
            elif payment_method == 'sslcommerz':
                return PaymentService.create_sslcommerz_session(user_id, course_id, course.fee, 'BDT')
            else:
                # For manual payments, create a pending payment record and return success
                payment = Payment(
                    user_id=user_id,
                    course_id=course_id,
                    amount=course.fee,
                    currency='BDT',
                    payment_method='manual',
                    payment_status='pending'
                )
                
                db.session.add(payment)
                db.session.commit()
                
                domain = current_app.config['BASE_URL']
                return domain + url_for('public.payment_success', payment_id=payment.id, manual=True)
                
        except Exception as e:
            logging.error(f"Error creating payment session: {str(e)}")
            return None
    
    @staticmethod
    def create_stripe_session(user_id, course_id, amount, currency='bdt'):
        """
        Create a Stripe checkout session
        
        Args:
            user_id: User ID
            course_id: Course ID
            amount: Payment amount
            currency: Currency code (default: 'bdt')
            
        Returns:
            Checkout session URL if successful, None otherwise
        """
        from app import db
        from models import User, Course
        
        try:
            # Get user and course
            user = User.query.get(user_id)
            course = Course.query.get(course_id)
            
            if not user or not course:
                return None
            
            # Create a new payment record
            payment = Payment(
                user_id=user_id,
                course_id=course_id,
                amount=amount,
                currency=currency,
                payment_method='stripe',
                payment_status='pending'
            )
            
            db.session.add(payment)
            db.session.commit()
            
            # Create Stripe checkout session
            domain = current_app.config['BASE_URL']
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': course.title,
                            'description': f"Registration for {course.title}"
                        },
                        'unit_amount': int(amount * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=domain + url_for('public.payment_success', payment_id=payment.id),
                cancel_url=domain + url_for('public.payment_cancel', payment_id=payment.id),
                metadata={
                    'payment_id': payment.id,
                    'user_id': user_id,
                    'course_id': course_id
                }
            )
            
            # Update payment with transaction ID
            payment.transaction_id = checkout_session.id
            db.session.commit()
            
            return checkout_session.url
            
        except Exception as e:
            logging.error(f"Error creating checkout session: {str(e)}")
            return None
    
    @staticmethod
    def handle_payment_success(payment_id):
        """
        Handle successful payment
        
        Args:
            payment_id: Payment ID
            
        Returns:
            True if successful, False otherwise
        """
        from app import db
        
        try:
            # Get payment
            payment = Payment.query.get(payment_id)
            
            if not payment:
                return False
            
            # Update payment status
            payment.payment_status = 'completed'
            payment.payment_date = datetime.utcnow()
            
            # Update registration status
            from models import registrations
            stmt = registrations.update().where(
                (registrations.c.user_id == payment.user_id) & 
                (registrations.c.course_id == payment.course_id)
            ).values(payment_status='completed')
            
            db.session.execute(stmt)
            db.session.commit()
            
            # Send payment receipt email
            from utils.email_service import EmailService
            EmailService.send_payment_receipt(payment.user, payment)
            
            return True
            
        except Exception as e:
            logging.error(f"Error handling payment success: {str(e)}")
            return False
    
    @staticmethod
    def create_sslcommerz_session(user_id, course_id, amount, currency='BDT'):
        """
        Create an SSLCommerz payment session
        
        Args:
            user_id: User ID
            course_id: Course ID
            amount: Payment amount
            currency: Currency code (default: 'BDT')
            
        Returns:
            SSLCommerz payment URL if successful, None otherwise
        """
        from app import db
        from models import User, Course
        
        try:
            # Get user and course
            user = User.query.get(user_id)
            course = Course.query.get(course_id)
            
            if not user or not course:
                return None
            
            # Create a new payment record
            payment = Payment(
                user_id=user_id,
                course_id=course_id,
                amount=amount,
                currency=currency,
                payment_method='sslcommerz',
                payment_status='pending'
            )
            
            db.session.add(payment)
            db.session.commit()
            
            # Prepare SSLCommerz parameters
            store_id = current_app.config['SSLCOMMERZ_STORE_ID']
            store_passwd = current_app.config['SSLCOMMERZ_STORE_PASSWORD']
            is_sandbox = current_app.config['SSLCOMMERZ_SANDBOX']
            
            domain = current_app.config['BASE_URL']
            success_url = domain + url_for('public.payment_success', payment_id=payment.id)
            fail_url = domain + url_for('public.payment_cancel', payment_id=payment.id)
            cancel_url = domain + url_for('public.payment_cancel', payment_id=payment.id)
            
            # Build the request parameters
            post_data = {
                'store_id': store_id,
                'store_passwd': store_passwd,
                'total_amount': amount,
                'currency': currency,
                'tran_id': f"TXNID{payment.id}",
                'success_url': success_url,
                'fail_url': fail_url,
                'cancel_url': cancel_url,
                'cus_name': user.full_name,
                'cus_email': user.email,
                'cus_phone': user.phone,
                'product_category': 'Course',
                'product_profile': 'training',
                'product_name': course.title,
                'shipping_method': 'No',
                'emi_option': 0,
                'num_of_item': 1,
                'product_amount': amount
            }
            
            # Determine the URL for sandbox or production
            if is_sandbox:
                url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
            else:
                url = "https://securepay.sslcommerz.com/gwprocess/v4/api.php"
            
            # Make the API request to SSLCommerz
            response = requests.post(url, data=post_data)
            data = response.json()
            
            if data.get('status') == 'SUCCESS':
                # Update payment with transaction ID
                payment.transaction_id = data.get('sessionkey')
                db.session.commit()
                
                return data.get('GatewayPageURL')
            else:
                logging.error(f"SSLCommerz Error: {data.get('failedreason')}")
                return None
            
        except Exception as e:
            logging.error(f"Error creating SSLCommerz session: {str(e)}")
            return None
    
    @staticmethod
    def handle_payment_cancel(payment_id):
        """
        Handle canceled payment
        
        Args:
            payment_id: Payment ID
            
        Returns:
            True if successful, False otherwise
        """
        from app import db
        
        try:
            # Get payment
            payment = Payment.query.get(payment_id)
            
            if not payment:
                return False
            
            # Update payment status
            payment.payment_status = 'canceled'
            db.session.commit()
            
            return True
            
        except Exception as e:
            logging.error(f"Error handling payment cancel: {str(e)}")
            return False
