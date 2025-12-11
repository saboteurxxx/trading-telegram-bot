# models/simple_model.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

class SimpleTradingModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.model.fit(X_train_scaled, y_train)
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        print(f'Обучение завершено!')
        print(f'Точность на обучающей выборке: {train_score:.2%}')
        print(f'Точность на тестовой выборке: {test_score:.2%}')
        self.is_trained = True
        return train_score, test_score
    
    def predict(self, X):
        if not self.is_trained:
            print('Модель не обучена!')
            return 0, 0.0
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        confidence = self.model.predict_proba(X_scaled)[0].max()
        return int(prediction), float(confidence)
    
    def save(self, model_path, scaler_path):
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        print(f'Модель сохранена в {model_path}')
    
    def load(self, model_path, scaler_path):
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.is_trained = True
            print('Модель загружена!')
        else:
            raise FileNotFoundError('Файлы модели не найдены')
