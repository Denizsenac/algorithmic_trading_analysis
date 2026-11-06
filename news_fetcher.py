import pandas as pd
import yfinance as yf

NEWS_COLUMNS = ["Title", "Publisher", "Date", "Link"]


class NewsFetcher:
    def __init__(self, ticker_symbol, demo=False):
        self.ticker_symbol = ticker_symbol.upper()
        self.demo = demo  # True ise gerçek haber yerine SAHTE test haberleri üretilir
        self.ticker = yf.Ticker(self.ticker_symbol)

    @staticmethod
    def _parse_article(article):
        """Tek bir haberi standart sözlüğe çevirir.

        yfinance'in YENİ formatını (her şey 'content' altında iç içe) ve
        ESKİ formatını (düz alanlar) birlikte destekler. Başlığı ya da tarihi
        olmayan haberler için None döner.
        """
        content = article.get("content")

        if isinstance(content, dict):  # yeni format
            title = content.get("title")
            publisher = (content.get("provider") or {}).get("displayName")
            raw_date = content.get("pubDate") or content.get("displayTime")
            url_obj = content.get("canonicalUrl") or content.get("clickThroughUrl") or {}
            link = url_obj.get("url", "")
            date = pd.to_datetime(raw_date, utc=True, errors="coerce")
        else:  # eski format
            title = article.get("title")
            publisher = article.get("publisher")
            link = article.get("link", "")
            timestamp = article.get("providerPublishTime")
            if timestamp is None:
                date = pd.NaT
            else:
                date = pd.to_datetime(timestamp, unit="s", utc=True, errors="coerce")

        if not title or pd.isna(date):
            return None

        return {
            "Title": title,
            "Publisher": publisher or "Unknown",
            "Date": date,
            "Link": link,
        }

    def _demo_news(self):
        """SADECE test içindir. Gerçek analizde asla kullanılmaz."""
        now = pd.Timestamp.now(tz="UTC")
        publisher = "DEMO (sahte veri)"
        return pd.DataFrame(
            [
                {"Title": f"{self.ticker_symbol} reports record breaking earnings and positive outlook",
                 "Publisher": publisher, "Date": now - pd.Timedelta(days=3), "Link": ""},
                {"Title": f"Investors are worried about {self.ticker_symbol}'s recent supply chain issues and delays",
                 "Publisher": publisher, "Date": now - pd.Timedelta(days=4), "Link": ""},
                {"Title": f"{self.ticker_symbol} announces steady growth in quarterly review",
                 "Publisher": publisher, "Date": now - pd.Timedelta(days=5), "Link": ""},
            ],
            columns=NEWS_COLUMNS,
        )

    def fetch_news(self):
        print(f"[{self.ticker_symbol}] haberler çekiliyor...\n")

        if self.demo:
            print("⚠️  DEMO MODU: Haberler SAHTEDİR. Sonuçlar gerçek analiz değildir!\n")
            return self._demo_news()

        try:
            raw_news = self.ticker.news or []
        except Exception as e:
            print(f"Uyarı: Haberler alınamadı ({e}).")
            raw_news = []

        parsed_news = []
        for article in raw_news:
            parsed = self._parse_article(article)
            if parsed:
                parsed_news.append(parsed)

        if not parsed_news:
            # Sahte veri YOK: boş döner, DataProcessor bunu "No News" / skor 0 olarak işler.
            print("Uyarı: Bu hisse için kullanılabilir haber bulunamadı. "
                  "Duygu skoru 0 kabul edilecek. (Test için: --demo)\n")
            return pd.DataFrame(columns=NEWS_COLUMNS)

        return pd.DataFrame(parsed_news, columns=NEWS_COLUMNS)