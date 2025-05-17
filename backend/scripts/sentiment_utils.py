import torch
import torch.nn as nn
import joblib  

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

def load_model(weights_path="models/sentiment_model_weights.pt", vectorizer_path="models/vectorizer.joblib"):
    vectorizer = joblib.load(vectorizer_path)
    model = SimpleNN(input_dim=1000)
    model.load_state_dict(torch.load(weights_path))
    model.eval()

    return model, vectorizer
