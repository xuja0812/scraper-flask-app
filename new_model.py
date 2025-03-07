from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
import pandas as pd
from fb_scraper import scrape

# Load pre-trained sentiment analysis model and tokenizer
def load_model():
    tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
    model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
    return tokenizer, model

# Determine the sentiment score (1-5) of a review
def sentiment_score(review, tokenizer, model):
    tokens = tokenizer.encode(review[:512], return_tensors='pt')  # Limit to 512 tokens
    result = model(tokens)
    return float(torch.argmax(result.logits)) + 1

# Process scraped data and compute sentiment scores
def model_data(url, num_reviews):
    tokenizer, model = load_model()
    df = scrape(url, num_reviews)
    
    df['sentiment'] = df['texts'].apply(lambda x: sentiment_score(x, tokenizer, model))
    
    output_path = '/Users/jasmi/Downloads/personal-project-xuja0812-3/model/FINAL_DATA.txt'
    df.to_csv(output_path, sep=' ', index=False, header=False)
    
    # Format output
    avg_sentiment = df['sentiment'].mean()
    formatted_reviews = []
    
    for _, row in df.iterrows():
        user = row['users']
        recommendation = ' '.join(re.split(r'\s+', row['ratings'])[:2])  # Extract recommendation text
        review_text = row['texts']
        sentiment = row['sentiment']
        
        formatted_reviews.append(f"\n{user}\n\n{recommendation}\n\n{review_text}\n\nSentiment: {sentiment}\n")
    
    printable = f"THE AVERAGE SENTIMENT IS: {avg_sentiment:.2f}\n\n" + "".join(formatted_reviews)
    return printable
