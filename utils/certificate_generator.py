import os
from flask import current_app
from weasyprint import HTML
from jinja2 import Template
import uuid
import datetime
from models import Certificate, User, Course

class CertificateGenerator:
    @staticmethod
    def get_default_template_html():
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Certificate</title>
    <style>
        body {
            font-family: 'Times New Roman', serif;
            margin: 0;
            padding: 40px;
            background: #f9f9f9;
        }
        .certificate {
            background: white;
            border: 10px solid #2c5282;
            padding: 60px;
            text-align: center;
            max-width: 800px;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .certificate-title {
            font-size: 48px;
            color: #2c5282;
            margin-bottom: 30px;
            font-weight: bold;
        }
        .certificate-text {
            font-size: 24px;
            margin: 20px 0;
            color: #333;
        }
        .recipient-name {
            font-size: 36px;
            color: #2c5282;
            font-weight: bold;
            margin: 30px 0;
            text-decoration: underline;
        }
        .course-name {
            font-size: 28px;
            color: #2c5282;
            font-style: italic;
            margin: 30px 0;
        }
        .certificate-footer {
            margin-top: 50px;
            font-size: 16px;
            color: #666;
        }
        .certificate-number {
            position: absolute;
            bottom: 20px;
            right: 20px;
            font-size: 12px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="certificate">
        <div class="certificate-title">CERTIFICATE OF COMPLETION</div>
        
        <div class="certificate-text">This is to certify that</div>
        
        <div class="recipient-name">{{user.full_name}}</div>
        
        <div class="certificate-text">has successfully completed the course</div>
        
        <div class="course-name">{{course.title}}</div>
        
        <div class="certificate-text">on {{date}}</div>
        
        <div class="certificate-footer">
            <p>Insight Sphere BD</p>
            <p>Industrial Engineering Consultancy & Training</p>
        </div>
        
        <div class="certificate-number">Certificate No: {{certificate.certificate_number}}</div>
    </div>
</body>
</html>
        """
    
    @staticmethod
    def generate_certificate(user_id, course_id, template_id=None):
        # Implementation for certificate generation
        pass

class CertificateGenerator:
    @staticmethod
    def generate_certificate(user_id, course_id, template_id=None):
        """
        Generate a PDF certificate for a user who completed a course
        
        Args:
            user_id: User ID
            course_id: Course ID
            template_id: Certificate template ID (optional)
            
        Returns:
            Certificate object if successful, None otherwise
        """
        from app import db
        
        try:
            # Get user and course
            user = User.query.get(user_id)
            course = Course.query.get(course_id)
            
            if not user or not course:
                return None
            
            # Get certificate template
            from models import CertificateTemplate
            if template_id:
                template = CertificateTemplate.query.get(template_id)
            else:
                template = CertificateTemplate.query.filter_by(is_default=True).first()
            
            if not template:
                return None
            
            # Generate a unique certificate number
            certificate_number = f"ISBD-{course_id}-{user_id}-{uuid.uuid4().hex[:6].upper()}"
            
            # Create certificate record
            certificate = Certificate(
                user_id=user_id,
                course_id=course_id,
                certificate_number=certificate_number,
                issue_date=datetime.datetime.utcnow()
            )
            
            # Add to database
            db.session.add(certificate)
            db.session.commit()
            
            # Generate PDF
            pdf_filename = f"certificate_{certificate.id}.pdf"
            pdf_path = os.path.join(current_app.root_path, 'static', 'certificates', pdf_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            # Render HTML template
            template_data = {
                'user': user,
                'course': course,
                'certificate': certificate,
                'date': certificate.issue_date.strftime('%B %d, %Y')
            }
            
            html_content = Template(template.html_template).render(**template_data)
            
            # Generate PDF from HTML
            HTML(string=html_content).write_pdf(pdf_path)
            
            # Update certificate with PDF URL
            certificate.pdf_url = f"/static/certificates/{pdf_filename}"
            db.session.commit()
            
            return certificate
            
        except Exception as e:
            current_app.logger.error(f"Error generating certificate: {str(e)}")
            return None
    
    @staticmethod
    def get_default_template_html():
        """Return the default certificate template HTML"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Certificate of Completion</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    text-align: center;
                    color: #333;
                    background-image: url('{{ background_url }}');
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                    padding: 50px;
                    position: relative;
                }
                .certificate {
                    width: 800px;
                    height: 600px;
                    margin: 0 auto;
                    border: 20px solid #0066cc;
                    padding: 50px;
                    position: relative;
                    background: rgba(255, 255, 255, 0.9);
                }
                .logo {
                    margin-bottom: 20px;
                }
                h1 {
                    font-size: 36px;
                    margin-bottom: 20px;
                    color: #0066cc;
                }
                h2 {
                    font-size: 28px;
                    margin-bottom: 20px;
                }
                .recipient {
                    font-size: 30px;
                    font-weight: bold;
                    margin: 30px 0;
                    color: #333;
                }
                .course {
                    font-size: 24px;
                    margin: 20px 0;
                }
                .date {
                    font-size: 18px;
                    margin: 20px 0;
                }
                .signature {
                    margin: 40px 0 20px;
                }
                .signature-name {
                    font-weight: bold;
                    border-top: 1px solid #333;
                    display: inline-block;
                    padding-top: 10px;
                    min-width: 200px;
                }
                .certificate-number {
                    position: absolute;
                    bottom: 20px;
                    right: 20px;
                    font-size: 14px;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <div class="certificate">
                <div class="logo">
                    <h3>Insight Sphere BD</h3>
                </div>
                <h1>Certificate of Completion</h1>
                <p>This certifies that</p>
                <div class="recipient">{{ user.full_name }}</div>
                <p>has successfully completed</p>
                <div class="course">{{ course.title }}</div>
                <div class="date">Issued on {{ date }}</div>
                <div class="signature">
                    <div class="signature-name">Director, Insight Sphere BD</div>
                </div>
                <div class="certificate-number">Certificate ID: {{ certificate.certificate_number }}</div>
            </div>
        </body>
        </html>
        '''
