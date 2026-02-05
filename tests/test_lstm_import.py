import importlib


def test_lstm_import():
    mod = importlib.import_module('src.lstm_model')
    assert hasattr(mod, 'LSTMPredictor')
    cls = mod.LSTMPredictor
    inst = cls(lags=5)
    # always usable; if torch missing it should run in dummy mode
    assert hasattr(inst, 'predict')
