TO DO LIST: 
## 18 Write tests for python & javascript
    ## model tests
    ## python function tests
    ## route tests
        ## user routes
        ## book routes
        ## challenge routes
        ## calendar routes
    ## javascript tests
## 17 Styling
    ## favicon.ico
    ## logo
    ## fix it so that on login, you get the appropriate flash message
    ## go over site with Augustin for design considerations
    ## reformat user profile 
    ## list displays
    ## add books button to the right place
    ## search form display
    ## search results display
    ## display of authors on edit form
    ## fix tabs to be visible
    ## make empty book list display look nice
    ## make tables go across the full page regardless of how long the text content is
    ## better response to axios errors than stupid little alerts
## 16 Documentation
    ## create ReadMe


    ## create help section
        ## create documentation for sending in emails
        ## create documentation for creating challenges
## 15 Implement schedule books functionality
    ## set post days 
    ## set calendar days as work or off based on a set schedule
        ## set work schedule button
        ## pop-up with form to set work days
        ## add recurring events to the calendar for work days and off days
    ## set calendar days as work or off based on a less regular schedule
        ## add second tab to pop-up for setting individual days to work or off
        ## add events to the calendar for work days
    ## schedule a book individually
        ## autosuggest search field
        ## load cover image on select
        ## start event, calculate end event
        ## or end event, calculate start event
        ## recommend post date (but let them change it)
    ## schedule 1 - 12 months of books randomly
    ## oops I deleted my calendar button
    ## display book cover on calendar on start date
## 14 Implement email reminders functionality 
    ## what books will you need over the next 3 months?
    ## time to start a book
    ## time to finish a book
    ## time to post a book
## 13 Refactor based on feedback from mentor and hatchways and Augustin
## 12 Small Screen Styling
## 11 Implement upload user image and book cover image
## 10 Implement book covers on homepage are links that take you to a book form where you can add them to your list
    ## increase the number of book covers displayed? 
    ## make it so books without covers will not display
## 9 Implement importation functionality
## 8 Implement OpenAI connection 
## 7 Implement friendship & challenging functionality 
## 6 Implement challenge categories
    ## include a way to search what books other people have assigned to what categories and add them to your lists
    ## a checklist of categories that users can check off
    ## hover over a book cover shows what category it is fulfilling
## 5 Implement bookstore connection
## 4 Implement library connection
## 3 Refactor and take out all the print & console.logs
## 2 Fully population database with 100 challenges and 500 books
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

