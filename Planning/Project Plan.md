TO DO LIST: 
## 21 Implement challenge functionalitys
    ## assign books to challenges
        ## figure out why the book covers aren't displaying (question in to Karishma)
## 20 figure out ngrok
## 19 Implement schedule books functionality
    ## figure out google oAuth
        ## figure out authentication scopes
        ## how to make the button disappear once permission has been given
    ## create calendar on button press
    ## embed calendar on calendar page
    ## save calendar idenifier to user profile to assist in future embedding
    ## set post days based on user profile
    ## set calendar days as work or off based on a set schedule
    ## set calendar days as work or off based on click
    ## schedule a book individually
        ## autosuggest search field
        ## load cover image on select
        ## start event, calculate end event
        ## or end event, calculate start event
        ## recommend post date (but let them change it)
    ## schedule a year, month, etc. of books randomly
## 18 Implement email reminders functionality 
    ## what books will you need over the next month?
    ## time to start a book
    ## time to finish a book
    ## time to post a book
## 17 Implement scripts & notes functionality 
    ## allow user to email in notes
        ##https://sendgrid.com/en-us/blog/how-to-receive-emails-with-the-flask-framework-for-python
        ## process incoming email to correct book (DONE)
        ## append notes to existing notes information (DONE)
## 16 Write tests for all routes & for javascript
    ## figure out why tests aren't working
## 15 Styling
    ## favicon.ico
    ## fix it so that on login, you get the appropriate flash message
    ## reformat user profile 
    ## list displays
    ## add books button to the right place
    ## search form display
    ## search results display
    ## display of authors on edit form
    ## display of description on edit form
    ## fix tabs to be visible
    ## make notes and script field big enough to read easily
    ## display book cover on calendar on start date
    ## make empty book list display look nice
    ## make tables go across the full page regardless of how long the text content is
    ## better response to axios errors than stupid little alerts
## 14 Documentation
    ## create help section
        ## create documentation for sending in emails
        ## create documentation for creating challenges
    ## create ReadMe
## 13 Deployment
## 12 Refactor based on feedback from mentor and hatchways
## 11 Small Screen Styling
## 10 Implement upload user image
## 9 Implement book covers on homepage are links that take you to a book form where you can add them to your list
    ## maybe increase the number of book covers displayed? 
## 8 Implement importation functionality
## 7 Implement OpenAI connection 
## 6 Implement friendship & challenging functionality 
## 5 Implement bookstore connection
## 4 Implement library connection
## 3 Refactor
## 2 Populate Database
## 1 Test with actual users and add functionality as needed



# APIs

## Google Books
    route: https://www.googleapis.com/books/v2/volumes
    requests: query field: intitle, inauthor, isbn
    data fields:    items[].volumeInfo.title
                    items[].volumeInfo.subtitle
                    items[].volumeInfo.authors
                    items[].volumeInfo.publisher
                    items[].volumeInfo.publishedDate
                    items[].volumeInfo.description
                    items[].volumeInfo.industryIdentifiers (.type = ISBN_13, .identifier = actual identifier)
                    items[].volumeInfo.pageCount
                    items[].volumeInfo.imageLinks.smallThumbnail
                    items[].id

## Google Calendar
    POST https://www.googleapis.com/calendar/v3/calendars - creates a secondary calendar
        request body: summary: (title of the calendar)
    POST https://www.googleapis.com/calendar/v3/calendars/calendarId/events - creates an event
        parameters: 
            calendarId
        request body: 
            end
            start
            start.date = if this is an all-day event
            summary = title of the event
    PUT https://www.googleapis.com/calendar/v3/calendars/caldenarId/events/eventId - updates an event

## Open AI
    pip install --upgrade openai
    code example on site

# 3rd Party Tools & Python Libraries
    - calendar
    - flask-mail
    - flask
    - flask_debugtoolbar
    - flask_sqlalchemy
    - sqlalchemy
    - wtforms
    - flask_wtf
    - Bookshop.org widgets
    - Pandas (for importing excel spreadsheets)

