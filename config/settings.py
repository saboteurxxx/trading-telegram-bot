# config/settings.py
class Config:
    SYMBOL = "BTC/USDT"
    TIMEFRAME = "1h"
    INITIAL_BALANCE = 1000
    RISK_PER_TRADE = 0.02
    STOP_LOSS = 0.02
    TAKE_PROFIT = 0.04
    CHECK_INTERVAL = 300
    MODEL_PATH = "models/trading_model.pkl"
    SCALER_PATH = "models/scaler.pkl"
    MIN_CONFIDENCE = 0.60
