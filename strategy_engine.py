import pandas as pd
import numpy as np

class StrategyEngine:
    def __init__(self, df):
        self.df = df.copy() # Orijinal veriyi bozmamak için kopyasını alıyoruz

    def generate_signals(self):
        print("Generating hybrid trading signals (Technical + Sentiment)...\n")
        
        # Sinyalleri tutacak yeni bir sütun oluşturuyoruz (0: Bekle, 1: Al, -1: Sat)
        self.df['Signal'] = 0
        
        # --- HİBRİT ALIM SİNYALİ (BUY) ---
        # 1. RSI 40'ın altındaysa (Biraz düşmüşse) VEYA Fiyat SMA_20'nin üzerindeyse
        # 2. VE O günkü haberlerin genel duyarlılık skoru pozitifse (Sentiment_Score > 0.05)
        buy_condition = (
            ((self.df['RSI_14'] < 40) | (self.df['Close'] > self.df['SMA_20'])) & 
            (self.df['Sentiment_Score'] > 0.05)
        )
        self.df.loc[buy_condition, 'Signal'] = 1
        
        # --- HİBRİT SATIM SİNYALİ (SELL) ---
        # 1. RSI 60'ın üzerindeyse (Şişmişse) VEYA Fiyat SMA_20'nin altındaysa
        # 2. VE O günkü haberlerin genel duyarlılık skoru negatifse (Sentiment_Score < -0.05)
        sell_condition = (
            ((self.df['RSI_14'] > 60) | (self.df['Close'] < self.df['SMA_20'])) & 
            (self.df['Sentiment_Score'] < -0.05)
        )
        self.df.loc[sell_condition, 'Signal'] = -1
        
        # Alım-satım noktalarını daha okunaklı metinlere çeviriyoruz
        self.df['Action'] = self.df['Signal'].map({1: 'BUY', -1: 'SELL', 0: 'HOLD'})
        
        return self.df