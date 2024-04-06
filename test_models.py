"Tests user & book model methods"

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Book, Friendship

os.environ['DATABASE_URL'] = "postgresql:///tbread-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test methods on user model"""

    def setUp(self):
        """Clear out old data, create test client, add sample data"""

        User.query.delete()
        Friendship.query.delete()

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

        db.session.add_all([u1, u2])
        db.session.commit()

        u1.friends.append(u2)
        db.session.add(u1)
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
    
    def test_is_friend_true(self):
        """Does is_friend correctly identify when the relationship exists?"""

        janedoe = db.session.query(User).filter(User.username == "janedoe").first()
        johndoe = db.session.query(User).filter(User.username == "johndoe").first()

        self.assertTrue(janedoe.is_friend(johndoe))

    def test_is_friend_false(self):
        """Does is_friend correctly identify when the relationship does not exist?"""

        janedoe = db.session.query(User).filter(User.username == "janedoe").first()
        johndoe = db.session.query(User).filter(User.username == "johndoe").first()

        self.assertFalse(johndoe.is_friend(janedoe))

    def test_is_friended_true(self):
        """Does is_friended correctly identify when the relationship exists?"""

        janedoe = db.session.query(User).filter(User.username == "janedoe").first()
        johndoe = db.session.query(User).filter(User.username == "johndoe").first()

        self.assertTrue(johndoe.is_friended(janedoe))
    
    def test_is_friended_false(self):
        """Does is_friended correctly identify when the relationship does not exist?"""

        janedoe = db.session.query(User).filter(User.username == "janedoe").first()
        johndoe = db.session.query(User).filter(User.username == "johndoe").first()

        self.assertFalse(janedoe.is_friend(johndoe))
    
    def test_signup_correct(self):
        """Does signup correctly create a user when appropriate data is given?"""

        u = User.signup(username="testing", email="test@test.com", password="testing", user_image=None)
        db.session.commit()

        self.assertIsInstance(u, User)
        self.assertNotEqual(7, len(u.password))
        self.assertEqual(u.username, "testing")
        self.assertEqual(u.user_image, "/static/images/default-pic.png")

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