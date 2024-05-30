"""Auth Views tests"""

import os
from unittest import TestCase
from app import do_login, do_logout, add_user_to_g, mail
from flask import g, session
from models import db, connect_db, User, Book, User_Book, List, Challenge, User_Book_List, User_Challenge
from sqlalchemy import update

os.environ['DATABASE_URL'] = "postgresql:///tbread-test"

from app import app, CURR_USER_KEY
app.app_context().push()

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class AuthViewTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """create test client, add sample data"""

        User_Book_List.query.delete()
        List.query.delete()
        User_Challenge.query.delete()
        Challenge.query.delete()
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
        """Clean up any fouled transactions and clear session and outbox"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                if change_session.get(CURR_USER_KEY):
                    change_session.pop(CURR_USER_KEY)
            with mail.record_messages() as outbox:
                if outbox:
                    outbox.pop()
        db.session.rollback()

#DOES NOT WORK    
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

#DOES NOT WORK    
    def test_do_logout(self):
        """Does do_logout function work?"""
        with app.test_request_context():
            with self.client as c:
                with c.session_transaction() as session:
                    session[CURR_USER_KEY] = self.testuser.user_id
                do_logout()

                self.assertNotIn(CURR_USER_KEY, session)
    
    def test_signup_already_logged_in(self):
        """Does site respond appropriately if user is already logged in?"""

        with self.client as c: 
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post('/signup', json={'username': 'testuser3', 'password': 'password', 'email': 'testuser3@test.com', 'userImage': ''})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')

    def test_signup_already_logged_in_redirect(self):
        """Does site redirect appropriately if user is already logged in?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post('/signup', json={'username': 'testuser3', 'password': 'password', 'email': 'testuser3@test.com', 'userImage': ''},  follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are already logged in', html)
            self.assertIn('Log out', html)
    
    def test_signup_correct(self):
        """Does signup route sign a user up for the site?"""

        with self.client as c:
            resp = c.post('/signup', json={'username': 'testuser3', 'password': 'password', 'email': 'testuser3@test.com', 'userImage': ''})
            user_id = db.session.execute(db.select(User.user_id).where(User.username =='testuser3')).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{user_id}/lists/tbr')

    def test_signup_correct_redirect(self):
        """Does signup route sign a user up for the site?"""

        with self.client as c:
            resp = c.post('/signup', json={'username': 'testuser3', 'password': 'password', 'email': 'testuser3@test.com', 'userImage': ''}, follow_redirects=True)
            user_id = db.session.execute(db.select(User.user_id).where(User.username =='testuser3')).scalar()
            user_image = db.session.execute(db.select(User.user_image).where(User.username == 'testuser3')).scalar()
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add Books', html)
            self.assertIn('Log out', html)
            self.assertEqual(user_id, session[CURR_USER_KEY])
            self.assertEqual(user_image, '/static/images/image.png')
    
    def test_signup_duplicate_email(self):
        """Does a duplicate email return the correct json error response?"""

        with self.client as c:
            resp = c.post('/signup', json={'username': 'testuser3', 'password': 'password', 'email': 'testuser2@test.com', 'userImage': ''})
            
            self.assertEqual(resp.status_code, 200)
            self.assertFalse(session.get(CURR_USER_KEY))
            self.assertEqual(resp.json, {'error': 'Email already taken'})
    
    def test_signup_duplicate_username(self):
        """Does a duplicate username return the correct json error response?"""

        with self.client as c:
            resp = c.post('/signup', json={'username': 'testuser', 'password': 'password', 'email': 'testuser3@test.com', 'userImage': ''})

            self.assertEqual(resp.status_code, 200)
            self.assertFalse(session.get(CURR_USER_KEY))
            self.assertEqual(resp.json, {'error': 'Username already taken'})
    
    def test_login_already_loggedin(self):
        """Does the site respond appropriately if a logged in user tries to log in?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post('/login', json={'username': 'testuser', 'password': 'testuser'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{session[CURR_USER_KEY]}/lists/tbr')

    def test_login_already_loggedin_redirect(self):
        """Does site redirect appropriately if a logged in user tries to log in?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post('/login', json={'username': 'testuser', 'password': 'testuser'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are already logged in', html)
    
    def test_login_correct(self):
        """Does the site log in a user if given the appropriate information?"""

        with self.client as c:
            resp = c.post('/login', json={'username': 'testuser', 'password': 'testuser'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr' )
    
    def test_login_correct_redirect(self):
        """Does the site redirect appropriately upon login?"""

        with self.client as c:
            resp = c.post('/login', json={'username': 'testuser', 'password': 'testuser'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(self.testuser.user_id, session[CURR_USER_KEY])
            self.assertEqual(self.testuser, g.user)
            self.assertIn('Add Books', html)

    def test_login_incorrect_username(self):
        """Does the site send the appropriate json error message if the wrong username is given?"""

        with self.client as c:
            resp = c.post('/login', json={'username': 'janedoe', 'password': 'testuser'})

            self.assertEqual(resp.status_code, 200)
            self.assertFalse(session.get(CURR_USER_KEY))
            self.assertEqual(resp.json, {'error': 'Invalid username'})
    
    def test_login_incorrect_password(self):
        """Does the site send the appropriate json error message if the wrong password is given?"""

        with self.client as c:
            resp = c.post('/login', json={'username': 'testuser', 'password': 'password'})

            self.assertEqual(resp.status_code, 200)
            self.assertFalse(session.get(CURR_USER_KEY))
            self.assertEqual(resp.json, {'error': 'Invalid password'})
    
    def test_logout_not_loggedin(self):
        """Does the site respond appropriate if an anonymous user sends a post request to logout?"""

        with self.client as c:
            resp = c.post('/logout')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')

    def test_logout_not_loggedin_redirect(self):
        """Does the site redirect appropriately if an anonymous user sends a post request to logout?"""

        with self.client as c:
            resp = c.post('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are not logged in', html)
            self.assertIn('Sign up', html)
    
    # DOES NOT WORK
    def test_logout_correct(self):
        """Does the site log a user out correctly?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post('/logout')

            self.assertEqual(resp.status_code, 302)
            self.assertFalse(session.get(CURR_USER_KEY))
            self.assertEqual(resp.location, '/')
    
    # DOES NOT WORK
    def test_logout_correct_redirect(self):
        """Does the site redirect correctly after logging a user out"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertFalse(session.get(CURR_USER_KEY))
            self.assertFalse(g.user)
            self.assertIn('You have logged out', html)
            self.assertIn('Sign up', html)
    
    def test_send_username_reminder_loggedin(self):
        """Does the site respond correctly if a logged-in user tries to send a username reminder?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            with mail.record_messages() as outbox:
            
                resp = c.post('/forgotusername', json={'email': 'testuser@test.com'})

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
                self.assertEqual(len(outbox), 0)
    
    def test_send_username_reminder_loggedin_redirect(self):
        """Does the site redirect correctly if a logged-in user tries to send a username reminder?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            with mail.record_messages() as outbox:
            
                resp = c.post('/forgotusername', json={'email': 'testuser@test.com'}, follow_redirects=True)
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('Log out', html)
                self.assertIn('Add Books', html)
                self.assertEqual(len(outbox), 0)
    
    def test_send_username_reminder_correct(self):
        """Does the site send an email and the correct json response when a username reminder is requested?"""

        with self.client as c:
            with mail.record_messages() as outbox:
                resp = c.post('/forgotusername', json={'email': 'testuser@test.com'})

                self.assertEqual(resp.status_code, 200)
                self.assertEqual(len(outbox), 1)
                self.assertEqual(outbox[0].subject, 'Username reminder')
                self.assertEqual(resp.json, {'success': 'Email sent'})
    
    def test_send_username_reminder_unknown_email(self):
        """Does the site send the correct json response if an unknown email is entered?"""

        with self.client as c:
            with mail.record_messages() as outbox:
                resp = c.post('/forgotusername', json={'email': 'camdent@gmail.com'})

                self.assertEqual(resp.status_code, 200)
                self.assertEqual(len(outbox), 0)
                self.assertEqual(resp.json, {'error': 'Email not in database. Please signup.'})
    
    def test_send_password_reset_loggedin(self):
        """Does the site respond correctly if a logged-in user tries to send a password reset?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            with mail.record_messages() as outbox:
                resp = c.post('/forgotpassword', json={'email': 'testuser@test.com'})

                self.assertEqual(resp.status_code, 302)
                self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
                self.assertEqual(len(outbox), 0)
    
    def test_send_password_reset_loggedin_redirect(self):
        """Does the site redirect correctly if a logged-in user tries to send a password reset?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id
            with mail.record_messages() as outbox:
                resp = c.post('/forgotpassword', json={'email': 'testuser@test.com'}, follow_redirects=True)
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('Log out', html)
                self.assertEqual(len(outbox), 0)
    
    def test_send_password_reset_correct(self):
        """Does the site send an email and the correct json response if a password reset is requested?"""

        with self.client as c:
            with mail.record_messages() as outbox:
                resp = c.post('/forgotpassword', json={'email': 'testuser@test.com'})

                self.assertEqual(resp.status_code, 200)
                self.assertEqual(len(outbox), 1)
                self.assertEqual(outbox[0].subject, 'Password Reset Link')
                self.assertIsNotNone(self.testuser.password_reset_token)
                self.assertIn(f'https://tb-read.com/passwordreset?prt={self.testuser.password_reset_token}&email=testuser@test.com', outbox[0].html, )
                self.assertEqual(resp.json, {'success': 'Email sent'})
    
    def test_send_password_reset_unknown_email(self):
        """Does the site send the correct json error if a password reset is requested with an unknown email?"""

        with self.client as c:
            with mail.record_messages() as outbox:
                resp = c.post('/forgotpassword', json={'email': 'camdent@gmail.com'})

                self.assertEqual(resp.status_code, 200)
                self.assertEqual(len(outbox), 0)
                self.assertEqual(resp.json, {'error': 'Email not in database. Please signup.'})

    def test_password_reset_loggedin(self):
        """Does the site respond correctly if a logged in user tries to use a password reset link?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id

            stmt = (update(User).where(User.user_id == self.testuser.user_id).values(password_reset_token = 'prt'))
            db.session.execute(stmt)
            db.session.commit()
            resp = c.get('/passwordreset?prt=prt&email=testuser@test.com')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')

    def test_password_reset_loggedin_redirect(self):
        """Does the site redirect correctly if a logged in user tries to use a password reset link?"""
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id

            stmt = (update(User).where(User.user_id == self.testuser.user_id).values(password_reset_token = 'prt'))
            db.session.execute(stmt)
            db.session.commit()
            resp = c.get('/passwordreset?prt=prt&email=testuser@test.com', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are already logged in', html)
            self.assertIn('Log out', html)
    
    def test_password_reset_bad_prt(self):
        """Does the site respond correctly if an invalid password reset token is used?"""

        with self.client as c:
            stmt = (update(User).where(User.user_id == self.testuser.user_id).values(password_reset_token = 'prt'))
            db.session.execute(stmt)
            db.session.commit()
            resp = c.get('/passwordreset?prt=prtprt&email=testuser@test.com')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')

    def test_password_reset_bad_prt_redirect(self):
        """Does the site redirect correctly if an invalid password reset token is used?"""

        with self.client as c:
            stmt = (update(User).where(User.user_id == self.testuser.user_id).values(password_reset_token = 'prt'))
            db.session.execute(stmt)
            db.session.commit()
            resp = c.get('/passwordreset?prt=prtprt&email=testuser@test.com', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Unauthorized password reset attempt', html)

    def test_password_reset_get(self):
        """Does the site show the password reset form when a valid password reset token is used?"""

        with self.client as c:
            stmt = (update(User).where(User.user_id == self.testuser.user_id).values(password_reset_token = 'prt'))
            db.session.execute(stmt)
            db.session.commit()
            resp = c.get('/passwordreset?prt=prt&email=testuser@test.com')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Update Password", html)

    def test_password_reset_correct(self):
        """Does the site reset a password correctly?"""

        with self.client as c:
            stmt = (update(User).where(User.user_id == self.testuser.user_id).values(password_reset_token = 'prt'))
            db.session.execute(stmt)
            db.session.commit()
            oldpassword = db.session.execute(db.select(User.password).where(User.email == 'testuser@test.com')).scalar()
            resp = c.post('/passwordreset?prt=prt&email=testuser@test.com', data={'password': 'kJeP7!9!wYGou%WD', 'password2': 'kJeP7!9!wYGou%WD'})
            prt = db.session.execute(db.select(User.password_reset_token).where(User.email == 'testuser@test.com')).scalar()
            newpassword = db.session.execute(db.select(User.password).where(User.email == 'testuser@test.com')).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
            self.assertEqual(prt, None)
            self.assertNotEqual(oldpassword, newpassword)


    def test_password_reset_correct_redirect(self):
        """Does the site redirect correctly when a password is reset?"""

        with self.client as c:
            stmt = (update(User).where(User.user_id == self.testuser.user_id).values(password_reset_token = 'prt'))
            db.session.execute(stmt)
            db.session.commit()
            oldpassword = db.session.execute(db.select(User.password).where(User.email == 'testuser@test.com')).scalar()
            resp = c.post('/passwordreset?prt=prt&email=testuser@test.com', data={'password': 'kJeP7!9!wYGou%WD', 'password2': 'kJeP7!9!wYGou%WD'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            prt = db.session.execute(db.select(User.password_reset_token).where(User.email == 'testuser@test.com')).scalar()
            newpassword = db.session.execute(db.select(User.password).where(User.email == 'testuser@test.com')).scalar()

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign up', html)
            self.assertEqual(prt, None)
            self.assertNotEqual(oldpassword, newpassword)
    
    def test_update_password_logged_out(self):
        """Does the site respond correctly when an anonymouse user reaches the update password page?"""

        with self.client as c:
            resp = c.post('/updatepassword', json={'password': 'kJeP7!9!wYGou%WD', 'password2': 'kJeP7!9!wYGou%WD'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')

    def test_update_password_logged_out_redirect(self):
        """Does the site redirect correctly when an anonymous user reaches the update password page?"""

        with self.client as c:
            resp = c.post('/updatepassword', json={'password': 'kJeP7!9!wYGou%WD', 'password2': 'kJeP7!9!wYGou%WD'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
            self.assertIn('Sign up', html)
    
    def test_update_password(self):
        """Does the site send the appropriate json when a user's password is updated? """

        with self.client as c:            
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id

            oldpassword = db.session.execute(db.select(User.password).where(User.user_id == self.testuser.user_id)).scalar()
            resp = c.post('/updatepassword', json={'password': 'kJeP7!9!wYGou%WD', 'password2': 'kJeP7!9!wYGou%WD'})
            newpassword = db.session.execute(db.select(User.password).where(User.user_id == self.testuser.user_id)).scalar()
            
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {'success': 'Password updated'})
            self.assertNotEqual(oldpassword, newpassword)
