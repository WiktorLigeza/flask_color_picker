import asyncio
from flask import Flask, session, flash, redirect, url_for, render_template, request
import json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from functools import wraps
from datetime import datetime
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from manager_package import socket_manager as sm

################################################ INIT
connected = set()
secret_key = 'DDUPAZBITA'
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'user.sqlite')
app.config['SQLALCHEMY_BINDS'] = {'two': 'sqlite:///' + os.path.join(basedir, 'device.sqlite'),
                                  'three': 'sqlite:///' + os.path.join(basedir, 'mood.sqlite'),}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init migrate
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


# Init ma
ma = Marshmallow(app)
app.config.from_pyfile('config.cfg')

mail = Mail(app)

s = URLSafeTimedSerializer(secret_key)


################################################ USER DB HANDLING
# User Class/Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(25))
    isActive = db.Column(db.BOOLEAN)


    def __init__(self, name, email, username, password, isActive):
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.isActive = isActive


# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'username', 'password', 'isActive')


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
    owner_id = db.Column(db.Integer)

    def __init__(self, name, tag, connection_key, owner_id):
        self.name = name
        self.tag = tag
        self.connection_key = connection_key
        self.owner_id = owner_id


# Device Schema
class DeviceSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'tag', 'connection_key', 'registration_date', 'owners_id')


# Init schema
device_schema = DeviceSchema()
devices_schema = DeviceSchema(many=True)


class Mood(db.Model):
    __bind_key__ = 'three'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    payload = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer)

    def __init__(self, name, payload, owner_id):
        self.name = name
        self.payload = payload
        self.owner_id = owner_id


# Device Schema
class MoodSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'payload', 'owner_id')


# Init schema
mood_schema = MoodSchema()
moods_schema = MoodSchema(many=True)

from manager_package.user_management import *
from manager_package.device_menagement import *
from manager_package.mood_management import *


class MoodJS:
    def __init__(self, id, name, payload, owner_id):
        self.id = id
        self.name = name
        self.payload = payload
        self.owner_id = owner_id


def serialize_mood(query_list):
    mood_list_serializable = []
    for obj in query_list:
        mood_list_serializable.append({"id":obj.id, "name":obj.name, "payload":json.loads(obj.payload),"owner_id":obj.owner_id})
    return mood_list_serializable

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
    return user_registration(s=s, mail=mail, form=form, db=db)


@app.route('/login', methods=['GET', 'POST'])
def login():
    return user_log_in(session=session)


@app.route("/dashboard")
@is_logged_in
def dashboard():
    user_name = session['username']
    owner = User.query.filter_by(username=user_name).first()
    device_list = Device.query.filter_by(owner_id=owner.id).all()
    mood_list = Mood.query.filter_by(owner_id=owner.id).all()
    if len(device_list) > 0:
        return render_template('dashboard.html', devicelist=device_list, moodList=mood_list)
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
    old_tag = device.tag
    device_id = id

    if request.method == 'POST' and form.validate():
        device.name = request.form['name']
        device.tag = request.form['tag']
        db.session.commit()
        flash('Device successfully updated', 'success')
        loop = asyncio.new_event_loop().run_until_complete(sm.update_tag(device.tag, device.name, old_tag))
        asyncio.set_event_loop(loop)

        return redirect(url_for('dashboard'))
    return render_template('edit_device.html', form=form, device_id=device_id)


@app.route("/edit_device/edit_connection_key/<string:id>", methods=['GET', 'POST'])
@is_logged_in
def edit_connection_key(id):
    device = Device.query.get(id)
    print(id)
    form = ResetConnectionKey(request.form)

    if request.method == 'POST' and form.validate():
        device.connection_key = sha256_crypt.encrypt(str(form.connection_key.data))
        db.session.commit()
        flash('Device successfully updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_connection_key.html', form=form)


@app.route("/delete_device/<string:id>", methods=['POST'])
@is_logged_in
def delete_device(id):
    device = Device.query.get(id)
    db.session.delete(device)
    db.session.commit()

    flash('Device successfully deleted', 'success')
    return redirect(url_for('dashboard'))


@app.route("/delete_mood/<string:id>", methods=['POST'])
@is_logged_in
def delete_mood(id):
    mood = Mood.query.get(id)
    db.session.delete(mood)
    db.session.commit()

    flash('Mood successfully deleted', 'success')
    return redirect(url_for('dashboard'))


@app.route("/edit_mood/<string:id>", methods=['GET', 'POST'])
@is_logged_in
def edit_mood(id):
    mood = Mood.query.get(id)
    name = mood.name
    payload = mood.payload

    if request.method == "POST":
        if len(request.form.get('name')) != 0 and len(request.form.get('colorList')) != 0:
            name = request.form.get('name')
            color_list = request.form.get('colorList')
            brightness = request.form.get('brightness')
            speed = request.form.get('speed')
            loop = request.form.get('drone')
            payload = {"color_list": color_list, "brightness": brightness, "speed": speed, "loop": loop}
            mood.name = name
            mood.payload = json.dumps(payload)
            db.session.commit()
            flash('Device successfully updated', 'success')
            return redirect(url_for('dashboard'))
    return render_template('edit_mood.html',  data={"name": name, "payload": json.loads(payload), 'hexa': "#911abc"})


@app.route('/color/<string:id>', methods=['GET', 'POST'])
def color(id):
    user_name = session['username']
    owner = User.query.filter_by(username=user_name).first()
    device = Device.query.get(id)
    mood_list = Mood.query.filter_by(owner_id=owner.id).all()
    mood_js = serialize_mood(mood_list)

    if request.method == "POST":
        backend_value = request.form.get('colorChange')
        if backend_value is None:
            backend_value = request.form.get('colorChange_MOOD')
        data = {'hexa': backend_value}
        print(backend_value)

        return render_template('color.html', data=data, device=device, moodList=mood_list, moodListJS=mood_js)
    data = {'hexa': "#911abc"}
    return render_template('color.html', data=data, device=device, moodList=mood_list, moodListJS=mood_js)


@app.route("/add_device", methods=['GET', 'POST'])
@is_logged_in
def add_device():
    user_name = session['username']
    owner = User.query.filter_by(username=user_name).first()
    form = DeviceForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        tag = form.tag.data
        connection_key = sha256_crypt.encrypt(str(form.connection_key.data))

        new_device = Device(name, tag, connection_key, owner.id)

        db.session.add(new_device)
        db.session.commit()
        flash('New device successfully added', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_device.html', form=form)


@app.route('/logout')
@is_logged_in
def logout():
    return user_log_out(session=session)


@app.route('/add_mood', methods=['GET', 'POST'])
@is_logged_in
def add_mood():
    user_name = session['username']
    owner = User.query.filter_by(username=user_name).first()
    if request.method == "POST":
        data = {'hexa': request.form.get('colorChange')}
        if len(request.form.get('name')) != 0 and len(request.form.get('colorList')) != 0:
            name = request.form.get('name')
            color_list = request.form.get('colorList')
            brightness = request.form.get('brightness')
            speed = request.form.get('speed')
            loop = request.form.get('drone')
            payload = {"color_list": color_list, "brightness": brightness, "speed": speed, "loop": loop}

            new_mood = Mood(name, json.dumps(payload), owner.id)
            db.session.add(new_mood)
            db.session.commit()

            flash('New mood successfully added', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Provide mood name', 'success')
            return render_template('mood_creator.html', data=data)

    data = {'hexa': "#911abc"}
    return render_template('mood_creator.html', data=data)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=72800)
    except SignatureExpired:
        to_die = User.query.filter(User.email.endswith(s.loads(token, salt='email-confirm'))).all()
        db.session.delete(to_die[0])
        db.session.commit()
        flash('The token is expired! Pleas register again', 'danger')
        return redirect(url_for('register'))

    result = User.query.filter(User.email.endswith(email)).all()
    result[0].isActive = True
    db.session.commit()
    flash('Your email is confirmed you can now logg in', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    #socketio.run(app)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.secret_key = secret_key
    app.run(debug=False)

# arr_x = []
# arr_y = []
# @app.route("/heatmap", methods=['GET', 'POST'])
# def heatmap():
#     global arr_x,arr_y
#     if request.method == "POST":
#         x = request.form["x-arr"]
#         y = request.form["y-arr"]
#
#
#         try:
#             arr_x = [int(i) for i in x.split(',')]
#             arr_y = [int(i) for i in y.split(',')]
#
#             print('X length: ', len(arr_x))
#             print('Y length: ', len(arr_y))
#             print('shape:', len(arr_y))
#             return redirect(url_for('chart'))
#
#
#
#         except: print("start")
#
#     return render_template('heatmap.html')

# @app.route('/chart')
# def chart():
#     fig = px.line(x=arr_x, y=arr_y)
#     return html.Div([dcc.Graph(figure=fig)])

