from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for users and courses (registrations)
registrations = db.Table('registrations',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('registration_date', db.DateTime, default=datetime.utcnow),
    db.Column('payment_status', db.String(20), default='pending'),
    db.Column('completion_status', db.Boolean, default=False),
    db.Column('certificate_issued', db.Boolean, default=False)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='user')  # user, admin, super_admin, consultant
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', secondary=registrations, 
                             backref=db.backref('participants', lazy='dynamic'))
    payments = db.relationship('Payment', backref='user', lazy=True)
    certificates = db.relationship('Certificate', backref='user', lazy=True)
    
    # For consultants
    is_consultant = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text)
    position = db.Column(db.String(100))
    photo_url = db.Column(db.String(255))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role in ['admin', 'super_admin']
    
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_active(self):
        return True
        
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    duration = db.Column(db.String(50))  # e.g., "3 days", "2 weeks"
    fee = db.Column(db.Float, default=0.0)
    capacity = db.Column(db.Integer)
    location = db.Column(db.String(100))
    is_online = db.Column(db.Boolean, default=True)
    session_link = db.Column(db.String(255))  # Zoom, Google Meet, etc.
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    registration_open = db.Column(db.Boolean, default=True)
    
    # Payment options
    payment_methods = db.Column(db.String(255), default='stripe,sslcommerz,manual')  # Comma-separated list of payment methods
    allow_bkash = db.Column(db.Boolean, default=True)  # via SSLCommerz
    allow_nagad = db.Column(db.Boolean, default=True)  # via SSLCommerz
    allow_rocket = db.Column(db.Boolean, default=True)  # via SSLCommerz
    allow_cards = db.Column(db.Boolean, default=True)  # via Stripe or SSLCommerz
    
    # Relationships
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', foreign_keys=[creator_id])
    videos = db.relationship('CourseVideo', backref='course', lazy=True)
    materials = db.relationship('CourseMaterial', backref='course', lazy=True)
    
    def is_registered(self, user):
        return user in self.participants
    
    def available_seats(self):
        return self.capacity - self.participants.count() if self.capacity else "Unlimited"


class CourseVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    video_type = db.Column(db.String(20))  # youtube, vimeo, uploaded
    video_url = db.Column(db.String(255))
    order = db.Column(db.Integer, default=0)
    duration = db.Column(db.String(20))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CourseMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_type = db.Column(db.String(20))  # pdf, doc, ppt, etc.
    file_url = db.Column(db.String(255))
    order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='BDT')
    payment_method = db.Column(db.String(20))  # stripe, sslcommerz, manual
    transaction_id = db.Column(db.String(100))
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    payment_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    course = db.relationship('Course')


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    certificate_number = db.Column(db.String(50), unique=True)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    pdf_url = db.Column(db.String(255))
    is_sent = db.Column(db.Boolean, default=False)
    
    # Relationship
    course = db.relationship('Course')


class SiteContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(50), nullable=False)  # e.g., hero, about, mission, etc.
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    media_url = db.Column(db.String(255))
    order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # For administrative purposes
    editor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    editor = db.relationship('User')


class CertificateTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    background_url = db.Column(db.String(255))
    html_template = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User')
