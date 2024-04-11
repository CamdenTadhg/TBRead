import os
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Book
from forms import UserAddForm, LoginForm
from flask_debugtoolbar import DebugToolbarExtension
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

    print('**************************')
    print(list(request.json))
    print(request.json['username'])
    print(request.json['password'])
    print(request.json['email'])
    print(request.json['userImage'])
    print('*********************')    

    try: 
        user = User.signup(
            username=request.json['username'],
            password=request.json['password'], 
            email=request.json['email'],
            user_image = request.json['userImage']
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
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.login_username.data,
                                 form.login_password.data)
        
        if user: 
            do_login(user)
            flash(f'Hello, {user.username}', 'success')
            return redirect(f'/users/{session[CURR_USER_KEY]}/lists/tbr')
        
        flash('Invalid credentials', 'danger')
        return redirect('/#signupModal')


    
@app.route('/logout', methods=['POST'])
def logout():
    """Handle logout of user"""

    if not g.user:
        flash('You are not logged in', 'danger')
        return redirect('/')
    else:
        do_logout()
        ## flash not working
        flash('You have logged out', 'success')
        return redirect('/')

#########################################################################################
# User Routes

@app.route('/users/<user_id>/lists/tbr')
def display_tbr_list(user_id):
    """Display user's tbr list. Also functions as homepage for logged in user."""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    return render_template('tbrlist.html')




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
        display_books = db.session.query(Book).order_by(Book.added.desc()).limit(12).all()
        return render_template('home-anon.html', display_books=display_books, form=form, form2=form2)





## Select a free theme
## Implement user functionality
    ## login form validation
        ## is username incorrect?
            ## define objects to work with
            ## send data via axios
            ## deal with returned error
        ## is password incorrect?
            ## define objects to work with
            ## send data via axios
            ## deal with returned error
    ## clear errors when new error is posted
    ## clear forms when cancel is pressed
    ## create form for user profile page
    ## create user profile page
    ## patch user
    ## form validation
    ## delete user
    ## create modal for password reset
    ## password reset
    ## create modal for sending username
    ## forgot username
    ## testing routes
    ## testing javascript
## Implement create lists functionality 
## Implement schedule books functionality 
## Implement email reminders functionality 
## Implement scripts & notes functionality 
## Implement challenge functionality 
## Styling
    ## favicon.ico
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