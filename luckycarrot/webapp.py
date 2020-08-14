from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", home=True)


@app.route("/about")
def about():
    return render_template('about.html', home=False)


@app.route("/blog")
def blog():
    return render_template('blog.html', home=False)


@app.route('/updates')
def updates():
    return render_template('updates.html', home=False)


if __name__ == '__main__':
    app.run(debug=True)
