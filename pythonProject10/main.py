from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from user_management import *
from device_menagement import DeviceForm, DeviceFormUpdate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from functools import wraps
from datetime import datetime


################################################ INIT
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'user.sqlite')
app.config['SQLALCHEMY_BINDS'] = {'two' : 'sqlite:///' + os.path.join(basedir, 'device.sqlite')}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)


################################################ USER DB HANDLING
# User Class/Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(25))


    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self.password = password


# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'username', 'password')


# Init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)


################################################ DEVICE DB HANDLING
# Device Class/Model
class Device(db.Model):
    __bind_key__ = 'two'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    tag = db.Column(db.String(100), unique=True)
    connection_key = db.Column(db.String(25))
    registration_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)


    def __init__(self, name, tag, connection_key):
        self.name = name
        self.tag = tag
        self.connection_key = connection_key


# Device Schema
class DeviceSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'tag', 'connection_key', 'registration_date')


# Init schema
device_schema = DeviceSchema()
devices_schema = DeviceSchema(many=True)


################################################ ROUTES
# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    return user_registration(form = form, db = db)


@app.route('/login', methods=['GET', 'POST'])
def login():
    return user_log_in(session=session)


@app.route("/dashboard")
@is_logged_in
def dashboard():
    devicelist = Device.query.all()
    if len(devicelist) > 0:
        return render_template('dashboard.html', devicelist=devicelist)
    else:
        msg = "no devices"
        return render_template('dashboard.html', msg=msg)


@app.route("/edit_device/<string:id>", methods=['GET', 'POST'])
@is_logged_in
def edit_device(id):
    device = Device.query.get(id)
    form = DeviceFormUpdate(request.form)
    form.name.data = device.name
    form.tag.data = device.tag

    if request.method == 'POST' and form.validate():
        device.name = request.form['name']
        device.tag = request.form['tag']
        db.session.commit()
        flash('Device successfully updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_device.html', form=form)


@app.route("/delete_device/<string:id>", methods=['POST'])
@is_logged_in
def delete_device(id):
    device = Device.query.get(id)
    db.session.delete(device)
    db.session.commit()

    flash('Device successfully deleted', 'success')
    return redirect(url_for('dashboard'))


@app.route("/add_device", methods=['GET', 'POST'])
@is_logged_in
def add_device():
    form = DeviceForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        tag = form.tag.data
        connection_key = sha256_crypt.encrypt(str(form.connection_key.data))

        new_device = Device(name, tag, connection_key)

        db.session.add(new_device)
        db.session.commit()
        flash('New device successfully added', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_device.html', form=form)


@app.route('/logout')
@is_logged_in
def logout():
    return user_log_out(session=session)


if __name__ == '__main__':
    app.secret_key = 'jpgmd'
    app.run(debug=True)