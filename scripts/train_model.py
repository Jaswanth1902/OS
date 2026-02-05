"""Train a simple model on synthetic CPU usage data and save it.

This script is intentionally lightweight and uses scikit-learn.
"""
import os
import numpy as np
from src.ml_model import SimpleMLModel
import joblib


def generate_synthetic_series(length=1000):
    t = np.arange(length)
    series = 500000 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 100))
    # add bursts
    for i in range(50, length, 200):
        series[i:i+5] += 300000
    series += np.random.normal(scale=20000, size=length)
    return series.tolist()


def main():
    series = generate_synthetic_series(2000)
    model = SimpleMLModel(lags=20)
    model.fit(series)
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/simple_model.joblib')
    print('Saved model to models/simple_model.joblib')


if __name__ == '__main__':
    main()
