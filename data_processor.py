import pandas as pd
import nltk 
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# VADER sözlüğünü arka planda indiriyoruz (sadece ilk çalışmada indirir, sonraki çalışmalarda es geçer)
nltk.download('vader_lexicon', quiet=True)

class DataProcessor:
    def __init__(self, price_data, news_data):
        self.price_data = price_data
        self.news_data = news_data
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