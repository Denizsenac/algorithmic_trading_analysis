import asyncio

import yfinance as yf


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
        # history() senkron (bloklayıcı) bir çağrı; ayrı thread'de çalıştırarak
        # event loop'u bloklamıyoruz. (to_thread, get_running_loop kullanır.)
        historical_data = await asyncio.to_thread(self.ticker.history, period=period)
        return historical_data