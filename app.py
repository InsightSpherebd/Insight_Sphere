import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize SQLAlchemy base
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

# Create app
app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)
csrf.init_app(app)

# Configure login
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Import models and create tables
with app.app_context():
    import models
    db.create_all()
    
    # Create super admin user if not exists
    from models import User
    super_admin = User.query.filter_by(email='admin@insightspherebd.com').first()
    if not super_admin:
        super_admin = User(
            username='superadmin',
            email='admin@insightspherebd.com',
            full_name='System Administrator',
            phone='+88019XXXXXXXX',
            role='super_admin'
        )
        super_admin.set_password('Admin@123')
        db.session.add(super_admin)
        db.session.commit()
        logging.info('Created super admin user')
    
    # Add new columns to Course table if they don't exist
    from sqlalchemy import text
    try:
        db.session.execute(text("""ALTER TABLE course 
            ADD COLUMN IF NOT EXISTS payment_methods VARCHAR(255) DEFAULT 'stripe,sslcommerz,manual',
            ADD COLUMN IF NOT EXISTS allow_bkash BOOLEAN DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS allow_nagad BOOLEAN DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS allow_rocket BOOLEAN DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS allow_cards BOOLEAN DEFAULT TRUE;
        """))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating schema: {str(e)}")
        pass

# Register blueprints
from routes.auth import auth_bp
from routes.public import public_bp
from routes.admin import admin_bp
from routes.user import user_bp

app.register_blueprint(auth_bp)
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Make config available to all templates
@app.context_processor
def inject_config():
    from datetime import datetime
    return {'config': app.config, 'now': datetime.utcnow()}
