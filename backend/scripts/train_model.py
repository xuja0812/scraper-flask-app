import torch
import torch.nn as nn
import pandas as pd
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
import os
import numpy as np
import re

def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def load_glove(path="glove/glove.6B.100d.txt", dim=100):
    embeddings = {}
    with open(path, 'r', encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            word = parts[0]
            vec = np.array(parts[1:], dtype=np.float32)
            embeddings[word] = vec
    embeddings["<unk>"] = np.random.randn(dim).astype(np.float32)
    return embeddings

class GloveDataset(Dataset):
    def __init__(self, texts, labels, glove, dim=100):
        self.X = []
        self.y = []
        for text, label in zip(texts, labels):
            tokens = tokenize(text)
            vectors = [glove[token] if token in glove else glove["<unk>"] for token in tokens]
            if vectors:
                avg_vec = np.mean(vectors, axis=0)
                self.X.append(avg_vec)
                self.y.append(label)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return torch.tensor(self.X[idx], dtype=torch.float32), torch.tensor(self.y[idx], dtype=torch.long)

class SimpleNN(nn.Module):
    def __init__(self, input_dim):
        super(SimpleNN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 5)
        )

    def forward(self, x):
        return self.net(x)

def evaluate(model, dataloader, criterion):
    model.eval()
    correct, total, total_loss = 0, 0, 0
    with torch.no_grad():
        for X_batch, y_batch in dataloader:
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            total_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            correct += (preds == y_batch).sum().item()
            total += y_batch.size(0)
    return correct / total, total_loss / len(dataloader)

def main():
    df = pd.read_csv("data/reviews.csv")
    df['label'] = df['label'] - 1

    print("Loading GloVe embeddings...")
    embedding_dim = 100
    glove = load_glove("glove/glove.6B.100d.txt", dim=embedding_dim)

    total_tokens = 0
    covered_tokens = 0
    for text in df["text"]:
        tokens = tokenize(text)
        total_tokens += len(tokens)
        covered_tokens += sum(1 for token in tokens if token in glove)
    coverage_pct = covered_tokens / total_tokens if total_tokens > 0 else 0
    print(f"Token coverage in GloVe embeddings: {coverage_pct:.2%}")

    X_train, X_val, y_train, y_val = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42
    )

    train_data = GloveDataset(X_train.tolist(), y_train.tolist(), glove, dim=embedding_dim)
    val_data = GloveDataset(X_val.tolist(), y_val.tolist(), glove, dim=embedding_dim)

    train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=32)

    model = SimpleNN(input_dim=embedding_dim)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=5e-3)

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2, verbose=True)

    num_epochs = 20
    for epoch in range(num_epochs):
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
        val_acc, val_loss = evaluate(model, val_loader, criterion)

        print(f"Epoch {epoch+1:02d}/{num_epochs} | Train Loss: {avg_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")
        scheduler.step(val_acc)

    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/sentiment_model_glove.pt")
    print("Model weights saved to models/sentiment_model_glove.pt")

if __name__ == "__main__":
    main()
