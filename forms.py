from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class UserNameForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])


class postUrlForm(FlaskForm):
    url = StringField('url', validators=[DataRequired()])
