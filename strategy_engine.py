import pandas as pd
import numpy as np


class StrategyEngine:
    def __init__(self, df):
        self.df = df.copy()  # Orijinal veriyi bozmamak için kopyasını alıyoruz

    def generate_signals(self):
        print("Generating hybrid trading signals (Technical + Sentiment)...\n")
        
        # Sinyalleri tutacak sütun: 0: Bekle (HOLD), 1: Al (BUY), -1: Sat (SELL)
        self.df['Signal'] = 0
        
        # 1. Testere Piyasasını Önleyen Çift Teyitli Trend Analizi:
        # Tek bir günlük fiyat gürültüsü yerine EMA_9 ve EMA_21 kesişimi + SMA_20 birlikte bakılır
        ema_9 = self.df.get('EMA_9', self.df['Close'])
        ema_21 = self.df.get('EMA_21', self.df['SMA_20'])
        
        uptrend = (self.df['Close'] > self.df['SMA_20']) & (ema_9 >= ema_21)
        downtrend = (self.df['Close'] < self.df['SMA_20']) & (ema_9 <= ema_21)

        # 2. Momentum Filtreleri:
        healthy_momentum = (self.df['RSI_14'] >= 42) & (self.df['RSI_14'] <= 72)
        oversold_bounce = self.df['RSI_14'] < 32
        overbought_exhaustion = self.df['RSI_14'] > 78

        # Teknik Alım ve Satım:
        tech_buy = (uptrend & healthy_momentum) | oversold_bounce
        tech_sell = downtrend | overbought_exhaustion

        # 3. Duygu (Sentiment) Katmanı:
        # Haber varsa pozitif duygu alımı destekler, negatif duygu kesin satış üretir ve alımı kilitler.
        sentiment_positive = self.df['Sentiment_Score'] > 0.05
        sentiment_negative = self.df['Sentiment_Score'] < -0.05

        # Nihai Hibrit Karar:
        buy_condition = (tech_buy | sentiment_positive) & (~sentiment_negative)
        sell_condition = tech_sell | sentiment_negative

        self.df.loc[buy_condition, 'Signal'] = 1
        self.df.loc[sell_condition, 'Signal'] = -1
        
        # Alım-satım noktalarını okunaklı metinlere çeviriyoruz
        self.df['Action'] = self.df['Signal'].map({1: 'BUY', -1: 'SELL', 0: 'HOLD'})
        
        return self.df

