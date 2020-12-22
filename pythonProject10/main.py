from flask import Flask, render_template, request
from flask_colorpicker import colorpicker
from flask_bootstrap import Bootstrap


app = Flask(__name__)
Bootstrap(app)
colorpicker(app)

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
# import dash_core_components as dcc
# import dash_html_components as html
# import plotly.express as px
# import pandas as pd
#
# @app.route('/chart')
# def chart():
#     df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_apple_stock.csv')
#
#     fig = px.line(df, x='AAPL_x', y='AAPL_y', title='Apple Share Prices over time (2014)')
#     fig.show()
#     return  html.Div([dcc.Graph(figure=fig)])
