import os
import secrets
from PIL import Image
from flask import render_template, url_for, request, redirect, flash, abort
from luckycarrot import app, db, bcrypt, mail
from luckycarrot.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                                PostForm, RequestResetForm, ResetPasswordForm)
from luckycarrot.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
def home():
    return render_template("home.html", home=True)


@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


@app.route("/blog", methods=['GET', 'POST'])
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('blog.html', posts=posts)


@app.route('/blog/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template('post.html', post=post)



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


def save_profile_picture(form_picture):
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
            picture_file = save_profile_picture(form.picture.data)
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


def save_post_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_pictures', picture_fn)
    form_picture.save(picture_path)

    return picture_fn

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    if not current_user.admin_user:
        return redirect(url_for('home'))
    
    if form.validate_on_submit():

        if not form.picture.data:
            flash('Error in creating post. Please upload a picture.', 'danger')
            return redirect(url_for('create_post'))

        image = save_post_picture(form.picture.data)
        post = Post(title=form.title.data, content=form.content.data, image_file=image, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Success! Post Created!', 'success')
        return redirect(url_for('blog'))

    return render_template('create_post.html', form=form, legend="Create New Post")


@app.route('/blog/<int:post_id>/update', methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_post_picture(form.picture.data)
            post.image_file = picture_file

        post.title = form.title.data 
        post.content = form.content.data 
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content 


    return render_template('update_post.html', form=form, legend="Update Post")


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash('Post has been deleted.', 'success')
    return redirect(url_for('blog'))


def send_reset_email(user):
    token = user.get_reset_token()

    msg = Message('Password Reset Request', sender='theluckycarrot1@gmail.com', recipients=[user.email])

    msg.body = f"""To complete your password reset, visit the link below.

{url_for('reset_token', token=token, _external=True)}

If you did not request a password reset, then ignore this email and your password will not be changed.
"""
    mail.send(msg)



@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Please check your email for instructions on how to reset your password.', 'info')
        return redirect(url_for('login'))

    return render_template('reset_request.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)

    if user is None:
        flash("That is an invalid or expired token.", 'info')
        return redirect(url_for('reset_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash(f'Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login'))

    

    return render_template('reset_token.html', form=form)