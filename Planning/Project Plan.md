TO DO LIST: 
## 23 Refactor based on feedback from hatchways and resubmit
    - basic small screen styling
        - fix sidebar and main content so it doesn't overlap 
        - get logout link back and in the right place
        - get login and signup back
    - fix sort
        - use css to make it not have the right cursor for clicking, as a temporary fix
    - run tests
    - switch let for testing to const
    - commit to regular branch
    - commit to hatchways branch
    - resubmit
    - increase modularization of app.py
        - move code out of the routes to helper functions
            - try just one and see if the context messes everything up
        - identify functionality which can be separated out
        - make a helpers.py to deal with helpers
    - better response to axios errors than stupid little alerts
        - look at what I'm doing to say welcome to the site
    - switch const back to let for testing
    - write any necessary tests for the modularization
    - run tests
## 22 Styling Well
    ## alerts (success & error)
    ## edit books (and manual add page) page
    ## edit challenge page
    ## edit your challenge page
    ## add new books page
    ## anonymous home page
    ## about page
    ## lists and challenges part 1
        ## Rewrite table logic including sort
            ## no sort on cover field
            ## have arrow show up in every column of the table that you can sort by
                ## get actual sorting arrow to appear in the right place
                ## have sort arrow appear on every column
                ## make it disappear when you search by that column and reappear when you search by another column
                ## write tests for new javascript
                ## run jasmine tests
        ## short description of what the page does for you
    ## lists and challenges part 2
        ## check boxes to the left of the titles and buttons to click to move them to the list so you can move a bunch at one time
            ## where do you end up? 
            ## write tests for new code
        ## search in the corner that lets you search for any book you have in the system (that will be standardized across pages)
            ## write tests for new code
## 21 Transfer database to new service
## 20 fix buttons on challenge list, to show leave or join depending on status and update table based on click. 
## 19 Allow user to add book to any list
## 18 Implement schedule books functionality
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
        ## is this necessary or is there a way to get the calendar back? 
    ## display book cover on calendar on start date
    ## write tests for all calendar views
    ## write tests for all calendar javascript
## 17 Implement email reminders functionality 
    ## what books will you need over the next 3 months?
    ## time to start a book
    ## time to finish a book
    ## time to post a book
    ## write tests
## 16 FAQ/Documentation
    ## flesh out documentation section
        ## create documentation for sending in emails
        ## create documentation for creating challenges
    ## figure out how to run tests on render
        ## python tests
        ## javascript tests
## 15 Create an architecture diagram
## 14 Sorting refinements
    ## take out the, an, a
    ## author by last name
## 13 Small Screen Styling
    ## also zoomed screen styling
    ## make sidebar a drop-down
## 12 Implement upload user image and book cover image
    ## write tests
## 11 Implement book covers on homepage are links that take you to a book form where you can add them to your list
    ## increase the number of book covers displayed? 
    ## Do I make it its own home page once logged in, because you need to be logged in to do that
    ## write tests
## 10 Implement importation functionality
    ## write tests
## 9 Implement OpenAI connection 
    ## write tests
## 8 Implement friendship & challenging functionality 
    ## write tests
## 7 Implement challenge categories
    ## include a way to search what books other people have assigned to what categories and add them to your lists
    ## a checklist of categories that users can check off
    ## hover over a book cover shows what category it is fulfilling
    ## write tests
## 6 Implement bookstore connection
    ## write tests
## 5 Implement library connection
    ## write tests
## 4 Refactor and take out all the print & console.logs
## 3 Speed it up
    ## add loading screens/visuals anywhere it is slow
## 2 Fully populate database with 100 challenges and 500 books
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
    - flask-mail
    - flask
    - flask_debugtoolbar
    - flask_sqlalchemy
    - sqlalchemy
    - wtforms
    - flask_wtf
    - Bookshop.org widgets
    - Pandas (for importing excel spreadsheets)

