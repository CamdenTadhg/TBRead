import os
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, insert
from models import db, connect_db, User, Book, List, Author
from forms import UserAddForm, LoginForm, UserProfileForm, EmailForm, UpdatePasswordForm, BookSearchForm, BookEditForm
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message
import requests
from io import StringIO
from html.parser import HTMLParser
from local_settings import MAIL_PASSWORD
import calendar
import pdb

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///tbread'))
# app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', "postgresql:///tbread-test"))
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
    create_lists(user)

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
        return jsonify({'success': 'Email sent'})
    else: 
        return jsonify({'error': 'Email not in database. Please signup.'})
    
@app.route('/forgotpassword', methods=['POST'])
def send_password_reset():
    """Send user a password reset email"""

    if g.user:
        flash('You are already logged in', 'danger')
        return redirect(f'/users/${g.user.user_id}/lists/tbr')
    
    email = request.json['email']
    print('*********************')
    print(email)
    user = db.session.execute(db.select(User).where(User.email == email)).scalar()
    if user:
        prt = user.get_password_reset_token()
        stmt = update(User).where(User.email == email).values(password_reset_token=prt)
        db.session.execute(stmt)
        db.session.commit()
        msg = Message(subject='Password Reset Link', sender='theenbydeveloper@gmail.com', recipients=[email])
        msg.html = render_template('emails/passwordresetemail.html', prt=prt, email=email)
        mail.send(msg)
        return jsonify({'success': 'Email sent'})
    else:
        return jsonify({'error': 'Email not in database. Please signup.'})
    
@app.route('/passwordreset', methods=['GET', 'POST'])
def password_reset():
    """Displays password reset form and resets password from password reset link"""
    if g.user:
        flash('You are already logged in', 'danger')
        return redirect(f'/users/${g.user.user_id}/lists/tbr')
    
    form = UpdatePasswordForm()
    email = request.args.get('email')
    prt = request.args.get('prt')
    user = db.session.execute(db.select(User).where(User.email == email)).scalar()

    if form.validate_on_submit():
        password = form.password.data
        stmt = user.update_password(pwd=password, email=email)
        db.session.execute(stmt)
        try:
            db.session.commit()
        except:
            flash('Something went wrong. Please try again')
        stmt2 = update(User).where(User.email == email).values(password_reset_token=None)
        db.session.execute(stmt2)
        try:
            db.session.commit()
        except:
            flash('Something went wrong. Please try again')
        return redirect('/')
    elif user and user.password_reset_token == prt:
        return render_template('passwordreset.html', form=form)
    else: 
        flash('Unauthorized password reset attempt', 'danger')
        return redirect('/')
    
@app.route('/updatepassword', methods=["POST"])
def update_password():
    """Updates user's password"""

    user=db.session.execute(db.select(User).where(User.user_id == g.user.user_id)).scalar()

    password=request.json['password']
    stmt = user.update_password(pwd=password, email=user.email)
    db.session.execute(stmt)
    try:
        db.session.commit()
    except:
        return jsonify({'error': 'Something went wrong'})
    return jsonify({'success': 'Password updated'})

    
#########################################################################################
# User Routes

def create_lists(user):
    """Create three lists when new user is created"""

    stmt = (insert(List).values(list_type='TBR', user_id=user.user_id))
    stmt2 = (insert(List).values(list_type='DNF', user_id=user.user_id))
    stmt3 = (insert(List).values(list_type='Complete', user_id=user.user_id))
    db.session.execute(stmt)
    db.session.execute(stmt2)
    db.session.execute(stmt3)
    db.session.commit()
    
@app.route('/users/<user_id>', methods=['GET', 'POST'])
def display_user_profile(user_id):
    """Display user's profile for editing"""

    if int(g.user.user_id) != int(user_id):
        flash('You do not have permission to view this page', 'danger')
        return redirect('/')
        
    form=UserProfileForm(obj=g.user)
    form2= UpdatePasswordForm()

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
        
    return render_template('profile.html', form=form, form2=form2, user=g.user)


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
# Book Routes

def addBookToDatabase(google_id):
    api_url = f"https://www.googleapis.com/books/v1/volumes/{google_id}"
    print('***********************')
    print(api_url)
    response = requests.get(api_url)
    data = response.json()
    print('************************')
    print(data)
    google_id = data['id']
    if data['volumeInfo'].get('subtitle'):
        title = f"{data['volumeInfo']['title']}: {data['volumeInfo']['subtitle']}"
    else: 
        title = data['volumeInfo']['title']
    publisher = data['volumeInfo']['publisher']
    pub_date = data['volumeInfo']['publishedDate'][0:4]
    description = data['volumeInfo']['description']
    for item in data['volumeInfo']['industryIdentifiers']:
        if item['type'] == "ISBN_13":
            isbn = item['identifier']
    page_count = data['volumeInfo']['pageCount']
    thumbnail = data['volumeInfo']['imageLinks']['smallThumbnail']
    new_book = Book(google_id=google_id, title=title, publisher=publisher, pub_date=pub_date, description=description, isbn=isbn, page_count=page_count, thumbnail=thumbnail)
    db.session.add(new_book)
    db.session.commit()
    for item in data['volumeInfo']['authors']:
        author = db.session.execute(db.select(Author).where(Author.name == item)).scalar()
        if author:
            new_book.authors.append(author)
            db.session.add(new_book)
            db.session.commit()
        else:
            new_author = Author(name=item)
            db.session.add(new_author)
            db.session.commit()
            new_book.authors.append(new_author)
            db.session.add(new_book)
            db.session.commit()
    return new_book

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict=False
        self.convert_charrefs=True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()
    
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

@app.route('/books', methods=['GET', 'POST'])
def add_books():
    """Add books to a user's TBR list"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    form = BookSearchForm()

    return render_template('books/addbooks.html', form=form)

@app.route('/books/<google_id>', methods=['GET', 'POST'])
def edit_book(google_id):
    """Add book to database, edit record, add to user's lists of books"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    book = db.session.execute(db.select(Book).where(Book.google_id == google_id)).scalar()
    if book:
        form=BookEditForm(title=book.title, authors=book.authors, publisher=book.publisher, pub_date=book.pub_date, description=book.description, isbn=book.isbn, page_count=book.page_count, thumbnail=book.thumbnail)
    else:
        new_book = addBookToDatabase(google_id)
        description = strip_tags(new_book.description)
        form =BookEditForm(title=new_book.title, authors=new_book.authors, publisher=new_book.publisher, pub_date=new_book.pub_date, description=description, isbn=new_book.isbn, page_count=new_book.page_count, thumbnail=new_book.thumbnail)

        
    
    return render_template('books/editbook.html', form=form)


@app.route('/users/<user_id>/lists/tbr')
def display_tbr_list(user_id):
    """Display user's tbr list. Also functions as homepage for logged in user."""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    return render_template('books/tbrlist.html')


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


## Implement create lists functionality 
    ## add books
            ## on click of save, add book to user_books
            ## add book to list
    ## add book manually
    ## edit book
    ## delete book
    ## display TBR appropriately
        ## search field
        ## each title should be a link to open the edit book form
    ## move books from one list to another functionality
    ## display other two lists appropriately
## Implement schedule books functionality 
## Implement email reminders functionality 
## Implement scripts & notes functionality 
## Implement challenge functionality 
## Write tests for all routes & for javascript
## Styling
    ## favicon.ico
    ## fix it so that on login, you get the appropriate flash message
    ## reformat user profile 
    ## list displays
    ## add books button to the right place
    ## search results display
    ## display of authors on edit form
    ## display of description on edit form
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