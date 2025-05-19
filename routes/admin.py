from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy import desc
from app import db
from werkzeug.utils import secure_filename
import os
import time
from models import (User, Course, CourseVideo, CourseMaterial, 
                   SiteContent, Certificate, CertificateTemplate,
                   Payment, registrations)
from forms import (CourseForm, CourseVideoForm, CourseMaterialForm, 
                  SiteContentForm, ConsultantForm, CertificateTemplateForm)
from utils.certificate_generator import CertificateGenerator
from werkzeug.utils import secure_filename
import os
import csv
import io
import datetime
import os
import glob

admin_bp = Blueprint('admin', __name__)

# Admin access decorator
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return login_required(decorated_function)

# Super admin access decorator
def super_admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_super_admin():
            abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return login_required(decorated_function)

@admin_bp.route('/')
@admin_required
def dashboard():
    # Get counts for dashboard
    course_count = Course.query.count()
    user_count = User.query.filter_by(role='user').count()
    payment_total = db.session.query(db.func.sum(Payment.amount)).filter_by(payment_status='completed').scalar() or 0
    recent_registrations = db.session.query(
        User, Course
    ).join(
        registrations, User.id == registrations.c.user_id
    ).join(
        Course, Course.id == registrations.c.course_id
    ).order_by(
        desc(registrations.c.registration_date)
    ).limit(5).all()

    return render_template('admin/dashboard.html',
                         title='Admin Dashboard',
                         course_count=course_count,
                         user_count=user_count,
                         payment_total=payment_total,
                         recent_registrations=recent_registrations)

# Content Management
@admin_bp.route('/content')
@admin_required
def content_editor():
    # Get all site content sections
    hero_content = SiteContent.query.filter_by(section='hero').order_by(SiteContent.order).all()
    about_content = SiteContent.query.filter_by(section='about').order_by(SiteContent.order).all()
    mission_vision = SiteContent.query.filter_by(section='mission_vision').first()

    return render_template('admin/content_editor.html',
                         title='Content Editor',
                         hero_content=hero_content,
                         about_content=about_content,
                         mission_vision=mission_vision)

@admin_bp.route('/content/add', methods=['GET', 'POST'])
@admin_required
def content_add():
    form = SiteContentForm()
    if form.validate_on_submit():
        content = SiteContent(
            section=form.section.data,
            title=form.title.data,
            content=form.content.data,
            media_url=form.media_url.data,
            order=form.order.data,
            is_published=form.is_published.data,
            editor_id=current_user.id
        )
        db.session.add(content)
        db.session.commit()
        flash('Content added successfully!', 'success')
        return redirect(url_for('admin.content_editor'))

    return render_template('admin/content_form.html',
                         title='Add Content',
                         form=form)

@admin_bp.route('/content/edit/<int:content_id>', methods=['GET', 'POST'])
@admin_required
def content_edit(content_id):
    content = SiteContent.query.get_or_404(content_id)
    form = SiteContentForm(obj=content)

    if form.validate_on_submit():
        content.section = form.section.data
        content.title = form.title.data
        content.content = form.content.data
        content.media_url = form.media_url.data
        content.order = form.order.data
        content.is_published = form.is_published.data
        content.editor_id = current_user.id

        db.session.commit()
        flash('Content updated successfully!', 'success')
        return redirect(url_for('admin.content_editor'))

    return render_template('admin/content_form.html',
                         title='Edit Content',
                         form=form)

@admin_bp.route('/content/delete/<int:content_id>', methods=['POST'])
@admin_required
def content_delete(content_id):
    content = SiteContent.query.get_or_404(content_id)
    db.session.delete(content)
    db.session.commit()
    flash('Content deleted successfully!', 'success')
    return redirect(url_for('admin.content_editor'))

# Course Management
@admin_bp.route('/courses')
@admin_required
def course_manager():
    courses = Course.query.order_by(desc(Course.created_at)).all()
    return render_template('admin/course_manager.html',
                         title='Course Manager',
                         courses=courses)

@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@admin_required
def course_add():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            duration=form.duration.data,
            fee=form.fee.data,
            capacity=form.capacity.data,
            location=form.location.data,
            is_online=form.is_online.data,
            session_link=form.session_link.data,
            is_published=form.is_published.data,
            registration_open=form.registration_open.data,
            allow_bkash=form.allow_bkash.data,
            allow_nagad=form.allow_nagad.data,
            allow_rocket=form.allow_rocket.data,
            allow_cards=form.allow_cards.data,
            creator_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash('Course added successfully!', 'success')
        return redirect(url_for('admin.course_manager'))

    return render_template('admin/course_form.html',
                         title='Add Course',
                         form=form)

@admin_bp.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@admin_required
def course_edit(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)

    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.date = form.date.data
        course.duration = form.duration.data
        course.fee = form.fee.data
        course.capacity = form.capacity.data
        course.location = form.location.data
        course.is_online = form.is_online.data
        course.session_link = form.session_link.data
        course.is_published = form.is_published.data
        course.registration_open = form.registration_open.data
        course.allow_bkash = form.allow_bkash.data
        course.allow_nagad = form.allow_nagad.data
        course.allow_rocket = form.allow_rocket.data
        course.allow_cards = form.allow_cards.data

        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin.course_manager'))

    return render_template('admin/course_form.html',
                         title='Edit Course',
                         form=form,
                         course=course)

@admin_bp.route('/courses/delete/<int:course_id>', methods=['POST'])
@admin_required
def course_delete(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin.course_manager'))

# Course Video Management
@admin_bp.route('/courses/<int:course_id>/videos')
@admin_required
def course_videos(course_id):
    course = Course.query.get_or_404(course_id)
    videos = CourseVideo.query.filter_by(course_id=course_id).order_by(CourseVideo.order).all()

    return render_template('admin/course_videos.html',
                         title=f'Videos for {course.title}',
                         course=course,
                         videos=videos)

@admin_bp.route('/courses/<int:course_id>/videos/add', methods=['GET', 'POST'])
@admin_required
def course_video_add(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseVideoForm()

    if form.validate_on_submit():
        video = CourseVideo(
            course_id=course_id,
            title=form.title.data,
            description=form.description.data,
            video_type=form.video_type.data,
            video_url=form.video_url.data,
            order=form.order.data,
            duration=form.duration.data,
            is_published=form.is_published.data
        )
        db.session.add(video)
        db.session.commit()
        flash('Video added successfully!', 'success')
        return redirect(url_for('admin.course_videos', course_id=course_id))

    return render_template('admin/course_video_form.html',
                         title=f'Add Video to {course.title}',
                         form=form,
                         course=course)

@admin_bp.route('/courses/videos/edit/<int:video_id>', methods=['GET', 'POST'])
@admin_required
def course_video_edit(video_id):
    video = CourseVideo.query.get_or_404(video_id)
    course = Course.query.get_or_404(video.course_id)
    form = CourseVideoForm(obj=video)

    if form.validate_on_submit():
        video.title = form.title.data
        video.description = form.description.data
        video.video_type = form.video_type.data
        video.video_url = form.video_url.data
        video.order = form.order.data
        video.duration = form.duration.data
        video.is_published = form.is_published.data

        db.session.commit()
        flash('Video updated successfully!', 'success')
        return redirect(url_for('admin.course_videos', course_id=course.id))

    return render_template('admin/course_video_form.html',
                         title=f'Edit Video for {course.title}',
                         form=form,
                         course=course,
                         video=video)

@admin_bp.route('/courses/videos/delete/<int:video_id>', methods=['POST'])
@admin_required
def course_video_delete(video_id):
    video = CourseVideo.query.get_or_404(video_id)
    course_id = video.course_id
    db.session.delete(video)
    db.session.commit()
    flash('Video deleted successfully!', 'success')
    return redirect(url_for('admin.course_videos', course_id=course_id))

# Course Material Management
@admin_bp.route('/courses/<int:course_id>/materials')
@admin_required
def course_materials(course_id):
    course = Course.query.get_or_404(course_id)
    materials = CourseMaterial.query.filter_by(course_id=course_id).order_by(CourseMaterial.order).all()

    return render_template('admin/course_materials.html',
                         title=f'Materials for {course.title}',
                         course=course,
                         materials=materials)

@admin_bp.route('/courses/<int:course_id>/materials/add', methods=['GET', 'POST'])
@admin_required
def course_material_add(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseMaterialForm()

    if form.validate_on_submit():
        material = CourseMaterial(
            course_id=course_id,
            title=form.title.data,
            description=form.description.data,
            file_type=form.file_type.data,
            file_url=form.file_url.data,
            order=form.order.data,
            is_published=form.is_published.data
        )
        db.session.add(material)
        db.session.commit()
        flash('Material added successfully!', 'success')
        return redirect(url_for('admin.course_materials', course_id=course_id))

    return render_template('admin/course_material_form.html',
                         title=f'Add Material to {course.title}',
                         form=form,
                         course=course)

@admin_bp.route('/courses/materials/edit/<int:material_id>', methods=['GET', 'POST'])
@admin_required
def course_material_edit(material_id):
    material = CourseMaterial.query.get_or_404(material_id)
    course = Course.query.get_or_404(material.course_id)
    form = CourseMaterialForm(obj=material)

    if form.validate_on_submit():
        material.title = form.title.data
        material.description = form.description.data
        material.file_type = form.file_type.data
        material.file_url = form.file_url.data
        material.order = form.order.data
        material.is_published = form.is_published.data

        db.session.commit()
        flash('Material updated successfully!', 'success')
        return redirect(url_for('admin.course_materials', course_id=course.id))

    return render_template('admin/course_material_form.html',
                         title=f'Edit Material for {course.title}',
                         form=form,
                         course=course,
                         material=material)

@admin_bp.route('/courses/materials/delete/<int:material_id>', methods=['POST'])
@admin_required
def course_material_delete(material_id):
    material = CourseMaterial.query.get_or_404(material_id)
    course_id = material.course_id
    db.session.delete(material)
    db.session.commit()
    flash('Material deleted successfully!', 'success')
    return redirect(url_for('admin.course_materials', course_id=course_id))

# Participant Management
@admin_bp.route('/courses/<int:course_id>/participants')
@admin_required
def course_participants(course_id):
    course = Course.query.get_or_404(course_id)

    # Get participants with registration data
    participants = db.session.query(
        User, registrations
    ).join(
        registrations, User.id == registrations.c.user_id
    ).filter(
        registrations.c.course_id == course_id
    ).all()

    return render_template('admin/participants.html',
                         title=f'Participants for {course.title}',
                         course=course,
                         participants=participants)

@admin_bp.route('/courses/<int:course_id>/participants/export')
@admin_required
def export_participants(course_id):
    course = Course.query.get_or_404(course_id)

    # Get participants data
    participants = db.session.query(
        User, registrations
    ).join(
        registrations, User.id == registrations.c.user_id
    ).filter(
        registrations.c.course_id == course_id
    ).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Full Name', 'Email', 'Phone', 'Registration Date', 
                    'Payment Status', 'Completion Status'])

    # Write participant data
    for user, reg in participants:
        writer.writerow([
            user.full_name,
            user.email,
            user.phone,
            reg.registration_date.strftime('%Y-%m-%d %H:%M') if reg.registration_date else '',
            reg.payment_status,
            'Completed' if reg.completion_status else 'Not Completed'
        ])

    # Prepare response
    from flask import Response
    output.seek(0)
    filename = f"{course.title.replace(' ', '_')}_participants_{datetime.datetime.now().strftime('%Y%m%d')}.csv"

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

@admin_bp.route('/participants/update-status', methods=['POST'])
@admin_required
def update_participant_status():
    user_id = request.form.get('user_id', type=int)
    course_id = request.form.get('course_id', type=int)
    completion_status = request.form.get('completion_status') == 'true'

    if not user_id or not course_id:
        return jsonify({'success': False, 'message': 'Invalid request'}), 400

    # Update completion status in registrations table
    stmt = registrations.update().where(
        (registrations.c.user_id == user_id) & 
        (registrations.c.course_id == course_id)
    ).values(completion_status=completion_status)

    db.session.execute(stmt)
    db.session.commit()

    # If marked as completed, prepare for certificate generation
    if completion_status:
        return jsonify({
            'success': True, 
            'message': 'Status updated. User can now receive certificate.',
            'canGenerateCertificate': True,
            'user_id': user_id,
            'course_id': course_id
        })

    return jsonify({'success': True, 'message': 'Status updated successfully'})

@admin_bp.route('/certificate/generate', methods=['POST'])
@admin_required
def generate_certificate():
    user_id = request.form.get('user_id', type=int)
    course_id = request.form.get('course_id', type=int)
    template_id = request.form.get('template_id', type=int)

    if not user_id or not course_id:
        return jsonify({'success': False, 'message': 'Invalid request'}), 400

    # Generate certificate
    certificate = CertificateGenerator.generate_certificate(user_id, course_id, template_id)

    if certificate:
        # Update certificate_issued status in registrations table
        stmt = registrations.update().where(
            (registrations.c.user_id == user_id) & 
            (registrations.c.course_id == course_id)
        ).values(certificate_issued=True)

        db.session.execute(stmt)
        db.session.commit()

        # Send certificate email
        from utils.email_service import EmailService
        user = User.query.get(user_id)
        EmailService.send_certificate(user, certificate)

        return jsonify({
            'success': True, 
            'message': 'Certificate generated and sent successfully',
            'certificate_url': certificate.pdf_url
        })

    return jsonify({'success': False, 'message': 'Failed to generate certificate'})

# Consultant Management
@admin_bp.route('/consultants')
@admin_required
def consultant_manager():
    consultants = User.query.filter_by(is_consultant=True).all()
    return render_template('admin/consultant_manager.html',
                         title='Consultant Manager',
                         consultants=consultants)

@admin_bp.route('/consultants/add', methods=['GET', 'POST'])
@admin_required
def consultant_add():
    form = ConsultantForm()

    def save_file(file, consultant_id, file_type):
        if not file:
            return None
        filename = secure_filename(f"{consultant_id}_{file_type}_{file.filename}")
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'consultants')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        return filename

    # Populate user_id choices with existing admins
    admins = User.query.filter(User.role.in_(['admin', 'super_admin'])).all()
    form.user_id.choices = [(0, 'Create New User')] + [(u.id, f"{u.full_name} ({u.email})") for u in admins]

    if form.validate_on_submit():
        if form.user_id.data > 0:
            # Use existing user
            consultant = User.query.get(form.user_id.data)
            consultant.is_consultant = True
        else:
            # Create new user
            consultant = User(
                username=form.email.data.split('@')[0],
                email=form.email.data,
                full_name=form.full_name.data,
                is_consultant=True,
                role='consultant'
            )
            consultant.set_password(form.password.data)
            db.session.add(consultant)

        # Update consultant info
        consultant.bio = form.bio.data
        consultant.position = form.position.data
        consultant.photo_url = form.photo_url.data

        db.session.commit()
        flash('Consultant added successfully!', 'success')
        return redirect(url_for('admin.consultant_manager'))

    return render_template('admin/consultant_form.html',
                         title='Add Consultant',
                         form=form)

@admin_bp.route('/consultants/edit/<int:consultant_id>', methods=['GET', 'POST'])
@admin_required
def consultant_edit(consultant_id):
    consultant = User.query.get_or_404(consultant_id)

    if not consultant.is_consultant:
        abort(404)

    form = ConsultantForm(obj=consultant)
    form.user_id.choices = [(consultant.id, f"{consultant.full_name} ({consultant.email})")]
    form.user_id.data = consultant.id

    # Don't require password for edit
    form.password.validators = []

    if form.validate_on_submit():
        consultant.full_name = form.full_name.data
        consultant.email = form.email.data
        consultant.bio = form.bio.data
        consultant.position = form.position.data
        consultant.is_consultant = True

        if form.photo.data:
            photo_file = form.photo.data
            photo_filename = secure_filename(f"{consultant.id}_photo_{int(time.time())}{os.path.splitext(photo_file.filename)[1]}")
            photo_file.save(os.path.join('static/uploads/consultants', photo_filename))
            consultant.photo_filename = photo_filename

        if form.cv.data:
            cv_file = form.cv.data
            cv_filename = secure_filename(f"{consultant.id}_cv_{int(time.time())}.pdf")
            cv_file.save(os.path.join('static/uploads/consultants', cv_filename))
            consultant.cv_filename = cv_filename

        db.session.commit()
        flash('Consultant updated successfully', 'success')
        return redirect(url_for('admin.consultant_manager'))

    return render_template('admin/consultant_form.html',
                         title='Edit Consultant',
                         form=form,
                         consultant=consultant)

@admin_bp.route('/consultants/delete/<int:consultant_id>', methods=['POST'])
@admin_required
def consultant_delete(consultant_id):
    consultant = User.query.get_or_404(consultant_id)

    if not consultant.is_consultant:
        abort(404)

    consultant.is_consultant = False
    db.session.commit()
    flash('Consultant removed successfully!', 'success')
    return redirect(url_for('admin.consultant_manager'))

@admin_bp.route('/consultants/<int:consultant_id>/cv')
@admin_required
def download_cv(consultant_id):
    consultant = User.query.get_or_404(consultant_id)
    if not consultant.cv_filename:
        abort(404)
    return send_from_directory(
        os.path.join(current_app.config['UPLOAD_FOLDER'], 'consultants'),
        consultant.cv_filename
    )
    consultant = User.query.get_or_404(consultant_id)

    if not consultant.is_consultant:
        abort(404)

    consultant.is_consultant = False
    db.session.commit()
    flash('Consultant removed successfully!', 'success')
    return redirect(url_for('admin.consultant_manager'))

# Certificate Builder
@admin_bp.route('/certificates/templates')
@admin_required
def certificate_templates():
    templates = CertificateTemplate.query.all()
    return render_template('admin/certificate_builder.html',
                         title='Certificate Templates',
                         templates=templates)

@admin_bp.route('/certificates/templates/add', methods=['GET', 'POST'])
@admin_required
def certificate_template_add():
    form = CertificateTemplateForm()

    if form.validate_on_submit():
        template = CertificateTemplate(
            name=form.name.data,
            background_url=form.background_url.data,
            html_template=form.html_template.data or CertificateGenerator.get_default_template_html(),
            is_default=form.is_default.data,
            created_by=current_user.id
        )

        # If this is default, unset other defaults
        if template.is_default:
            CertificateTemplate.query.filter_by(is_default=True).update({'is_default': False})

        db.session.add(template)
        db.session.commit()
        flash('Certificate template added successfully!', 'success')
        return redirect(url_for('admin.certificate_templates'))

    # Populate with default template HTML
    if not form.html_template.data:
        form.html_template.data = CertificateGenerator.get_default_template_html()

    return render_template('admin/certificate_template_form.html',
                         title='Add Certificate Template',
                         form=form)

@admin_bp.route('/certificates/templates/edit/<int:template_id>', methods=['GET', 'POST'])
@admin_required
def certificate_template_edit(template_id):
    template = CertificateTemplate.query.get_or_404(template_id)
    form = CertificateTemplateForm(obj=template)

    if form.validate_on_submit():
        template.name = form.name.data
        template.background_url = form.background_url.data
        template.html_template = form.html_template.data

        # Handle default status
        if form.is_default.data and not template.is_default:
            CertificateTemplate.query.filter_by(is_default=True).update({'is_default': False})
            template.is_default = True
        elif not form.is_default.data and template.is_default:
            # Can't unset default if this is the only template
            if CertificateTemplate.query.count() > 1:
                template.is_default = False
            else:
                flash('Cannot remove default status from the only template.', 'warning')
                template.is_default = True

        db.session.commit()
        flash('Certificate template updated successfully!', 'success')
        return redirect(url_for('admin.certificate_templates'))

    return render_template('admin/certificate_template_form.html',
                         title='Edit Certificate Template',
                         form=form,
                         template=template)

@admin_bp.route('/certificates/templates/delete/<int:template_id>', methods=['POST'])
@admin_required
def certificate_template_delete(template_id):
    template = CertificateTemplate.query.get_or_404(template_id)

    # Don't allow deleting the default template if it's the only one
    if template.is_default and CertificateTemplate.query.count() == 1:
        flash('Cannot delete the only template.', 'danger')
        return redirect(url_for('admin.certificate_templates'))

    # If deleting default, set another one as default
    if template.is_default:
        new_default = CertificateTemplate.query.filter(CertificateTemplate.id != template_id).first()
        if new_default:
            new_default.is_default = True

    db.session.delete(template)
    db.session.commit()
    flash('Certificate template deleted successfully!', 'success')
    return redirect(url_for('admin.certificate_templates'))

# User Management (Super Admin only)
@admin_bp.route('/users')
@super_admin_required
def user_manager():
    users = User.query.all()
    return render_template('admin/user_manager.html',
                         title='User Manager',
                         users=users)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@super_admin_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Update user role
        role = request.form.get('role')
        if role in ['user', 'admin', 'super_admin', 'consultant']:
            user.role = role

            # Update consultant status based on role
            user.is_consultant = (role == 'consultant')

            db.session.commit()
            flash('User role updated successfully!', 'success')

        return redirect(url_for('admin.user_manager'))

    return render_template('admin/user_edit.html',
                         title='Edit User',
                         user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@super_admin_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)

    # Can't delete yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.user_manager'))

    # Delete user
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.user_manager'))


# File Manager - For Super Admins to edit program files
@admin_bp.route('/file-manager')
@super_admin_required
def file_manager():
    path = request.args.get('path', '.')
    # Security check to prevent directory traversal attacks
    if '..' in path or path.startswith('/'):
        flash('Invalid path specified.', 'danger')
        path = '.'

    files = []
    directories = []

    # Get list of files and directories
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                directories.append({
                    'name': item,
                    'path': item_path,
                    'type': 'directory'
                })
            else:
                files.append({
                    'name': item,
                    'path': item_path,
                    'size': os.path.getsize(item_path),
                    'type': 'file'
                })
    except Exception as e:
        flash(f'Error accessing path: {str(e)}', 'danger')
        path = '.'
        directories = []
        files = []

    # Sort alphabetically
    directories.sort(key=lambda x: x['name'])
    files.sort(key=lambda x: x['name'])

    return render_template('admin/file_manager.html',
                        title='File Manager',
                        current_path=path,
                        directories=directories,
                        files=files)

@admin_bp.route('/file-edit', methods=['GET', 'POST'])
@super_admin_required
def file_edit():
    path = request.args.get('path', '')

    # Security check to prevent directory traversal attacks
    if '..' in path or path.startswith('/'):
        flash('Invalid path specified.', 'danger')
        return redirect(url_for('admin.file_manager'))

    if request.method == 'POST':
        content = request.form.get('content', '')

        try:
            with open(path, 'w') as f:
                f.write(content)
            flash('File saved successfully!', 'success')
        except Exception as e:
            flash(f'Error saving file: {str(e)}', 'danger')

        # Redirect back to the same page to clear POST data
        return redirect(url_for('admin.file_edit', path=path))

    # Get file content for GET request
    try:
        with open(path, 'r') as f:
            content = f.read()
    except Exception as e:
        flash(f'Error reading file: {str(e)}', 'danger')
        return redirect(url_for('admin.file_manager'))

    return render_template('admin/file_edit.html',
                         title=f'Edit File: {os.path.basename(path)}',
                         path=path,
                         content=content)