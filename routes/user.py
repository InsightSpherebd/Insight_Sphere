from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from models import Course, CourseVideo, CourseMaterial, Certificate, registrations

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's registered courses
    results = db.session.query(Course, registrations).join(
        registrations, Course.id == registrations.c.course_id
    ).filter(registrations.c.user_id == current_user.id).all()
    
    # Format data for template
    courses = []
    for course, reg in results:
        courses.append({
            'course': course,
            'registration_date': reg.registration_date,
            'payment_status': reg.payment_status,
            'completion_status': reg.completion_status,
            'certificate_issued': reg.certificate_issued
        })
    
    # Get user's certificates
    certificates = Certificate.query.filter_by(user_id=current_user.id).all()
    
    return render_template('user/dashboard.html',
                         title='My Dashboard',
                         courses=courses,
                         certificates=certificates)

@user_bp.route('/courses/<int:course_id>')
@login_required
def course_access(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if user is registered for this course
    if not course.is_registered(current_user):
        flash('You are not registered for this course.', 'warning')
        return redirect(url_for('user.dashboard'))
    
    # Check payment status
    registration = db.session.query(registrations).filter(
        (registrations.c.user_id == current_user.id) & 
        (registrations.c.course_id == course_id)
    ).first()
    payment_status = registration.payment_status if registration else None
    
    if payment_status != 'completed' and course.fee > 0:
        flash('Please complete your payment to access course materials.', 'warning')
        return redirect(url_for('public.course_payment', course_id=course_id))
    
    # Get course videos and materials
    videos = CourseVideo.query.filter_by(course_id=course_id, is_published=True).order_by(CourseVideo.order).all()
    materials = CourseMaterial.query.filter_by(course_id=course_id, is_published=True).order_by(CourseMaterial.order).all()
    
    return render_template('user/course_access.html',
                         title=course.title,
                         course=course,
                         videos=videos,
                         materials=materials)

@user_bp.route('/certificates')
@login_required
def certificates():
    certificates = Certificate.query.filter_by(user_id=current_user.id).all()
    
    return render_template('user/certificates.html',
                         title='My Certificates',
                         certificates=certificates)
