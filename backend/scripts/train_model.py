import torch
import torch.nn as nn
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from torch.utils.data import Dataset, DataLoader
import os
import joblib  

class ReviewDataset(Dataset):
    def __init__(self, texts, labels, vectorizer):
        self.X = vectorizer.transform(texts).toarray()
        self.y = labels

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return torch.tensor(self.X[idx], dtype=torch.float32), torch.tensor(self.y[idx], dtype=torch.long)

class SimpleNN(nn.Module):
    def __init__(self, input_dim):
        super(SimpleNN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(64, 5)
        )

    def forward(self, x):
        return self.fc(x)

def evaluate(model, dataloader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for X_batch, y_batch in dataloader:
            outputs = model(X_batch)
            _, preds = torch.max(outputs, 1)
            correct += (preds == y_batch).sum().item()
            total += y_batch.size(0)
    return correct / total

def main():
    df = pd.read_csv("data/reviews.csv")
    df['label'] = df['label'] - 1  
    X_train, X_val, y_train, y_val = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42
    )

    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    vectorizer.fit(X_train)

    train_data = ReviewDataset(X_train.tolist(), y_train.tolist(), vectorizer)
    val_data = ReviewDataset(X_val.tolist(), y_val.tolist(), vectorizer)

    train_loader = DataLoader(train_data, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=16)

    model = SimpleNN(input_dim=1000)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(5):
        model.train()
        running_loss = 0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        avg_loss = running_loss / len(train_loader)
        val_acc = evaluate(model, val_loader)
        print(f"Epoch {epoch+1}, Loss: {avg_loss:.4f}, Validation Accuracy: {val_acc:.4f}")

    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/sentiment_model_weights.pt") 
    joblib.dump(vectorizer, "models/vectorizer.joblib") 
    print("Model weights saved to models/sentiment_model_weights.pt")
    print("Vectorizer saved to models/vectorizer.joblib")

if __name__ == "__main__":
    main()
