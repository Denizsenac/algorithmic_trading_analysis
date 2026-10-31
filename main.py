import asyncio
from data_fetcher import MarketDataFetcher
from news_fetcher import NewsFetcher
from data_processor import DataProcessor
from ticker_search import TickerSearch
from strategy_engine import StrategyEngine
from Backtester import Backtester
from predictor import PricePredictor

async def main():
    search_engine = TickerSearch()
    company_input = input("Enter the name or symbolic feel of the company you want to analyze (e.g., Apple or THYAO.IS): ")
    target_ticker = search_engine.search_company(company_input)

    if not target_ticker:
        print("the transaction was canceled")
        return

    # Asenkron (Hızlı) Veri Çekme
    market = MarketDataFetcher(target_ticker)
    price_task = market.fetch_data(period="6mo")
    
    # Not: Eğer NewsFetcher asenkron değilse, onu da ayrı bir dosyada aiohttp ile güncellemeliyiz.
    news = NewsFetcher(target_ticker)
    news_df = news.fetch_news()
    
    # Fiyat verisini bekle
    price_df = await price_task

    print("\n--- ÇEKİLEN HAM HABERLER ---")
    if not news_df.empty and 'Date' in news_df.columns:
        print(news_df[['Date', 'Title', 'Publisher']])
    else:
        print("No news returned")

    # Verileri Birleştir
    processor = DataProcessor(price_data=price_df, news_data=news_df)
    final_dataset = processor.merge_data()

    # İndikatör Hesaplamaları
    final_dataset['SMA_20'] = final_dataset['Close'].rolling(window=20).mean()
    
    delta = final_dataset['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    final_dataset['RSI_14'] = 100 - (100 / (1 + rs))
    
    # KRİTİK DÜZELTME: İndikatörlerin yarattığı boş (NaN) günleri siliyoruz ki yapay zeka çökmesin.
    final_dataset = final_dataset.dropna()

    print(f"\n--- FINAL MERGED DATASET FOR {target_ticker} ---")
    print(final_dataset[['Close', 'Sentiment_Score', 'Title']].tail(10))

    # Sinyal Üretimi
    engine = StrategyEngine(final_dataset)
    strategy_results = engine.generate_signals()

    print(f"\n--- STRATEGY RESULTS FOR {target_ticker} ---")
    print(strategy_results[['Close', 'RSI_14', 'Sentiment_Score', 'Action']].tail(15))

    # Backtest (Geçmiş Performans Simülasyonu)
    user_budget = 10000.0
    simulator = Backtester(strategy_results, initial_balance=user_budget)
    final_value, roi = simulator.run_simulation()

    print(f"\n--- BACKTEST RESULTS FOR {target_ticker} ---")
    print(f"Initial Investment : ${user_budget:,.2f}") 
    print(f"Final Portfolio    : ${final_value:,.2f}")
    print(f"Net Profit / Loss  : {roi:.2f}%")

    # Makine Öğrenmesi (Gelecek Fiyat Tahmini)
    print(f"\n--- MACHINE LEARNING PREDICTION FOR {target_ticker} ---")
    ai_predictor = PricePredictor(strategy_results)
    predicted_price, next_day_name = ai_predictor.train_and_predict()

    last_actual_price = strategy_results.iloc[-1]['Close']
    price_difference = predicted_price - last_actual_price
    percentage_change = (price_difference / last_actual_price) * 100

    print(f"Today's Actual Close Price   : ${last_actual_price:,.2f}")
    print(f"{next_day_name}'s Predicted Price : ${predicted_price:,.2f}")

    if price_difference > 0:
        print(f"Prediction Trend             : 📈 UP by {percentage_change:.2f}%")
    else:
        print(f"Prediction Trend             : 📉 DOWN by {percentage_change:.2f}%")
        
    # Tahmini JSON'a kaydet (Retrieval adımı için)
    ai_predictor.save_prediction(target_ticker, predicted_price, next_day_name, last_actual_price)

if __name__ == "__main__":
    asyncio.run(main())