import json
import os
from datetime import datetime

import pandas as pd
from pandas.tseries.offsets import BDay
from sklearn.linear_model import LinearRegression

LOG_FILE = "predictions_log.json"


class PricePredictor:
    def __init__(self, df):
        self.df = df.copy()
        self.model = LinearRegression()

    def train_and_predict(self):
        """Bir sonraki işlem günü için fiyat tahmini üretir.

        Döner: (tahmin_edilen_fiyat, hedef_tarih)
        Hedef tarih, BUGÜNE değil verinin SON GÜNÜNE göre hesaplanır; böylece
        hafta sonu çalıştırılsa bile doğru işlem gününü verir.
        (Not: BDay resmi tatilleri bilmez. Tatiller için exchange_calendars gibi
        bir takvim kütüphanesi eklenebilir.)
        """
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

        target_date = (self.df.index[-1] + BDay(1)).normalize()
        return predicted_tomorrow_price, target_date

    # ------------------------------------------------------------------
    # Log işlemleri
    # ------------------------------------------------------------------
    @staticmethod
    def _load_log():
        if not os.path.exists(LOG_FILE):
            return []
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            # Bozuk dosyanın üzerine yazıp veriyi kaybetmemek için yedeğini alıyoruz
            backup = LOG_FILE + ".bak"
            os.replace(LOG_FILE, backup)
            print(f"Uyarı: {LOG_FILE} bozuktu, yedeği {backup} olarak saklandı.")
            return []
        except OSError as e:
            print(f"Uyarı: {LOG_FILE} okunamadı: {e}")
            return []
        return data if isinstance(data, list) else []

    def save_prediction(self, ticker, predicted_price, target_date_str,
                        actual_price_today, prediction_date_str=None):
        """Tahmini kaydeder. (Ticker, Target_Date) aynıysa üzerine yazar (upsert)."""
        log_entry = {
            "Ticker": ticker,
            "Prediction_Date": prediction_date_str or datetime.today().strftime('%Y-%m-%d'),
            "Target_Date": target_date_str,
            "Predicted_Close": float(predicted_price),
            "Actual_Close_Today": float(actual_price_today),
        }

        # Aynı anahtara sahip eski tekrarlar da burada tek kayda iner (son yazılan kazanır)
        entries = {}
        for log in self._load_log():
            if isinstance(log, dict):
                entries[(log.get("Ticker"), log.get("Target_Date"))] = log
        entries[(ticker, target_date_str)] = log_entry

        # Önce geçici dosyaya yazıp sonra değiştiriyoruz: yazma yarıda kesilirse log bozulmaz
        tmp_file = LOG_FILE + ".tmp"
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(list(entries.values()), f, indent=4)
        os.replace(tmp_file, LOG_FILE)
        print(f"[{ticker}] Prediction saved to {LOG_FILE}")

    def evaluate_past_predictions(self, ticker, price_df, max_show=5):
        """Geçmiş tahminleri, hedef tarihin GERÇEK kapanış fiyatıyla karşılaştırır."""
        print(f"\n--- GEÇMİŞ TAHMİN KONTROLÜ ({ticker}) ---")

        closes = price_df['Close']
        last_date = closes.index[-1]
        results = []
        pending = 0

        for log in self._load_log():
            if not isinstance(log, dict) or log.get("Ticker") != ticker:
                continue
            try:
                target = pd.Timestamp(log.get("Target_Date"))
            except (ValueError, TypeError):
                continue  # eski/bozuk kayıt (örn. "Monday (Post-Weekend)")
            if pd.isna(target):
                continue

            if target > last_date:
                pending += 1  # hedef gün henüz gelmedi
            elif target in closes.index:
                results.append((target, log["Predicted_Close"], float(closes.loc[target])))
            # hedef gün veri setinde yoksa (tatil / pencere dışı) atlanır

        if not results:
            msg = f"[{ticker}] için karşılaştırılabilecek geçmiş tahmin yok."
            if pending:
                msg += f" ({pending} tahmin hedef günü bekliyor)"
            print(msg)
            return

        results.sort(key=lambda r: r[0])
        errors = []
        for target, predicted, actual in results[-max_show:]:
            error_percentage = abs(predicted - actual) / actual * 100
            errors.append(error_percentage)

            print(f"Hedeflenen Tarih     : {target.strftime('%Y-%m-%d')}")
            print(f"Geçmişteki Tahmin    : ${predicted:,.2f}")
            print(f"O Günkü Gerçek Fiyat : ${actual:,.2f}")
            if error_percentage <= 1.0:
                print(f"Sonuç                : ✅ ÇOK BAŞARILI (Sapma: Sadece %{error_percentage:.2f})")
            elif error_percentage <= 3.0:
                print(f"Sonuç                : ⚠️ KABUL EDİLEBİLİR (Sapma: %{error_percentage:.2f})")
            else:
                print(f"Sonuç                : ❌ YANILGI BÜYÜK (Sapma: %{error_percentage:.2f})")
            print("-" * 40)

        print(f"Ortalama sapma ({len(errors)} tahmin): %{sum(errors) / len(errors):.2f}")
        if pending:
            print(f"({pending} tahmin hedef günü bekliyor)")