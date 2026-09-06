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

    def fetch_data(self, period="3mo"): # İndikatörler için süreyi biraz uzatıyoruz
        print(f"[{self.ticker_symbol}] ({self.market}) fetching market data...\n")
        
        historical_data = self.ticker.history(period=period)
        
        target_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        historical_data = historical_data[target_columns]
        
        # --- FEATURE ENGINEERING ---
        historical_data['SMA_20'] = historical_data['Close'].rolling(window=20).mean()
        historical_data['EMA_20'] = historical_data['Close'].ewm(span=20, adjust=False).mean()
        
        delta = historical_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        historical_data['RSI_14'] = 100 - (100 / (1 + rs))
        
        historical_data.dropna(inplace=True)
        return historical_data
        