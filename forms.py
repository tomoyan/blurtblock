from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class UserNameForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])


class postUrlForm(FlaskForm):
    url = StringField('url', validators=[DataRequired()])


class TrailForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    posting = StringField('posting', validators=[DataRequired()])


class DelegateForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    amount = StringField('amount', validators=[DataRequired()])
    wif = StringField('wif', validators=[DataRequired()])
