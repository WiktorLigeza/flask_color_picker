from passlib.hash import sha256_crypt
from wtforms import Form, StringField,PasswordField, validators


# Register Form Class
class MoodForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    payload = StringField('Colors')


class MoodFormUpdate(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    payload = StringField('Colors')
    id = StringField('Id')
