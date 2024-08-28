from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
# from text_processor import process
from fb_scraper import scrape

# DETERMINES THE SENTIMENT (1-5) OF A REVIEW

def sentiment_score(review, tokenizer, model):
    tokens = tokenizer.encode(review, return_tensors='pt')
    result = model(tokens)
    return float(torch.argmax(result.logits)) + 1

# CREATE TOKENIZER AND MODEL FROM PRETRAINED SOURCES

def model_data(url, n):
    tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
    model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

    # SCRAPE THE DATA
    df = scrape(url, n)

    pd.set_option('display.max_columns', 7)
    df['sentiment'] = df['texts'].apply(lambda x: sentiment_score(x[:512], tokenizer, model))

    with open(f'/Users/jasmi/Downloads/personal-project-xuja0812-3/model/FINAL_DATA.txt',"w", encoding="utf-8") as data_file:
        dfAsString = df.to_string(header=False, index=False)
        data_file.write(dfAsString)

    # FORMATTING
    
    result = df.to_string(header=False, index=False)
    result_split = result.split("\n")
    printable = ""
    sum = 0.0
    for review in result_split:
        words = re.split(r"\s+", review)
        sen = float(words[len(words)-1])
        sum += sen
    for review in result_split:
        words = re.split(r"\s+", review)
        rec = ""
        index = 0
        while index < len(words) and words[index] != 'recommend' and words[index] != 'recommends' and words[index] != 'rating':
            rec += words[index] + " "
            index+=1
        rec += words[index]
        index += 1
        name = words[index]
        index += 1
        rev = ""
        for i in range (index, len(words)-1):
            rev += words[i] + " "
        sentiment = words[len(words)-1]
        printable += "\n" + name + "\n\n" + rec + "\n\n" + rev + "\n\n" + sentiment + "\n"
    avg = sum / len(result_split)
    printable = "THE AVERAGE SENTIMENT IS: " + str(avg) + "\n\n\n" + printable
    return printable
