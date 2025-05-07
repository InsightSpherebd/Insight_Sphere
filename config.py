import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev_key')
    SESSION_COOKIE_SECURE = True

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///insightsphere.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Mail settings
    MAIL_SERVER = 'smtp.gmail.com'  # Or your SMTP server
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@gmail.com'  # Your email
    MAIL_PASSWORD = 'your-app-password'  # Your email password/app password
    MAIL_DEFAULT_SENDER = 'Insight Sphere BD <your-email@gmail.com>'

    # File uploads
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

    # Stripe
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')

    # SSLCommerz settings
    SSLCOMMERZ_STORE_ID = 'your-store-id'  # Your SSLCommerz Store ID
    SSLCOMMERZ_STORE_PASSWORD = 'your-store-password'  # Your SSLCommerz Password
    SSLCOMMERZ_SANDBOX = False  # Set to False for production

    # Website settings
    SITE_NAME = 'Insight Sphere BD'
    DOMAIN = os.environ.get('DOMAIN', 'localhost:5000')
    BASE_URL = f"https://{DOMAIN}" if DOMAIN != 'localhost:5000' else f"http://{DOMAIN}"