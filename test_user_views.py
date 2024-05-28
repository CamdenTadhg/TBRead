"""Auth Views tests"""

import os
from unittest import TestCase
from app import create_lists, add_book_to_tbr
from flask import g, session
from models import db, connect_db, User, Book, User_Book, List, Challenge, User_Challenge, User_Book_List

os.environ['DATABASE_URL'] = "postgresql:///tbread-test"

from app import app, CURR_USER_KEY
app.app_context().push()

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """create test client, add sample data"""

        User_Book_List.query.delete()
        List.query.delete()
        User_Challenge.query.delete()
        Challenge.query.delete()
        User_Book.query.delete()
        Book.query.delete()
        User.query.delete()


        self.testuser = User.signup(username="testuser",
                                    email='testuser@test.com', 
                                    password='testuser', 
                                    user_image=None)
        self.testuser2 = User.signup(username="testuser2", 
                                     email="testuser2@test.com", 
                                     password = 'testuser2',
                                     user_image = None)

        db.session.commit()

        self.b1 = Book(google_id = "lahsgoiawog", 
                 title = "test book", 
                 authors = "Mr. Testy Test",
                 publisher="PenguinRandomHouse", 
                 pub_date = 2024)
        
        db.session.add(self.b1)
        db.session.commit()

        self.ub1 = User_Book(title = "test book", 
                 user_id = self.testuser.user_id,
                 book_id = self.b1.book_id,
                 authors = "Mr. Testy Test",
                 publisher="PenguinRandomHouse", 
                 pub_date = 2024,
                 thumbnail = "https://books.google.com/books?id=wrOQLV6xB-wC&printsec=frontcover&dq=harry+potter&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwiZ44Obka-GAxVBMzQIHfH9DVUQ6wF6BAgJEAE",
                 page_count = 100)
        
        db.session.add(self.ub1)
        db.session.commit()

        self.tbrlist = List(list_type = "TBR",
                       user_id = self.testuser.user_id)
        
        db.session.add(self.tbrlist)
        db.session.commit()

        self.ubl1 = User_Book_List(list_id = self.tbrlist.list_id, 
                              userbook_id = self.ub1.userbook_id)
        
        db.session.add(self.ubl1)
        db.session.commit()

        self.client = app.test_client()

    
    def tearDown(self):
        """Clean up any fouled transactions and clear session and outbox"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                if change_session.get(CURR_USER_KEY):
                    change_session.pop(CURR_USER_KEY)
        db.session.rollback()

    def test_create_lists(self):
        """Does the create_lists function create three lists for a user?"""

        create_lists(self.testuser)
        tbrlist = db.session.execute(db.select(List).where(List.user_id == self.testuser.user_id).where(List.list_type == 'TBR')).scalar()
        dnflist = db.session.execute(db.select(List).where(List.user_id == self.testuser.user_id).where(List.user_id == self.testuser.user_id).where(List.list_type == 'DNF')).scalar()
        completelist = db.session.execute(db.select(List).where(List.user_id == self.testuser.user_id).where(List.list_type == 'Complete')).scalar()

        self.assertTrue(tbrlist)
        self.assertTrue(dnflist)
        self.assertTrue(completelist)

    def test_display_user_profile_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to access a user profile?"""

        with self.client as c:
            resp = c.get(f'/users/{self.testuser.user_id}')
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, '/')
    
    def test_display_user_profile_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access a user profile?"""

        with self.client as c:
            resp = c.get(f'/users/{self.testuser.user_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_display_user_profile_get(self):
        """Does the site display the user's profile correctly?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.get(f'/users/{self.testuser.user_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('User Profile', html)
            self.assertIn('testuser', html)
    
    def test_display_user_profile_edit(self):
        """Does the site update the user's profile correctly?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post(f'/users/{self.testuser.user_id}', data = {'username': 'testuser', 'email': 'testuser@test.com', 'user_image': '/static/images/image.png', 'reading_time_work_day': 4, 'reading_time_day_off': 0, 'reading_speed_adult': 0, 'reading_speed_YA': 0, 'reading_speed_children': 0, 'reading_speed_graphic': 0, 'posting_frequency': 15, 'prep_days': 4, 'content_account': 'testuser', 'email_reminders': True})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Changes saved', html)
            self.assertEqual(self.testuser.posting_frequency, 15)
    
    def test_display_user_profile_duplicate_email(self):
        """Does the site respond correctly when a user tries to update their email to an email already in the database?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post(f'/users/{self.testuser.user_id}', data = {'username': 'testuser', 'email': 'testuser2@test.com', 'user_image': '/static/images/image.png', 'reading_time_work_day': 4, 'reading_time_day_off': 0, 'reading_speed_adult': 0, 'reading_speed_YA': 0, 'reading_speed_children': 0, 'reading_speed_graphic': 0, 'posting_frequency': 15, 'prep_days': 4, 'content_account': 'testuser', 'email_reminders': True})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Email already in use', html)
            self.assertEqual(self.testuser.posting_frequency, 0)
    
    def test_display_user_profile_duplicate_username(self):
        """Does the site respond correctly when a user tries to update their username to a username already in the database"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post(f'/users/{self.testuser.user_id}', data = {'username': 'testuser2', 'email': 'testuser@test.com', 'user_image': '/static/images/image.png', 'reading_time_work_day': 4, 'reading_time_day_off': 0, 'reading_speed_adult': 0, 'reading_speed_YA': 0, 'reading_speed_children': 0, 'reading_speed_graphic': 0, 'posting_frequency': 15, 'prep_days': 4, 'content_account': 'testuser', 'email_reminders': True})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Username already in use', html)
            self.assertEqual(self.testuser.posting_frequency, 0)
    
    def test_display_tbr_list_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to access a tbr list?"""

        with self.client as c:
            resp = c.get(f'/users/{self.testuser.user_id}/lists/tbr')
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, '/')
    
    def test_display_tbr_list_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access a tbr list?"""

        with self.client as c:
            resp = c.get(f'/users/{self.testuser.user_id}/lists/tbr', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)

    def test_display_tbr_list(self):
        """Does the TBR list display correctly?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            resp = c.get(f'/users/{self.testuser.user_id}/lists/tbr')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('tbrlistTable', html)

    def test_return_tbr_list_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to access a tbr list api?"""

        with self.client as c:
            resp = c.get(f'/api/{self.testuser.user_id}/lists/tbr')
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, '/')
    
    def test_return_tbr_list_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access a tbr list api?"""

        with self.client as c:
            resp = c.get(f'/api/{self.testuser.user_id}/lists/tbr', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_return_tbr_list(self):
        """Does the site return the correct json when the tbr list is requested?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            resp = c.get(f'/api/{self.testuser.user_id}/lists/tbr')
            
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {"id": self.ub1.userbook_id, "title": "test book", "author": "Mr. Testy Test", "publisher": "PenguinRandomHouse", "pub_date": "2024" , "cover": "https://books.google.com/books?id=wrOQLV6xB-wC&printsec=frontcover&dq=harry+potter&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwiZ44Obka-GAxVBMzQIHfH9DVUQ6wF6BAgJEAE" , "pages": 100})