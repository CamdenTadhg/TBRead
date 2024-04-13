from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, IntegerField, BooleanField, SelectField, EmailField
from wtforms.validators import DataRequired, Email, Length, InputRequired

class UserAddForm(FlaskForm):
    """Form for adding users to the system."""

    signup_username = StringField('Username', validators=[DataRequired()])
    signup_password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8)])
    email = EmailField('E-mail', validators=[DataRequired()])
    user_image = StringField('(Optional) User Image URL')

class LoginForm(FlaskForm):
    """Login form"""
    login_username = StringField('Username', validators=[DataRequired()])
    login_password = PasswordField('Password', validators=[Length(min=8)])

class UserProfileForm(FlaskForm):
    """Form for editing user information."""
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('E-mail', validators=[DataRequired()])
    user_image = StringField('User Image')
    reading_time_work_day = DecimalField('How many hours do you read on work days?', places=2, default=0)
    reading_time_day_off = DecimalField('How many hours do you read on off days?', places=2, default=0)
    reading_speed_adult = IntegerField('How many pages of an adult book do you read per hour?', default=0)
    reading_speed_YA = IntegerField('How many pages of a YA book do you read per hour?', default=0)
    reading_speed_children = IntegerField('How many pages of a kids book do you read per hour?', default=0)
    posting_frequency = IntegerField('How often do you post, in days?', default=0)
    posting_day = SelectField('What day do you post?', choices=[('', ''), ('mon', 'Monday'), ('tues', 'Tuesday'), ('wed', 'Wednesday'), ('thurs', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday')])
    prep_days = IntegerField('How many days before posting would you like to finish books?', default=0)
    content_account = StringField('URL of posting account')
    email_reminders = BooleanField('Do you want email reminders?')

    def matching_passwords(self):
        rv = FlaskForm.validate(self)
        if not rv: 
            return False
        
        if self.password.data != self.password2.data:
            self.password.errors.append('Passwords do not match')
            return False
        return True
    
class EmailForm(FlaskForm):
    email = EmailField('Please enter your email', validators=[InputRequired(message="Please enter your email")])