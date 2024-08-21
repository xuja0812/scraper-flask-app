# Scraper Flask App

Main Scraper
- uses Selenium to scrape reviews from a a specified URL on FaceBook as dictated by information being sent from the user (frontend) to a Flask backend
- continuously scrolls down the specified page until a positive number of reviews is detected
- archives the fully scrolled-through FaceBook page and saves it locally

Sentiment Analysis
- runs each review through a pretrained BERT model that determines a sentiment from 1-5, 5 being the most positive
- attaches this sentiment to each review to be formatted in the frontend

Backend
- Flask and MySQL
- users can create accounts and format scrapes that they request
