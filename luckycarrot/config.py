import os

class Config:
    SECRET_KEY = os.environ.get('LUCKY_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('LUCKY_DB')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('LUCKY_EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('LUCKY_EMAIL_PASS')