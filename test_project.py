import unittest
import pandas as pd
import numpy as np
from data_processor import DataProcessor
from strategy_engine import StrategyEngine
from Backtester import Backtester
from predictor import PricePredictor

class TestTradingProject(unittest.TestCase):
    def setUp(self):
        # 40 günlük sentetik borsa verisi
        dates = pd.date_range(start="2026-01-01", periods=40, freq="B")
        np.random.seed(42)
        base_price = 100.0
        returns = np.random.normal(0.001, 0.02, size=len(dates))
        prices = base_price * np.cumprod(1 + returns)
        
        self.mock_df = pd.DataFrame({
            'Open': prices * 0.99,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': np.random.randint(10000, 50000, size=len(dates))
        }, index=dates)

        self.mock_news = pd.DataFrame({
            'Title': ['Test Positive News Headline', 'Test Negative News Headline'],
            'Publisher': ['Test Provider', 'Test Provider'],
            'Date': [dates[-2], dates[-5]],
            'Link': ['http://test.com', 'http://test.com']
        })

    def test_data_processor(self):
        dp = DataProcessor(self.mock_df, self.mock_news)
        merged = dp.merge_data()
        self.assertIn('Sentiment_Score', merged.columns)
        self.assertEqual(len(merged), len(self.mock_df))

        with_indicators = dp.calculate_indicators(merged)
        self.assertIn('SMA_20', with_indicators.columns)
        self.assertIn('RSI_14', with_indicators.columns)
        self.assertIn('ATR_14', with_indicators.columns)
        self.assertIn('EMA_9', with_indicators.columns)
        self.assertIn('EMA_21', with_indicators.columns)
        self.assertFalse(with_indicators.empty)

    def test_strategy_engine(self):
        dp = DataProcessor(self.mock_df, self.mock_news)
        data = dp.calculate_indicators(dp.merge_data())
        engine = StrategyEngine(data)
        signals = engine.generate_signals()
        self.assertIn('Action', signals.columns)
        self.assertTrue(set(signals['Action'].unique()).issubset({'BUY', 'SELL', 'HOLD'}))

    def test_backtester(self):
        dp = DataProcessor(self.mock_df, self.mock_news)
        data = dp.calculate_indicators(dp.merge_data())
        engine = StrategyEngine(data)
        signals = engine.generate_signals()

        backtester = Backtester(signals, initial_balance=10000.0, use_trailing_stop=True)
        final_val, roi = backtester.run_simulation()
        self.assertIsInstance(final_val, float)
        self.assertIsInstance(roi, float)
        self.assertIn('Win_Rate', backtester.metrics)

    def test_predictor(self):
        dp = DataProcessor(self.mock_df, self.mock_news)
        data = dp.calculate_indicators(dp.merge_data())
        predictor = PricePredictor(data)
        pred_price, target_date = predictor.train_and_predict()
        self.assertGreater(pred_price, 0)
        self.assertIsNotNone(target_date)

if __name__ == '__main__':
    unittest.main()
