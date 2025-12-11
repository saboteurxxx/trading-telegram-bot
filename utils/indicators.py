# utils/indicators.py
import pandas as pd
from ta import add_all_ta_features

class IndicatorCalculator:
    @staticmethod
    def calculate_all_indicators(df):
        try:
            df_copy = df.copy()
            df_with_indicators = add_all_ta_features(
                df_copy, open='open', high='high', low='low', close='close', volume='volume', fillna=True
            )
            important_cols = [
                'close', 'volume',
                'trend_macd', 'trend_macd_signal', 'trend_macd_diff',
                'trend_sma_fast', 'trend_sma_slow',
                'trend_ema_fast', 'trend_ema_slow',
                'momentum_rsi', 'momentum_stoch_rsi',
                'volatility_bbh', 'volatility_bbl', 'volatility_bbm',
                'volume_obv'
            ]
            result = df_with_indicators[important_cols].copy()
            result.columns = [
                'close', 'volume',
                'macd', 'macd_signal', 'macd_diff',
                'sma_fast', 'sma_slow',
                'ema_fast', 'ema_slow',
                'rsi', 'stoch_rsi',
                'bb_high', 'bb_low', 'bb_mid',
                'obv'
            ]
            return result.dropna()
        except Exception as e:
            print(f'Ошибка расчёта индикаторов: {e}')
            return df
    
    @staticmethod
    def prepare_features_for_model(df):
        lookahead = 3
        future_price = df['close'].shift(-lookahead)
        price_change = (future_price - df['close']) / df['close']
        df = df.copy()
        df['target'] = 0
        df.loc[price_change > 0.01, 'target'] = 1
        df.loc[price_change < -0.01, 'target'] = -1
        df = df.dropna()
        feature_cols = [col for col in df.columns if col != 'target']
        X = df[feature_cols]
        y = df['target']
        return X, y
