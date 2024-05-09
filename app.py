import os
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify, url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, insert
from models import db, connect_db, User, Book, List, User_Book, Challenge, User_Challenge, User_Book_Challenge, AgeCategory, Event
from forms import UserAddForm, LoginForm, UserProfileForm, EmailForm, UpdatePasswordForm, BookSearchForm, BookEditForm, ChallengeForm, UserChallengeForm, PostDaysForm
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message
from local_settings import MAIL_PASSWORD, SECRET_KEY
import requests
from io import StringIO
from html.parser import HTMLParser
import random
import pdb
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.cloud import storage
import json 
import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials
import string
from datetime import date
import re
from oauthlib.oauth2 import TokenExpiredError
from google.auth.transport.requests import Request

CURR_USER_KEY = "curr_user"
CLIENT_SECRETS_FILE = "client_secret_962453248563-u7b22jm1ekb7hellta4vcp05t24firg4.apps.googleusercontent.com.json"

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
    with app.app_context():
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
    print('*****************')
    print('user edit form displayed')

    if form.validate_on_submit():
        print('**********************')
        print('form validated')
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
    with app.app_context():
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
        description = strip_tags(data['volumeInfo'].get('description'))
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
        return new_book.book_id

class MLStripper(HTMLParser):
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
    with app.app_context():
        s = MLStripper()
        s.feed(html)
        return s.get_data()

def add_book_to_tbr(userbook_id):
    with app.app_context():
        if CURR_USER_KEY in session:
            g.user = db.session.query(User).get(session[CURR_USER_KEY])
        else: 
            g.user = None
        print('************')
        print(g.user.user_id)
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
        description = strip_tags(book.description)
        form=BookEditForm(title=book.title, authors=book.authors, publisher=book.publisher, pub_date=book.pub_date, description=description, isbn=book.isbn, page_count=book.page_count, thumbnail=book.thumbnail)
    else:
        new_book_id = addBookToDatabase(google_id)
        new_book = db.session.execute(db.select(Book).where(Book.book_id == new_book_id)).scalar()
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
        ## add the book to the books table in the database
        new_book = Book(google_id=google_id, title=title, authors=authors, publisher=publisher, pub_date=pub_date, description=description, isbn=isbn, page_count=page_count, thumbnail=thumbnail)
        db.session.add(new_book)
        db.session.commit()
        ## add the book to the users_books table in the database
        new_user_book = User_Book(user_id=g.user.user_id, book_id=new_book.book_id, title=title, authors=authors, publisher=publisher, pub_date=pub_date, description=description, isbn=isbn, page_count=page_count, age_category=age_category, thumbnail=thumbnail, notes=notes, script=script)
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
        userbook.age_category = AgeCategory(form.age_category.data)
        userbook.thumbnail = form.thumbnail.data
        userbook.notes = form.notes.data
        userbook.script = form.script.data
        db.session.add(userbook)
        db.session.commit()
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
            db.session.commit()
        else: 
            flash('You do not have permission to do that', 'danger')
    else:
        flash('Book not found. Please try again')
    
    return redirect(f'/users/{g.user.user_id}/lists/tbr')

@app.route('/users_books/<userbook_id>/transfer/<list_type>', methods=["POST"])
def transfer_between_lists(userbook_id, list_type):
    """Transfer a book between lists"""
    print('transfer request received')

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    print('list_type = ', list_type)
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
    if list_type == 'Complete':
        userbook_challenges = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == userbook.userbook_id)).scalars()
        print(userbook_challenges)
        for userbook_challenge in userbook_challenges:
            userbook_challenge.complete = True
            db.session.add(userbook_challenge)
            db.session.commit()
    else: 
        userbook_challenges = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == userbook.userbook_id)).scalars()
        for userbook_challenge in userbook_challenges:
            userbook_challenge.complete = False
            db.session.add(userbook_challenge)
            db.session.commit()
    
    return redirect(f'/users/{g.user.user_id}/lists/tbr')

@app.route('/api/users_books/<userbook_id>/assign', methods=['POST'])
def assign_book(userbook_id):
    """Assign a user copy of a book to a challenge"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == userbook_id)).scalar()
    data = request.json
    challenge_id = data.get('challenge_id')
    challenge = db.session.execute(db.select(Challenge).where(Challenge.challenge_id == challenge_id)).scalar()
    if userbook:
        userbook.challenges.append(challenge)
        try: 
            db.session.add(userbook)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Book already in challenge'})
        if userbook.lists[0].list_type == 'Complete':
            print('userbook complete')
            userbook_challenge = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == userbook.userbook_id).where(User_Book_Challenge.challenge_id == challenge.challenge_id)).scalar()
            userbook_challenge.complete = True
            db.session.add(userbook_challenge)
            db.session.commit()
    
    return jsonify({'success': 'Book added'})

@app.route('/api/users_books/<userbook_id>/remove', methods=['POST'])
def remove_book(userbook_id):
    """Remove a user copy of a book from a challenge"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')

    userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == userbook_id)).scalar()
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

    print('************************')
    print('email received')

    envelope = json.loads(request.form['envelope'].replace("'", '"'))
    email = envelope['from']
    print(email)
    subject = request.form['subject']
    body = str(request.form['text'])

    user = db.session.execute(db.select(User).where(User.email == email)).scalar()
    userbook = db.session.execute(db.select(User_Book).where(User_Book.title == subject).where(User_Book.user_id == user.user_id)).scalar()

    try: 
        stmt = (update(User_Book).where(User_Book.userbook_id == userbook.userbook_id).values(notes = User_Book.notes + " " + body))
        db.session.execute(stmt)
        db.session.commit()
        ('database updated')
    except: 
        db.session.rollback()

    return ''

#########################################################################################
# Calendar Routes

def get_credentials(user_id, redirect_uri):
    with app.app_context():
        print('LOGGED HERE: function get credentials starts')
        user = db.session.execute(db.select(User).where(User.user_id == user_id)).scalar()
        print('LOGGED HERE: user', user)

        if user and user.google_code: 
            print('LOGGED HERE: if statement starts')
            print('LOGGED HERE: user', user)
            print('LOGGED HERE: user.google_code', user.google_code)
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE,
                scopes=['https://www.googleapis.com/auth/calendar.app.created'])
            print('LOGGED HERE: flow', flow)
            flow.redirect_uri= redirect_uri
            print('LOGGED HERE: redirect_uri', redirect_uri)
            print('LOGGED HERE: flow.redirect_uri', flow.redirect_uri)

            try: 
                print('LOGGED HERE: try starts')
                print('LOGGED HERE: flow.fetch_token', flow.fetch_token(code=user.google_code))
                flow.fetch_token(code=user.google_code)
                print('LOGGED HERE')
                print('flow.credentials', flow.credentials)
                print('flow.credentials.expired', flow.credentials.expired)
                if flow.credentials.expired:
                    flow.credentials.refresh(Request())
                print('LOGGED HERE')
                print('flow.credentials', flow.credentials)
                return flow.credentials
            except TokenExpiredError or Exception: 
                print('LOGGED HERE: exception', Exception)
                print('LOGGED HERE: execept starts', TokenExpiredError)
                return None
        return None

@app.route('/users/<user_id>/calendar')
def show_calendar(user_id):
    """Show user's calendar"""

    if not g.user: 
        flash ('Please log in', 'danger')
        return redirect('/')   

    user = db.session.execute(db.select(User).where(User.user_id == user_id)).scalar()
    calendar_id = user.calendar_id 

    return render_template('calendars/calendar.html', calendar_id=calendar_id)

@app.route('/users/<user_id>/oauth')
def connect_to_google_create_calendar(user_id):

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
    if not state:
        flash('OAuth state mismatch', 'danger')
        return redirect('/')
    
    
    code = request.args.get('code')
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=['https://www.googleapis.com/auth/calendar.app.created'], state=state)
    flow.redirect_uri = url_for('create_calendar', _external=True)
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id, 
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    service = build('calendar', 'v3', credentials=credentials)
    calendar = {
        'summary': 'TB Read Calendar'
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    user = db.session.execute(db.select(User).where(User.user_id == g.user.user_id)).scalar()
    user.calendar_id = created_calendar['id']
    user.google_code = code
    db.session.add(user)
    db.session.commit()
    print('****************************')
    print(user.calendar_id)
    service.close()

    return redirect(f'/users/{g.user.user_id}/calendar')

@app.route('/posting', methods=['GET', 'POST'])
def schedule_posting_days():
    """Schedule a user's posting schedule on the google calendar"""
    print('LOGGED HERE: Function Schedule Posting Days starts')

    if not g.user: 
        flash ('Please log in', 'danger')
        return redirect('/') 
    
    form = PostDaysForm()

    if form.validate_on_submit():
        print('LOGGED HERE: if validate on submit starts')
        redirect_uri = url_for('schedule_posting_days', external=True)
        credentials = get_credentials(g.user.user_id, redirect_uri)
        if credentials is None:
            print('LOGGED HERE: if credentials is none starts')
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=['https://www.googleapis.com/auth/calendar.app.created'])
            flow.redirect_uri = redirect_uri
            authorization_url, _ = flow.authorization_url(
                access_type="offline", include_granted_scopes="true", prompt="consent"
            )
            return redirect(authorization_url)
    
        last_post_date = form.last_post_date.data
        posting_frequency = form.posting_frequency.data

        service = build('calendar', 'v3', credentials=credentials)
        ## Check if a posting date event currently exists
        existing_posting_event = db.session.execute(db.select(Event).where(Event.user_id == g.user.user_id).where(Event.eventcategory == 'Posting')).scalar()
        ## Delete remaining recurring posting events
        if existing_posting_event.google_event_id: 
            post_event = service.events().get(calendarId=g.user.calendar_id, eventId = existing_posting_event.google_event_id).execute()
            today = date.today()
            post_event['recurrance'] = [f'RRULE: FREQ=DAILY; COUNT=g.user.posting_frequency; UNTIL={today}']
            service.events().update(calendarId=g.user.calendar_id, EventId = existing_posting_event.google_event_id, body=post_event).execute()
        ## Add new posting date event
        event = {
            'summary': 'Posting Day',
            'start.date': last_post_date,
            'end.date': last_post_date,
            'recurrence': [f'RRULE: FREQ=DAILY; COUNT={posting_frequency}']
        }
        posting_day = service.events().insert(calendarId = g.user.calendar_id, body=event).execute()
        print('**************************')
        print(posting_day)
        service.close()
        ## Update user profile
        if g.user.posting_frequency != posting_frequency:
            user = db.session.execute(db.select(User).where(User.user_id == g.user.user_id)).scalar()
            user.posting_frequency = posting_frequency
            db.session.add(user)
            db.session.commit()

        return redirect(f'/users/{g.user.user_id}/calendar')
    
    return render_template('/calendars/posting.html', form=form)


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
        db.session.commit()
        ## add the challenge to the user's profile
        user = db.session.execute(db.select(User).where(User.user_id == g.user.user_id)).scalar()
        user.challenges.append(new_challenge)
        db.session.add(user)
        db.session.commit()
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
        db.session.commit()
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
    except: 
        db.session.rollback()
        flash('You are already signed up for this challenge.', 'danger')

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
    db.session.commit()

    return redirect(f'/users/{g.user.user_id}/challenges')

@app.route('/users/<user_id>/challenges/<challenge_id>', methods=["GET", "POST"])
def edit_user_challenge(user_id, challenge_id):
    """Display an individual challenge with a user has enrolled in"""

    if not g.user:
        flash('Please log in', 'danger')
        return redirect('/')
    
    user_challenge = db.session.execute(db.select(User_Challenge).where(User_Challenge.user_id == g.user.user_id).where(User_Challenge.challenge_id == challenge_id)).scalar()
    books = db.session.execute(db.select(User_Book).join(User_Book_Challenge, User_Book.userbook_id == User_Book_Challenge.userbook_id).where(User_Book_Challenge.complete == True).where(User_Book_Challenge.challenge_id == challenge_id)).scalars()
    print('list of books')
    print(books)
    form = UserChallengeForm(name = user_challenge.challenge.name, num_books = user_challenge.challenge.num_books, description = user_challenge.challenge.description, start_date = 
                             user_challenge.start_date, end_date = user_challenge.end_date)

    if form.validate_on_submit():
        user_challenge.start_date = form.start_date.data
        user_challenge.end_date = form.end_date.data
        db.session.add(user_challenge)
        db.session.commit()
        flash('Changes saved', 'success')

    return render_template('challenges/edit_user_challenge.html', form=form, books=books)


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