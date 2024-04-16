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
    Adult = 1
    YA = 2
    Childrens = 3

class EventCategory(enum.Enum):
    Order = 1
    Start = 2
    Finish = 3
    Post = 4

# class Friendship(db.Model):
#     """connection between friending user and friended user"""

#     __tablename__ = "friendships"

#     friending_user = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
#     friended_user = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)

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
    calendar_id = db.Column(db.Text, unique=True)
    posting_frequency = db.Column(db.Integer, default=0)
    posting_day = db.Column(db.Text)
    prep_days = db.Column(db.Integer, default=0)
    content_account = db.Column(db.Text)
    calendar = db.Column(db.Text)
    email_reminders = db.Column(db.Boolean)
    password_reset_token = db.Column(db.String)

    user_books = db.relationship("User_Book", backref="users", cascade="all, delete-orphan")
    lists = db.relationship("List", backref="users", cascade="all, delete-orphan")
    # friends = db.relationship("Friendship", backref="users", primaryjoin=(Friendship.friending_user == user_id), cascade="all, delete-orphan")
    # friends_of = db.relationship("Friendship", backref="users", primaryjoin=(Friendship.friended_user == user_id), cascade="all, delete-orphan")
    events = db.relationship("Event", backref="users", cascade="all, delete-orphan")
    challenges = db.relationship("Challenge", secondary="users_challenges", backref="users")
    user_challenges = db.relationship("User_Challenge", backref="users", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.user_id}: {self.username}, {self.email}>"
    
    def is_friend(self, other_user):
        """Has this user friended 'other user'"""

        found_user_list = [user for user in self.friends if user == other_user]
        return len(found_user_list) == 1
    
    def is_friended(self, other_user):
        """Has this user been friended by 'other user'"""

        found_user_list = [user for user in self.friends_of if user == other_user]
        return len(found_user_list) == 1
    
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
    publisher = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.Text)
    description = db.Column(db.Text)
    isbn = db.Column(db.BigInteger)
    page_count = db.Column(db.Integer)
    thumbnail = db.Column(db.Text)
    added = db.Column(db.DateTime, nullable=False, default=datetime.now())

    authors = db.relationship("Author", secondary="books_authors", backref="books")

    def __repr__(self):
        return f"<Book {self.google_id}: {self.title}, {self.pub_date}>"

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

    categories = db.relationship("Category", secondary="challenges_categories", backref="challenges")

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
    isbn = db.Column(db.Integer)
    page_count = db.Column(db.Integer)
    age_category = db.Column(db.Enum(AgeCategory))
    thumbnail = db.Column(db.Text)
    notes = db.Column(db.Text)
    script = db.Column(db.Text)

    categories = db.relationship("Category", secondary="books_categories", backref="users_books")

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


class Event(db.Model):
    """events associated with each book, reading start, reading end, etc."""

    __tablename__ = "events"

    event_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    userbook_id = db.Column(db.Integer, db.ForeignKey('users_books.userbook_id'))
    date = db.Column(db.Date, nullable=False)
    eventcategory = db.Column(db.Enum(EventCategory), nullable=False)

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