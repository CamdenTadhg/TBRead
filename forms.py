from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, IntegerField, BooleanField, SelectField, EmailField, DateField
from wtforms.validators import DataRequired, Email, Length, InputRequired, ValidationError
from wtforms.widgets import TextArea
import re


def password_requirements(form, field):
    password_regex = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$')
    if not password_regex.match(form.password.data):
        raise ValidationError('Password must include one capital letter, one lowercase letter, one number, and one special character')
    
def matching_passwords(form, field):
    if form.password.data != form.password2.data:
        raise ValidationError('Passwords do not match. Please try again.')
    
class UserAddForm(FlaskForm):
    """Form for adding users to the system."""

    signup_username = StringField('Username', validators=[DataRequired(message="Please enter a username.")])
    signup_password = PasswordField('Password', validators=[DataRequired(message="Please enter a password"), Length(min=8, message="Please enter a password of at least 8 characters."), password_requirements, matching_passwords])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(message="Please confirm your password"), Length(min=8, message="Please enter a password of at least 8 characters.")])
    signup_email = EmailField('E-mail', validators=[DataRequired(message="Please enter an email"), Email(message="Your email appears invalid. Please try again.")])
    user_image = StringField('(Optional) User Image URL')

class LoginForm(FlaskForm):
    """Login form"""
    login_username = StringField('Username', validators=[DataRequired(message="Please enter your username")])
    login_password = PasswordField('Password', validators=[DataRequired(message="Please enter your password"), Length(min=8, message="Passwords must be 8 characters long.")])

class UserProfileForm(FlaskForm):
    """Form for editing user information."""
    username = StringField('Username', validators=[DataRequired(message="Please enter a username")])
    email = EmailField('E-mail', validators=[DataRequired(message="Please enter an email"), Email(message="Your email appears invalid. Please try again.")])
    user_image = StringField('User Image')
    reading_time_work_day = DecimalField('How many hours do you read on work days?', places=2, default=0)
    reading_time_day_off = DecimalField('How many hours do you read on off days?', places=2, default=0)
    reading_speed_adult = IntegerField('How many pages of an adult book do you read per hour?', default=0)
    reading_speed_YA = IntegerField('How many pages of a YA book do you read per hour?', default=0)
    reading_speed_children = IntegerField('How many pages of a kids book do you read per hour?', default=0)
    reading_speed_graphic = IntegerField('How many pages of a graphic novel do you read per hour?', default=0)
    posting_frequency = IntegerField('How often do you post, in days?', default=0)
    posting_day = SelectField('What day do you post?', choices=[('', ''), ('mon', 'Monday'), ('tues', 'Tuesday'), ('wed', 'Wednesday'), ('thurs', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday')])
    prep_days = IntegerField('How many days before posting would you like to finish books?', default=0)
    content_account = StringField('URL of posting account')
    email_reminders = BooleanField('Do you want email reminders?')
    incoming_email = StringField('Your notes email')
    
class EmailForm(FlaskForm):
    email = EmailField('Please enter your email', validators=[InputRequired(message="Please enter your email."), Email(message="Your email appears invalid. Please try again.")])

class UpdatePasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired(message='Please enter a password'), password_requirements, matching_passwords])
    password2 = PasswordField('Confirm Password', validators=[InputRequired(message='Please confirm your password')])

class BookSearchForm(FlaskForm):
    field = SelectField('Search Field', choices=[('title', 'Title'), ('author', 'Author'), ('isbn', 'ISBN')])
    term = StringField('Search Term')

class BookEditForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(message="Please enter a title.")])
    authors = StringField('Authors', validators=[DataRequired(message="Please enter an author.")])
    publisher = StringField('Publisher')
    pub_date = StringField('Publication Date')
    description = StringField('Description', widget=TextArea())
    isbn = IntegerField('ISBN', default=0)
    page_count = IntegerField('Page Count', default=0)
    age_category = SelectField('Age Category', choices=[('N/A', 'N/A'), ('Adult', 'Adult'), ('YA', 'YA'), ('Childrens', 'Childrens'), ('Graphic', 'Graphic')])
    thumbnail = StringField('Cover Image')
    notes = StringField('Notes', widget=TextArea())
    script = StringField('Script', widget=TextArea())

class ChallengeForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(message="Please enter a challenge name.")])
    num_books = IntegerField("Number of Books", validators=[InputRequired(message="Please enter a number of books.")])
    description = StringField('Description')

class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(message="Please enter a name for this category")])
    description = StringField('Description', widget=TextArea())

class UserChallengeForm(FlaskForm):
    name = StringField('Name')
    num_books = IntegerField('Number of Books')
    description = StringField('Description')
    start_date = StringField('Start date')
    end_date = StringField('End date')

class PostDaysForm(FlaskForm):
    last_post_date = DateField('When was your last post day?')
    posting_frequency = IntegerField('How often do you post, in days?', default=0)
    posting_day = SelectField('What day do you post?', choices=[('', ''), ('mon', 'Monday'), ('tues', 'Tuesday'), ('wed', 'Wednesday'), ('thurs', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday')])
