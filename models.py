"""SQL Alchemy models for TBRead"""

import enum
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from datetime import datetime
import secrets
from sqlalchemy import update


bcrypt = Bcrypt()
db = SQLAlchemy()

class AgeCategory(enum.Enum):
    Adult = 'Adult'
    YA = 'YA'
    Childrens = 'Childrens'
    Graphic = 'Graphic'
    NA = 'N/A'

class EventCategory(enum.Enum):
    Order = 'Order'
    Start = 'Start'
    Finish = 'Finish'
    Post = 'Post'
    Posting = 'Posting'
    Work = 'Work'

class User(db.Model): 
    """ User in the TBRead system"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    user_image = db.Column(db.Text)
    reading_time_work_day = db.Column(db.Float(precision=2), default=0)
    reading_time_day_off = db.Column(db.Float(precision=2), default=0)
    reading_speed_adult = db.Column(db.Integer, default=0)
    reading_speed_YA = db.Column(db.Integer, default=0)
    reading_speed_children = db.Column(db.Integer, default=0)
    reading_speed_graphic = db.Column(db.Integer, default=0)
    calendar_id = db.Column(db.Text, unique=True)
    posting_frequency = db.Column(db.Integer, default=0)
    prep_days = db.Column(db.Integer, default=0)
    content_account = db.Column(db.Text)
    email_reminders = db.Column(db.Boolean)
    password_reset_token = db.Column(db.String)

    user_books = db.relationship("User_Book", backref="users", cascade="all, delete-orphan")
    lists = db.relationship("List", backref="users", cascade="all, delete-orphan")
    events = db.relationship("Event", backref="users", cascade="all, delete-orphan")
    challenges = db.relationship("Challenge", secondary="users_challenges", backref="users")

    def __repr__(self):
        return f"<User {self.user_id}: {self.username}, {self.email}>"
    
    @classmethod
    def signup(cls, username, password, email, user_image):
        """Sign up user. Hashes password and adds user to system"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username, 
            password=hashed_pwd, 
            email=email, 
            user_image=user_image
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Finds user with given username and password. Returns false if user is not found"""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
            
        return False
    
    def get_password_reset_token(self):
        """creates a pssword reset token"""
        return secrets.token_hex(16)
    
    def update_password(self, pwd, email):
        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode('utf8')
        return update(User).where(User.email == email).values(password=hashed_utf8)


class Book(db.Model):
    """Book in database, imported from Google Books or entered manually"""

    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.Text, unique=True)
    title = db.Column(db.Text, nullable=False)
    authors = db.Column(db.Text, nullable=False)
    publisher = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.Text)
    description = db.Column(db.Text)
    isbn = db.Column(db.BigInteger)
    page_count = db.Column(db.Integer)
    thumbnail = db.Column(db.Text)
    added = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"<Book {self.google_id}: {self.title}, {self.pub_date}>"

class Challenge(db.Model):
    """Challenge in database"""

    __tablename__ = "challenges"

    challenge_id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    name = db.Column(db.Text, nullable=False, unique=True)
    num_books = db.Column(db.Integer)
    description = db.Column(db.Text)

    def serialize_challenges(self):
        return {
            "id": self.challenge_id,
            "creator_id": self.creator_id,
            "name": self.name,
            "num_books": self.num_books,
            "description": self.description
        }

class User_Book(db.Model):
    """copy of book data specific to a certain user"""

    __tablename__ = "users_books"

    userbook_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), primary_key=True)
    title = db.Column(db.Text)
    authors = db.Column(db.Text)
    publisher = db.Column(db.Text)
    pub_date = db.Column(db.Text)
    description = db.Column(db.Text)
    isbn = db.Column(db.BigInteger)
    page_count = db.Column(db.Integer)
    age_category = db.Column(db.Enum(AgeCategory), default='NA')
    thumbnail = db.Column(db.Text)
    notes = db.Column(db.Text)
    script = db.Column(db.Text)

    challenges = db.relationship("Challenge", secondary="users_books_challenges", backref="users_books")
    book = db.relationship("Book", backref="users_books")

    def __repr__(self):
        return f"<User_Book {self.userbook_id}: {self.title}, {self.pub_date}>"

    def serialize_user_book(self):
        return {
            "id": self.userbook_id,
            "title": self.title,
            "author": self.authors, 
            "publisher": self.publisher, 
            "pub_date": self.pub_date,
            "cover": self.thumbnail,
            "id": self.userbook_id,
            "pages": self.page_count
        }

class List(db.Model):
    """three lists belonging to each user - TBR, DNF, and completed"""

    __tablename__ = "lists"

    list_id = db.Column(db.Integer, primary_key=True)
    list_type = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    user_books = db.relationship("User_Book", secondary="users_books_lists", backref="lists")

    def __repr__(self):
        return f"<List {self.list_id} {self.list_type}>"

class User_Book_List(db.Model):
    """connection between user copy of books and lists"""

    __tablename__ = "users_books_lists"

    list_id = db.Column(db.Integer, db.ForeignKey('lists.list_id'), primary_key=True)
    userbook_id = db.Column(db.Integer, db.ForeignKey('users_books.userbook_id'), primary_key=True)


class Event(db.Model):
    """events associated with each book, reading start, reading end, etc."""

    __tablename__ = "events"

    event_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    userbook_id = db.Column(db.Integer, db.ForeignKey('users_books.userbook_id'))
    date = db.Column(db.Date)
    eventcategory = db.Column(db.Enum(EventCategory), nullable=False)
    google_event_id = db.Column(db.Text)

class User_Challenge(db.Model):
    """connection between users and challenges"""

    __tablename__ = "users_challenges"

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.challenge_id'), primary_key=True)
    start_date = db.Column(db.Text)
    end_date = db.Column(db.Text)

    challenge = db.relationship('Challenge', backref="user_challenges", viewonly=True)

    def serialize_user_challenges(self):
        return {
            "start_date": self.start_date,
            "end_date": self.end_date
        }

class User_Book_Challenge(db.Model):
    """connection between user_books and challenges"""

    __tablename__ = "users_books_challenges"

    userbook_id = db.Column(db.Integer, db.ForeignKey('users_books.userbook_id'), primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.challenge_id'), primary_key=True)
    complete = db.Column(db.Boolean)


def connect_db(app):
    """Connect this database to provided Flask app"""
    with app.app_context():
        db.app = app
        db.init_app(app)
        db.create_all()