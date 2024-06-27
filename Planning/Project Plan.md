TO DO LIST: 
## 22 Styling
    ## Color palette
        ## two contrasting colors (purple and teal)
            ## teal is too bright, make a lighter teal and change buttons to lighter teal as well as sidebar
            ## change green to purple
                ## add edit class tag to all alert classes
                ## in css use those selectors [.edit-css .alert-success and .edit-css .alert-danger] to change background color, border color, and color
            ## pick a font to use throughout 
    ## homepage
        ## make covers display correctly on all size screens
        ## Logo change to To Be Read so we know what they stand for
        ## one line pitch below the navbar. why do I want to be on this website in the first place? 
    ## about page
        ## accessible when you aren't signed in. why this tool? who it's for in more detail? what it does? Snippet about who I am  (match this up with readme)
## 21 Write readme and submit here
## 20 Styling
    ## fix it so that on login, you get the appropriate flash message
    ## lists
        ## see if arrow can show up in every column of the table so you know you can sort by that
        ## see if you can turn off sorting for the cover image
        ## short description of what the page does for you
        ## search in the corner that lets you search for any book you have in the system (that will be standardized across pages)
        ## tab should say did not finish
        ## tabs should look like the add books. 
        ## check boxes to the left of the titles and button to click to move them to the list so you can move a bunch at one time
            ## where do you end up? 
        ## take away the table lines
        ## make table header words a little bit bigger and choose a different font for them
        ## spread out empty table so you can actually read the columns
    ## add books page
        ## make the field and term in a line, like the HCLIB search bar. 
        ## search bar should go across the top and search results appear below
        ## add book manually shows up at the bottom below any search results. All on one line. Increase font size. 
        ## no lines in the search results
    ## same things on the challenge page as on the lists page
## 19 Refactor based on feedback from mentor and hatchways and Augustin
    ## better response to axios errors than stupid little alerts
## 18 Transfer database to new service
## 17 fix buttons on challenge list, to show leave or join depending on status and update table based on click. 
## 16 Documentation
    ## create help section
        ## create documentation for sending in emails
        ## create documentation for creating challenges
    ## figure out how to run tests on render
        ## python tests
        ## javascript tests
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
    ## write tests for all calendar views
    ## write tests for all calendar javascript
## 14 Implement email reminders functionality 
    ## what books will you need over the next 3 months?
    ## time to start a book
    ## time to finish a book
    ## time to post a book
    ## write tests
## 13 Create an architecture diagram
## 12 Small Screen Styling
## 11 Implement upload user image and book cover image
    ## write tests
## 10 Implement book covers on homepage are links that take you to a book form where you can add them to your list
    ## increase the number of book covers displayed? 
    ## write tests
## 9 Implement importation functionality
    ## write tests
## 8 Implement OpenAI connection 
    ## write tests
## 7 Implement friendship & challenging functionality 
    ## write tests
## 6 Implement challenge categories
    ## include a way to search what books other people have assigned to what categories and add them to your lists
    ## a checklist of categories that users can check off
    ## hover over a book cover shows what category it is fulfilling
    ## write tests
## 5 Implement bookstore connection
    ## write tests
## 4 Implement library connection
    ## write tests
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

