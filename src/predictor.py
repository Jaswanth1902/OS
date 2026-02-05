from typing import List

class MovingAveragePredictor:
    """Tiny predictor used in the prototype.

    API:
    - `fit(history: List[float])`
    - `predict(horizon: int) -> float`

    Replace with LSTM/TNC/other in future phases.
    """
    def __init__(self, window: int = 5):
        self.window = window
        self.history = []

    def fit(self, history: List[float]):
        self.history = list(history)

    def predict(self, horizon: int = 1) -> float:
        if not self.history:
            return 0.0
        window = self.history[-self.window:]
        return sum(window) / len(window)
