import yfinance as yf
import pandas as pd

class MarketDataFetcher: 
    def __init__(self, ticker_symbol): 
       
        self.ticker_symbol = ticker_symbol.upper()
        
       
        if self.ticker_symbol.endswith(".IS"):
            self.market = "Local"
        else:
            self.market = "Global"
            
       
        self.ticker = yf.Ticker(self.ticker_symbol)

    def fetch_data(self, interval="1mo"):
       
        print(f"[{self.ticker_symbol}] ({self.market}) borsa verisi çekiliyor...\n")
        
        # Hafızadaki motoru çalıştırıp veriyi alıyoruz
        historical_data = self.ticker.history(interval=interval)
        return historical_data