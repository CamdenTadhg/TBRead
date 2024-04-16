"""User Views tests (plus homepage)"""

import os
from unittest import TestCase
from app import do_login, do_logout, add_user_to_g
from flask import g, session
from models import db, connect_db, User, Book

os.environ['DATABASE_URL'] = "postgresql:///tbread-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """create test client, add sample data"""

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

class HomepageTestCase(TestCase):
    """Test view for homepage"""

    def setUp(self):
        """create test client, add sample data"""

        User.query.delete()
        Book.query.delete()

        self.client = app.test_client()

        self.test_user = User.signup(username="testuser", 
                                     email="testuser@test.com", 
                                     password="testuser", 
                                     user_image=None)
        db.session.commit()

        self.test_book = Book(google_id="lasowndo", title="The Testy Test Book", publisher="PenguinRandomHouse")
        db.session.add(self.test_book)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transactions"""
        db.session.rollback()
    
    def test_homepage_loggedout(self):
        """Does anonymous homepage display correctly?"""
        with self.client as c:
            resp = c.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign up', html)
            self.assertIn('The Testy Test Book', html)
        
    def test_homepage_loggedin(self):
        """Does the logged in homepage redirect correctly?"""
        with self.client as c:
            with c. session_transaction() as session:
                session[CURR_USER_KEY] = self.test_user.user_id
            user_id = self.test_user.user_id
            resp = c.get('/')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{user_id}/lists/tbr')