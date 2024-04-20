import os
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, insert
from models import db, connect_db, User, Book, List, User_Book
from forms import UserAddForm, LoginForm, UserProfileForm, EmailForm, UpdatePasswordForm, BookSearchForm, BookEditForm
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message
import requests
from io import StringIO
from html.parser import HTMLParser
from local_settings import MAIL_PASSWORD
import calendar
from datetime import date
import random
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
app.config['MAIL_USERNAME'] = 'tbreadlistmanager@gmail.com'
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
        user.reading_speed_graphic = form.reading_speed_graphic.data
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

@app.route('/users/<user_id>/lists/tbr', methods=['GET'])
def display_tbr_list(user_id):
    """Display user's tbr list. Also functions as homepage for logged in user."""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    return render_template('books/tbrlist.html')

@app.route('/api/<user_id>/lists/tbr', methods=['GET'])
def return_tbr_list(user_id):
    """Returns contents of tbr list to axios request"""

    list = db.session.execute(db.select(List).where(List.list_type == 'TBR').where(List.user_id == g.user.user_id)).scalar()
    serialized_user_books = [user_book.serialize_user_book() for user_book in list.user_books]
    serialized_user_books
    return jsonify(serialized_user_books)

@app.route('/users/<user_id>/lists/dnf', methods=['GET'])
def display_dnf_list(user_id):
    """Display user's tbr list. Also functions as homepage for logged in user."""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    return render_template('books/dnflist.html')

@app.route('/api/<user_id>/lists/dnf', methods=['GET'])
def return_dnf_list(user_id):
    """Returns contents of dnf list to axios request"""

    list = db.session.execute(db.select(List).where(List.list_type == 'DNF').where(List.user_id == g.user.user_id)).scalar()
    serialized_user_books = [user_book.serialize_user_book() for user_book in list.user_books]
    serialized_user_books
    return jsonify(serialized_user_books)

@app.route('/users/<user_id>/lists/complete', methods=['GET'])
def display_complete_list(user_id):
    """Display user's tbr list. Also functions as homepage for logged in user."""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    return render_template('books/completelist.html')

@app.route('/api/<user_id>/lists/complete', methods=['GET'])
def return_complete_list(user_id):
    """Returns contents of dnf list to axios request"""

    list = db.session.execute(db.select(List).where(List.list_type == 'Complete').where(List.user_id == g.user.user_id)).scalar()
    serialized_user_books = [user_book.serialize_user_book() for user_book in list.user_books]
    serialized_user_books
    return jsonify(serialized_user_books)

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
    response = requests.get(api_url)
    data = response.json()
    google_id = data['id']
    if data['volumeInfo'].get('subtitle'):
        title = f"{data['volumeInfo']['title']}: {data['volumeInfo']['subtitle']}"
    else: 
        title = data['volumeInfo']['title']
    if data['volumeInfo'].get('authors'):
        if len(data['volumeInfo']['authors']) == 1:
            authors = data['volumeInfo']['authors'][0]
        elif len(data['volumeInfo']['authors']) == 2:
            authorA = data['volumeInfo']['authors'][0]
            authorB = data['volumeInfo']['authors'][1]
            authors = f'{authorA} & {authorB}'
        else: 
            authors = ', '.join(data['volumeInfo']['authors'])
            print('*************************')
            print(authors)
    publisher = data['volumeInfo'].get('publisher')
    if data['volumeInfo'].get('publishedDate'):
        pub_date = data['volumeInfo']['publishedDate'][0:4]
    else:
        pub_date = '0000'
    description = data['volumeInfo'].get('description')
    if data['volumeInfo'].get('industryIdentifiers'):
        for item in data['volumeInfo'].get('industryIdentifiers'):
            if item['type'] == "ISBN_13":
                isbn = item['identifier']
        if isbn == '':
            isbn = 0
    else:
        isbn=0
    if data['volumeInfo'].get('pageCount'):
        page_count = data['volumeInfo'].get('pageCount')
    else:
        page_count = 0
    if data['volumeInfo'].get('imageLinks'):
        thumbnail = data['volumeInfo'].get('imageLinks').get('smallThumbnail')
    else: 
        thumbnail = ''
    new_book = Book(google_id=google_id, title=title, authors=authors, publisher=publisher, pub_date=pub_date, description=description, isbn=isbn, page_count=page_count, thumbnail=thumbnail)
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

def add_book_to_tbr(userbook_id):
    list = db.session.execute(db.select(List).where(List.list_type == 'TBR').where(List.user_id == g.user.user_id)).scalar()
    userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == userbook_id)).scalar()
    list.user_books.append(userbook)
    db.session.add(list)
    db.session.commit()

@app.route('/books', methods=['GET'])
def add_books():
    """Search for a book to add to the database"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    form = BookSearchForm()

    return render_template('books/addbooks.html', form=form)

@app.route('/books/<google_id>', methods=['GET', 'POST'])
def edit_new_book(google_id):
    """Add book to database, edit record, add to user's lists of books"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    book = db.session.execute(db.select(Book).where(Book.google_id == google_id)).scalar()
    if book:
        form=BookEditForm(title=book.title, authors=book.authors, publisher=book.publisher, pub_date=book.pub_date, description=book.description, isbn=book.isbn, page_count=book.page_count, thumbnail=book.thumbnail)
    else:
        new_book = addBookToDatabase(google_id)
        ## remove html tags from description
        description = strip_tags(new_book.description)
        form =BookEditForm(title=new_book.title, authors=new_book.authors, publisher=new_book.publisher, pub_date=new_book.pub_date, description=description, isbn=new_book.isbn, page_count=new_book.page_count, thumbnail=new_book.thumbnail)

    if form.validate_on_submit():
        adding_book = db.session.execute(db.select(Book).where(Book.google_id == google_id)).scalar()
        title = form.title.data
        authors = form.authors.data
        publisher = form.publisher.data
        pub_date = form.pub_date.data
        description = form.description.data
        isbn = form.isbn.data
        page_count = form.page_count.data
        age_category = form.age_category.data
        thumbnail = form.thumbnail.data
        notes = form.notes.data
        script = form.script.data
        ## check if user has already added this book
        check_book = db.session.execute(db.select(User_Book).where(User_Book.user_id == g.user.user_id).where(User_Book.book_id == adding_book.book_id)).scalar()
        if not check_book:
            new_user_book = User_Book(user_id=g.user.user_id, book_id=adding_book.book_id, title=title, authors=authors, publisher=publisher, pub_date=pub_date, description=description, isbn=isbn, page_count=page_count, age_category=age_category, thumbnail=thumbnail, notes=notes, script=script) 
            db.session.add(new_user_book)
            db.session.commit()
            add_book_to_tbr(new_user_book.userbook_id)
            return redirect(f'/users/{g.user.user_id}/lists/tbr')
        else:
            flash('This book is already on your lists', 'danger')
    
    return render_template('books/editnewbook.html', form=form)

@app.route('/books/manual', methods=['GET', 'POST'])
def add_book_manually():
    """Add a custom book, not found in GoogleAPI to your TBR list"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    form=BookEditForm()

    if form.validate_on_submit():
        google_id = random.randint(10000000, 99999999)
        title = form.title.data
        author = form.authors.data
        publisher = form.publisher.data
        pub_date = form.pub_date.data
        description = form.description.data
        isbn = form.isbn.data
        page_count = form.page_count.data
        age_category = form.age_category.data
        thumbnail = form.thumbnail.data
        notes = form.notes.data
        script = form.script.data
        ## add the book to the books table in the database
        new_book = Book(google_id=google_id, title=title, author=author, publisher=publisher, pub_date=pub_date, description=description, isbn=isbn, page_count=page_count, thumbnail=thumbnail)
        ## add the book to the users_books table in the database
        new_user_book = User_Book(user_id=g.user.user_id, book_id=new_book.book_id, title=title, author=author, publisher=publisher, pub_date=pub_date, description=description, isbn=isbn, page_count=page_count, age_category=age_category, thumbnail=thumbnail, notes=notes, script=script)
        db.session.add(new_user_book)
        db.session.commit()
        add_book_to_tbr(new_user_book.userbook_id)
        return redirect(f'/users/{g.user.user_id}/lists/tbr')
    
    return render_template('books/manualbook.html', form=form)

@app.route('/users_books/<userbook_id>', methods=['GET', 'POST'])
def edit_book(userbook_id):
    """Edit user copy of book in database"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == userbook_id)).scalar()
    if userbook:
        form=BookEditForm(title=userbook.title, authors=userbook.authors, publisher=userbook.publisher, pub_date=userbook.pub_date, description=userbook.description, isbn=userbook.isbn, page_count=userbook.page_count, thumbnail=userbook.thumbnail)
    else: 
        flash('Book not found. Please try again.')
        return redirect(f'/users/{g.user.user_id}/lists/tbr')

    if form.validate_on_submit():
        userbook.title = form.title.data
        userbook.authors = form.authors.data
        userbook.publisher = form.publisher.data
        userbook.pub_date = form.pub_date.data
        userbook.description = form.description.data
        userbook.isbn = form.isbn.data
        userbook.page_count = form.page_count.data
        userbook.age_category = form.age_category.data
        userbook.thumbnail = form.thumbnail.data
        userbook.notes = form.notes.data
        userbook.script = form.script.data
        db.session.add(userbook)
        db.session.commit()
        return redirect(f'/users/{g.user.user_id}/lists/tbr')

    return render_template('books/editbook.html', form=form, userbook=userbook)

@app.route('/users_books/<userbook_id>/delete', methods=["POST"])
def delete_book(userbook_id):
    """Delete user copy of book from database"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == userbook_id)).scalar()
    if userbook:
        if g.user.user_id == userbook.user_id:
            db.session.delete(userbook)
            db.session.commit()
        else: 
            flash('You do not have permission to do that', 'danger')
    else:
        flash('Book not found. Please try again')
    
    return redirect(f'/users/{g.user.user_id}/lists/tbr')

@app.route('/users_books/<userbook_id>/transfer/<list_type>', methods=["POST"])
def transfer_to_dnf(userbook_id, list_type):
    """Transfer a book between lists"""
    print('transfer request received')

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == userbook_id)).scalar()
    print(userbook)
    list = db.session.execute(db.select(List).where(List.list_type == list_type).where(List.user_id == g.user.user_id)).scalar()
    print(list)
    if userbook: 
        del userbook.lists[0]
        userbook.lists.append(list)
        print(userbook.lists)
        db.session.add(userbook)
        db.session.commit()
    else:
        flash('Book not found. Please try again')
    
    return redirect(f'/users/{g.user.user_id}/lists/tbr')
    
#########################################################################################
# Calendar Routes

@app.route('/users/<user_id>/calendar')
def show_calendar(user_id):
    """Show user's calendar"""

    if not g.user: 
        flash ('Please log in', 'danger')
        return redirect('/')    

    return render_template('calendars/calendar.html')

#########################################################################################
# Notes and Scripts Routes

@app.route('/users/<user_id>/notesandscripts')
def show_books(user_id):
    """Displays all books on the user's lists"""

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


## Implement scripts & notes functionality 
    ## change form inputs for notes & scripts & descriptions to be nice and big
    ## can the user email in notes?
## Implement challenge functionality
    ## create new challenge in detail
    ## display existing challenges in detail
    ## assign books to challenges
    ## assign books to categories
## Deployment
## Implement schedule books functionality
    ## figure out google oAuth
    ## button to create calendar
    ## create calendar on button press
    ## set post days based on user profile
    ## set calendar days as work or off based on a set schedule
    ## set caledar days as work or off based on click
    ## schedule a book individually
        ## autosuggest search field
        ## load cover image on select
        ## start event, calculate end event
        ## or end event, calculate start event
        ## recommend post date (but let them change it)
    ## schedule a year, month, etc. of books randomly
## Implement email reminders functionality 
    ## what books will you need over the next month?
    ## time to start a book
    ## time to finish a book
## Write tests for all routes & for javascript
## Styling
    ## favicon.ico
    ## fix it so that on login, you get the appropriate flash message
    ## reformat user profile 
    ## list displays
    ## add books button to the right place
    ## search form display
    ## search results display
    ## display of authors on edit form
    ## display of description on edit form
    ## fix tabs to be visible
    ## make notes and script field big enough to read easily
    ## display book cover on calendar on start date
    ## make empty book list display look nice
## Documentation
## Refactor based on feedback from mentor and hatchways
## Small Screen Styling
## Implement upload user image
## Implement book covers on homepage are links that take you to a book form where you can add them to your list
## Implement Google Calendar connection
## Implement importation functionality
## Implement OpenAI connection 
## Implement friendship & challenging functionality 
## Implement bookstore connection
## Implement library connection
## Refactor
## Test with actual users and add functionality as needed