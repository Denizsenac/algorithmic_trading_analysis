import yfinance as yf
import pandas as pd

class NewsFetcher:
    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol.upper()
        self.ticker = yf.Ticker(self.ticker_symbol)

    def fetch_news(self):
        print(f"[{self.ticker_symbol}] fetching news and market sentiment...\n")
        raw_news = self.ticker.news
        
        parsed_news = []
        for article in raw_news:
            parsed_news.append({
                "Title": article.get("title"),
                "Publisher": article.get("publisher"),
                "Date": pd.to_datetime(article.get("providerPublishTime"), unit='s'),
                "Link": article.get("link")
            })
            
        news_df = pd.DataFrame(parsed_news)
        return news_df