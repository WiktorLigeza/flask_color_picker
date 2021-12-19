from passlib.hash import sha256_crypt
from wtforms import Form, StringField, PasswordField, validators, BooleanField


# Register Form Class
class ControllerForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    tag = StringField('Tag', [validators.Length(min=4, max=8)])
    has_relay = BooleanField('Relay')


class ControllerFormUpdate(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    tag = StringField('Tag', [validators.Length(min=4, max=8)])
    id = StringField('Id')
    has_relay = BooleanField('Relay')
