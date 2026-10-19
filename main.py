from data_fetcher import MarketDataFetcher
from news_fetcher import NewsFetcher
from data_processor import DataProcessor
from ticker_search import TickerSearch

# Kullanıcıya sorma ve arama kısmı
search_engine = TickerSearch()
company_input = input("Analiz etmek istediğiniz şirket adını veya hisse sembolünü girin (Örn: Apple veya THYAO.IS): ")

target_ticker = search_engine.search_company(company_input)

# Eğer kullanıcı geçerli bir seçim yaparsa analize devam et
if target_ticker:
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
    print(final_dataset[['Close', 'Sentiment_Score', 'Title']].tail(10))
else:
    print("İşlem iptal edildi.")

# 1. Fetch Price Data
market = MarketDataFetcher(target_ticker)
price_df = market.fetch_data(period="6mo")

# 2. Fetch News Data
news = NewsFetcher(target_ticker)
news_df = news.fetch_news()

# 2. Fetch News Data
news = NewsFetcher(target_ticker)
news_df = news.fetch_news()

print("\n--- ÇEKİLEN HAM HABERLER ---")
# Eğer tablo boş DEĞİLSE ve içinde 'Date' kolonu VARSA yazdır
if not news_df.empty and 'Date' in news_df.columns:
    print(news_df[['Date', 'Title', 'Publisher']])
else:
    print("Yahoo Finance bu hisse için şu an hiçbir haber döndürmedi (Liste boş).")

# 3. Merge Both Datasets
processor = DataProcessor(price_data=price_df, news_data=news_df)
final_dataset = processor.merge_data()

# Print the final result
print(f"--- FINAL MERGED DATASET FOR {target_ticker} ---")
# main.py dosyasının en alt satırını şu şekilde değiştir:
print(final_dataset[['Close', 'Sentiment_Score', 'Title']].tail(10))