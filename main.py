from data_fetcher import MarketDataFetcher
from news_fetcher import NewsFetcher
from data_processor import DataProcessor

target_ticker = "AAPL"

# 1. Fetch Price Data
market = MarketDataFetcher(target_ticker)
price_df = market.fetch_data(period="1mo")

# 2. Fetch News Data
news = NewsFetcher(target_ticker)
news_df = news.fetch_news()

# 3. Merge Both Datasets
processor = DataProcessor(price_data=price_df, news_data=news_df)
final_dataset = processor.merge_data()

# Print the final result
print(f"--- FINAL MERGED DATASET FOR {target_ticker} ---")
print(final_dataset[['Close', 'Title']].tail(10))