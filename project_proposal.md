## Overview

The project will be a website designed for social media book content producers to manage their To Be Read(TBR) lists. Such influencers work on tight timelines to get content regularly posted and need to plan out their reading to have the appropriate books finished on time. 

## Users

Social media content producers who are part of Booktok, Booktube, and other social media book communities. 

## Tools

Python, Flask, PostgreSQL, SQLAlchemy, Render, Jinja, Javascript, HTML, CSS, WTForms

## Data
- Google Books API to import titles into the database
- Library of Congress API to import titles into the database
- Google Calendar API to add scheduled events to a google calendar
- Twilio API for text messaging
- OpenAI for script drafts? 

## Features: Essentials
- Create new TBR list by importing titles from Google Books
- Schedule books on a calendar or have the system schedule books randomly for you. 
- Set up email or text reminders for key events from the calendar such as requesting the book from the library and starting reading
- Create and join reading challenges and track your completion of the challenge
- Maintain notes & scripts for content production

## Features: Stretch Goals
- Import existing TBR list from a spreadsheet
- OpenAI connection for script drafts
- Become "friends" with other users and challenge them to reading challenges
- Option to purchase the book from a local bookstore
- Link to local library for requesting books

## Database Schema
![database schema](/Planning/Initial%20Schema%20Sketch.jpg)

## Sample of User Flow
![sample user flow](/Planning/Sample%20User%20Flow.jpg)

## Potential Issues
- I haven't done a ton of testing with the API, but Google Book's normal interface can be a bit finicky about finding the right book. Sometimes it pulls results that don't make a lot of sense. I have selected the Library of Congress API as a backup in case I have trouble getting the Google Book API to be accurate enough in its searching.
- My major potential issue will be time. I'd like to make a very full-featured website and I have a limited amount of time in which to do it.
- I doubt that I will predict everything I need the database to contain before I start coding, so if I don't want to delete my whole database every time I realize I need a new field, I'll need to learn to use Alter statements to alter my model after it has been created.
- I expect learning how to export the calendar data into a google calendar to be one of the more challenging tasks. 

## Security Considerations
- User security will be handled by bcrypt using hashed passwords.
- User records will all be private by default. If I implement the friends feature, I would try to make it so you can open your record to your friends if you want.
- No financial information will be involved in the website. Even if I figure out the links to local bookstores, all the purchasing would happen on the bookstore's website, not on my website. 
