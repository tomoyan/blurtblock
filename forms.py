from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange, ValidationError
import re


def username_check(form, field):
    pattern = '^[a-zA-Z0-9-.]+$'
    if not bool(re.match(pattern, field.data)):
        raise ValidationError('Invalid username')


class UserNameForm(FlaskForm):
    username = StringField('username', validators=[
                           DataRequired(), username_check])


class postUrlForm(FlaskForm):
    url = StringField('url', validators=[DataRequired()])


class TrailForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    posting = StringField('posting', validators=[DataRequired()])
    # weight = IntegerField('weight', validators=[DataRequired()])
    weight = IntegerField('weight', validators=[
        DataRequired(), NumberRange(min=10, max=100)])


class DelegateForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    amount = StringField('amount', validators=[DataRequired()])
    wif = StringField('wif', validators=[DataRequired()])
