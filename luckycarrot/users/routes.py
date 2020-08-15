from flask import render_template, url_for, request, redirect, flash, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from luckycarrot import db, bcrypt
from luckycarrot.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                                RequestResetForm, ResetPasswordForm)
from luckycarrot.models import User, Post
from luckycarrot.users.utils import save_profile_picture, send_reset_email

users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_pw, updates=form.updates.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created! You can now log in.', 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', form=form)


@users.route('/login', methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('main.home'))

        else:
            flash(f'Login Unsuccessful. Please try again.', 'danger')

    return render_template('login.html', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for('users.account'))

    elif request.method == 'GET':

        # Display user info in form
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.updates.data = current_user.updates

    image_file = url_for(
        'static', filename='profile_pictures/' + current_user.image_file)

    return render_template('account.html', image_file=image_file, form=form)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Please check your email for instructions on how to reset your password.', 'info')
        return redirect(url_for('users.login'))

    return render_template('reset_request.html', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_reset_token(token)

    if user is None:
        flash("That is an invalid or expired token.", 'info')
        return redirect(url_for('users.reset_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash(f'Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('users.login'))

    

    return render_template('reset_token.html', form=form)


