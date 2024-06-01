"""Challenge Views tests"""

import os
from unittest import TestCase
from flask import g, session
from models import db, connect_db, User, Book, User_Book, List, Challenge, User_Challenge, User_Book_List, User_Book_Challenge
from sqlalchemy import update, insert

os.environ['DATABASE_URL'] = "postgresql:///tbread-test"

from app import app, CURR_USER_KEY
app.app_context().push()

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class ChallengeViewTestCase(TestCase):
    """Test views for books"""

    def setUp(self):
        """create test client, add sample data"""

        User_Book_List.query.delete()
        User_Book_Challenge.query.delete()
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
                 page_count = 100,
                 age_category = 'NA')
        
        db.session.add(self.ub1)
        db.session.commit()

        self.tbrlist = List(list_type = "TBR",
                            user_id = self.testuser.user_id)
        self.dnflist = List(list_type = "DNF", 
                            user_id = self.testuser.user_id)
        self.completelist = List(list_type = "Complete",
                                 user_id = self.testuser.user_id)
        
        db.session.add_all([self.tbrlist, self.dnflist, self.completelist])
        db.session.commit()

        self.userbooklist = User_Book_List(list_id = self.tbrlist.list_id, userbook_id = self.ub1.userbook_id)
        db.session.add(self.userbooklist)
        db.session.commit()

        self.challenge = Challenge(creator_id = self.testuser.user_id, name="test challenge", num_books=10, description='')
        db.session.add(self.challenge)
        db.session.commit()

        stmt = (insert(User_Challenge).values(user_id = self.testuser.user_id, challenge_id = self.challenge.challenge_id))
        db.session.execute(stmt)
        db.session.commit()

        self.client = app.test_client()

    
    def tearDown(self):
        """Clean up any fouled transactions and clear session and outbox"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                if change_session.get(CURR_USER_KEY):
                    change_session.pop(CURR_USER_KEY)
        db.session.rollback()

    def test_show_challenges_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to access the challenge list page?"""

        with self.client as c:
            resp = c.get('/challenges')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_show_challenges_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access the challenges list page?"""

        with self.client as c:
            resp = c.get('/challenges', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_show_challenges(self):
        """Does the site correctly display the page for listing all challenges"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.get('/challenges')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add a Challenge', html)
    
    def test_show_user_challenges_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to access the user challenge list page?"""

        with self.client as c:
            resp = c.get(f'/users/{self.testuser.user_id}/challenges')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_show_user_challenges_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access the user challenges list page?"""

        with self.client as c:
            resp = c.get(f'/users/{self.testuser.user_id}/challenges', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_show_user_challenges(self):
        """Does the site correctly display the page for listing all challenges"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.get(f'/users/{self.testuser.user_id}/challenges')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Start Date', html)
    
    def test_return_challenges_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to access the challenge api?"""

        with self.client as c:
            resp = c.get('/api/challenges')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_return_challenges_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access the challenge api?"""

        with self.client as c:
            resp = c.get('/api/challenges', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_return_challenges(self):
        """Does the site correctly return the information for listing all challenges"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.get('/api/challenges')

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, [{'creator_id': self.testuser.user_id, 'description': '', 'id': self.challenge.challenge_id, 'name': 'test challenge', 'num_books': 10}])

    def test_return_your_challenges_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to access the user challenge api?"""

        with self.client as c:
            resp = c.get('/api/yourchallenges')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_return_your_challenges_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access the user challenge api?"""

        with self.client as c:
            resp = c.get('/api/yourchallenges', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_return_your_challenges(self):
        """Does the site correctly return the information for listing the user's challenges"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.get('/api/yourchallenges')

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, [{'creator_id': self.testuser.user_id, 'description': '', 'end date': None, 'id': self.challenge.challenge_id, 'name': 'test challenge', 'num_books': 10, 'start_date': None}])

    def test_add_challenge_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to create a new challenge?"""

        with self.client as c:
            resp = c.get('/challenges/add')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_add_challenge_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to create a new challenge?"""

        with self.client as c:
            resp = c.get('/challenges/add', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_add_challenge_get(self):
        """Does the site correctly display the form for creating a new challenge?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.get('/challenges/add')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Number of Books', html)
    
    def test_add_challenge(self):
        """Does the site correctly create a new challenge and add the user to it?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
        
            resp = c.post('/challenges/add', data={'name': 'Second Test Challenge', 'num_books': 10, 'description': 'test description'})
            challenge = db.session.execute(db.select(Challenge).where(Challenge.name == 'Second Test Challenge')).scalar()
            user_challenge = db.session.execute(db.select(User_Challenge).where(User_Challenge.user_id == self.testuser.user_id).where(User_Challenge.challenge_id == challenge.challenge_id)).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/challenges')
            self.assertTrue(challenge)
            self.assertTrue(user_challenge)
    
    def test_add_challenge_redirect(self):
        """Does the site redirect correctly after creating a new challenge?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
        
            resp = c.post('/challenges/add', data={'name': 'Second Test Challenge', 'num_books': 10, 'description': 'test description'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add a Challenge', html)

    def test_edit_challenge_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to edit a challenge?"""

        with self.client as c:
            resp = c.get(f'/challenges/{self.challenge.challenge_id}')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_edit_challenge_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to edit a challenge?"""

        with self.client as c:
            resp = c.get(f'/challenges/{self.challenge.challenge_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_edit_challenge_get(self):
        """Does the site correctly display the edit challenge form?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.get(f'/challenges/{self.challenge.challenge_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('test challenge', html)
    
    def test_edit_challenge(self):
        """Does the site correctly edit an existing challenge?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
        
            resp = c.post(f'/challenges/{self.challenge.challenge_id}', data={'name': 'Test Challenge 2024', 'num_books': 10, 'description': 'test description'})
            html = resp.get_data(as_text=True)
            challenge = db.session.execute(db.select(Challenge).where(Challenge.name == 'Test Challenge 2024')).scalar()

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(challenge)
            self.assertEqual(challenge.description, 'test description')
            self.assertIn('Changes saved', html)
    
    def test_edit_challenge_wrong_user(self):
        """Does the site respond correctly when a user tries to edit a challenge they did not create?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser2.user_id
        
            resp = c.post(f'/challenges/{self.challenge.challenge_id}', data={'name': 'Test Challenge 2024', 'num_books': 10, 'description': 'test description'})
            challenge = db.session.execute(db.select(Challenge).where(Challenge.name == 'Test Challenge 2024')).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/challenges')
            self.assertFalse(challenge)
    
    def test_edit_challenge_wrong_user_redirect(self):
        """Does the site redirect correctly when a user tries to edit a challenge they did not create?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser2.user_id
        
            resp = c.post(f'/challenges/{self.challenge.challenge_id}', data={'name': 'Test Challenge 2024', 'num_books': 10, 'description': 'test description'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add a Challenge', html)

    def test_join_challenge_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to join a challenge?"""

        with self.client as c:
            resp = c.post(f'/challenges/join/{self.challenge.challenge_id}')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_join_challenge_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to join a challenge?"""

        with self.client as c:
            resp = c.post(f'/challenges/join/{self.challenge.challenge_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_join_challenge(self):
        """Does the site correctly add a user_challenge record when a user requests to join a challenge?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            new_challenge = Challenge(creator_id = self.testuser.user_id, name='Double Test Challenge', num_books=30, description='more challenge testing')
            db.session.add(new_challenge)
            db.session.commit()
            
            resp = c.post(f'/challenges/join/{new_challenge.challenge_id}')
            user_challenge = db.session.execute(db.select(User_Challenge).where(User_Challenge.user_id == self.testuser.user_id).where(User_Challenge.challenge_id == new_challenge.challenge_id)).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/challenges')
            self.assertTrue(user_challenge)
    
    def test_join_challenge_redirect(self):
        """Does the site redirect correctly after adding a user to a challenge?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            new_challenge = Challenge(creator_id = self.testuser.user_id, name='Double Test Challenge', num_books=30, description='more challenge testing')
            db.session.add(new_challenge)
            db.session.commit()
            
            resp = c.post(f'/challenges/join/{new_challenge.challenge_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You have joined the test challenge challenge', html)
    
    def test_join_challenge_already_in(self):
        """Does the site respond correctly when a user tries to join a challenge they have already joined?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post(f'/challenges/join/{self.challenge.challenge_id}')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/challenges')
    
    def test_join_challenge_already_in_redirect(self):
        """Does the site redirect correctly when a user tries to join a challenge they have already joined?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post(f'/challenges/join/{self.challenge.challenge_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are already signed up for this challenge', html)
