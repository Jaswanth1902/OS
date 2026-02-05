"""LSTM predictor implemented with PyTorch. Falls back gracefully when torch is absent.

API:
 - class LSTMPredictor(lags=20, hidden_size=32, num_layers=1)
   - fit(history, epochs=5)
   - predict(history, horizon=1) -> float

The implementation is intentionally small and geared for prototyping.
"""
from typing import Sequence, Optional
import warnings

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    _TORCH_AVAILABLE = True
except Exception:
    torch = None
    nn = None
    optim = None
    _TORCH_AVAILABLE = False


class LSTMPredictor:
    def __init__(self, lags: int = 20, hidden_size: int = 32, num_layers: int = 1, lr: float = 1e-3):
        self.lags = lags
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lr = lr
        self.is_dummy = not _TORCH_AVAILABLE
        if self.is_dummy:
            warnings.warn('PyTorch not available; LSTMPredictor running in dummy (moving-average) mode')
            self.model = None
            self.trained = False
        else:
            class _Model(nn.Module):
                def __init__(self, input_size, hidden_size, num_layers):
                    super().__init__()
                    self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                    self.fc = nn.Linear(hidden_size, 1)

                def forward(self, x):
                    # x: (batch, seq_len, input_size)
                    out, _ = self.lstm(x)
                    # take last time step
                    out = out[:, -1, :]
                    out = self.fc(out)
                    return out

            self.model = _Model(1, hidden_size, num_layers)
            self.criterion = nn.MSELoss()
            self.trained = False

    def _make_dataset(self, series: Sequence[float]):
        if torch is None:
            return None, None
        s = list(series)
        X, y = [], []
        for i in range(self.lags, len(s)):
            seq = s[i - self.lags:i]
            X.append(seq)
            y.append(s[i])
        if not X:
            return None, None
        Xt = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)  # (N, lags, 1)
        yt = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)
        return Xt, yt

    def fit(self, history: Sequence[float], epochs: int = 5, batch_size: int = 32):
        if self.is_dummy:
            self.trained = False
            return
        X, y = self._make_dataset(history)
        if X is None:
            return
        opt = optim.Adam(self.model.parameters(), lr=self.lr)
        dataset = torch.utils.data.TensorDataset(X, y)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        self.model.train()
        for _ in range(epochs):
            for xb, yb in loader:
                pred = self.model(xb)
                loss = self.criterion(pred, yb)
                opt.zero_grad()
                loss.backward()
                opt.step()
        self.trained = True

    def predict(self, history: Optional[Sequence[float]] = None, horizon: int = 1) -> float:
        # fallback
        if self.is_dummy or not self.trained:
            if history is None or len(history) == 0:
                return 0.0
            window = list(history)[-self.lags:]
            return float(sum(window) / len(window))

        seq = list(history[-self.lags:])
        preds = []
        self.model.eval()
        with torch.no_grad():
            for _ in range(horizon):
                x = torch.tensor(seq[-self.lags:], dtype=torch.float32).unsqueeze(0).unsqueeze(-1)  # (1,lags,1)
                p = float(self.model(x).item())
                preds.append(p)
                seq.append(p)
        return preds[-1]
