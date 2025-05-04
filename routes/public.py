from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, current_app
from flask_login import current_user, login_required
from sqlalchemy import desc
from app import db
from models import Course, User, SiteContent, registrations, Payment
from forms import CourseRegistrationForm
from utils.payment_service import PaymentService
from utils.email_service import EmailService

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    # Get site content for homepage sections
    hero_content = SiteContent.query.filter_by(section='hero', is_published=True).order_by(SiteContent.order).all()
    featured_courses = Course.query.filter_by(is_published=True, registration_open=True).order_by(desc(Course.created_at)).limit(3).all()
    
    return render_template('index.html', 
                         title='Welcome to Insight Sphere BD',
                         hero_content=hero_content,
                         featured_courses=featured_courses)

@public_bp.route('/about')
def about():
    # Get about page content
    mission_vision = SiteContent.query.filter_by(section='mission_vision', is_published=True).first()
    about_content = SiteContent.query.filter_by(section='about', is_published=True).order_by(SiteContent.order).all()
    
    # Get consultants
    consultants = User.query.filter_by(is_consultant=True).all()
    
    return render_template('about.html', 
                         title='About Us',
                         mission_vision=mission_vision,
                         about_content=about_content,
                         consultants=consultants)

@public_bp.route('/courses')
def courses():
    # Get all published courses
    all_courses = Course.query.filter_by(is_published=True).order_by(desc(Course.date)).all()
    
    return render_template('courses.html', 
                         title='Courses & Events',
                         courses=all_courses)

@public_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    
    if not course.is_published:
        abort(404)
    
    is_registered = False
    if current_user.is_authenticated:
        is_registered = course.is_registered(current_user)
    
    return render_template('course_detail.html', 
                         title=course.title,
                         course=course,
                         is_registered=is_registered)

@public_bp.route('/register/course/<int:course_id>', methods=['GET', 'POST'])
def register_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if not course.is_published or not course.registration_open:
        flash('Registration is not available for this course.', 'warning')
        return redirect(url_for('public.course_detail', course_id=course_id))
    
    # Check if user is already registered
    if current_user.is_authenticated and course.is_registered(current_user):
        flash('You are already registered for this course.', 'info')
        return redirect(url_for('public.course_detail', course_id=course_id))
    
    form = CourseRegistrationForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            user = current_user
        else:
            # Check if user with this email already exists
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash('An account with this email already exists. Please log in.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            # Create new user
            user = User(
                username=form.email.data.split('@')[0],
                email=form.email.data,
                full_name=form.full_name.data,
                phone=form.phone.data
            )
            user.set_password('temporary')  # Set a temporary password
            db.session.add(user)
            db.session.commit()
        
        # Register user for course
        if not course.is_registered(user):
            user.courses.append(course)
            db.session.commit()
            
            # Send registration confirmation email
            EmailService.send_registration_confirmation(user, course)
            
            # If course has a fee, redirect to payment
            if course.fee > 0:
                flash('Registration successful! Please proceed to payment.', 'success')
                return redirect(url_for('public.course_payment', course_id=course_id))
            else:
                flash('Registration successful!', 'success')
                return redirect(url_for('public.course_detail', course_id=course_id))
    
    return render_template('register.html', 
                         title=f'Register for {course.title}',
                         course=course,
                         form=form)

@public_bp.route('/course/<int:course_id>/payment')
@login_required
def course_payment(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if user is registered
    if not course.is_registered(current_user):
        flash('You must register for this course before payment.', 'warning')
        return redirect(url_for('public.register_course', course_id=course_id))
    
    # Check if payment is already completed
    stmt = db.select([registrations.c.payment_status]).where(
        (registrations.c.user_id == current_user.id) & 
        (registrations.c.course_id == course_id)
    )
    payment_status = db.session.execute(stmt).scalar()
    
    if payment_status == 'completed':
        flash('You have already paid for this course.', 'info')
        return redirect(url_for('user.dashboard'))
    
    # Show payment options
    return render_template('payment_options.html',
                         title='Payment Options',
                         course=course)

@public_bp.route('/course/<int:course_id>/payment/process')
@login_required
def process_payment(course_id):
    course = Course.query.get_or_404(course_id)
    payment_method = request.args.get('method', 'stripe')
    
    # Check if user is registered
    if not course.is_registered(current_user):
        flash('You must register for this course before payment.', 'warning')
        return redirect(url_for('public.register_course', course_id=course_id))
    
    # Check if payment is already completed
    stmt = db.select([registrations.c.payment_status]).where(
        (registrations.c.user_id == current_user.id) & 
        (registrations.c.course_id == course_id)
    )
    payment_status = db.session.execute(stmt).scalar()
    
    if payment_status == 'completed':
        flash('You have already paid for this course.', 'info')
        return redirect(url_for('user.dashboard'))
    
    # Create payment session
    checkout_url = PaymentService.create_payment_session(
        user_id=current_user.id,
        course_id=course_id,
        payment_method=payment_method
    )
    
    if checkout_url:
        return redirect(checkout_url)
    else:
        flash('Error creating payment session. Please try again.', 'danger')
        return redirect(url_for('public.course_payment', course_id=course_id))

@public_bp.route('/payment/success/<int:payment_id>')
@login_required
def payment_success(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    # Verify that the payment belongs to the current user
    if payment.user_id != current_user.id:
        abort(403)
    
    # Handle successful payment
    if PaymentService.handle_payment_success(payment_id):
        flash('Payment successful! You are now registered for the course.', 'success')
    else:
        flash('Error processing payment confirmation.', 'warning')
    
    return render_template('payment_success.html', 
                         title='Payment Successful',
                         payment=payment,
                         course=payment.course)

@public_bp.route('/payment/cancel/<int:payment_id>')
@login_required
def payment_cancel(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    
    # Verify that the payment belongs to the current user
    if payment.user_id != current_user.id:
        abort(403)
    
    # Handle canceled payment
    PaymentService.handle_payment_cancel(payment_id)
    
    return render_template('payment_cancel.html', 
                         title='Payment Canceled',
                         payment=payment,
                         course=payment.course)
