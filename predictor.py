import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import json
import os
from datetime import datetime

class PricePredictor:
    def __init__(self, df):
        self.df = df.copy()
        self.model = LinearRegression()

    def train_and_predict(self):
        print("Training model for next trading day prediction...\n")
        
        self.df['Target_Next_Close'] = self.df['Close'].shift(-1)
        if not pd.api.types.is_datetime64_any_dtype(self.df.index):
            self.df.index = pd.to_datetime(self.df.index)
        self.df['Day_of_Week'] = self.df.index.dayofweek
        
        last_day_features = self.df.iloc[[-1]].copy()
        training_data = self.df.dropna(subset=['Target_Next_Close'])
        
        features = ['Close', 'SMA_20', 'RSI_14', 'Sentiment_Score', 'Day_of_Week']
        X = training_data[features]
        y = training_data['Target_Next_Close']
        
        self.model.fit(X, y)
        X_today = last_day_features[features]
        predicted_tomorrow_price = self.model.predict(X_today)[0]
        
        today_index = last_day_features['Day_of_Week'].values[0]
        if today_index == 4:
            next_day_name = "Monday (Post-Weekend)"
        else:
            next_day_name = "Next Trading Day"
            
        return predicted_tomorrow_price, next_day_name
        
    # YENİ EKLENEN KAYIT FONKSİYONU
    def save_prediction(self, ticker, predicted_price, target_date_str, actual_price_today):
        filename = "predictions_log.json"
        log_entry = {
            "Ticker": ticker,
            "Prediction_Date": datetime.today().strftime('%Y-%m-%d'),
            "Target_Date": target_date_str,
            "Predicted_Close": predicted_price,
            "Actual_Close_Today": actual_price_today
        }
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
        else:
            data = []
            
        data.append(log_entry)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"[{ticker}] Prediction saved to {filename}")

    def evaluate_past_predictions(self, ticker, actual_price_today):
        filename = "predictions_log.json"
        
        # Log dosyası yoksa veya boşsa hiç işlem yapma
        if not os.path.exists(filename):
            print(f"[{ticker}] için geçmiş tahmin kaydı bulunamadı.\n")
            return
            
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

        # Bugünkü tarihi buluyoruz (Örn: "2026-11-02")
        today_str = datetime.today().strftime('%Y-%m-%d')
        
        found_past_prediction = False
        
        print(f"\n--- GEÇMİŞ TAHMİN KONTROLÜ ({ticker}) ---")
        for log in data:
            # Eğer geçmişte, hedef tarihi (Target_Date) "Bugün" olan bir tahmin yapılmışsa
            if log.get("Ticker") == ticker and log.get("Target_Date") == today_str:
                found_past_prediction = True
                past_pred_price = log.get("Predicted_Close")
                
                # Hata Payını (Error Margin) hesaplıyoruz
                error_margin = abs(past_pred_price - actual_price_today)
                error_percentage = (error_margin / actual_price_today) * 100
                
                print(f"Hedeflenen Tarih     : {today_str}")
                print(f"Geçmişteki Tahmin    : ${past_pred_price:,.2f}")
                print(f"Bugünkü Gerçek Fiyat : ${actual_price_today:,.2f}")
                
                # Sapma oranına göre başarılı/başarısız durumu
                if error_percentage <= 1.0:
                    print(f"Sonuç                : ✅ ÇOK BAŞARILI (Sapma: Sadece %{error_percentage:.2f})")
                elif error_percentage <= 3.0:
                    print(f"Sonuç                : ⚠️ KABUL EDİLEBİLİR (Sapma: %{error_percentage:.2f})")
                else:
                    print(f"Sonuç                : ❌ YANILGI BÜYÜK (Sapma: %{error_percentage:.2f})")
                print("-" * 40)
                
        if not found_past_prediction:
            print(f"Bugünün tarihine ({today_str}) ait geçmiş bir tahmin kaydı bulunamadı.")