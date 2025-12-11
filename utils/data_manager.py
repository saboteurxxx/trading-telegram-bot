# utils/data_manager.py
import pandas as pd
import ccxt

class DataManager:
    def __init__(self):
        self.exchange = ccxt.binance()
        
    def get_historical_data(self, symbol="BTC/USDT", timeframe="1h", limit=100):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f'Ошибка при загрузке данных: {e}')
            return pd.DataFrame()
    
    def get_current_price(self, symbol="BTC/USDT"):
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f'Ошибка получения цены: {e}')
            return None
