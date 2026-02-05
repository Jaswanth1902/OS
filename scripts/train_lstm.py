"""Train an LSTM predictor on synthetic CPU usage traces and save the model.

This script requires PyTorch. If PyTorch is not installed it will print an explanatory
message and exit.
"""
from src.lstm_model import LSTMPredictor
import os


def generate_synthetic_series(length=2000):
    import math, random
    series = []
    for t in range(length):
        base = 500000 * (0.5 + 0.5 * math.sin(2 * math.pi * t / 100))
        if t % 200 in range(50, 55):
            base += 300000
        base += random.gauss(0, 20000)
        series.append(base)
    return series


def main():
    model = LSTMPredictor(lags=20, hidden_size=32, num_layers=1)
    if model.is_dummy:
        print('PyTorch not installed; cannot train LSTM. Install torch and retry.')
        return

    series = generate_synthetic_series(3000)
    model.fit(series, epochs=3, batch_size=64)
    os.makedirs('models', exist_ok=True)
    import torch
    torch.save(model.model.state_dict(), 'models/lstm_state.pt')
    print('Saved LSTM state to models/lstm_state.pt')


if __name__ == '__main__':
    main()
