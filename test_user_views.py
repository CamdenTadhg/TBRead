"""User Views tests"""

import os
from unittest import TestCase
from app import do_login, do_logout, add_user_to_g
from flask import g, session
from models import db, connect_db, User, Book, User_Book

os.environ['DATABASE_URL'] = "postgresql:///tbread-test"

from app import app, CURR_USER_KEY
app.app_context().push()

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """create test client, add sample data"""

        User_Book.query.delete()
        User.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email='testuser@test.com', 
                                    password='testuser', 
                                    user_image=None)
        self.testuser2 = User.signup(username="testuser2", 
                                     email="testuser2@test.com", 
                                     password='testuser2', 
                                     user_image=None)
        db.session.commit()
    
    def tearDown(self):
        """Clean up any fouled transactions"""

        db.session.rollback()
    
    def test_add_user_to_g(self):
        """Does add_user_to_g function work?"""
        with app.test_request_context():
            with self.client as c:
                with c.session_transaction() as session:
                    session[CURR_USER_KEY] = self.testuser.user_id
                add_user_to_g()

                self.assertEqual(g.user, self.testuser)
    
    def test_do_login(self):
        """Does do_login function work?"""
        with app.test_request_context():
            with self.client as c:
                do_login(self.testuser)

                self.assertEqual(session[CURR_USER_KEY], self.testuser.user_id)
    
    def test_do_logout(self):
        """Does do_logout function work?"""
        with app.test_request_context():
            with self.client as c:
                with c.session_transaction() as session:
                    session[CURR_USER_KEY] = self.testuser.user_id
                do_logout()

                self.assertFalse(session.get(CURR_USER_KEY))
    
    def test_signup_already_logged_in(self):
        """Does site respond appropriately if user is already logged in?"""

        with self.client as c: 
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post('/signup')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')

    def test_signup_already_logged_in_redirect(self):
        """Does site redirect appropriately if user is already logged in?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post('/signup', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are already logged in', html)
    
    def test_signup_correct(self):
        """Does signup route sign a user up for the site?"""

        with self.client as c:
            resp = c.post('/signup', json={'username': 'testuser3', 'password': 'password', 'email': 'testuser3@test.com', 'user_image': None})
            user_id = db.session.execute(db.select(User.user_id).where(User.username =='testuser3')).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{user_id}/lists/tbr')

    def test_signup_correct_redirect(self):
        """Does signup route sign a user up for the site?"""

        with self.client as c:
            resp = c.post('/signup', json={'username': 'testuser3', 'password': 'password', 'email': 'testuser3@test.com', 'user_image': None}, follow_redirects=True)
            user_id = db.session.execute(db.select(User.user_id).where(User.username =='testuser3')).scalar()
            user_image = db.session.execute(db.select(User.user_image).where(User.username == 'testuser3')).scalar()
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add Books', html)
            self.assertEqual(user_id, session[CURR_USER_KEY])
            self.assertEqual(user_image, 'static/images/image.png')
    
    def test_signup_duplicate_email(self):
        """Does a duplicate email return the correct json error response?"""

        with self.client as c:
            resp = c.post('/signup', json={'username': 'testuser3', 'password': 'password', 'email': 'testuser2@test.com', 'user_image': None})
            
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {'error': 'Email already taken'})
    
    def test_signup_duplicate_username(self):
        """Does a duplicate username return the correct json error response?"""

        with self.client as c:
            resp = c.post('/signup', json={'username': 'testuser', 'password': 'password', 'email': 'testuser3@test.com', 'user_image': None})

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {'error': 'Username already taken'})
    

