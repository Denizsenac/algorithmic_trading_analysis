import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
from sklearn.linear_model import Ridge

LOG_FILE = "predictions_log.json"


class PricePredictor:
    def __init__(self, df):
        self.df = df.copy()
        self.model = Ridge(alpha=1.0)
        self.features = [
            'Return_1d',
            'Return_5d',
            'SMA_20_Dist',
            'RSI_14',
            'Sentiment_Score',
            'Vol_20d',
            'Vol_Ratio'
        ]
        self.feature_importance = {}

    def _prepare_features(self):
        """Özniteliklerin (features) durağan (stationary) ve eksiksiz olduğundan emin olur."""
        if 'Return_1d' not in self.df.columns:
            self.df['Return_1d'] = self.df['Close'].pct_change(1)
        if 'Return_5d' not in self.df.columns:
            self.df['Return_5d'] = self.df['Close'].pct_change(5)
        if 'SMA_20' not in self.df.columns:
            self.df['SMA_20'] = self.df['Close'].rolling(20).mean()
        if 'SMA_20_Dist' not in self.df.columns:
            self.df['SMA_20_Dist'] = (self.df['Close'] - self.df['SMA_20']) / self.df['SMA_20']
        if 'RSI_14' not in self.df.columns:
            delta = self.df['Close'].diff()
            gain = delta.clip(lower=0).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
            loss = (-delta.clip(upper=0)).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
            rs = gain / loss.replace(0, np.nan)
            self.df['RSI_14'] = 100.0 - (100.0 / (1.0 + rs))
        if 'Sentiment_Score' not in self.df.columns:
            self.df['Sentiment_Score'] = 0.0
        if 'Vol_20d' not in self.df.columns:
            self.df['Vol_20d'] = self.df['Return_1d'].rolling(20).std().fillna(0.0)
        if 'Vol_Ratio' not in self.df.columns:
            if 'Volume' in self.df.columns:
                mean_vol = self.df['Volume'].rolling(20).mean().replace(0, np.nan)
                self.df['Vol_Ratio'] = (self.df['Volume'] / mean_vol).fillna(1.0)
            else:
                self.df['Vol_Ratio'] = 1.0

        # Durağan Hedef Değişken: Ham fiyat yerine bir sonraki günün % GETİRİSİ
        # (Ham fiyat rastgele yürüyüş gösterdiği için yanıltıcı R2 ve sahte başarı üretir)
        self.df['Target_Next_Return'] = self.df['Close'].pct_change().shift(-1)

    def train_and_predict(self):
        """Bir sonraki işlem günü için getiri odaklı fiyat tahmini üretir.

        Döner: (tahmin_edilen_fiyat, hedef_tarih)
        """
        print("Training model for next trading day prediction (stationary returns model)...\n")
        self._prepare_features()

        training_data = self.df.dropna(subset=['Target_Next_Return'] + self.features)
        if len(training_data) < 15:
            # Yetersiz veri durumunda son kapanışı koru
            last_price = float(self.df.iloc[-1]['Close'])
            target_date = (self.df.index[-1] + BDay(1)).normalize()
            return last_price, target_date

        X = training_data[self.features]
        y = training_data['Target_Next_Return']

        self.model.fit(X, y)

        # -------------------------------------------------------------
        # Sentiment Guard (Seyreklik ve Mantık Sapması Koruması):
        # 1. Eğitim setinde 5 günden az haber varsa regresyon katsayısı rastgele gürültü ezberler.
        # 2. Katsayı negatif çıkmışsa ("iyi haber gelince fiyat düşer" yanılgısı), katsayıyı sıfırlıyoruz.
        # -------------------------------------------------------------
        if 'Sentiment_Score' in self.features:
            non_zero_sent = int((training_data['Sentiment_Score'] != 0.0).sum())
            sent_idx = self.features.index('Sentiment_Score')
            sent_coef = float(self.model.coef_[sent_idx])

            if non_zero_sent < 5:
                print(f"ℹ️  [Sentiment Guard] Eğitim setinde sadece {non_zero_sent} gün haber skoru var (seyrek veri). Regresyon katsayısı nötrlendi.")
                self.model.coef_[sent_idx] = 0.0
            elif sent_coef < 0:
                print(f"⚠️  [Sentiment Guard] Yapay zekanın negatif duygu katsayısı ({sent_coef:+.5f}) ekonomik mantık filtresiyle sıfırlandı.")
                self.model.coef_[sent_idx] = 0.0

        self.feature_importance = dict(zip(self.features, self.model.coef_))

        last_day_features = self.df.iloc[[-1]][self.features].fillna(0.0)
        predicted_return = float(self.model.predict(last_day_features)[0])

        # Eğer bugünkü güncel haberlerde güçlü bir duygu varsa, getiriye sezgisel teyit ekle
        current_sentiment = float(last_day_features['Sentiment_Score'].iloc[0])
        if abs(current_sentiment) > 0.15:
            sentiment_adjustment = np.clip(current_sentiment * 0.005, -0.015, 0.015)
            predicted_return += sentiment_adjustment

        last_actual_price = float(self.df.iloc[-1]['Close'])
        predicted_tomorrow_price = last_actual_price * (1.0 + predicted_return)

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
        """Geçmiş tahminleri, hedef tarihin GERÇEK kapanış fiyatıyla ve YÖN doğruluğuyla karşılaştırır."""
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
                actual_close = float(closes.loc[target])
                predicted_close = float(log["Predicted_Close"])
                actual_today = float(log.get("Actual_Close_Today", actual_close))
                results.append((target, predicted_close, actual_close, actual_today))

        if not results:
            msg = f"[{ticker}] için karşılaştırılabilecek geçmiş tahmin yok."
            if pending:
                msg += f" ({pending} tahmin hedef günü bekliyor)"
            print(msg)
            return

        results.sort(key=lambda r: r[0])
        errors = []
        correct_directions = 0

        for target, predicted, actual, ref_today in results[-max_show:]:
            error_percentage = abs(predicted - actual) / actual * 100.0
            errors.append(error_percentage)

            pred_change = predicted - ref_today
            actual_change = actual - ref_today
            pred_up = pred_change >= 0
            actual_up = actual_change >= 0
            is_dir_correct = (pred_up == actual_up)
            if is_dir_correct:
                correct_directions += 1

            dir_str = "🟢 YÖN DOĞRU" if is_dir_correct else "🔴 YÖN YANLIŞ"

            print(f"Hedeflenen Tarih     : {target.strftime('%Y-%m-%d')}")
            print(f"Tahmin Edilen Fiyat  : ${predicted:,.2f} ({'Artış' if pred_up else 'Azalış'})")
            print(f"Gerçekleşen Fiyat    : ${actual:,.2f} ({'Artış' if actual_up else 'Azalış'})")
            print(f"Fiyat Sapması        : %{error_percentage:.2f} | Yön Kararı: {dir_str}")
            print("-" * 45)

        avg_error = sum(errors) / len(errors)
        dir_acc = (correct_directions / len(errors)) * 100.0
        print(f"Ortalama Fiyat Sapması ({len(errors)} tahmin) : %{avg_error:.2f}")
        print(f"Yön İsabet Oranı (Directional Hit Rate)  : %{dir_acc:.1f}")
        if pending:
            print(f"({pending} tahmin hedef günü bekliyor)")
