from passlib.hash import sha256_crypt
from wtforms import Form, StringField,PasswordField, validators


# Register Form Class
class DeviceForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    tag = StringField('Tag', [validators.Length(min=4, max=8)])
    connection_key = PasswordField('connection key', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='connection key do not match')
    ])
    confirm = PasswordField('Confirm connection key')


class DeviceFormUpdate(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    tag = StringField('Tag', [validators.Length(min=4, max=8)])


# def add_device(form, db, request):
#     if request.method == 'POST' and form.validate():
#         name = form.name.data
#         tag = form.tag.data
#         connection_key = sha256_crypt.encrypt(str(form.connection_key.data))
#
#         new_device = Device(name, tag, connection_key)
#
#         db.session.add(new_device)
#         db.session.commit()
#         flash('New device successfully added', 'success')
#
#         return redirect(url_for('devices'))
#     return render_template('add_device.html', form=form)
