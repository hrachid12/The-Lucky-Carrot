from flask import render_template, url_for, request, redirect, flash
from luckycarrot import app, db, bcrypt
from luckycarrot.forms import RegistrationForm, LoginForm
from luckycarrot.models import User, Post
from flask_login import login_user, current_user, logout_user


@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
def home():
    return render_template("home.html", home=True)


@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


@app.route("/blog", methods=['GET', 'POST'])
def blog():
    return render_template('blog.html')


@app.route('/updates')
def updates():
    return render_template('updates.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw, updates=form.updates.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if form.validate_on_submit():
        
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))

        else:
            flash(f'Login Unsuccessful. Please try again.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
