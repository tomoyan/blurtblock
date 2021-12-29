from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange


class UserNameForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])


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
