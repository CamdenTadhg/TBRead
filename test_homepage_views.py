"""Homepage Views tests"""

import os
from unittest import TestCase
from models import db, User, Book, User_Book

os.environ['DATABASE_URL'] = "postgresql:///tbread-test"

from app import app, CURR_USER_KEY
app.app_context().push()

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class HomepageTestCase(TestCase):
    """Test view for homepage"""

    def setUp(self):
        """create test client, add sample data"""

        User_Book.query.delete()
        User.query.delete()
        Book.query.delete()

        self.client = app.test_client()

        self.test_user = User.signup(username="testuser", 
                                     email="testuser@test.com", 
                                     password="testuser", 
                                     user_image=None)
        db.session.commit()

        self.test_book = Book(google_id="lasowndo", title="The Testy Test Book", authors = "Mr. Testy Test", publisher="PenguinRandomHouse")
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
            with c. session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.test_user.user_id
            user_id = self.test_user.user_id
            resp = c.get('/')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{user_id}/lists/tbr')