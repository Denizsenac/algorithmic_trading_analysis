from data_fetcher import MarketDataFetcher
from news_fetcher import NewsFetcher
from data_processor import DataProcessor
from ticker_search import TickerSearch

# --- main.py DOSYANIN EN ALTINA EKLENECEK KISIM ---
from strategy_engine import StrategyEngine

# --- main.py DOSYANIN EN ALTINA EKLENECEK KISIM ---
from Backtester import Backtester


# Kullanıcıya sorma ve arama kısmı
search_engine = TickerSearch()
company_input = input("Enter the name or symbolic feel of the company you want to analyze (e.g., Apple or THYAO.IS): ")

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
    print("the transaction was canceled")

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
    print("No news returned")

# 3. Merge Both Datasets
processor = DataProcessor(price_data=price_df, news_data=news_df)
final_dataset = processor.merge_data()

# Print the final result
print(f"--- FINAL MERGED DATASET FOR {target_ticker} ---")
# main.py dosyasının en alt satırını şu şekilde değiştir:
print(final_dataset[['Close', 'Sentiment_Score', 'Title']].tail(10))

# 4. Generate Algorithmic Trading Signals (Technical + Sentiment)
engine = StrategyEngine(final_dataset)
strategy_results = engine.generate_signals()

# Sonuçları daha okunaklı görebilmek için sadece aksiyon, fiyat ve duygu skorunu yazdırıyoruz
print(f"\n--- STRATEGY RESULTS FOR {target_ticker} ---")
print(strategy_results[['Close', 'RSI_14', 'Sentiment_Score', 'Action']].tail(15))

# 5. Run Historical Simulation (Backtesting)
simulator = Backtester(strategy_results, initial_balance=10000.0)
final_value, roi = simulator.run_simulation()

user_budget = 10000.0  

# 5. Run Historical Simulation (Backtesting)
simulator = Backtester(strategy_results, initial_balance=user_budget)
final_value, roi = simulator.run_simulation()

print(f"--- BACKTEST RESULTS FOR {target_ticker} ---")
print(f"Initial Investment : ${user_budget:,.2f}") 
print(f"Final Portfolio    : ${final_value:,.2f}")
print(f"Net Profit / Loss  : {roi:.2f}%")