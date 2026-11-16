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
    parser.add_argument("--period", default="1y",
                        help="Fiyat verisi periyodu (varsayılan: 1y, en az 1 yıllık veri önerilir)")
    parser.add_argument("--demo", action="store_true",
                        help="Gerçek haber yerine SAHTE örnek haberlerle çalış (sadece test için)")
    parser.add_argument("--no-chart", action="store_true",
                        help="Tarayıcıda grafik açmayı atla (sadece terminal analizi ve dosya kaydı)")
    return parser.parse_args()


async def main():
    args = parse_args()

    search_engine = TickerSearch()
    company_input = args.company or input(
        "Enter the name or ticker symbol of the company you want to analyze (e.g., Apple or THYAO.IS): "
    )
    # CLI argümanı verilmişse kullanıcıyı bekletmeden sembolü doğrulamaya çalış
    target_ticker = search_engine.search_company(company_input, interactive=(args.company is None))

    if not target_ticker:
        print("the transaction was canceled")
        return

    if args.demo:
        print("\n" + "=" * 60)
        print("⚠️  DEMO MODU AKTİF: Haberler sahte. Tahmin log'a KAYDEDİLMEYECEK.")
        print("=" * 60)

    # Fiyat ve haber çekimi paralel çalışır
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

    # Verileri Birleştir ve İndikatörleri Hesapla
    processor = DataProcessor(price_data=price_df, news_data=news_df)
    raw_merged = processor.merge_data()
    final_dataset = processor.calculate_indicators(raw_merged)

    if final_dataset.empty:
        print("İndikatörler için yeterli veri yok (en az ~20 işlem günü gerekir). "
              "Daha uzun bir --period deneyin.")
        return

    print(f"\n--- FINAL MERGED DATASET FOR {target_ticker} ---")
    display_cols = [c for c in ['Close', 'SMA_20', 'RSI_14', 'Sentiment_Score', 'Title'] if c in final_dataset.columns]
    print(final_dataset[display_cols].tail(10))

    # Sinyal Üretimi
    engine = StrategyEngine(final_dataset)
    strategy_results = engine.generate_signals()

    print(f"\n--- STRATEGY RESULTS FOR {target_ticker} ---")
    print(strategy_results[['Close', 'RSI_14', 'Sentiment_Score', 'Action']].tail(15))

    # Backtest (Geçmiş Performans Simülasyonu)
    user_budget = 10000.0
    simulator = Backtester(strategy_results, initial_balance=user_budget)
    final_value, roi = simulator.run_simulation()
    metrics = simulator.metrics

    print(f"\n--- BACKTEST RESULTS FOR {target_ticker} ---")
    print(f"Initial Investment : ${user_budget:,.2f}")
    print(f"Final Portfolio    : ${final_value:,.2f}")
    print(f"Strategy Net Profit: {roi:+.2f}%")
    print(f"Benchmark (B&H)    : {metrics.get('Benchmark_ROI', 0.0):+.2f}%")
    print(f"Total / Closed Tr. : {metrics.get('Total_Trades', 0)} / {metrics.get('Closed_Trades', 0)}")
    print(f"Trade Win Rate     : {metrics.get('Win_Rate', 0.0):.1f}%")
    print(f"Max Drawdown       : {metrics.get('Max_Drawdown', 0.0):.2f}%")

    # Makine Öğrenmesi (Gelecek Fiyat Tahmini)
    print(f"\n--- MACHINE LEARNING PREDICTION FOR {target_ticker} ---")
    ai_predictor = PricePredictor(strategy_results)
    predicted_price, target_date = ai_predictor.train_and_predict()

    last_actual_date = strategy_results.index[-1]
    last_actual_price = strategy_results.iloc[-1]['Close']
    price_difference = predicted_price - last_actual_price
    percentage_change = (price_difference / last_actual_price) * 100

    target_date_str = target_date.strftime('%Y-%m-%d')
    last_actual_date_str = last_actual_date.strftime('%Y-%m-%d')

    # 1. ÖNCE GEÇMİŞİ SORGULA: hedef günün GERÇEK kapanışıyla ve yön doğruluğuyla karşılaştırılır
    ai_predictor.evaluate_past_predictions(target_ticker, strategy_results)

    # Model Öznitelik Ağırlıkları (Feature Coefficients)
    if ai_predictor.feature_importance:
        print("\nModel Öznitelik Katkıları (Features Coefficients on Expected Return):")
        for feat, coef in ai_predictor.feature_importance.items():
            print(f"  • {feat:16}: {coef:+.5f}")

    # 2. SONRA SIRADAKİ TAHMİNİ GÖSTER
    print(f"\nLast Actual Close ({last_actual_date_str}) : ${last_actual_price:,.2f}")
    print(f"Predicted Close ({target_date.strftime('%A %Y-%m-%d')}) : ${predicted_price:,.2f}")

    if price_difference > 0:
        print(f"Prediction Trend             : 📈 UP by {percentage_change:+.2f}%")
    else:
        print(f"Prediction Trend             : 📉 DOWN by {percentage_change:+.2f}%")

    # 3. YENİ TAHMİNİ KAYDET ((Ticker, Target_Date) için upsert; demo modunda kaydedilmez)
    if not args.demo:
        ai_predictor.save_prediction(
            target_ticker, predicted_price, target_date_str,
            last_actual_price, prediction_date_str=last_actual_date_str,
        )

    # 4. GÖRSELLEŞTİRME
    viz = MarketVisualizer(target_ticker)
    viz.create_candlestick_chart(strategy_results)
    viz.add_trading_signals(strategy_results)
    viz.add_ml_prediction(target_date_str, predicted_price, last_actual_date_str, last_actual_price)
    
    if not args.no_chart:
        print(f"\n[{target_ticker}] İnteraktif analiz grafiği hazırlanıyor...")
        viz.display_chart(show_browser=True, save_html=True)
    else:
        viz.display_chart(show_browser=False, save_html=True)



if __name__ == "__main__":
    asyncio.run(main())