from flask import current_app, render_template
from flask_mail import Message
from app import mail
import logging

class EmailService:
    @staticmethod
    def send_email(subject, recipients, template, **kwargs):
        """
        Send email using a template
        
        Args:
            subject: Email subject
            recipients: List of email recipients
            template: Template file path (without .html extension)
            **kwargs: Variables to pass to the template
        """
        try:
            sender = current_app.config['MAIL_DEFAULT_SENDER']
            msg = Message(subject, sender=sender, recipients=recipients)
            msg.html = render_template(f"emails/{template}.html", **kwargs)
            mail.send(msg)
            logging.info(f"Email sent to {recipients} with subject: {subject}")
            return True
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    def send_registration_confirmation(user, course):
        """Send registration confirmation email"""
        return EmailService.send_email(
            subject=f"Registration Confirmed: {course.title}",
            recipients=[user.email],
            template="registration_confirmation",
            user=user,
            course=course
        )
    
    @staticmethod
    def send_payment_receipt(user, payment):
        """Send payment receipt email"""
        return EmailService.send_email(
            subject=f"Payment Receipt: {payment.course.title}",
            recipients=[user.email],
            template="payment_receipt",
            user=user,
            payment=payment,
            course=payment.course
        )
    
    @staticmethod
    def send_certificate(user, certificate):
        """Send certificate email"""
        return EmailService.send_email(
            subject=f"Certificate for {certificate.course.title}",
            recipients=[user.email],
            template="certificate_email",
            user=user,
            certificate=certificate,
            course=certificate.course
        )
