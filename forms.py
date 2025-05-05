from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, 
                    TextAreaField, SelectField, IntegerField, FloatField, 
                    DateTimeField, HiddenField, FileField, URLField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, URL
from datetime import datetime

# Authentication Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

# Course Registration
class CourseRegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Register for Course')

# Admin Forms
class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateTimeField('Start Date/Time', format='%Y-%m-%d %H:%M', validators=[Optional()], render_kw={"placeholder": "YYYY-MM-DD HH:MM"})
    duration = StringField('Duration (e.g., "3 days")', validators=[DataRequired(), Length(max=50)])
    fee = FloatField('Fee (0 for free)', default=0.0)
    capacity = IntegerField('Capacity (0 for unlimited)', default=0)
    location = StringField('Location', validators=[Length(max=100)])
    is_online = BooleanField('Is Online?', default=True)
    session_link = URLField('Session Link (Zoom, Meet, etc.)', validators=[Optional(), URL()])
    is_published = BooleanField('Published?', default=False)
    registration_open = BooleanField('Registration Open?', default=True)
    
    # Payment method options
    allow_bkash = BooleanField('Allow bKash', default=True)
    allow_nagad = BooleanField('Allow Nagad', default=True)
    allow_rocket = BooleanField('Allow Rocket (DBBL)', default=True)
    allow_cards = BooleanField('Allow Credit/Debit Cards', default=True)
    
    submit = SubmitField('Save Course')

class CourseVideoForm(FlaskForm):
    title = StringField('Video Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    video_type = SelectField('Video Type', choices=[
        ('youtube', 'YouTube'), 
        ('vimeo', 'Vimeo'), 
        ('uploaded', 'Uploaded Video')
    ])
    video_url = URLField('Video URL', validators=[DataRequired(), URL()])
    duration = StringField('Duration (e.g., "10:30")', validators=[Optional(), Length(max=20)])
    order = IntegerField('Display Order', default=0)
    is_published = BooleanField('Published?', default=True)
    submit = SubmitField('Save Video')

class CourseMaterialForm(FlaskForm):
    title = StringField('Material Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    file_type = SelectField('File Type', choices=[
        ('pdf', 'PDF'), 
        ('doc', 'Word Document'), 
        ('ppt', 'PowerPoint'), 
        ('link', 'External Link')
    ])
    file_url = URLField('File URL', validators=[DataRequired(), URL()])
    order = IntegerField('Display Order', default=0)
    is_published = BooleanField('Published?', default=True)
    submit = SubmitField('Save Material')

class SiteContentForm(FlaskForm):
    section = SelectField('Content Section', choices=[
        ('hero', 'Hero Section'),
        ('about', 'About Us Section'),
        ('mission_vision', 'Mission & Vision'),
        ('footer', 'Footer Content')
    ])
    title = StringField('Title', validators=[Length(max=100)])
    content = TextAreaField('Content')
    media_url = URLField('Media URL (Image or Video)', validators=[Optional(), URL()])
    order = IntegerField('Display Order', default=0)
    is_published = BooleanField('Published?', default=True)
    submit = SubmitField('Save Content')

class ConsultantForm(FlaskForm):
    user_id = SelectField('User', coerce=int)
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    bio = TextAreaField('Biography', validators=[DataRequired()])
    position = StringField('Position/Title', validators=[DataRequired(), Length(max=100)])
    photo_url = URLField('Photo URL', validators=[Optional(), URL()])
    submit = SubmitField('Save Consultant')

class CertificateTemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired(), Length(max=100)])
    background_url = URLField('Background Image URL', validators=[Optional(), URL()])
    html_template = TextAreaField('HTML Template')
    is_default = BooleanField('Set as Default Template?', default=False)
    submit = SubmitField('Save Template')
