import os
import secrets
from PIL import Image
from flask import render_template, url_for, request, redirect, flash
from luckycarrot import app, db, bcrypt
from luckycarrot.forms import RegistrationForm, LoginForm, UpdateAccountForm
from luckycarrot.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


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
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_pw, updates=form.updates.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('home'))

        else:
            flash(f'Login Unsuccessful. Please try again.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pictures', picture_fn)

    # Resize picture
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    prev_picture = os.path.join(app.root_path, 'static/profile_pictures', current_user.image_file)
    if os.path.exists(prev_picture) and current_user.image_file != 'default.png':
        os.remove(prev_picture)

    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        # Update user info in db
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.updates = form.updates.data
        db.session.commit()
        flash('You have updated your account!', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':

        # Display user info in form
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.updates.data = current_user.updates

    image_file = url_for(
        'static', filename='profile_pictures/' + current_user.image_file)

    return render_template('account.html', image_file=image_file, form=form)


@app.route('/create_post')
@login_required
def create_post():
    if not current_user.admin_user:
        return redirect(url_for('home'))

    return render_template('create_post.html')
