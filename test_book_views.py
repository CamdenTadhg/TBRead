"""Book Views tests"""


import os
from unittest import TestCase
from flask import g, session
from models import db, connect_db, User, Book, User_Book, List, Challenge, User_Challenge, User_Book_List, User_Book_Challenge
from sqlalchemy import update, insert
from werkzeug.datastructures import ImmutableMultiDict

os.environ['DATABASE_URL'] = "postgresql:///tbread-test"

from app import app, CURR_USER_KEY, add_book_to_database, strip_tags, add_book_to_tbr

app.app_context().push()

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class BookViewTestCase(TestCase):
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
    
    def test_strip_tags(self):
        """Does the function strip html tags from the text?"""

        text = '<b>#1 <i>NEW YORK TIMES</i> BESTSELLER • “<i>The Uninhabitable Earth</i> hits you like a comet, with an overflow of insanely lyrical prose about our pending Armageddon.”—Andrew Solomon, author of <i>The Noonday Demon<br></i></b><br><b>With a new afterword</b><br><br>'
        
        self.assertEqual(strip_tags(text), '#1 NEW YORK TIMES BESTSELLER • “The Uninhabitable Earth hits you like a comet, with an overflow of insanely lyrical prose about our pending Armageddon.”—Andrew Solomon, author of The Noonday DemonWith a new afterword')

    def test_add_book_to_database_standard(self):
        """Does the site correctly process incoming google books data for title, single author, publisher, pub_date, description, ISBN, page_count, and thumbnail?"""

        return_value = add_book_to_database('9nPrzgEACAAJ')
        book = db.session.execute(db.select(Book).where(Book.google_id == '9nPrzgEACAAJ')).scalar()

        self.assertEqual(return_value, book.book_id)
        self.assertEqual(book.title, 'A Night of Wings and Starlight')
        self.assertEqual(book.authors, 'Alexis L. Menard')
        self.assertEqual(book.publisher, 'CITY OWL Press')
        self.assertEqual(book.pub_date, '2022')
        self.assertIn('Breaking the curse will risk her heart', book.description)
        self.assertEqual(book.isbn, 9781648981708)
        self.assertEqual(book.page_count, 258)
        self.assertIn('9nPrzgEACAAJ', book.thumbnail)

    def test_add_book_to_database_special_case_one(self):
        """Does the site correctly process incoming google books data when the book has no thumbnail, description, or ISBN?"""

        return_value = add_book_to_database('ef27ngEACAAJ')
        book = db.session.execute(db.select(Book).where(Book.google_id == 'ef27ngEACAAJ')).scalar()

        self.assertEqual(return_value, book.book_id)
        self.assertFalse(book.thumbnail)
        self.assertFalse(book.description)
        self.assertFalse(book.isbn)
    
    def test_add_book_to_database_special_case_two(self):
        """Does the site correctly process incoming google books data when the book has a subtitle and two authors?"""

        return_value = add_book_to_database('DyeOd0Vb5lQC')
        book = db.session.execute(db.select(Book).where(Book.google_id == 'DyeOd0Vb5lQC')).scalar()

        self.assertEqual(return_value, book.book_id)
        self.assertEqual(book.title, "Intrinsic and Extrinsic Motivation: The Search for Optimal Motivation and Performance")
        self.assertEqual(book.authors, "Carol Sansone & Judith M. Harackiewicz")
    
    def test_add_book_to_database_special_case_three(self):
        """Does the site correctly process incoming google books data when the book has more than two authors?"""

        return_value = add_book_to_database('0xRoEAAAQBAJ')
        book = db.session.execute(db.select(Book).where(Book.google_id == '0xRoEAAAQBAJ')).scalar()

        self.assertEqual(return_value, book.book_id)
        self.assertEqual(book.authors, "Johnmarshall Reeve, Richard M. Ryan, Sung Hyeon Cheon, Lennia Matos, Haya Kaplan")
    
    def test_add_book_to_tbr(self):
        """Does the site correctly add a given userbook to the user's TBR?"""

        with self.client as c:    
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            userbook_id = db.session.execute(db.select(User_Book.userbook_id).where(User_Book.title == "test book")).scalar()
            c.get('/')
            add_book_to_tbr(userbook_id)
            user_book_list_record = db.session.execute(db.select(User_Book_List).where(User_Book_List.list_id == self.tbrlist.list_id).where(User_Book_List.userbook_id == userbook_id)).scalar()

            self.assertTrue(user_book_list_record)
    
    def test_add_books_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to access the book search page?"""

        with self.client as c:
            resp = c.get('/books')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_add_books_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access the book search page?"""

        with self.client as c:
            resp = c.get('/books', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_add_books(self):
        """Does the site correctly display the book search form?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.get('/books')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search Field', html)

    def test_edit_new_book_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to access the edit new book page?"""

        with self.client as c:
            resp = c.get('/books/lahsgoiawog')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_edit_new_book_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access the edit new book page?"""

        with self.client as c:
            resp = c.get('/books/lahsgoiawog', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_edit_new_book_already_in_database(self):
        """Does the site respond correctly when a user selects a book to add that is already in the database?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.get('/books/lahsgoiawog')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Mr. Testy Test', html)
    
    def test_edit_new_book_new_to_database(self):
        """Does the site respond correctly when a user selects a book to add that is not yet in the database?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.get('/books/9nPrzgEACAAJ')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('A Night of Wings and Starlight', html)


    def test_edit_new_book_submit(self):
        """Does the site respond correctly when a user submits the edit new book form?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post('/books/9nPrzgEACAAJ', data={'title': 'A Night of Wings and Starlight', 'authors': 'Alexis L. Menard', 'publisher': 'CITY OWL Press', 'pub_date': '2002', 'description': 'test description', 'isbn': 9781648981708, 'page_count': 258, 'age_category': 'N/A', 'thumbnail': 'http://books.google.com/books/content?id=9nPrzgEACAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE717h3kk2-sG3o37iYp74u20bWxdRiWnUZHEh2MfjoeyNXrBs5WhJG6xD-24R4M_I6xNqhtSvlaF464-jsLiUkcOibyF0B8JOgyyegKktji7vHhA2QoLVoKRkhlOTdI46vdF-3UM&source=gbs_api', 'notes': '', 'script': ''})
            userbook = db.session.execute(db.select(User_Book).where(User_Book.title == 'A Night of Wings and Starlight')).scalar()
            userbook_list = db.session.execute(db.select(User_Book_List).where(User_Book_List.userbook_id == userbook.userbook_id).where(User_Book_List.list_id == self.tbrlist.list_id)).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
            self.assertTrue(userbook)
            self.assertTrue(userbook_list)

    def test_edit_new_book_submit_redirect(self):
        """Does the site redirect correctly when a user submits the edit new book form?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post('/books/9nPrzgEACAAJ', data={'title': 'A Night of Wings and Starlight', 'authors': 'Alexis L. Menard', 'publisher': 'CITY OWL Press', 'pub_date': '2002', 'description': 'test description', 'isbn': 9781648981708, 'page_count': 258, 'age_category': 'N/A', 'thumbnail': 'http://books.google.com/books/content?id=9nPrzgEACAAJ&printsec=frontcover&img=1&zoom=5&imgtk=AFLRE717h3kk2-sG3o37iYp74u20bWxdRiWnUZHEh2MfjoeyNXrBs5WhJG6xD-24R4M_I6xNqhtSvlaF464-jsLiUkcOibyF0B8JOgyyegKktji7vHhA2QoLVoKRkhlOTdI46vdF-3UM&source=gbs_api', 'notes': '', 'script': ''}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            userbook = db.session.execute(db.select(User_Book).where(User_Book.title == 'A Night of Wings and Starlight')).scalar()
            userbook_list = db.session.execute(db.select(User_Book_List).where(User_Book_List.userbook_id == userbook.userbook_id).where(User_Book_List.list_id == self.tbrlist.list_id)).scalar()

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add Books', html)
            self.assertTrue(userbook)
            self.assertTrue(userbook_list)

    def test_edit_new_book_already_on_list(self):
        """Does the site respond correctly when a user tries to add a book to their TBR that is already on their TBR?"""

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post('/books/lahsgoiawog', data={'title': self.b1.title, 'authors': self.b1.authors, 'publisher': self.b1.publisher, 'pub_date': self.b1.pub_date, 'description': 'test description', 'isbn': 978254618254, 'page_count': 150, 'age_category': 'N/A', 'thumbnail': '/static/fakebookcover', 'notes': '', 'script': ''})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This book is already on your lists', html)

    def test_add_book_manually_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to access the page to add a book manually?"""

        with self.client as c:
            resp = c.get('/books/manual')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_add_book_manually_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access the page to add a book manually?"""

        with self.client as c:
            resp = c.get('/books/manual', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)

    def test_add_book_manually_get(self):
        """Does the site correctly display the form to add a book manually?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            resp = c.get('/books/manual')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('year only', html)
    
    def test_add_book_manually(self):
        """Does the site correctly add a book to the database if entered manually?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post('/books/manual', data={'google_id': 12345678, 'title': 'manual test', 'authors': 'Mr. Testy Test', 'publisher': 'Simon & Schuster', 'pub_date': 2024, 'description': 'test description', 'isbn': 9781542654352, 'page_count': 234, 'age_category': 'N/A', 'thumbnail': '/static/fakebookcover', 'notes': '', 'script': ''})
            book = db.session.execute(db.select(Book).where(Book.title == 'manual test')).scalar()
            userbook = db.session.execute(db.select(User_Book).where(User_Book.title == 'manual test')).scalar()
            userbooklist = db.session.execute(db.select(User_Book_List).where(User_Book_List.userbook_id == userbook.userbook_id).where(User_Book_List.list_id == self.tbrlist.list_id)).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
            self.assertTrue(book)
            self.assertTrue(userbook)
            self.assertTrue(userbooklist)

    def test_add_book_manually_redirect(self):
        """Does the site correctly redirect after adding a book to the database if entered manually?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post('/books/manual', data={'google_id': 12345678, 'title': 'manual test', 'authors': 'Mr. Testy Test', 'publisher': 'Simon & Schuster', 'pub_date': 2024, 'description': 'test description', 'isbn': 9781542654352, 'page_count': 234, 'age_category': 'N/A', 'thumbnail': '/static/fakebookcover', 'notes': '', 'script': ''}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            book = db.session.execute(db.select(Book).where(Book.title == 'manual test')).scalar()
            userbook = db.session.execute(db.select(User_Book).where(User_Book.title == 'manual test')).scalar()
            userbooklist = db.session.execute(db.select(User_Book_List).where(User_Book_List.userbook_id == userbook.userbook_id).where(User_Book_List.list_id == self.tbrlist.list_id)).scalar()

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(book)
            self.assertTrue(userbook)
            self.assertTrue(userbooklist)
            self.assertIn('Add Books', html)

    def test_edit_book_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to access the edit book page?"""

        with self.client as c:
            resp = c.get(f'/users_books/{self.ub1.userbook_id}')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_edit_book_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access the edit book page?"""

        with self.client as c:
            resp = c.get(f'/users_books/{self.ub1.userbook_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_edit_book_get(self):
        """Does the site correctly display the edit book form?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
        
        resp = c.get(f'/users_books/{self.ub1.userbook_id}')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Edit Book', html)
        self.assertIn('test book', html)
    
    def test_edit_book_get_not_found(self):
        """Does the site respond correctly when a book is not found?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
        
        resp = c.get('/users_books/0')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
    
    def test_edit_book_get_not_found_redirect(self):
        """Does the site redirect correctly when a book is not found?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
        
        resp = c.get('/users_books/0', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('tbrlistTable', html)
    
    def test_edit_book_submit(self):
        """Does the site respond correctly when an edit book form is submitted?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post(f'/users_books/{self.ub1.userbook_id}', data={'title': 'test book', 'authors': 'Mr. Testy Test', 'publisher': 'Simon & Schuster', 'pub_date': 2024, 'description': 'test description', 'isbn': '9785236412563', 'page_count': 243, 'age_category': 'Adult', 'thumbnail': "https://books.google.com/books?id=wrOQLV6xB-wC&printsec=frontcover&dq=harry+potter&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwiZ44Obka-GAxVBMzQIHfH9DVUQ6wF6BAgJEAE", 'notes': '', 'script': ''})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
            self.assertEqual(self.ub1.publisher, 'Simon & Schuster')
            self.assertEqual(str(self.ub1.age_category), 'AgeCategory.Adult')
        
    def test_edit_book_submit_redirect(self):
        """Does the site redirect correctly when an edit book form is submitted?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post(f'/users_books/{self.ub1.userbook_id}', data={'title': 'test book', 'authors': 'Mr. Testy Test', 'publisher': 'Simon & Schuster', 'pub_date': 2024, 'description': 'test description', 'isbn': '9785236412563', 'page_count': 243, 'age_category': 'Adult', 'thumbnail': "https://books.google.com/books?id=wrOQLV6xB-wC&printsec=frontcover&dq=harry+potter&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwiZ44Obka-GAxVBMzQIHfH9DVUQ6wF6BAgJEAE", 'notes': '', 'script': ''}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('tbrlistTable', html)
            self.assertEqual(self.ub1.publisher, 'Simon & Schuster')
            self.assertEqual(str(self.ub1.age_category), "AgeCategory.Adult")

    def test_delete_book_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to delete a book?"""

        with self.client as c:
            resp = c.post(f'/users_books/{self.ub1.userbook_id}/delete')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_delete_book_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to access the edit book page?"""

        with self.client as c:
            resp = c.post(f'/users_books/{self.ub1.userbook_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)

    def test_delete_book(self):
        """Does the site delete a user's copy of a book from the database?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post(f'/users_books/{self.ub1.userbook_id}/delete')
            userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == self.ub1.userbook_id).where(User_Book.user_id == self.testuser.user_id)).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
            self.assertFalse(userbook)
    
    def test_delete_book_redirect(self):
        """Does the site redirect correctly after deleting a user's copy of a book?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post(f'/users_books/{self.ub1.userbook_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)
            userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == self.ub1.userbook_id).where(User_Book.user_id == self.testuser.user_id)).scalar()

            self.assertEqual(resp.status_code, 200)
            self.assertIn('tbrlistTable', html)
            self.assertFalse(userbook)
    
    def test_delete_book_not_found(self):
        """Does the site provide appropriate feedback if the book for deletion is not found?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post(f'/users_books/0/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
    
    def test_delete_book_not_found_redirect(self):
        """Does the site redirect correctly when a book is not found for deletion?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post(f'/users_books/0/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('tbrlistTable', html)
            self.assertIn('Book not found', html)

    def test_delete_book_wrong_user(self):
        """Does the site provide appropriate feedback when a user tries to delete a book that does not belong to them?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser2.user_id

            resp = c.post(f'/users_books/{self.ub1.userbook_id}/delete')
            userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == self.ub1.userbook_id).where(User_Book.user_id == self.testuser.user_id)).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser2.user_id}/lists/tbr')
            self.assertTrue(userbook)
    
    def test_delete_book_wrong_user_redirect(self):
        """Does the site redirect correctly when a user tries to delete a book that does not belong to them?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser2.user_id

            resp = c.post(f'/users_books/{self.ub1.userbook_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)
            userbook = db.session.execute(db.select(User_Book).where(User_Book.userbook_id == self.ub1.userbook_id).where(User_Book.user_id == self.testuser.user_id)).scalar()

            self.assertEqual(resp.status_code, 200)
            self.assertIn('tbrlistTable', html)
            self.assertIn('You do not have permission', html)
            self.assertTrue(userbook)

    def test_transfer_between_lists_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to transfer a book between lists?"""

        with self.client as c:
            resp = c.post(f'/users_books/{self.ub1.userbook_id}/transfer/Complete')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_transfer_between_lists_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to transfer a book between lists?"""

        with self.client as c:
            resp = c.post(f'/users_books/{self.ub1.userbook_id}/transfer/Complete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_transfer_between_lists(self):
        """Does the site correctly transfer a book between one list and another?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post(f'/users_books/{self.ub1.userbook_id}/transfer/DNF')
            userbooklist = db.session.execute(db.select(User_Book_List).where(User_Book_List.userbook_id == self.ub1.userbook_id).where(User_Book_List.list_id == self.dnflist.list_id))

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
            self.assertTrue(userbooklist)
    
    def test_transfer_between_lists_redirect(self):
        """Does the site redirect correctly after transfering a book?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            resp = c.post(f'/users_books/{self.ub1.userbook_id}/transfer/DNF', follow_redirects=True)
            userbooklist = db.session.execute(db.select(User_Book_List).where(User_Book_List.userbook_id == self.ub1.userbook_id).where(User_Book_List.list_id == self.dnflist.list_id))
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('tbrlistTable', html)
            self.assertTrue(userbooklist)
    
    def test_transfer_between_lists_not_found(self):
        """Does the site provide correct feedback if a book is not found?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post(f'/users_books/0/transfer/Complete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
    
    def test_transfer_between_lists_not_found_redirect(self):
        """Does the site redirect correctly if a book is not found?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post(f'/users_books/0/transfer/Complete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('tbrlistTable', html)
            self.assertIn('Book not found', html)

    def test_transfer_between_lists_complete(self):
        """Does the site correctly update the challenge listing if a book is transfered to the complete list?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            stmt = insert(User_Book_Challenge).values(userbook_id = self.ub1.userbook_id, challenge_id=self.challenge.challenge_id)
            db.session.execute(stmt)
            db.session.commit()
            
            resp = c.post(f'/users_books/{self.ub1.userbook_id}/transfer/Complete')
            userbookchallenge = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == self.ub1.userbook_id)).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
            self.assertTrue(userbookchallenge.complete)
    
    def test_transfer_between_lists_not_complete(self):
        """Does the site correctly update the challenge listing if a book is transfered off the complete list?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            stmt = insert(User_Book_Challenge).values(userbook_id = self.ub1.userbook_id, challenge_id=self.challenge.challenge_id, complete=True)
            db.session.execute(stmt)
            db.session.commit()
            stmt2 = update(User_Book_List).where(User_Book_List.userbook_id == self.ub1.userbook_id).values(list_id = self.completelist.list_id)
            db.session.execute(stmt2)
            db.session.commit()
            
            resp = c.post(f'/users_books/{self.ub1.userbook_id}/transfer/DNF')
            userbookchallenge = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == self.ub1.userbook_id)).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser.user_id}/lists/tbr')
            self.assertFalse(userbookchallenge.complete)
    
    def test_transfer_between_lists_wrong_user(self):
        """Does the site respond appropriately when a user tries to transfer a book on another user's lists?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser2.user_id

            resp = c.post(f'/users_books/{self.ub1.userbook_id}/transfer/Complete')
            userbooklist = db.session.execute(db.select(User_Book_List).where(User_Book_List.userbook_id == self.ub1.userbook_id).where(User_Book_List.list_id == self.tbrlist.list_id)).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser2.user_id}/lists/tbr')
            self.assertTrue(userbooklist)


    def test_transfer_between_lists_wrong_user_redirect(self):
        """Does the site redirect correctly when a user tries to transfer a book on another user's lists?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser2.user_id

            resp = c.post(f'/users_books/{self.ub1.userbook_id}/transfer/Complete', follow_redirects=True)
            userbooklist = db.session.execute(db.select(User_Book_List).where(User_Book_List.userbook_id == self.ub1.userbook_id).where(User_Book_List.list_id == self.tbrlist.list_id)).scalar()
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('tbrlistTable', html)
            self.assertIn('You do not have permission to do that', html)
            self.assertTrue(userbooklist)

    def test_assign_book_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to assign a book to a challenge?"""

        with self.client as c:
            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/assign')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_assign_book_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to assign a book to a challenge?"""

        with self.client as c:
            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/assign', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_assign_book(self):
        """Does the site correctly assign a users's copy of a book to a challenge?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/assign', json={'challenge_id': self.challenge.challenge_id})
            user_book_challenge = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == self.ub1.userbook_id).where(User_Book_Challenge.challenge_id == self.challenge.challenge_id)).scalar()

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(user_book_challenge)
            self.assertEqual(user_book_challenge.complete, False)
            self.assertEqual(resp.json, {'success': 'Book added'})
    
    def test_assign_book_already_in(self):
        """Does the site respond with the correct error message when a user tries to assign a book to a challenge it has already been assigned to?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            stmt = (insert(User_Book_Challenge).values(userbook_id = self.ub1.userbook_id, challenge_id = self.challenge.challenge_id))
            db.session.execute(stmt)
            db.session.commit()

            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/assign', json={'challenge_id': self.challenge.challenge_id})

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {'error': 'Book already in challenge'})
    
    def test_assign_book_complete(self):
        """Does the site correctly update a completed book's user_book_challenge record when it is assigned to a challenge?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            stmt = (update(User_Book_List).where(User_Book_List.userbook_id == self.ub1.userbook_id).values(list_id = self.completelist.list_id))
            db.session.execute(stmt)
            db.session.commit()

            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/assign', json={'challenge_id': self.challenge.challenge_id})
            user_book_challenge = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == self.ub1.userbook_id).where(User_Book_Challenge.challenge_id == self.challenge.challenge_id)).scalar()

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(user_book_challenge.complete)
    
    def test_assign_book_wrong_user(self):
        """Does the site respond correctly when a user tries to assign another user's book to a challenge?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser2.user_id
            
            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/assign', json={'challenge_id': self.challenge.challenge_id})
            user_book_challenge = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == self.ub1.userbook_id).where(User_Book_Challenge.challenge_id == self.challenge.challenge_id)).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser2.user_id}/lists/tbr')
            self.assertFalse(user_book_challenge)

    def test_assign_book_wrong_user_redirect(self):
        """Does the site redirect correctly when a user tries to assign another user's book to a challenge?"""
    
        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser2.user_id

            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/assign', json={'challenge_id': self.challenge.challenge_id}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            user_book_challenge = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == self.ub1.userbook_id).where(User_Book_Challenge.challenge_id == self.challenge.challenge_id)).scalar()

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You do not have permission', html)
            self.assertFalse(user_book_challenge)

    def test_remove_book_loggedout(self):
        """Does the site respond correctly when an anonymous user tries to remove a book from a challenge?"""

        with self.client as c:
            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/remove')
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')
    
    def test_remove_book_loggedout_redirect(self):
        """Does the site redirect correctly when an anonymous user tries to remove a book from a challenge?"""

        with self.client as c:
            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/remove', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', html)
    
    def test_remove_book(self):
        """Does the site correctly remove a users's copy of a book from a challenge?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id
            
            stmt = (insert(User_Book_Challenge).values(userbook_id = self.ub1.userbook_id, challenge_id = self.challenge.challenge_id))
            db.session.execute(stmt)
            db.session.commit()

            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/remove', json={'challenge_id': self.challenge.challenge_id})
            user_book_challenge = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == self.testuser.user_id).where(User_Book_Challenge.challenge_id == self.challenge.challenge_id)).scalar()

            self.assertEqual(resp.status_code, 200)
            self.assertFalse(user_book_challenge)
            self.assertEqual(resp.json, {'success': 'Book removed'})
    
    def test_remove_book_not_in(self):
        """Does the site respond with the correct error message when a user tries to remove a book from a challenge which it is not assigned to?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser.user_id

            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/remove', json={'challenge_id': self.challenge.challenge_id})

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {'error': 'Book is not assigned to this challenge'})
    
    def test_remove_book_wrong_user(self):
        """Does the site respond correctly when a user tries to remove another user's book from a challenge?"""

        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser2.user_id
            
            stmt = (insert(User_Book_Challenge).values(userbook_id = self.ub1.userbook_id, challenge_id = self.challenge.challenge_id))
            db.session.execute(stmt)
            db.session.commit()
            
            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/remove', json={'challenge_id': self.challenge.challenge_id})
            user_book_challenge = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == self.ub1.userbook_id).where(User_Book_Challenge.challenge_id == self.challenge.challenge_id)).scalar()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{self.testuser2.user_id}/lists/tbr')
            self.assertTrue(user_book_challenge)

    def test_remove_book_wrong_user_redirect(self):
        """Does the site redirect correctly when a user tries to assign another user's book to a challenge?"""
    
        with self.client as c: 
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.testuser2.user_id

            stmt = (insert(User_Book_Challenge).values(userbook_id = self.ub1.userbook_id, challenge_id = self.challenge.challenge_id))
            db.session.execute(stmt)
            db.session.commit()

            resp = c.post(f'/api/users_books/{self.ub1.userbook_id}/remove', json={'challenge_id': self.challenge.challenge_id}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            user_book_challenge = db.session.execute(db.select(User_Book_Challenge).where(User_Book_Challenge.userbook_id == self.ub1.userbook_id).where(User_Book_Challenge.challenge_id == self.challenge.challenge_id)).scalar()

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You do not have permission', html)
            self.assertTrue(user_book_challenge)

    def test_receive_email(self):
        """Does the site correctly process incoming emails to the correct user and book in the notes field without deleting the contents of the notes field?"""

        with self.client as c: 

            stmt = (update(User_Book).where(User_Book.userbook_id == self.ub1.userbook_id).values(notes = 'did i get deleted?'))
            db.session.execute(stmt)
            db.session.commit()

            resp = c.post('/email', data=ImmutableMultiDict([('subject', 'test book'), ('text', 'test adding to notes'), ('envelope', '{"to": ["notes@tb-read.com"], "from":"testuser@test.com"}')]))

            self.assertEqual(resp.status_code, 200)
            self.assertIn('did i get deleted?', self.ub1.notes)
            self.assertIn('test adding to notes', self.ub1.notes)