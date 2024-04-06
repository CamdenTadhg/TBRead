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

def connect_db(app):
    """Connect this database to provided Flask app"""

    db.app = app
    db.init_app(app)