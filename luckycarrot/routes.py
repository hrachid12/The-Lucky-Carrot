from flask import render_template, url_for, request, redirect, flash
from luckycarrot import app
from luckycarrot.forms import RegistrationForm, LoginForm
from luckycarrot.models import User, Post


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
    form = RegistrationForm()

    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('register'))

    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        if form.email.data == 'test@gmail.com' and form.password.data == '123':
            flash(f'You have been logged in!', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Login Unsuccessful. Please try again.', 'danger')

    return render_template('login.html', form=form)
