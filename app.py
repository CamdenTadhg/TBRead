import os
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify, url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, insert
from models import db, connect_db, User, Book, List, User_Book, Challenge, User_Challenge, User_Book_Challenge, AgeCategory, Event
from forms import UserAddForm, LoginForm, UserProfileForm, EmailForm, UpdatePasswordForm, BookEditForm, ChallengeForm, UserChallengeForm, PostDaysForm
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message
from local_settings import MAIL_PASSWORD, SECRET_KEY, CLIENT_SECRETS_FILE
import requests
from io import StringIO
from html.parser import HTMLParser
import random
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import json 
import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials
from datetime import date

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///tbread'))
# app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', "postgresql:///tbread-test"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'tbreadlistmanager@gmail.com'
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD

mail=Mail(app)

debug=DebugToolbarExtension(app)

connect_db(app)



#########################################################################################
# Authentication

@app.before_request
def add_user_to_g():
    """If we're logged in, add current user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = db.session.execute(db.select(User).where(User.user_id == session[CURR_USER_KEY])).scalar()

    else: 
        g.user = None

def do_login(user):
    """Log in user"""
    with app.app_context():
        session[CURR_USER_KEY] = user.user_id

def do_logout():
    """Logout user"""
    with app.app_context():
        if CURR_USER_KEY in session:
            del session[CURR_USER_KEY]

@app.route('/signup', methods=["POST"])
def signup():
    """Handle user signup. Create new user, add to DB and redirect to main list page.
    
    if form not valid, flash error message"""

    if g.user: 
        flash('You are already logged in', 'danger')
        return redirect(f'/users/{g.user.user_id}/lists/tbr')    

    # add default user image to data
    user_image = request.json['userImage']
    if user_image == '':
        user_image = '/static/images/image.png'

    username=request.json['username'],
    try: 
        user = User.signup(
            username,
            password=request.json['password'], 
            email=request.json['email'],
            user_image = user_image
        )
        db.session.commit()
    # handle duplicate email or username errors
    except IntegrityError as e:
        db.session.rollback()
        if "users_email_key" in str(e):
            return jsonify({'error': 'Email already taken'})
        if "users_username_key" in str(e):
            return jsonify({'error': 'Username already taken'})
    
    do_login(user)
    create_lists(user)

    return jsonify({'success': 'true'})
    
@app.route('/login', methods=['POST'])
def login():
    """Handle user login."""

    if g.user: 
        flash('You are already logged in.', 'danger')
        return redirect(f'/users/{g.user.user_id}/lists/tbr')    

    username = request.json['username']
    user = User.authenticate(username,
                            request.json['password'])
        
    if user: 
        do_login(user)
        return jsonify({'success': 'true'})
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
        return redirect(f'/users/{g.user.user_id}/lists/tbr')
    
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
        return redirect(f'/users/{g.user.user_id}/lists/tbr')
    
    email = request.json['email']
    user = db.session.execute(db.select(User).where(User.email == email)).scalar()
    if user:
        prt = user.get_password_reset_token()
        stmt = update(User).where(User.email == email).values(password_reset_token=prt)
        db.session.execute(stmt)
        try: 
            db.session.commit()
        except: 
            db.session.rollback()
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
        return redirect(f'/users/{g.user.user_id}/lists/tbr')
    
    form = UpdatePasswordForm()
    email = request.args.get('email')
    prt = request.args.get('prt')
    user = db.session.execute(db.select(User).where(User.email == email)).scalar()

    # handle password update
    if form.validate_on_submit():
        password = form.update_password.data
        stmt = user.update_password(pwd=password, email=email)
        db.session.execute(stmt)
        try:
            db.session.commit()
        except:
            flash('Something went wrong. Please try again')
            db.session.rollback()
        stmt2 = update(User).where(User.email == email).values(password_reset_token=None)
        db.session.execute(stmt2)
        try:
            db.session.commit()
        except:
            flash('Something went wrong. Please try again')
            db.session.rollback()
        return redirect('/')
    # display password update form
    elif user and user.password_reset_token == prt:
        return render_template('passwordreset.html', form=form)
    # handle unauthorized password update
    else: 
        flash('Unauthorized password reset attempt', 'danger')
        return redirect('/')
    
@app.route('/updatepassword', methods=["POST"])
def update_password():
    """Updates user's password from the user profile page"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')

    user=db.session.execute(db.select(User).where(User.user_id == g.user.user_id)).scalar()

    password=request.json['password']
    stmt = user.update_password(pwd=password, email=user.email)
    db.session.execute(stmt)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'error': 'Something went wrong'})
    return jsonify({'success': 'Password updated'})

    
#########################################################################################
# User Routes

def create_lists(user):   
    """Create three lists when new user is created"""
    with app.app_context():
        stmt = (insert(List).values(list_type='TBR', user_id=user.user_id))
        stmt2 = (insert(List).values(list_type='DNF', user_id=user.user_id))
        stmt3 = (insert(List).values(list_type='Complete', user_id=user.user_id))
        db.session.execute(stmt)
        db.session.execute(stmt2)
        db.session.execute(stmt3)
        try: 
            db.session.commit()
        except: 
            db.session.rollback()
    
@app.route('/users/<user_id>', methods=['GET', 'POST'])
def display_user_profile(user_id):
    """Display user's profile for editing"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    form=UserProfileForm(obj=g.user)
    # update password form appears as a modal upon button click
    form2= UpdatePasswordForm()

    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.user_id == g.user.user_id)).scalar()
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
        except: 
            db.session.rollback()
            flash('Something went wrong. Please try again')
        
    return render_template('profile.html', form=form, form2=form2, user=g.user)

@app.route('/users/<user_id>/lists/tbr', methods=['GET'])
def display_tbr_list(user_id):
    """Display user's tbr list. Also functions as homepage for logged in user."""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    return render_template('users/tbrlist.html')

@app.route('/api/<user_id>/lists/tbr', methods=['GET'])
def return_tbr_list(user_id):
    """Returns contents of tbr list to axios request"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')

    list = db.session.execute(db.select(List).where(List.list_type == 'TBR').where(List.user_id == g.user.user_id)).scalar()
    serialized_user_books = [user_book.serialize_user_book() for user_book in list.user_books]
    return jsonify(serialized_user_books)

@app.route('/users/<user_id>/lists/dnf', methods=['GET'])
def display_dnf_list(user_id):
    """Display user's dnf list."""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    return render_template('users/dnflist.html')

@app.route('/api/<user_id>/lists/dnf', methods=['GET'])
def return_dnf_list(user_id):
    """Returns contents of dnf list to axios request"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')

    list = db.session.execute(db.select(List).where(List.list_type == 'DNF').where(List.user_id == g.user.user_id)).scalar()
    serialized_user_books = [user_book.serialize_user_book() for user_book in list.user_books]
    return jsonify(serialized_user_books)

@app.route('/users/<user_id>/lists/complete', methods=['GET'])
def display_complete_list(user_id):
    """Display user's complete list."""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    return render_template('users/completelist.html')

@app.route('/api/<user_id>/lists/complete', methods=['GET'])
def return_complete_list(user_id):
    """Returns contents of complete list to axios request"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')

    list = db.session.execute(db.select(List).where(List.list_type == 'Complete').where(List.user_id == g.user.user_id)).scalar()
    serialized_user_books = [user_book.serialize_user_book() for user_book in list.user_books]
    return jsonify(serialized_user_books)

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """ Delete user"""

    if not g.user:
        flash('Please log in', 'danger')
    else:
        do_logout()

        db.session.delete(g.user)
        try: 
            db.session.commit()
        except: 
            db.session.rollback()
            flash('Delete failed. Please try again', 'danger')

        flash('Account deleted', 'danger')

    return redirect('/')

#########################################################################################
# Book Routes

class MLStripper(HTMLParser):
    """Used to strip html tags from google description field"""
    with app.app_context():
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
    """Used to strip html tags from google description field"""
    with app.app_context():
        s = MLStripper()
        s.feed(html)
        return s.get_data()
    
def add_book_to_database(google_id):
    """Parses google data into appropriate format and adds book to database"""
    with app.app_context():
        title=authors=publisher=description=thumbnail=''
        isbn=page_count=0
        pub_date='0000'
        api_url = f"https://www.googleapis.com/books/v1/volumes/{google_id}"
        response = requests.get(api_url)
        data = response.json()
        google_id = data['id']
        if data['volumeInfo'].get('subtitle'):
            title = f"{data['volumeInfo']['title']}: {data['volumeInfo']['subtitle']}"
        else: 
            title = data['volumeInfo']['title']
        # handle various combinations of authors
        if data['volumeInfo'].get('authors'):
            if len(data['volumeInfo']['authors']) == 1:
                authors = data['volumeInfo']['authors'][0]
            elif len(data['volumeInfo']['authors']) == 2:
                authorA = data['volumeInfo']['authors'][0]
                authorB = data['volumeInfo']['authors'][1]
                authors = f'{authorA} & {authorB}'
            else: 
                authors = ', '.join(data['volumeInfo']['authors'])
        publisher = data['volumeInfo'].get('publisher')
        if data['volumeInfo'].get('publishedDate'):
            pub_date = data['volumeInfo']['publishedDate'][0:4]
        if data['volumeInfo'].get('description'):
            description = strip_tags(data['volumeInfo']['description'])
        if data['volumeInfo'].get('industryIdentifiers'):
            for item in data['volumeInfo'].get('industryIdentifiers'):
                if item['type'] == "ISBN_13":
                    isbn = item['identifier']
        if data['volumeInfo'].get('pageCount'):
            page_count = data['volumeInfo'].get('pageCount')
        if data['volumeInfo'].get('imageLinks'):
            thumbnail = data['volumeInfo'].get('imageLinks').get('smallThumbnail')
        new_book = Book(google_id=google_id, title=title, authors=authors, publisher=publisher, pub_date=pub_date, description=description, isbn=isbn, page_count=page_count, thumbnail=thumbnail)
        db.session.add(new_book)
        try: 
            db.session.commit()
        except: 
            db.session.rollback()
        return new_book.book_id

def add_book_to_tbr(userbook_id):
    """Adds newly parsed book data to userbook table and user's tbr list"""
    with app.app_context():
        if CURR_USER_KEY in session:
            g.user = db.session.execute(db.select(User).where(User.user_id == session[CURR_USER_KEY])).scalar()
        else: 
            g.user = None
        list = db.session.execute(db.select(List).where(List.list_type == 'TBR').where(List.user_id == g.user.user_id)).scalar()
        userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == userbook_id)).scalar()
        list.user_books.append(userbook)
        db.session.add(list)
        try: 
            db.session.commit()
        except: 
            db.session.rollback()

@app.route('/books', methods=['GET'])
def add_books():
    """Search for a book to add to the database"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')

    return render_template('books/addbooks.html')

@app.route('/books/<google_id>', methods=['GET', 'POST'])
def edit_new_book(google_id):
    """Add book to database, edit record, add to user's lists of books"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    book = db.session.execute(db.select(Book).where(Book.google_id == google_id)).scalar()
    if book:
        if book.description: 
            ## strip tags code duplicated due to early incorrect data entry
            description = strip_tags(book.description)
        else: 
            description = ''
        form=BookEditForm(title=book.title, authors=book.authors, publisher=book.publisher, pub_date=book.pub_date, description=description, isbn=book.isbn, page_count=book.page_count, thumbnail=book.thumbnail)
    else:
        new_book_id = add_book_to_database(google_id)
        new_book = db.session.execute(db.select(Book).where(Book.book_id == new_book_id)).scalar()
        ## remove html tags from description
        if new_book.description: 
            description = strip_tags(new_book.description)
        else: 
            description = ''
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
        if form.age_category.data == 'N/A':
            age_category = 'NA'
        else:
            age_category = form.age_category.data
        thumbnail = form.thumbnail.data
        notes = form.notes.data
        script = form.script.data
        ## check if user has already added this book
        check_book = db.session.execute(db.select(User_Book).where(User_Book.user_id == g.user.user_id).where(User_Book.book_id == adding_book.book_id)).scalar()
        if not check_book:
            ## if book is not already on user's book list, add to user's book list
            new_user_book = User_Book(user_id=g.user.user_id, book_id=adding_book.book_id, title=title, authors=authors, publisher=publisher, pub_date=pub_date, description=description, isbn=isbn, page_count=page_count, age_category=age_category, thumbnail=thumbnail, notes=notes, script=script) 
            db.session.add(new_user_book)
            try: 
                db.session.commit()
            except: 
                db.session.rollback()
                flash('Something went wrong. Please try again', 'danger')
            add_book_to_tbr(new_user_book.userbook_id)
            return redirect(f'/users/{g.user.user_id}/lists/tbr')
        else:
            ## if book is already on user's book list, notify user. 
            flash('This book is already on your lists', 'danger')
    
    return render_template('books/editnewbook.html', form=form)

@app.route('/books/manual', methods=['GET', 'POST'])
def add_book_manually():
    """Add a custom book, not found in GoogleAPI to TBR list"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    form=BookEditForm()

    if form.validate_on_submit():
        google_id = random.randint(10000000, 99999999)
        title = form.title.data
        authors = form.authors.data
        publisher = form.publisher.data
        pub_date = form.pub_date.data
        description = form.description.data
        isbn = form.isbn.data
        page_count = form.page_count.data
        if form.age_category.data == 'N/A':
            age_category = 'NA'
        else:
            age_category = form.age_category.data
        thumbnail = form.thumbnail.data
        notes = form.notes.data
        script = form.script.data
        ## add the book to the books table in the database
        new_book = Book(google_id=google_id, title=title, authors=authors, publisher=publisher, pub_date=pub_date, description=description, isbn=isbn, page_count=page_count, thumbnail=thumbnail)
        db.session.add(new_book)
        try: 
            db.session.commit()
        except: 
            db.session.rollback()
        ## add the book to the users_books table in the database
        new_user_book = User_Book(user_id=g.user.user_id, book_id=new_book.book_id, title=title, authors=authors, publisher=publisher, pub_date=pub_date, description=description, isbn=isbn, page_count=page_count, age_category=age_category, thumbnail=thumbnail, notes=notes, script=script)
        db.session.add(new_user_book)
        try: 
            db.session.commit()
        except: 
            db.session.rollback()
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
    user_challenges = db.session.execute(db.select(User_Challenge).where(User_Challenge.user_id == g.user.user_id)).scalars()
    if userbook:
        form=BookEditForm(title=userbook.title, authors=userbook.authors, publisher=userbook.publisher, pub_date=userbook.pub_date, description=userbook.description, isbn=userbook.isbn, page_count=userbook.page_count, age_category=str(userbook.age_category.value), thumbnail=userbook.thumbnail, notes=userbook.notes, script=userbook.script)
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
        ## AgeCategory is an ENUM field
        userbook.age_category = AgeCategory(form.age_category.data)
        userbook.thumbnail = form.thumbnail.data
        userbook.notes = form.notes.data
        userbook.script = form.script.data
        db.session.add(userbook)
        try: 
            db.session.commit()
        except: 
            db.session.rollback()
            flash('Something went wrong. Please try again', 'danger')
        return redirect(f'/users/{g.user.user_id}/lists/tbr')

    return render_template('books/editbook.html', form=form, userbook=userbook, user_challenges=user_challenges)

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
            try: 
                db.session.commit()
            except: 
                db.session.rollback()
                flash('Delete failed. Please try again', 'danger')
        else: 
            flash('You do not have permission to do that', 'danger')
    else:
        flash('Book not found. Please try again')
    
    return redirect(f'/users/{g.user.user_id}/lists/tbr')

@app.route('/users_books/<userbook_id>/transfer/<list_type>', methods=["POST"])
def transfer_between_lists(userbook_id, list_type):
    """Transfer a book between lists. Books can only be on one list at a time."""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')

    userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == userbook_id)).scalar()
    list = db.session.execute(db.select(List).where(List.list_type == list_type).where(List.user_id == g.user.user_id)).scalar()
    if userbook: 
        if g.user.user_id == userbook.user_id:
            del userbook.lists[0]
            userbook.lists.append(list)
            db.session.add(userbook)
            try: 
                db.session.commit()
            except: 
                db.session.rollback()
                flash('Something went wrong. Please try again.', 'danger')
        else: 
            flash('You do not have permission to do that', 'danger')
            return redirect(f'/users/{g.user.user_id}/lists/tbr')
    else:
        flash('Book not found. Please try again')
        return redirect(f'/users/{g.user.user_id}/lists/tbr')
    ## If transfering a book to the Complete list, change the complete boolean value in the userbook_challenge table so it will appear appropriately in the challenge listing
    if list_type == 'Complete':
        userbook_challenges = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == userbook.userbook_id)).scalars()
        for userbook_challenge in userbook_challenges:
            userbook_challenge.complete = True
            db.session.add(userbook_challenge)
            try: 
                db.session.commit()
            except: 
                db.session.rollback()
                flash('Something went wrong. Please try again.', 'danger')
    # If transfering book to TBR or DNF, ensure the complete boolean value in the userbook_challenge table is set to false
    else: 
        userbook_challenges = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == userbook.userbook_id)).scalars()
        for userbook_challenge in userbook_challenges:
            userbook_challenge.complete = False
            db.session.add(userbook_challenge)
            try: 
                db.session.commit()
            except: 
                db.session.rollback()
                flash('Something went wrong. Please try again.', 'danger')
    
    return redirect(f'/users/{g.user.user_id}/lists/tbr')

@app.route('/api/users_books/<userbook_id>/assign', methods=['POST'])
def assign_book(userbook_id):
    """Assign a user copy of a book to a challenge"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    ## find book being assigned
    userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == userbook_id)).scalar()
    if userbook.user_id != g.user.user_id:
        flash('You do not have permission to do that', 'danger')
        return redirect(f'/users/{g.user.user_id}/lists/tbr')
    data = request.json
    challenge_id = data.get('challenge_id')
    ## find challenge book is being assigned to
    challenge = db.session.execute(db.select(Challenge).where(Challenge.challenge_id == challenge_id)).scalar()
    ## create connection between book and challenge 
    if userbook:
        userbook.challenges.append(challenge)
        try: 
            db.session.add(userbook)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Book already in challenge'})
        except: 
            db.session.rollback()
            flash('Something went wrong. Please try again.', 'danger')
        userbook_challenge = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == userbook.userbook_id).where(User_Book_Challenge.challenge_id == challenge.challenge_id)).scalar()
        ## if book is completed, ensure userbook_challenge complete field is set to true so book will appear correctly in challenge listing
        if userbook.lists[0].list_type == 'Complete':
            userbook_challenge.complete = True
        else: 
            userbook_challenge.complete = False
        db.session.add(userbook_challenge)
        try: 
            db.session.commit()
        except:
            db.session.rollback()
            flash('Something went wrong. Please try again', 'danger')
    return jsonify({'success': 'Book added'})

@app.route('/api/users_books/<userbook_id>/remove', methods=['POST'])
def remove_book(userbook_id):
    """Remove a user copy of a book from a challenge"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')


    userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == userbook_id)).scalar()
    if userbook.user_id != g.user.user_id:
        flash('You do not have permission to do that', 'danger')
        return redirect(f'/users/{g.user.user_id}/lists/tbr')
    data = request.json
    challenge_id = data.get('challenge_id')
    challenge = db.session.execute(db.select(Challenge).where(Challenge.challenge_id == challenge_id)).scalar()
    if userbook:
        if challenge in userbook.challenges:
            userbook.challenges.remove(challenge)
            try: 
                db.session.add(userbook)
                db.session.commit()
            except: 
                db.session.rollback()
        else:
            return jsonify({'error': 'Book is not assigned to this challenge'}) 

    return jsonify({'success': 'Book removed'}) 

@app.route('/email', methods=["POST"])
def receive_email():
    """Parses an incoming email to notes@tb-read.com to append the email body to the notes field of the appropriate book"""

    envelope = json.loads(request.form['envelope'].replace("'", '"'))
    email = envelope['from']
    subject = request.form['subject']
    body = str(request.form['text'])

    ## find user based on from email
    user = db.session.execute(db.select(User).where(User.email == email)).scalar()
    ## find book based on email subject
    userbook = db.session.execute(db.select(User_Book).where(User_Book.title == subject).where(User_Book.user_id == user.user_id)).scalar()

    try: 
        stmt = (update(User_Book).where(User_Book.userbook_id == userbook.userbook_id).values(notes = User_Book.notes + " " + body))
        db.session.execute(stmt)
        db.session.commit()
    except: 
        db.session.rollback()

    return ''

#########################################################################################
# Calendar Routes

@app.route('/users/<user_id>/calendar')
def show_calendar(user_id):
    """Show user's embedded google calendar"""

    if not g.user: 
        flash ('Please log in', 'danger')
        return redirect('/')   

    user = db.session.execute(db.select(User).where(User.user_id == user_id)).scalar()
    calendar_id = user.calendar_id 

    return render_template('calendars/calendar.html', calendar_id=calendar_id)

@app.route('/users/<user_id>/oauth/create')
def connect_to_google_create_calendar(user_id):
    """Connect to google via oauth to create new calendar on user's google account"""

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=['https://www.googleapis.com/auth/calendar.app.created'])
    flow.redirect_uri = 'https://tb-read.com/createcalendar'
    authorization_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent")
    session['state'] = state

    return redirect(authorization_url)

@app.route('/createcalendar')
def create_calendar():
    """Create a new google calendar for the user"""

    if not g.user: 
        flash ('Please log in', 'danger')
        return redirect('/') 
    
    state = session.get('state')
    
    code = request.args.get('code')
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=['https://www.googleapis.com/auth/calendar.app.created'], state=state)
    flow.redirect_uri = url_for('create_calendar', _external=True)
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials

    ## create new calendar on user's google account
    service = build('calendar', 'v3', credentials=credentials)
    calendar = {
        'summary': 'TB Read Calendar'
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    user = db.session.execute(db.select(User).where(User.user_id == g.user.user_id)).scalar()
    ## update user's record with necessary data to display and interact with calendar in the future
    user.calendar_id = created_calendar['id']
    user.token = credentials.token
    user.refresh_token = credentials.refresh_token
    user.token_uri = credentials.token_uri
    user.client_id = credentials.client_id
    user.client_secret = credentials.client_secret
    user.scopes = credentials.scopes
    db.session.add(user)
    try: 
        db.session.commit()
    except: 
        db.session.rollback()
        flash('Something went wrong. Please try again', 'danger')
    service.close()

    return redirect(f'/users/{g.user.user_id}/calendar')


#########################################################################################
# Challenge Routes

@app.route('/challenges')
def show_challenges():
    """Show all available challenges in database"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    return render_template('challenges/challenges.html')

@app.route('/users/<user_id>/challenges')
def show_user_challenges(user_id):
    """Show all challenges the user has joined"""

    if not g.user: 
        flash('Please log in', 'danger')
        return redirect('/')
    
    return render_template('/challenges/user_challenges.html')

@app.route('/api/challenges')
def return_challenges():
    """Returns challenges to axios request from browser"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    list = db.session.query(Challenge).order_by(Challenge.name).all()
    serialized_challenges = [challenge.serialize_challenges() for challenge in list]
    return jsonify(serialized_challenges)

@app.route('/api/yourchallenges')
def return_your_challenges():
    """Returns challenges that a user has joined"""

    if not g.user: 
        flash('Please log in', 'danger')
        return redirect('/')
    
    user = db.session.execute(db.select(User).where(User.user_id == g.user.user_id)).scalar()
    list = user.challenges
    serialized_challenges = [challenge.serialize_challenges() for challenge in list]
    ##Add additional user_challenge field to serialized challenges
    for challenge in serialized_challenges:
        challenge_id = int(challenge['id'])
        user_challenge = db.session.execute(db.select(User_Challenge).where(User_Challenge.user_id == g.user.user_id).where(User_Challenge.challenge_id == challenge_id)).scalar()
        challenge['start_date'] = user_challenge.start_date
        challenge['end date'] = user_challenge.end_date
    return jsonify(serialized_challenges)

@app.route('/challenges/add', methods=['GET', 'POST'])
def add_challenge():
    """Add a challenge to the database"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    form = ChallengeForm()

    if form.validate_on_submit():
        name = form.name.data
        num_books = form.num_books.data
        description = form.description.data
        ## add the challenge to the challenge table in the database
        new_challenge = Challenge(creator_id = g.user.user_id, name=name, num_books=num_books, description=description)
        db.session.add(new_challenge)
        try: 
            db.session.commit()
        except:
            db.session.rollback()
            flash('Challenge not added. Please try again', 'danger')
        ## add the challenge to the user's profile
        user = db.session.execute(db.select(User).where(User.user_id == g.user.user_id)).scalar()
        user.challenges.append(new_challenge)
        db.session.add(user)
        try: 
            db.session.commit()
        except:
            db.session.rollback()
            flash('Something went wrong. Please try again.', 'danger')
        return redirect('/challenges')

    return render_template('challenges/new.html', form=form)

@app.route('/challenges/<challenge_id>', methods=['GET', 'POST'])
def edit_challenge(challenge_id):
    """Edit a challenge that the user created"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    challenge = db.session.execute(db.select(Challenge).where(Challenge.challenge_id == challenge_id)).scalar()
    if challenge.creator_id != g.user.user_id:
        flash('You do not have permissions to edit this challenge', 'danger')
        return redirect('/challenges')
    
    form = ChallengeForm(obj=challenge)

    if form.validate_on_submit():
        challenge.name = form.name.data
        challenge.num_books = form.num_books.data
        challenge.description = form.description.data
        db.session.add(challenge)
        try: 
            db.session.commit()
        except: 
            db.session.rollback()
            flash('Changes not saved. Please try again.', 'danger')
        flash('Changes saved', 'success')
    
    return render_template('challenges/edit_challenge.html', form=form)

@app.route('/challenges/join/<challenge_id>', methods=["POST"])
def join_challenge(challenge_id):
    """Sign user up to take part in a challenge"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    user = db.session.execute(db.select(User).where(User.user_id == g.user.user_id)).scalar()
    challenge = db.session.execute(db.select(Challenge).where(Challenge.challenge_id == challenge_id)).scalar()
    user.challenges.append(challenge)
    try: 
        db.session.add(user)
        db.session.commit()
        flash(f'You joined the {challenge.name}', 'success')
    ## deal with situation when user has already signed up for a challenge. 
    except IntegrityError: 
        db.session.rollback()
        flash('You are already signed up for this challenge.', 'danger')
    except: 
        db.session.rollback()
        flash('Something went wrong. Please try again.', 'danger')

    return redirect('/challenges')

@app.route('/challenges/leave/<challenge_id>', methods=["POST"])
def leave_challenge(challenge_id):
    """Unenroll user in a challenge"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    user = db.session.execute(db.select(User).where(User.user_id == g.user.user_id)).scalar()
    challenge = db.session.execute(db.select(Challenge).where(Challenge.challenge_id == challenge_id)).scalar()
    user.challenges.remove(challenge)
    db.session.add(user)
    try:
        db.session.commit()
        flash(f'You left the {challenge.name}', 'danger')

    except: 
        db.session.rollback()
        flash('Something went wrong. Please try again', 'danger')

    return redirect(f'/users/{g.user.user_id}/challenges')

@app.route('/users/<user_id>/challenges/<challenge_id>', methods=["GET", "POST"])
def edit_user_challenge(user_id, challenge_id):
    """Display an individual challenge that a user has enrolled in"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    user_challenge = db.session.execute(db.select(User_Challenge).where(User_Challenge.user_id == g.user.user_id).where(User_Challenge.challenge_id == challenge_id)).scalar()
    ## find completed books currently assigned to this challenge
    books = db.session.execute(db.select(User_Book).join(User_Book_Challenge, User_Book.userbook_id == User_Book_Challenge.userbook_id).where(User_Book_Challenge.complete == True).where(User_Book_Challenge.challenge_id == challenge_id)).scalars()
    form = UserChallengeForm(name = user_challenge.challenge.name, num_books = user_challenge.challenge.num_books, description = user_challenge.challenge.description, start_date = 
                             user_challenge.start_date, end_date = user_challenge.end_date)

    if form.validate_on_submit():
        user_challenge.start_date = form.start_date.data
        user_challenge.end_date = form.end_date.data
        db.session.add(user_challenge)
        try: 
            db.session.commit()
        except: 
            db.session.rollback()
            flash('Changes not saved. Please try again', 'danger')
        flash('Changes saved', 'success')

    return render_template('challenges/edit_user_challenge.html', form=form, books=books)


#########################################################################################
# Homepage and About

@app.route('/')
def homepage():
    """Show homepage: Anonymous users see a display of books; logged in users see their TBR list"""

    if g.user: 
        return redirect(f'/users/{g.user.user_id}/lists/tbr')

    else: 
        ## all three forms display as modals. 
        form = UserAddForm()
        form2 = LoginForm()
        form3 = EmailForm()
        ## Homepage for anonymous users shows most recent 12 books added to the database
        display_books = db.session.query(Book).where(Book.thumbnail != None).where(Book.thumbnail != '').order_by(Book.added.desc()).limit(12).all()
        return render_template('home-anon.html', display_books=display_books, form=form, form2=form2, form3=form3)

@app.route('/about')
def about():
    """Show about page"""
    ## all three forms display as modals
    form = UserAddForm()
    form2 = LoginForm()
    form3 = EmailForm()

    return render_template('about.html', form=form, form2=form2, form3=form3)