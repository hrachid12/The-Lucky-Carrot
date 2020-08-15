import os
import json

with open("/etc/config.json") as config_file:
    config = json.load(config_file)

class Config:
    SECRET_KEY = config.get('LUCKY_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config.get('LUCKY_DB')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = config.get('LUCKY_EMAIL_USER')
    MAIL_PASSWORD = config.get('LUCKY_EMAIL_PASS')
