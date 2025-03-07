# Scraper Flask App

## Main Scraper
- Uses Selenium to scrape reviews from a specified URL on Facebook based on user input from the frontend to the Flask backend.  
- Continuously scrolls down the specified page until a sufficient number of reviews are collected.  
- Archives the fully loaded Facebook page and saves it locally.  

## Sentiment Analysis
- Runs each review through a pretrained BERT model that assigns a sentiment score from 1 to 5, with 5 being the most positive.  
- Attaches this sentiment score to each review for formatting and display in the frontend.  

## Backend
- Uses Flask and MySQL.  
- Users can create accounts and request formatted review scrapes.  
