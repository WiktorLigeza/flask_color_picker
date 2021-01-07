from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from main import User,render_template, request, redirect, flash, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


def user_registration(s, mail, form, db):
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        new_user = User(name, email, username, password, isActive=False)

        #sending email
        email = request.form['email']
        token = s.dumps(email, salt='email-confirm')

        msg = Message('Confirm Email', sender='hal.home.and.led@gmail.com', recipients=[email])

        link = url_for('confirm_email', token=token, _external=True)

        msg.body = 'This link is active for 48 hours: {} '.format(link)

        mail.send(msg)

        db.session.add(new_user)
        db.session.commit()
        flash('Please confirm your email - the link will be active for 48 hours', 'info')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


def user_log_in(session):
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        result = User.query.filter(User.username.endswith(username)).all()
        if len(result) > 0:
            if result[0].isActive:
                password = result[0].password
                if sha256_crypt.verify(password_candidate, password):
                    # Passed
                    session['logged_in'] = True
                    session['username'] = username

                    flash('You are now logged in', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    error = 'Invalid password'
                    return render_template('login.html', error=error)
            else:
                error = 'Please confirm your email'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)


    return render_template('login.html')


def user_log_out(session):
    session.clear()
    flash('You are now logged out', 'info')
    return redirect(url_for('login'))