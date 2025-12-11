# main_simple.py
import time
import pandas as pd
from datetime import datetime

from config.settings import Config
from utils.data_manager import DataManager
from utils.indicators import IndicatorCalculator
from models.simple_model import SimpleTradingModel
from strategies.simple_strategy import SimpleTradingStrategy

def main():
    print("=" * 50)
    print("🚀 ЗАПУСК УПРОЩЕННОГО ТОРГОВОГО БОТА")
    print("=" * 50)
    
    config = Config()
    data_manager = DataManager()
    indicator_calculator = IndicatorCalculator()
    model = SimpleTradingModel()
    
    print("\n1. Загрузка исторических данных...")
    raw_data = data_manager.get_historical_data(
        symbol=config.SYMBOL,
        timeframe=config.TIMEFRAME,
        limit=500
    )
    if raw_data.empty:
        print("Не удалось загрузить данные. Проверьте интернет-соединение.")
        return
    
    print("\n2. Расчет индикаторов...")
    data_with_indicators = indicator_calculator.calculate_all_indicators(raw_data)
    
    print("\n3. Подготовка данных для модели...")
    X, y = indicator_calculator.prepare_features_for_model(data_with_indicators)
    
    print(f"Размерность данных: {X.shape}")
    print(f"Количество примеров: {len(X)}")
    print(f"Распределение классов: {y.value_counts().to_dict()}")
    
    print("\n4. Обучение модели...")
    try:
        model.load(config.MODEL_PATH, config.SCALER_PATH)
        print("Модель загружена!")
    except Exception as e:
        print("Обучение новой модели...")
        train_score, test_score = model.train(X, y)
        model.save(config.MODEL_PATH, config.SCALER_PATH)
    
    print("\n5. Создание торговой стратегии...")
    strategy = SimpleTradingStrategy(model, config)
    
    print("\n6. Запуск торгового цикла...")
    print(f"Торговая пара: {config.SYMBOL}")
    print(f"Таймфрейм: {config.TIMEFRAME}")
    print(f"Начальный баланс: ")
    print("-" * 50)
    
    for i in range(5):
        print(f"\n📊 Итерация {i+1}/5")
        print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        current_price = data_manager.get_current_price(config.SYMBOL)
        if current_price is None:
            print("Не удалось получить текущую цену")
            time.sleep(config.CHECK_INTERVAL)
            continue
            
        print(f"Текущая цена: ")
        
        recent_data = data_manager.get_historical_data(
            symbol=config.SYMBOL,
            timeframe=config.TIMEFRAME,
            limit=100
        )
        
        if not recent_data.empty:
            recent_with_indicators = indicator_calculator.calculate_all_indicators(recent_data)
            if len(recent_with_indicators) >= 10:
                latest_for_prediction = recent_with_indicators.iloc[-10:].copy()
                if 'target' in latest_for_prediction.columns:
                    latest_for_prediction = latest_for_prediction.drop(columns=['target'])
                decision, confidence = strategy.analyze(latest_for_prediction)
                print(f"Решение: {decision}")
                print(f"Уверенность: {confidence:.2%}")
                print(f"Минимальная уверенность: {config.MIN_CONFIDENCE:.2%}")
                
                if decision == "BUY" and confidence > config.MIN_CONFIDENCE:
                    print("🎯 СИГНАЛ НА ПОКУПКУ!")
                    position_size = strategy.calculate_position_size(current_price)
                    print(f"Рекомендуемый размер позиции: {position_size:.6f}")
                elif decision == "SELL" and confidence > config.MIN_CONFIDENCE:
                    print("🎯 СИГНАЛ НА ПРОДАЖУ!")
                    position_size = strategy.calculate_position_size(current_price)
                    print(f"Рекомендуемый размер позиции: {position_size:.6f}")
                else:
                    print("⏸️  Ждем сигнала...")
        
        print(f"\n⏳ Ожидание {config.CHECK_INTERVAL} секунд...")
        time.sleep(config.CHECK_INTERVAL)
    
    print("\n" + "=" * 50)
    print("✅ Торговый цикл завершен!")
    print("=" * 50)

if __name__ == "__main__":
    main()
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
