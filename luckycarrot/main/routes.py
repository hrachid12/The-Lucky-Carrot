from flask import Blueprint, render_template, request


main = Blueprint('main', __name__)



@main.route("/", methods=['GET'])
@main.route("/home", methods=['GET'])
def home():
    return render_template("home.html", home=True)


@main.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


@main.route('/updates')
def updates():
    return render_template('updates.html')