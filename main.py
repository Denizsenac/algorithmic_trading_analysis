import asyncio
from data_fetcher import MarketDataFetcher
from news_fetcher import NewsFetcher
from data_processor import DataProcessor
from ticker_search import TickerSearch
from strategy_engine import StrategyEngine
from Backtester import Backtester
from predictor import PricePredictor
from visualizer import MarketVisualizer

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

   # ... (Backtest kodlarından sonrası) ...
    # Makine Öğrenmesi (Gelecek Fiyat Tahmini)
    print(f"\n--- MACHINE LEARNING PREDICTION FOR {target_ticker} ---")
    ai_predictor = PricePredictor(strategy_results)
    predicted_price, next_day_name = ai_predictor.train_and_predict()

    last_actual_price = strategy_results.iloc[-1]['Close']
    price_difference = predicted_price - last_actual_price
    percentage_change = (price_difference / last_actual_price) * 100

    # 1. ÖNCE GEÇMİŞİ SORGULA VE KARŞILAŞTIR
    ai_predictor.evaluate_past_predictions(target_ticker, last_actual_price)

    # 2. SONRA YARININ TAHMİNİNİ GÖSTER
    print(f"\nToday's Actual Close Price   : ${last_actual_price:,.2f}")
    print(f"{next_day_name}'s Predicted Price : ${predicted_price:,.2f}")

    if price_difference > 0:
        print(f"Prediction Trend             : 📈 UP by {percentage_change:.2f}%")
    else:
        print(f"Prediction Trend             : 📉 DOWN by {percentage_change:.2f}%")
        
    # 3. YENİ TAHMİNİ JSON'A KAYDET
    # Not: "next_day_name" yerine, bir sonraki iş gününün GERÇEK TARİHİNİ kaydetmeliyiz ki
    # evaluate_past_predictions fonksiyonu günleri eşleştirebilsin.
    from datetime import datetime, timedelta
    
    # Eğer bugün Cuma ise 3 gün ekle (Pazartesi), değilse 1 gün ekle
    days_to_add = 3 if datetime.today().weekday() == 4 else 1
    target_date_obj = datetime.today() + timedelta(days=days_to_add)
    target_date_str = target_date_obj.strftime('%Y-%m-%d')
    
    ai_predictor.save_prediction(target_ticker, predicted_price, target_date_str, last_actual_price)

    # 4. GÖRSEL ŞÖLEN (VISUALIZER) BAŞLIYOR
    print(f"\n[{target_ticker}] İnteraktif analiz grafiği tarayıcıda açılıyor...")
    
    # Görselleştiriciyi başlat
    viz = MarketVisualizer(target_ticker)
    
    # Mumları ve Sinyalleri Çiz
    viz.create_candlestick_chart(strategy_results)
    viz.add_trading_signals(strategy_results)
    
    # Yapay Zeka Tahmin Çizgisini Ekle (Bugünden hedeflenen tarihe kadar)
    last_actual_date = strategy_results.index[-1].strftime('%Y-%m-%d')
    viz.add_ml_prediction(target_date_str, predicted_price, last_actual_date, last_actual_price)
    
    # Grafiği Ekranda Göster
    viz.display_chart()

if __name__ == "__main__":
    asyncio.run(main())

    