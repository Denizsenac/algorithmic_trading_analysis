import asyncio
import ssl
import certifi
import yfinance as yf


def ensure_ssl_certs():
    """Windows üzerinde kurumsal/antivirüs (örn. Avast) SSL kök sertifikalarını

    certifi paketine ekleyerek SSL doğrulama hatalarını önler.
    """
    try:
        ctx = ssl.create_default_context()
        der_certs = ctx.get_ca_certs(binary_form=True)
        if der_certs:
            ca_path = certifi.where()
            with open(ca_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            missing = []
            for d in der_certs:
                pem = ssl.DER_cert_to_PEM_cert(d)
                if pem not in content:
                    missing.append(pem)
            if missing:
                with open(ca_path, 'a', encoding='utf-8') as f:
                    f.write('\n# System CA Certificates\n' + '\n'.join(missing))
    except Exception:
        pass


class MarketDataFetcher:
    def __init__(self, ticker_symbol):
        ensure_ssl_certs()
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
