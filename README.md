# TB-Read: Read. Create. Influence: Your Book Content Companion
[https://tb-read.com/](https://tb-read.com)

You are a busy content creator in the book influencer universe.

You've got bookshelves coming out your windows and scripts saved every which where on your hard drive.

How's a Booktuber / Bookstagrammer / BookTokker to stay organized?

TB Read is here to help!

- Manage your TBR, DNF, and Completed reading lists.
- Easily move books between your reading lists.
- Keep notes & scripts in each book record.
- Email in notes on the go without visiting the site.
- Create reading challenges.
- Join other user's reading challenges.
- Track your reading challenge progress.
- More features coming soon

___

TB-Read is a powerful web app crafted specifically for book influencers on social media. It streamlines your workflow by tracking your reading lists and challenge completions while keeping all your notes and scripts organized in one convenient place. Stay focused and let TB-Read handle the chaos, so you can create compelling content effortlessly.

## Features: 
- **Add Books to Reading Lists**: Add books to your reading lists using metadata from the Google Books API. 
- **Manage Reading Lists**: Keep track of your TBR, DNF, and Completed books. Effortlessly shift books from one list to another as you progress through your reading list. 
- **Notes & Scripts**: Attach notes and scripts to each  book record, ensuring you have all your thoughts and content in one place. Send notes to your TB-Read account via email so you can update your records on the go without needing to log in to the site. 
- **Reading Challenges**: Create new reading challenges to share with all the users of the site. Participate in reading challenges created by other users. Reading challenges are an excellent way to motivate yourself and prioritize certain kinds of reading and content. 
- **Track Challenge Progress**: Monitor your progress in various reading challenges to stay on top of your goals. 

## Future Features: 
- **Schedule Books**: Using the Google Calendar API, keep a calendar of planned reading, including when to start, finish, and post content for a book. 
- **Randomize Schedule**: Have TBRead randomly select and schedule book reading for 1-6 months. 
- **Email Reminders**: Receive monthly reminders of books you will need access to over the next three months so you can plan accordingly. Also receive email reminders of when to start, finish, and post content for a book. 
- **Import Reading Lists**: Efficiently move your reading list tracking to TB-Read by importing reading lists from an excel spreadsheet. 
- **AI Script Support**: Using previous scripts as an example of your writing style, have AI write you a content script based on your saved notes for a book. 
- **Challenge Tracking**: More robust challenge tracking with books assigned to specific categories to meet challenge requirements and checklists of completion. 

## User Flow: 
**Authorization**\
**Sign Up**\
    1. Visit the [TB-Read website](https://tb-read.com).\
    2. Click on the Sign up link in the upper right.\
    3. Fill out the registration form. \
    4. Click Submit to create your account.\
**Log In**\
    1. Visit the [TB-Read website](https://tb-read.com).\
    2. Click on the Log in link in the upper right. \
    3. Enter your username and password. \
    4. Click Login to access your account. \
**Forgot Credentials**\
    1. Click on the Log in link in the upper right.\
    2. Click the Forgot Username/Password? link. \
    3. Enter your email. \
    4. Click Send username reminder to receive an email with your username or click Reset password to receive an email with a reset password link.

**Manage Reading Lists**\
**Add Books to Reading Lists**\
    1. After login, you will see your lists page, including three tabs: TBR (To Be Read), DNF (Did Not Finish), and Completed. \
    2. Click the Add Books button on the right to start adding books.\
    3. Select a search field from the drop down menu. \
    4. Enter a search term. \
    5. Click Search. \
    6. When the search results populate, click the title link to select the appropriate book. \
    7. In the edit form, edit any metadata that you would like to change. \
    8. Select an age category from the drop-down menu. \
    9. Click the Add to TBR button to add the book to your list. \
    10. If you can't find the book you want, click the Add a book manually button to enter the metadata yourself. \
**Move Books between Reading Lists**\
    1. On your list page, locate the appropriate book, either by scrolling or searching. \
    2. Click the button labeled with the list you would like to transfer to.\
**Edit Book Information**\
    1. On your list page, locate the appropriate book, either by scrolling or searching. \
    2. Click the book's title to open the edit book form. \
    3. Change any metadata you would like to change, or add notes or a script. \
    4. Click the Save changes button to save your changes. \
**Email in Notes**\
    1. Using the email registered on the site, create a new email. \
    2. Address the email to notes@tb-read.com. \
    3. Add the exact title of the appropriate book as the subject line of the email. \
    4. Add your notes to the body of the email. \
    5. Once sent, your notes will be appended to the end of any existing notes in the book's record.

**Manage Challenges**\
**Create a New Challenge**\
    1. Click on Challenges on the sidebar to open the challenges section. \
    2. Click the Add a Challenge button. \
    3. Enter a name, number of books, and description of your challenge. \
    4. Click the Create Challenge button to create your challenge. \
    5. You will automatically be signed up to participate in the challenge you have created. \
**Join an Existing Challenge**\
    1. Click on Challenges on the sidebar to open the challenges section.\
    2. Find the appropriate challenge by scrolling or searching. \
    3. Click the Join Challenge button on the right side of the row. \
**Access Challenges You Have Joined**\
    1. Click on Challenges on the sidebar to open the challenges section.\
    2. Click the Your Challenges tab to open a list of the challenges which you have joined. \
    3. To see your progress on a challenge, click the challenge name to open the edit challenge page. \
    4. All the books which you have assigned to the challenge and completed reading will be visible at the bottom of the page. \
**Assign a Book to a Challenge**\
    1. Click on Lists on the sidebar to open your reading list. \
    2. Find the appropriate book by scrolling or searching. \
    3. Scroll to the bottom of the page. \
    4. Select the challenge from the drop-down menu. \
    5. Click the Assign to challenge button to assign the book to the challenge.

## API:  
TB-Read utilizes the [Google Books API](https://developers.google.com/books) to search for and add books to your reading list. This API provides comprehensive book metadata, ensuring you have all the information you need for your content creation.  

## Tech Stack:
TB-Read is built using the following technologies: 
- Python
- Javascript
- Flask
- PostgreSQL
- SQLAlchemy
- WTForms

## Installation: 

To start your own instance of TBRead, you will need to:  

Step 1: Clone the repository.  
For directions, please see https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository  

Step 2: Add secret values  
The code uses three secret values that are not included in the repository. You will need a local_settings.py file containing:   
SECRET_KEY: any sequence will work.   
MAIL_PASSWORD: Your mail app password to run flask_mail. The code will run without this but the username and password reminder features will not work.   
CLIENT_SECRETS_FILE: The path to your client secrets file from Google.  
You will also need a Client Secrets File from Google. The code will run without this but the calendar feature will not work.   

Step 3: Install the dependencies  
`pip3 install -r requirements.txt`  
All requirements can be seen in the requirements.txt file.   

Step 4: Run the code  
`flask run`  
 
## Who am I?: 
I'm Camden, a librarian, book enthusiast, and newly minted software engineer. I'm passionate about data, education, and evidence-based decision making. This is my first project that I'm sharing with the world. Feedback always welcome at tbreadlistmanager@gmail.com

___

For more information, visit [TB-Read](https://tb-read.com) and start organizing your book content today!
