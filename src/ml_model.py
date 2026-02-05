from typing import Sequence, Optional
import warnings

try:
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    _SKLEARN_AVAILABLE = True
except Exception:
    np = None
    RandomForestRegressor = None
    train_test_split = None
    _SKLEARN_AVAILABLE = False


class SimpleMLModel:
    """A small wrapper around scikit-learn regressors for short-horizon CPU prediction.

    This implementation is resilient: if `numpy`/`scikit-learn` are not installed the
    class falls back to a safe, dependency-free implementation that uses a simple
    moving-average of recent observations. This allows other modules to import
    `src.ml_model` without hard failure in environments that don't have ML deps.

    API:
      - fit(history: Sequence[float])
      - predict(horizon: int = 1) -> float
    """

    def __init__(self, lags: int = 10):
        self.lags = lags
        self.is_dummy = not _SKLEARN_AVAILABLE
        if self.is_dummy:
            warnings.warn('scikit-learn or numpy not available; SimpleMLModel running in dummy mode (moving-average fallback)')
            self.is_trained = False
            self.model = None
        else:
            self.model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.is_trained = False

    def _make_dataset(self, series: Sequence[float]):
        if np is None:
            return None, None
        X, y = [], []
        s = list(series)
        for i in range(self.lags, len(s)):
            X.append(s[i - self.lags:i])
            y.append(s[i])
        if not X:
            return None, None
        return np.array(X), np.array(y)

    def fit(self, history: Sequence[float]):
        if self.is_dummy:
            # no-op in dummy mode
            self.is_trained = False
            return

        X, y = self._make_dataset(history)
        if X is None:
            return
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1, random_state=42)
        self.model.fit(X_train, y_train)
        self.is_trained = True

    def predict(self, history: Optional[Sequence[float]] = None, horizon: int = 1) -> float:
        # Dummy fallback: moving-average of last `lags` values
        if self.is_dummy or not self.is_trained:
            if history is None or len(history) == 0:
                return 0.0
            window = list(history)[-self.lags:]
            # if numpy is available use it for mean, otherwise use pure python
            if np is not None:
                return float(np.mean(window))
            else:
                return float(sum(window) / len(window))

        # iterative prediction using trained sklearn model
        seq = list(history[-self.lags:])
        preds = []
        for _ in range(horizon):
            x = np.array(seq[-self.lags:]).reshape(1, -1)
            p = float(self.model.predict(x)[0])
            preds.append(p)
            seq.append(p)
        return preds[-1]
