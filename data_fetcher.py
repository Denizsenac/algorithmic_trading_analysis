import yfinance as yf
import pandas as pd
import asyncio

class MarketDataFetcher:
    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol.upper()
        if self.ticker_symbol.endswith(".IS"):
            self.market = "Local"
        else:
            self.market = "Global"
        self.ticker = yf.Ticker(self.ticker_symbol)

    async def fetch_data(self, period="1mo"):
        print(f"[{self.ticker_symbol}] ({self.market}) borsa verisi çekiliyor...\n")
        loop = asyncio.get_event_loop()
        historical_data = await loop.run_in_executor(None, self.ticker.history, period)
        return historical_data