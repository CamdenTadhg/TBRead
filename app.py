import os
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Book
from forms import UserAddForm, LoginForm, UserProfileForm, EmailForm
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message
from local_settings import MAIL_PASSWORD
import pdb

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///tbread'))
# os.environ['DATABASE_URL'] = "postgresql:///tbread-test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'theenbydeveloper@gmail.com'
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD

mail=Mail(app)

debug=DebugToolbarExtension(app)

app.app_context().push()

connect_db(app)
db.create_all()

#########################################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add current user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = db.session.query(User).get(session[CURR_USER_KEY])

    else: 
        g.user = None

def do_login(user):
    """Log in user"""

    session[CURR_USER_KEY] = user.user_id

def do_logout():
    """Logout user"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["POST"])
def signup():
    """Handle user signup. Create new user, add to DB and redirect to main list page.
    
    if form not valid, flash error message"""

    if g.user: 
        flash('You are already logged in', 'danger')
        return redirect(f'/users/{g.user.user_id}/lists/tbr')    

    user_image = request.json['userImage']
    if user_image == '':
        user_image = '/static/images/image.png'

    try: 
        user = User.signup(
            username=request.json['username'],
            password=request.json['password'], 
            email=request.json['email'],
            user_image = user_image
        )
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if "users_email_key" in str(e):
            return jsonify({'error': 'Email already taken'})
        if "users_username_key" in str(e):
            return jsonify({'error': 'Username already taken'})
    
    do_login(user)

    return redirect(f'/users/{session[CURR_USER_KEY]}/lists/tbr')
    
@app.route('/login', methods=['POST'])
def login():
    """Handle user login."""

    if g.user: 
        flash('You are already logged in.', 'danger')
        return redirect('/')
      
    user = User.authenticate(request.json['username'],
                                 request.json['password'])
        
    if user: 
        do_login(user)
        flash(f'Hello, {user.username}', 'success')
        return redirect(f'/users/{session[CURR_USER_KEY]}/lists/tbr')
    elif not db.session.execute(db.select(User).where(User.username == request.json['username'])).scalar():
        return jsonify({'error': 'Invalid username'})
    else:
        return jsonify({'error': 'Invalid password'})
    
@app.route('/logout', methods=['POST'])
def logout():
    """Handle logout of user"""

    if not g.user:
        flash('You are not logged in', 'danger')
        return redirect('/')
    else:
        do_logout()
        flash('You have logged out', 'success')
        return redirect('/')
    
@app.route('/forgotusername', methods=['POST'])
def send_username_reminder():
    """Sends user an email reminding them of their username"""

    if g.user: 
        flash('You are already logged in', 'danger')
        return redirect(f'/users/${g.user.user_id}/lists/tbr')
    
    email = request.json['email']
    user = db.session.execute(db.select(User).where(User.email == email)).scalar()
    if user:
        msg = Message(subject='Username reminder', sender='theenbydeveloper@gmail.com', recipients=[user.email])
        msg.html = render_template('emails/usernamereminderemail.html', username=user.username)
        mail.send(msg)
        return redirect('/')
    else: 
        return jsonify({'error': 'Email not in database. Please signup.'})
    
#########################################################################################
# User Routes

@app.route('/users/<user_id>', methods=['GET', 'POST'])
def display_user_profile(user_id):
    """Display user's profile for editing"""

    if int(g.user.user_id) != int(user_id):
        flash('You do not have permission to view this page', 'danger')
        return redirect('/')
        
    form=UserProfileForm(obj=g.user)

    if form.validate_on_submit():
        user = db.session.query(User).get(user_id)
        user.username = form.username.data
        user.email = form.email.data
        user.user_image = form.user_image.data
        user.reading_time_work_day = form.reading_time_work_day.data
        user.reading_time_day_off = form.reading_time_day_off.data
        user.reading_speed_adult = form.reading_speed_adult.data
        user.reading_speed_YA = form.reading_speed_YA.data
        user.reading_speed_children = form.reading_speed_children.data
        user.posting_frequency = form.posting_frequency.data
        user.posting_day = form.posting_day.data
        user.prep_days = form.prep_days.data
        user.content_account = form.content_account.data
        user.email_reminders = form.email_reminders.data
        try: 
            db.session.add(user)
            db.session.commit()
            flash('Changes saved', 'success')
        except IntegrityError as e:
            db.session.rollback()
            if 'users_email_key' in str(e):
                flash('Email already in use', 'danger')
            if 'users_username_key' in str(e):
                flash('Username already in use', 'danger')
        
    return render_template('profile.html', form=form, user=g.user)

@app.route('/users/<user_id>/lists/tbr')
def display_tbr_list(user_id):
    """Display user's tbr list. Also functions as homepage for logged in user."""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    return render_template('tbrlist.html')

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """ Delete user"""

    if not g.user:
        flash('Please log in', 'danger')
    else:
        do_logout()

        db.session.delete(g.user)
        db.session.commit()

        flash('Account deleted', 'danger')

    return redirect('/')

#########################################################################################
# Homepage

@app.route('/')
def homepage():
    """Show homepage: Anonymous users see a display of books; logged in users see their TBR list"""

    if g.user: 
        return redirect(f'/users/{g.user.user_id}/lists/tbr')



    else: 
        form = UserAddForm()
        form2 = LoginForm()
        form3 = EmailForm()
        display_books = db.session.query(Book).order_by(Book.added.desc()).limit(12).all()
        return render_template('home-anon.html', display_books=display_books, form=form, form2=form2, form3=form3)





## Implement user functionality
    ## create modal for password reset
    ## send email via axios
    ## route to send password reset
    ## testing routes
    ## testing javascript
    ## switch to test database
    ## run all tests (include test_models.py)
## Implement create lists functionality 
    ## automatically create three lists when a user is created (TBR, DNF, Done)
    ## add books button
    ## add books to TBR functionality
    ## display TBR appropriately
    ## move books from one list to another functionality
    ## display other two lists appropriately
    ## testing routes
    ## testing javascript
## Implement schedule books functionality 
## Implement email reminders functionality 
## Implement scripts & notes functionality 
## Implement challenge functionality 
## Styling
    ## favicon.ico
    ## fix it so that on login, you get the appropriate flash message
    ## reformat user profile 
## Documentation
## Deployment
## Small Screen Styling
## Implement upload user image
## Implement book covers on homepage are links that take you to a book form where you can add them to your list
## Implement Google Calendar connection
## Implement importation functionality
## Implement OpenAI connection 
## Implement friendship & challenging functionality 
## Implement bookstore connection
## Implement library connection
## Test with actual users and add functionality as needed