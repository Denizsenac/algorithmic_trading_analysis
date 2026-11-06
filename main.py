import argparse
import asyncio

from data_fetcher import MarketDataFetcher
from news_fetcher import NewsFetcher
from data_processor import DataProcessor
from ticker_search import TickerSearch
from strategy_engine import StrategyEngine
from Backtester import Backtester
from predictor import PricePredictor
from visualizer import MarketVisualizer


def parse_args():
    parser = argparse.ArgumentParser(description="Borsa analiz aracı")
    parser.add_argument("company", nargs="?",
                        help="Şirket adı veya sembol (örn: Apple, THYAO.IS). Verilmezse sorulur.")
    parser.add_argument("--period", default="6mo",
                        help="Fiyat verisi periyodu (varsayılan: 6mo)")
    parser.add_argument("--demo", action="store_true",
                        help="Gerçek haber yerine SAHTE örnek haberlerle çalış (sadece test için)")
    return parser.parse_args()


async def main():
    args = parse_args()

    search_engine = TickerSearch()
    company_input = args.company or input(
        "Enter the name or ticker symbol of the company you want to analyze (e.g., Apple or THYAO.IS): "
    )
    target_ticker = search_engine.search_company(company_input)

    if not target_ticker:
        print("the transaction was canceled")
        return

    if args.demo:
        print("\n" + "=" * 60)
        print("⚠️  DEMO MODU AKTİF: Haberler sahte. Tahmin log'a KAYDEDİLMEYECEK.")
        print("=" * 60)

    # Fiyat ve haber çekimi GERÇEKTEN paralel çalışır
    market = MarketDataFetcher(target_ticker)
    news = NewsFetcher(target_ticker, demo=args.demo)
    price_df, news_df = await asyncio.gather(
        market.fetch_data(period=args.period),
        asyncio.to_thread(news.fetch_news),  # fetch_news senkron, ayrı thread'de çalışır
    )

    if price_df.empty:
        print(f"[{target_ticker}] için fiyat verisi alınamadı. Sembolü kontrol edin.")
        return

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

    # İndikatörlerin yarattığı boş (NaN) günleri siliyoruz ki model çökmesin.
    final_dataset = final_dataset.dropna()

    if final_dataset.empty:
        print("İndikatörler için yeterli veri yok (en az ~20 işlem günü gerekir). "
              "Daha uzun bir --period deneyin.")
        return

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
    predicted_price, target_date = ai_predictor.train_and_predict()

    last_actual_date = strategy_results.index[-1]
    last_actual_price = strategy_results.iloc[-1]['Close']
    price_difference = predicted_price - last_actual_price
    percentage_change = (price_difference / last_actual_price) * 100

    # Hedef tarih verinin son gününden türetildi (bugünün haftanın hangi günü olduğundan bağımsız)
    target_date_str = target_date.strftime('%Y-%m-%d')
    last_actual_date_str = last_actual_date.strftime('%Y-%m-%d')

    # 1. ÖNCE GEÇMİŞİ SORGULA: hedef günün GERÇEK kapanışıyla karşılaştırılır
    ai_predictor.evaluate_past_predictions(target_ticker, strategy_results)

    # 2. SONRA SIRADAKİ TAHMİNİ GÖSTER
    print(f"\nLast Actual Close ({last_actual_date_str}) : ${last_actual_price:,.2f}")
    print(f"Predicted Close ({target_date.strftime('%A %Y-%m-%d')}) : ${predicted_price:,.2f}")

    if price_difference > 0:
        print(f"Prediction Trend             : 📈 UP by {percentage_change:.2f}%")
    else:
        print(f"Prediction Trend             : 📉 DOWN by {percentage_change:.2f}%")

    # 3. YENİ TAHMİNİ KAYDET ((Ticker, Target_Date) için upsert; demo modunda kaydedilmez)
    if not args.demo:
        ai_predictor.save_prediction(
            target_ticker, predicted_price, target_date_str,
            last_actual_price, prediction_date_str=last_actual_date_str,
        )

    # 4. GÖRSELLEŞTİRME
    print(f"\n[{target_ticker}] İnteraktif analiz grafiği tarayıcıda açılıyor...")

    viz = MarketVisualizer(target_ticker)
    viz.create_candlestick_chart(strategy_results)
    viz.add_trading_signals(strategy_results)
    viz.add_ml_prediction(target_date_str, predicted_price, last_actual_date_str, last_actual_price)
    viz.display_chart()


if __name__ == "__main__":
    asyncio.run(main())