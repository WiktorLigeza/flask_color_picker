from flask import Flask, render_template, request



app = Flask(__name__)


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login')
def log_in():
    return render_template('login.html')

@app.route('/register')
def sign_up():
    return render_template('register.html')

@app.route("/test", methods=["POST"])
def test():
    name_of_slider = request.form["value"]
    return name_of_slider


if __name__ == '__main__':
    app.run(debug=True)
