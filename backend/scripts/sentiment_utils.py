import torch
import torch.nn as nn
import numpy as np
import re

def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def load_glove(path="glove/glove.6B.100d.txt", dim=100):
    embeddings = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            word = parts[0]
            vec = np.array(parts[1:], dtype=np.float32)
            embeddings[word] = vec
    embeddings["<unk>"] = np.random.randn(dim).astype(np.float32)
    return embeddings

def glove_to_tensor(tokens, glove, dim=100):
    vectors = [glove[token] if token in glove else glove["<unk>"] for token in tokens]
    if not vectors:
        avg_vec = np.zeros(dim, dtype=np.float32)
    else:
        avg_vec = np.mean(vectors, axis=0)
    return torch.tensor(avg_vec, dtype=torch.float32)

class SimpleNN(nn.Module):
    def __init__(self, input_dim=100):
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

def load_model(weights_path="models/sentiment_model_glove.pt", glove_path="glove/glove.6B.100d.txt"):
    glove = load_glove(glove_path)
    model = SimpleNN(input_dim=100)
    state_dict = torch.load(weights_path)
    model.load_state_dict(state_dict, strict=True)
    model.eval()
    return model, glove
