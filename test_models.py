"Tests user & book model methods"

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Book, Challenge, User_Book, List, User_Challenge

os.environ['DATABASE_URL'] = "postgresql:///tbread-test"

from app import app
app.app_context().push()

db.create_all()

class UserModelTestCase(TestCase):
    """Test methods on user model"""

    def setUp(self):
        """Clear out old data, create test client, add sample data"""

        User.query.delete()

        u1 = User(
            email="janedoe@test.com", 
            username="janedoe", 
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="johndoe@test.com", 
            username="johndoe", 
            password="HASHED_PASSWORD"
        )

        u3 = User(
            email="camdentadhg@test.com",
            username="camdentadhg", 
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u1, u2, u3])
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transactions"""

        db.session.rollback()

    def test_repr(self):
        """Does repr return the correct format?"""

        u = User(
            email="test@test.com",
            username="testuser", 
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit

        self.assertEqual(f'<User {u.user_id}: testuser, test@test.com>', str(u))
    
    def test_signup_correct(self):
        """Does signup correctly create a user when appropriate data is given?"""

        u = User.signup(username="testing", email="test@test.com", password="testing", user_image=None)
        db.session.commit()

        self.assertIsInstance(u, User)
        self.assertNotEqual(7, len(u.password))
        self.assertEqual(u.username, "testing")

    def test_signup_duplicate_username(self):
        """Does signup fail to return a user when a duplicate username is entered?"""

        with self.assertRaises(Exception) as context:
            u = User.signup(username="janedoe", email="janedoe2@test.com", password="testing", user_image=None)
            db.session.commit()

            self.assertTrue('IntegrityError' in str(context.exception))

    def test_signup_duplicate_email(self):
        """Does signup fail to return a user when a duplicate email is entered?"""

        with self.assertRaises(Exception) as context:
            u = User.signup(username="janedoe2", email="janedoe@test.com", password="testing", user_image=None)
            db.session.commit()

            self.assertTrue('IntegrityError' in str(context.exception))
    
    def test_signup_blank_username(self):
        """Does signup fail to return a user when no username is entered?"""

        with self.assertRaises(Exception) as context:
            u = User.signup(username=None, email="camdent@test.com", password="testing", user_image=None)
            db.session.commit()

            self.assertTrue('IntegrityError' in str(context.exception))
    
    def test_signup_blank_password(self):
        """Does signup fail to return a user when no password is entered?"""

        with self.assertRaises(Exception) as context:
            u = User.signup(username="testuser", email="camdent@test.com", password=None, user_image=None)
            db.session.commit()

            self.assertTrue('IntegrityError' in str(context.exception))

    def test_signup_blank_email(self):
        """Does signup fail to return a user when no email is entered?"""

        with self.assertRaises(Exception) as context:
            u = User.signup(username="testuser", email=None, password="testing", user_image=None)
            db.session.commit()

            self.assertTrue('IntegrityError' in str(context.exception))   

    def test_authenticate_true(self):
        """Does authenticate return a user when a correct username and password are entered?"""

        u = User.signup(username="camdentadhg2", email="camdentt@gmail.com", password="testing", user_image=None)
        db.session.commit()

        test_user = User.authenticate(username="camdentadhg2", password="testing")

        self.assertIsInstance(test_user, User)
        self.assertEqual(test_user.username, 'camdentadhg2')

    def test_authenticate_bad_username(self):
        """Does authenticate return False when an incorrect username is entered?"""

        u = User.signup(username="camdentadhg2", email="camdentt@gmail.com", password="testing", user_image=None)
        db.session.commit()

        test_user = User.authenticate(username="camdentadhg3", password="testing")

        self.assertNotIsInstance(test_user, User)
        self.assertFalse(test_user)

    def test_authenticate_bad_password(self):
        """Does authenticate return False when an incorrect password is entered?"""

        u = User.signup(username="camdentadhg2", email="camdentt@gmail.com", password="testing", user_image=None)
        db.session.commit()

        test_user = User.authenticate(username="camdentadhg2", password="password")

        self.assertNotIsInstance(test_user, User)
        self.assertFalse(test_user)
    
    def test_get_password_reset_token(self):
        user = db.session.execute(db.select(User).where(User.username=="janedoe")).scalar()
        prt = user.get_password_reset_token()

        self.assertEqual(len(prt), 32)

    def test_update_password(self):
        user = db.session.execute(db.select(User).where(User.username=="janedoe")).scalar()
        oldpassword = user.password
        stmt = user.update_password('passwordpassword!', 'janedoe@test.com')
        db.session.execute(stmt)
        db.session.commit()
        user2 = db.session.execute(db.select(User).where(User.username == "janedoe")).scalar()
        newpassword = user2.password

        self.assertNotEqual(oldpassword, newpassword)

class BookModelTestCase(TestCase):
    """Test methods for book model"""

    def setUp(self):
        """Create test client, clear out data"""

        Book.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transactions"""

        db.session.rollback()

    def test_repr(self):
        """Does repr return the correct format?"""

        b = Book(google_id = "lahsgoiawog", 
                 title = "test book", 
                 publisher="PenguinRandomHouse", 
                 pub_date = 2024)
        
        db.session.add(b)
        db.session.commit()

        self.assertEqual(f'<Book lahsgoiawog: test book, 2024>', str(b))

class ChallengeModelTestCase(TestCase):
    """Test methods for challenge model"""

    def setUp(self):
        "create test client, add data"

        Challenge.query.delete()
        User.query.delete()

        u1 = User(
            email="janedoe@test.com", 
            username="janedoe", 
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()

        self.client = app.test_client()
    
    def tearDown(self):
        """Clean up any fouled transactions"""

        db.session.rollback()
    
    def test_serialize_challenge(self):
        """Does serialize challenge return the right format?"""

        user_id = db.session.execute(db.select(User.user_id).where(User.username == "janedoe")).scalar()

        c1 = Challenge(
            creator_id=user_id, 
            name="Test Challenge", 
            num_books=12, 
            description="testing"
        )

        db.session.add(c1)
        db.session.commit()

        self.assertEqual(c1.serialize_challenges(), {"id": c1.challenge_id, "creator_id": user_id, "name": "Test Challenge", "num_books": 12, "description": "testing"} )

class User_BookModelTestCase(TestCase):
    """Test methods for user_book model"""

    def setUp(self):
        "create test client, add data"

        User_Book.query.delete()
        Book.query.delete()
        User.query.delete()


        u1 = User(
            email="janedoe@test.com", 
            username="janedoe", 
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()

        b = Book(google_id = "lahsgoiawog", 
                 title = "test book", 
                 publisher="PenguinRandomHouse", 
                 pub_date = 2024)
        
        db.session.add(b)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transactions"""

        db.session.rollback()
    
    def test_repr(self):
        """Does repr return the correct format?"""

        user_id = db.session.execute(db.select(User.user_id).where(User.username == "janedoe")).scalar()
        book_id = db.session.execute(db.select(Book.book_id).where(Book.google_id == "lahsgoiawog")).scalar()

        ub = User_Book(title = "test book", 
                 user_id = user_id,
                 book_id = book_id,
                 publisher="PenguinRandomHouse", 
                 pub_date = 2024)
        
        db.session.add(ub)
        db.session.commit()

        self.assertEqual(f'<User Book {ub.userbook_id}: test book, 2024>', str(ub))
    
    def test_serialize_user_book(self):
        """Does serialize user_book return the right format?"""

        user_id = db.session.execute(db.select(User.user_id).where(User.username == "janedoe")).scalar()
        book_id = db.session.execute(db.select(Book.book_id).where(Book.google_id == "lahsgoiawog")).scalar()

        ub = User_Book(title = "test book", 
                 user_id = user_id,
                 book_id = book_id,
                 authors = "Mr. Testy Test",
                 publisher="PenguinRandomHouse", 
                 pub_date = 2024,
                 cover = "https://books.google.com/books?id=wrOQLV6xB-wC&printsec=frontcover&dq=harry+potter&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwiZ44Obka-GAxVBMzQIHfH9DVUQ6wF6BAgJEAE",
                 pages = 100)
        
        db.session.add(ub)
        db.session.commit()

        self.assertEqual(ub.serialize_user_book(), {"id": ub.userbook_id, "title": "test book", "author": "Mr. Testy Test", "publisher": "PenguinRandomHouse", "pub_date": 2024, "cover":"https://books.google.com/books?id=wrOQLV6xB-wC&printsec=frontcover&dq=harry+potter&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwiZ44Obka-GAxVBMzQIHfH9DVUQ6wF6BAgJEAE", "pages": 100} )

class ListModelTestCase(TestCase):
    """Test methods for list model"""

    def setUp(self):
        "create test client, add data"
    
        User.query.delete()


        u1 = User(
            email="janedoe@test.com", 
            username="janedoe", 
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transactions"""

        db.session.rollback()

    def test_repr(self):
        """Does repr return the correct format?"""

        user_id = db.session.execute(db.select(User.user_id).where(User.username == "janedoe")).scalar()

        l1 = List(list_type = "TBR", 
                  user_id = user_id)
        
        db.session.add(l1)
        db.session.commit()

        self.assertEqual(f'<List {l1.list_id} TBR>', str(l1))

class UserChallengeTestCase(TestCase):
    """Test methods for user_challenge model"""

    def setUp(self):
        "create test client, add data"
    
        Challenge.query.delete()
        User.query.delete()

        u1 = User(
            email="janedoe@test.com", 
            username="janedoe", 
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()


        c1 = Challenge(
            creator_id=u1.user_id, 
            name="Test Challenge", 
            num_books=12, 
            description="testing"
        )

        db.session.add(c1)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transactions"""

        db.session.rollback()

    def test_serialize_user_challenge(self):
        """Does serialize user_challenge return the correct format?"""

        user_id = db.session.execute(db.select(User.user_id).where(User.username == "janedoe")).scalar()
        challenge_id = db.session.execute(db.select(Challenge.challenge_id).where(Challenge.name == "Test Challenge")).scalar()

        uc = User_Challenge(user_id = user_id,
                            challenge_id = challenge_id, 
                            start_date = "2024-01-01",
                            end_date = "2025-01-01")
        
        db.session.add(uc)
        db.session.commit()

        self.assertEqual(uc.serialize_user_challenge(), {"start_date": "2024-01-01", "end_date": "2025-01-01"})