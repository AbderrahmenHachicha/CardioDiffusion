import os
import torch
import torch.nn as nn
import numpy as np

# Resolve path to the cnn_model.pth file
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(BACKEND_DIR, "..", "models", "cnn_model.pth"))

# Label mappings
CLASSES = ['N', 'A', 'V', 'L', 'R']
CLASS_DESCRIPTIONS = {
    'N': 'Normal Beat',
    'A': 'Atrial Premature Beat',
    'V': 'Premature Ventricular Contraction',
    'L': 'Left Bundle Branch Block Beat',
    'R': 'Right Bundle Branch Block Beat'
}

class ECGClassifier(nn.Module):
    """
    1D CNN + BiLSTM model for ECG classification.
    """
    def __init__(self, num_classes=5):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv1d(1, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),

            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(2),
        )

        self.bilstm = nn.LSTM(128, 64, bidirectional=True, batch_first=True)

        self.classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        # Input shape: [batch_size, 187]
        x = x.unsqueeze(1)  # [batch_size, 1, 187]
        x = self.cnn(x)     # [batch_size, 128, 46] (approx)
        x = x.permute(0, 2, 1)  # [batch_size, 46, 128]
        x, _ = self.bilstm(x)   # [batch_size, 46, 128]
        x = x[:, -1, :]     # [batch_size, 128]
        return self.classifier(x)


def preprocess_signal(raw_signal) -> torch.Tensor:
    """
    Preprocess incoming ECG raw signal:
    1. Convert to a 1D NumPy array of float32.
    2. Pad with zeros or truncate to ensure the length is exactly 187.
    3. Apply min-max normalization: (val - min) / (max - min).
    4. Convert to a PyTorch tensor and add a batch dimension: shape (1, 187).
    """
    # Convert input to numpy array
    signal = np.array(raw_signal, dtype=np.float32)
    
    # Flatten if multi-dimensional (e.g. if it is shape (1, 187) or (187, 1))
    if signal.ndim > 1:
        signal = signal.flatten()
        
    # Ensure signal is exactly 187 elements long
    target_length = 187
    if len(signal) < target_length:
        padded = np.zeros(target_length, dtype=np.float32)
        padded[:len(signal)] = signal
        signal = padded
    elif len(signal) > target_length:
        signal = signal[:target_length]
        
    # Min-max normalization per signal
    sig_min = signal.min()
    sig_max = signal.max()
    denom = sig_max - sig_min
    if denom > 1e-8:
        signal = (signal - sig_min) / denom
    else:
        signal = np.zeros_like(signal)
        
    # Convert to PyTorch tensor and add batch dimension -> shape (1, 187)
    return torch.tensor(signal, dtype=torch.float32).unsqueeze(0)


# Global Model Instance (Lazy loaded to optimize startup)
_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
_model = None

def get_model() -> ECGClassifier:
    """
    Loads and returns the ECG Classifier model instance (singleton).
    """
    global _model
    if _model is None:
        model = ECGClassifier(num_classes=5)
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model checkpoint not found at: {MODEL_PATH}")
        # Load weights on the appropriate device
        model.load_state_dict(torch.load(MODEL_PATH, map_location=_device))
        model.to(_device)
        model.eval()
        _model = model
    return _model


def predict(raw_signal) -> dict:
    """
    Runs prediction on incoming ECG data.
    
    Parameters:
    - raw_signal: List of floats or 1D NumPy array representing the ECG signal.
    
    Returns:
    - dict: A dictionary containing:
        - "class": The predicted class code ('N', 'A', 'V', 'L', 'R')
        - "description": The full description of the class
        - "confidence": Confidence score of the prediction (float 0.0 - 1.0)
        - "probabilities": Dictionary mapping all class codes to their scores
    """
    # 1. Preprocess the signal
    tensor_signal = preprocess_signal(raw_signal).to(_device)
    
    # 2. Get the model
    model = get_model()
    
    # 3. Perform prediction
    with torch.no_grad():
        logits = model(tensor_signal)
        probs = torch.softmax(logits, dim=1).squeeze(0)
        
    # 4. Extract class and confidence
    pred_idx = torch.argmax(probs).item()
    pred_class = CLASSES[pred_idx]
    pred_desc = CLASS_DESCRIPTIONS[pred_class]
    confidence = probs[pred_idx].item()
    
    # Map all probabilities
    all_probs = {CLASSES[i]: float(probs[i].item()) for i in range(len(CLASSES))}
    
    return {
        "class": pred_class,
        "description": pred_desc,
        "confidence": float(confidence),
        "probabilities": all_probs
    }

