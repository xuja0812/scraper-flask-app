from datasets import load_dataset
import pandas as pd

dataset = load_dataset("yelp_review_full")
df = dataset["train"].to_pandas()[["text", "label"]]
df["label"] = df["label"] + 1  # change labels from 0-4 to 1-5
df.to_csv("data/reviews.csv", index=False)