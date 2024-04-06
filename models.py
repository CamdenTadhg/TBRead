"""SQL Alchemy models for TBRead"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model): 
    """ User in the TBRead system"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    user_image = db.Column(db.Text, default = '/static/images/default-pic.png')
    reading_time_work_day = db.Column(db.Float(precision=2))
    reading_time_day_off = db.Column(db.Float(precision=2))
    reading_speed_adult = db.Column(db.Integer)
    reading_speed_YA = db.Column(db.Integer)
    reading_speed_children = db.Column(db.Integer)
    calendar_id = db.Column(db.Text, unique=True)
    posting_frequency = db.Column(db.Text)
    posting_day = db.Column(db.Text)
    prep_days = db.Column(db.Integer)
    content_account = db.Column(db.Text)
    calendar = db.Column(db.Array)

class Book(db.Model):
    """Book in database, imported from Google Books or entered manually"""

    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.Text, unique=True)
    title = db.Column(db.Text, nullable=False)
    publisher = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.Text)
    description = db.Column(db.Text)
    isbn = db.Column(db.Integer(13))
    page_count = db.Column(db.Integer)
    thumbnail = db.Column(db.Text)

class Author(db.Model):
    """Author in database"""

    __tablename__ = "authors"

    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

class Challenge(db.Model):
    """Challenge in database"""

    __tablename__ = "challenges"

    challenge_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    num_books = db.Column(db.Integer)
    description = db.Column(db.Text)

class Category(db.Model):
    """Category of challenge requirement"""

    __tablename__ = "categories"

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.Text, nullable=False)
    category_desc = db.Column(db.Text)

class Book_Author(db.Model):
    """Connection of book and author"""

    __tablename__ = 'books_authors'

    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'), primary_key=True)

class User_Book(db.Model):
    """copy of book data specific to a certain user"""

    __tablename__ = "users_books"

    userbook_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    title = db.Column(db.Text)
    publisher = db.Column(db.Text)
    pub_date = db.Column(db.Text)
    description = db.Column(db.Text)
    isbn = db.Column(db.Integer(13))
    page_count = db.Column(db.Integer)
    age_category = db.Column(db.Text)
    thumbnail = db.Column(db.Text)
    notes = db.Column(db.Text)
    script = db.Column(db.Text)

class List(db.Model):
    """three lists belonging to each user - TBR, DNF, and completed"""

    __tablename__ = "lists"

    list_id = db.Column(db.Integer, primary_key=True)
    list_type = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

class User_Book_List(db.Model):
    """connection between user copy of books and lists"""

    __tablename__ = "users_books_lists"

    list_id = db.Column(db.Integer, primary_key=True)
    userbook_id = db.Column(db.Integer, primary_key=True)

class Friendship(db.Model):
    """connection between friending user and friended user"""

    __tablename__ = "friendships"

    friending_user = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    friended_user = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)

class Event(db.Model):
    """events associated with each book, reading start, reading end, etc."""

    __tablename__ = "events"

    event_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    userbook_id = db.Column(db.Integer, db.ForeignKey('users_books.userbook_id'))
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.Text, nullable=False)

class User_Challenge(db.Model):
    """connection between users and challenges"""

    __tablename__ = "users_challenges"

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.challenge_id'), primary_key=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

class Challenge_Category(db.Model):
    """connection between challenges and challenge categories"""

    __tablename__ = "challenges_categories"

    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.challenge_id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), primary_key=True)

class Book_Categories(db.Model):
    """connection between user copy of a book and a challenge category"""

    __tablename__ = "books_categories"

    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), primary_key=True)
    userbook_id = db.Column(db.Integer, db.ForeignKey('users_books.userbook_id'), primary_key=True)

def connect_db(app):
    """Connect this database to provided Flask app"""

    db.app = app
    db.init_app(app)