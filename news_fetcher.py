import yfinance as yf
import pandas as pd
import datetime

class NewsFetcher:
    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol.upper()
        self.ticker = yf.Ticker(self.ticker_symbol)

    def fetch_news(self):
        print(f"[{self.ticker_symbol}] news are being fetched...\n")
        
        raw_news = self.ticker.news
        parsed_news = []
        
        # Eğer Yahoo Finance gerçekten haber bulursa bunları kullan:
        if raw_news:
            for article in raw_news:
                parsed_news.append({
                    "Title": article.get("title"),
                    "Publisher": article.get("publisher"),
                    "Date": pd.to_datetime(article.get("providerPublishTime"), unit='s'),
                    "Link": article.get("link")
                })
        # Haber bulamazsa (boş dönerse), test yapabilmemiz için örnek haberler üret:
        else:
            print("Uyarı: Canlı haber çekilemedi. Strateji testi için örnek veriler kullanılıyor...")
            today = datetime.datetime.today()
            parsed_news = [
                # Çok Olumlu Haber (3 gün önce - Cuma)
                {"Title": f"{self.ticker_symbol} reports record breaking earnings and positive outlook", 
                 "Publisher": "TestNews", "Date": today - datetime.timedelta(days=3), "Link": ""},
                # Olumsuz Haber (4 gün önce - Perşembe)
                {"Title": f"Investors are worried about {self.ticker_symbol}'s recent supply chain issues and delays", 
                 "Publisher": "TestNews", "Date": today - datetime.timedelta(days=4), "Link": ""},
                # Nötr/Hafif Olumlu Haber (5 gün önce - Çarşamba)
                {"Title": f"{self.ticker_symbol} announces steady growth in quarterly review", 
                 "Publisher": "TestNews", "Date": today - datetime.timedelta(days=5), "Link": ""}
            ]
            
        news_df = pd.DataFrame(parsed_news)
        return news_df