
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '6d229a0fceeaf708f0737a0aa9cfb2b8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app) 
login_manager.login_view = 'login'
login_manager.login_message_category = 'secondary'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'theluckycarrot1@gmail.com'
app.config['MAIL_PASSWORD'] = 'HRachid12!gmail'
mail = Mail(app)

from luckycarrot import routes