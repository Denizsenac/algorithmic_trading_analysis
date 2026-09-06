from data_fetcher import MarketDataFetcher
from news_fetcher import NewsFetcher



kardemir=MarketDataFetcher("KARCL.IS")
apple=MarketDataFetcher("AAPL")

kardemir_data=kardemir.fetch_data()
apple_data = apple.fetch_data(period="5d")

print(kardemir_data.head())
print(apple_data.head())

apple_news = NewsFetcher("AAPL")

news_data = apple_news.fetch_news()

print("--- LATEST NEWS AND MARKET SENTIMENT ---")
if not news_data.empty:
    print(news_data[['Date', 'Publisher', 'Title']].head())
else:
    print("No recent news found.")