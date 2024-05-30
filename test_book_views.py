import os
from unittest import TestCase
from flask import g, session
from models import db, connect_db, User, Book, User_Book, List, Challenge, User_Challenge, User_Book_List
from sqlalchemy import update

os.environ['DATABASE_URL'] = "postgresql:///tbread-test"

from app import app, CURR_USER_KEY, add_book_to_database, strip_tags, add_book_to_tbr

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
        self.dnflist = List(list_type = "DNF", 
                            user_id = self.testuser.user_id)
        self.completelist = List(list_type = "Complete",
                                 user_id = self.testuser.user_id)
        
        db.session.add_all([self.tbrlist, self.dnflist, self.completelist])
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
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.user_id

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