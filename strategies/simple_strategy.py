# strategies/simple_strategy.py
class SimpleTradingStrategy:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.balance = config.INITIAL_BALANCE
        
    def analyze(self, data):
        latest_data = data.iloc[-1:].copy()
        if 'target' in latest_data.columns:
            latest_features = latest_data.drop(columns=['target'])
        else:
            latest_features = latest_data
        prediction, confidence = self.model.predict(latest_features)
        if prediction == 1 and confidence > self.config.MIN_CONFIDENCE:
            return "BUY", confidence
        elif prediction == -1 and confidence > self.config.MIN_CONFIDENCE:
            return "SELL", confidence
        else:
            return "HOLD", confidence
    
    def calculate_position_size(self, current_price):
        risk_amount = self.balance * self.config.RISK_PER_TRADE
        position_size = risk_amount / (current_price * self.config.STOP_LOSS)
        return position_size
