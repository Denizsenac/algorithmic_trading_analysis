import numpy as np
import pandas as pd
import nltk 
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# VADER sözlüğünü arka planda indiriyoruz (sadece ilk çalışmada indirir, sonraki çalışmalarda es geçer)
nltk.download('vader_lexicon', quiet=True)

class DataProcessor:
    def __init__(self, price_data, news_data):
        self.price_data = price_data.copy() if hasattr(price_data, 'copy') else price_data
        self.news_data = news_data.copy() if hasattr(news_data, 'copy') else news_data
        # Sentiment analiz aracını başlatıyoruz
        self.analyzer = SentimentIntensityAnalyzer()

    def get_sentiment(self, text):
        if text == "No News":
            return 0.0
        # 'compound' değeri -1 (negatif) ile +1 (pozitif) arasında bir duygu skoru verir
        scores = self.analyzer.polarity_scores(text)
        return scores['compound']

    def merge_data(self):
        print("Merging price and news data, calculating sentiment scores...\n")
        
        # 1. Fiyat verisinin tarih indeksindeki saat ve timezone bilgisini tamamen silip sade bir tarihe çeviriyoruz
        self.price_data.index = pd.to_datetime(self.price_data.index).normalize().tz_localize(None)
        
        if self.news_data.empty:
            self.price_data['Title'] = "No News"
            self.price_data['Publisher'] = "None"
            self.price_data['Sentiment_Score'] = 0.0
            return self.price_data

        # 2. Haber verisinin tarihlerindeki saat ve timezone bilgisini tamamen silip sade bir tarihe çeviriyoruz
        self.news_data['Date'] = pd.to_datetime(self.news_data['Date']).dt.normalize().dt.tz_localize(None)

        grouped_news = self.news_data.groupby('Date').agg({
            'Title': lambda titles: ' | '.join(titles),
            'Publisher': lambda publishers: ' | '.join(publishers)
        }).reset_index()
        
        grouped_news.set_index('Date', inplace=True)
        
        # Artık her iki veri seti de temiz bir tarih (örn: 2026-10-14) üzerinden sorunsuzca birleşecek
        merged_df = self.price_data.join(grouped_news, how='left')
        
        merged_df['Title'] = merged_df['Title'].fillna("No News")
        merged_df['Publisher'] = merged_df['Publisher'].fillna("None")
        
        # --- SENTIMENT ANALİZİ EKLENTİSİ ---
        merged_df['Sentiment_Score'] = merged_df['Title'].apply(self.get_sentiment)
        
        return merged_df

    @staticmethod
    def calculate_indicators(df):
        """Teknik indikatörleri ve durağan (stationary) öznitelikleri (features) hesaplar."""
        res = df.copy()

        # 1. Trend İndikatörleri (Hareketli Ortalamalar)
        res['SMA_20'] = res['Close'].rolling(window=20).mean()
        res['SMA_50'] = res['Close'].rolling(window=50).mean()
        res['EMA_9'] = res['Close'].ewm(span=9, adjust=False).mean()
        res['EMA_21'] = res['Close'].ewm(span=21, adjust=False).mean()

        # Durağan MA Mesafesi: Fiyatın hareketli ortalamaya olan % mesafesi
        res['SMA_20_Dist'] = (res['Close'] - res['SMA_20']) / res['SMA_20']

        # 2. Wilder's RSI (14 günlük üstel yumuşatmalı, sıfıra bölme korumalı standart RSI)
        delta = res['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        res['RSI_14'] = 100.0 - (100.0 / (1.0 + rs))
        res['RSI_14'] = res['RSI_14'].fillna(50.0)

        # 3. ATR (Average True Range) - Dinamik Risk ve Stop-Loss Hesaplaması İçin
        if 'High' in res.columns and 'Low' in res.columns:
            high_low = res['High'] - res['Low']
            high_close = (res['High'] - res['Close'].shift()).abs()
            low_close = (res['Low'] - res['Close'].shift()).abs()
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            res['ATR_14'] = tr.rolling(14).mean().bfill()
        else:
            # High/Low yoksa yaklaşık ATR: fiyatın %2'si
            res['ATR_14'] = res['Close'] * 0.02

        # 4. Getiri ve Momentum Öznitelikleri (Stationary Features)
        res['Return_1d'] = res['Close'].pct_change(1)
        res['Return_5d'] = res['Close'].pct_change(5)

        # 5. Volatilite Özniteliği (20 günlük hareketli standart sapma)
        res['Vol_20d'] = res['Return_1d'].rolling(window=20).std().fillna(0.0)

        # 6. Hacim Dinamiği (Göreceli Hacim)
        if 'Volume' in res.columns:
            vol_mean_20 = res['Volume'].rolling(window=20).mean().replace(0, np.nan)
            res['Vol_Ratio'] = (res['Volume'] / vol_mean_20).fillna(1.0)
        else:
            res['Vol_Ratio'] = 1.0

        # İndikatör başlangıcındaki NaN satırları temizle
        cleaned = res.dropna(subset=['SMA_20', 'RSI_14', 'ATR_14'])
        return cleaned
