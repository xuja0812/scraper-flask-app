# Google Review Analyzer

## Main Scraper
- Uses Selenium to scrape reviews from a specified URL on Google Maps based on user input from the frontend to the Flask backend.  
- Continuously scrolls down the specified page until a sufficient number of reviews are collected.  

## Sentiment Analysis
- Runs each review through a pretrained BERT model that assigns a sentiment score from 1 to 5, with 5 being the most positive.  
- Attaches this sentiment score to each review for formatting and display in the frontend.  

## Backend
- Uses Flask and MySQL. 

- Users can create accounts and request formatted review scrapes.

 <img width="712" alt="Screenshot 2025-05-17 at 7 18 55 PM" src="https://github.com/user-attachments/assets/7585ae01-560a-457d-962f-d5caa7198e0c" />
<img width="716" alt="Screenshot 2025-05-17 at 7 20 01 PM" src="https://github.com/user-attachments/assets/9b91344b-7af2-412c-bf31-d3d395d7c34c" />
<img width="722" alt="Screenshot 2025-05-17 at 7 20 15 PM" src="https://github.com/user-attachments/assets/e0edaa57-0ebc-4c51-af30-b584feec3b52" />
