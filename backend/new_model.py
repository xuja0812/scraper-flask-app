import re
import torch
import pandas as pd
from scripts.sentiment_utils import SimpleNN, load_model
from fb_scraper import scrape  

def clean_text(text):
    text = re.sub(r'http\S+', '', text)  
    text = re.sub(r'@\w+', '', text)     
    text = re.sub(r'#\w+', '', text)     
    return text.strip()

def map_to_binary_sentiment(pred):
    if pred >= 3:
        return "positive"
    else:
        return "negative"

def analyze_reviews(url, num_reviews):
    # example df for testing
    # df = pd.DataFrame({
    #     'text': ['Great product!', 'Not happy', 'Okay service']
    # })
    df = scrape(url, num_reviews)

    print("URL:", url)
    df['cleaned_text'] = df['text'].apply(clean_text)

    model, vectorizer = load_model()
    features = vectorizer.transform(df['cleaned_text']).toarray()
    inputs = torch.tensor(features, dtype=torch.float32)

    with torch.no_grad():
        logits = model(inputs)
        predicted_classes = torch.argmax(logits, dim=1).numpy()

    df['predicted_label'] = predicted_classes
    df['sentiment'] = df['predicted_label'].apply(map_to_binary_sentiment)

    positive = df[df['sentiment'] == 'positive']
    negative = df[df['sentiment'] == 'negative']
    avg_score = round(df['predicted_label'].mean(), 3) if not df.empty else 0.0

    return {
        "summary": {
            "total": len(df),
            "positive": len(positive),
            "negative": len(negative),
            "average_score": avg_score
        },
        "positive_reviews": positive.to_dict(orient="records"),
        "negative_reviews": negative.to_dict(orient="records"),
    }
