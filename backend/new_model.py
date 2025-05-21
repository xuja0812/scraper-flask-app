import re
import torch
import pandas as pd
from collections import Counter
from transformers import pipeline
from fb_scraper import scrape

import nltk
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

business_relevant_adjectives = {
    'good', 'great', 'bad', 'poor', 'excellent', 'friendly', 'rude', 'helpful', 'distracted',
    'cozy', 'clean', 'noisy', 'quiet', 'open', 'closed', 'available', 'reliable', 'trustworthy',
    'familiar', 'positive', 'negative', 'disappointing', 'amazing', 'quick', 'slow', 'fresh',
    'delicious', 'cheap', 'expensive', 'comfortable', 'professional', 'organized', 'welcoming',
    'efficient', 'dirty', 'crowded', 'long', 'short', 'pleasant', 'unpleasant'
}

complaint_keywords = {
    'wait', 'wait time', 'service', 'staff', 'order', 'experience', 'crowded',
    'line', 'food', 'quality', 'delay', 'rude', 'slow', 'cleanliness', 'problem',
    'issue', 'refund', 'payment', 'temperature', 'smell', 'taste', 'portion', 'bathroom',
    'parking', 'attention'
}

def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r"’", "'", text)
    text = re.sub(r"[^A-Za-z\s']", '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def extract_adjective_phrases(texts):
    adjectives = []
    for text in texts:
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        for word, tag in tagged:
            word_lower = word.lower()
            if tag.startswith('JJ') and word_lower in business_relevant_adjectives:
                adjectives.append(word_lower)
            elif word_lower == 'not':
                next_idx = tagged.index((word, tag)) + 1
                if next_idx < len(tagged):
                    next_word, next_tag = tagged[next_idx]
                    next_lower = next_word.lower()
                    if next_tag.startswith('JJ') and next_lower in business_relevant_adjectives:
                        adjectives.append(f"not {next_lower}")
    return adjectives

def extract_complaint_phrases(texts):
    complaint_phrases = []
    for text in texts:
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        for i, (word, tag) in enumerate(tagged):
            word_lower = word.lower()
            if word_lower in complaint_keywords:
                complaint_phrases.append(word_lower)
            elif (i + 1) < len(tagged):
                bigram = f"{word_lower} {tagged[i+1][0].lower()}"
                if bigram in complaint_keywords:
                    complaint_phrases.append(bigram)
    return complaint_phrases

def get_most_common_adjectives(texts, n=10):
    adj_list = extract_adjective_phrases(texts)
    freq = Counter(adj_list).most_common(n)
    return freq

def get_most_common_complaints_with_snippets(reviews, negative_texts, n=10):
    complaint_phrases = extract_complaint_phrases(reviews)
    freq = Counter(complaint_phrases).most_common(n)
    top_phrases = [phrase for phrase, _ in freq]

    phrase_to_reviews = {phrase: [] for phrase in top_phrases}

    for review in reviews:
        review_lower = review.lower()
        for phrase in top_phrases:
            if phrase in review_lower:
                phrase_to_reviews[phrase].append(review)

    negative_set = set(text.lower() for text in negative_texts)
    filtered_reviews = set()
    for phrase, reviews_list in phrase_to_reviews.items():
        for rev in reviews_list:
            if rev.lower() in negative_set:
                filtered_reviews.add(rev)

    return list(filtered_reviews)

def analyze_reviews(url, num_reviews):
    df = scrape(url, num_reviews)

    print("URL:", url)
    df['cleaned_text'] = df['text'].apply(clean_text)

    sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    sentiments = sentiment_analyzer(df['cleaned_text'].tolist(), truncation=True)
    df['sentiment_5star'] = [s['label'] for s in sentiments]
    df['predicted_label'] = [int(s['label'].split()[0]) for s in sentiments]

    def map_to_binary_sentiment(star_rating):
        return "positive" if star_rating >= 3 else "negative"

    df['sentiment'] = df['predicted_label'].apply(map_to_binary_sentiment)

    positive = df[df['sentiment'] == 'positive']
    negative = df[df['sentiment'] == 'negative']
    avg_score = round(float(df['predicted_label'].mean()), 3) if not df.empty else 0.0

    print("Sample cleaned reviews:")
    print(df['cleaned_text'].head(10).tolist())

    common_phrases = get_most_common_adjectives(df['cleaned_text'], n=10)
    common_complaints = get_most_common_complaints_with_snippets(df['text'], negative['text'], n=10)

    print("Common adjectives:", common_phrases)
    print("Common complaint snippets:")
    for snippet in common_complaints:
        print(f"  - {snippet}")

    return {
        "summary": {
            "total": int(len(df)),
            "positive": int(len(positive)),
            "negative": int(len(negative)),
            "average_score": avg_score
        },
        "positive_reviews": positive.to_dict(orient="records"),
        "negative_reviews": negative.to_dict(orient="records"),
        "common_words": [{"phrase": phrase, "count": int(count)} for phrase, count in common_phrases],
        "common_complaints": common_complaints
    }
