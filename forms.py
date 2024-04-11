from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class UserAddForm(FlaskForm):
    """Form for adding users to the system."""

    signup_username = StringField('Username', validators=[DataRequired()])
    signup_password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8)])
    email = StringField('E-mail', validators=[DataRequired()])
    user_image = StringField('(Optional) User Image URL')

class LoginForm(FlaskForm):
    """Login form"""
    login_username = StringField('Username', validators=[DataRequired()])
    login_password = PasswordField('Password', validators=[Length(min=8)])