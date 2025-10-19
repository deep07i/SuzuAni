import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-that-you-should-change'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///../instance/suzuani.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Mail Settings
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    
    # Agar environment variable set nahi hai, to default value istemal hogi.
    MAIL_USERNAME = os.environ.get('EMAIL_USER') or 'Suzubusiness07i@gmail.com'
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS') or 'pbwf ubbr fleb ktwq'