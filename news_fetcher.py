import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
import pandas as pd
import requests
import yfinance as yf
from data_fetcher import ensure_ssl_certs

NEWS_COLUMNS = ["Title", "Publisher", "Date", "Link"]


class NewsFetcher:
    def __init__(self, ticker_symbol, demo=False):
        ensure_ssl_certs()
        self.ticker_symbol = ticker_symbol.upper()
        self.demo = demo  # True ise gerçek haber yerine SAHTE test haberleri üretilir
        self.is_turkish = self.ticker_symbol.endswith(".IS")
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

    def _fetch_google_news_rss(self):
        """Yahoo Finance çöktüğünde veya haber bulamadığında Google News RSS akışından

        haber çeken güvenilir yedek (fallback) fonksiyon.
        """
        # Arama terimi: THYAO.IS ise 'THYAO hisse', AAPL ise 'AAPL stock'
        clean_symbol = self.ticker_symbol.replace(".IS", "")
        if self.is_turkish:
            query = f"{clean_symbol} hisse"
            hl = 'tr'
            gl = 'TR'
            ceid = 'TR:tr'
        else:
            query = f"{clean_symbol} stock"
            hl = 'en-US'
            gl = 'US'
            ceid = 'US:en'

        url = f"https://news.google.com/rss/search?q={query}&hl={hl}&gl={gl}&ceid={ceid}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            items = []
            for item in root.findall('.//item')[:20]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_elem = item.find('pubDate')
                src_elem = item.find('source')

                title = title_elem.text if title_elem is not None else ""
                link = link_elem.text if link_elem is not None else ""
                publisher = src_elem.text if src_elem is not None else "Google News"

                if not title:
                    continue

                try:
                    dt = parsedate_to_datetime(pub_elem.text) if pub_elem is not None else pd.Timestamp.now(tz="UTC")
                except Exception:
                    dt = pd.Timestamp.now(tz="UTC")

                items.append({
                    "Title": title,
                    "Publisher": publisher,
                    "Date": dt,
                    "Link": link
                })

            if items:
                print(f"[{self.ticker_symbol}] Google News RSS yedek kaynağından {len(items)} güncel haber çekildi.\n")
                return pd.DataFrame(items, columns=NEWS_COLUMNS)
        except Exception as e:
            print(f"Uyarı: Google News RSS yedek kaynağı da yanıt vermedi ({e}).")

        return pd.DataFrame(columns=NEWS_COLUMNS)

    def fetch_news(self):
        print(f"[{self.ticker_symbol}] haberler çekiliyor...\n")

        if self.demo:
            print("⚠️  DEMO MODU: Haberler SAHTEDİR. Sonuçlar gerçek analiz değildir!\n")
            return self._demo_news()

        # 1. Öncelikli Kaynak: Yahoo Finance
        parsed_news = []
        try:
            raw_news = self.ticker.news or []
            for article in raw_news:
                parsed = self._parse_article(article)
                if parsed:
                    parsed_news.append(parsed)
        except Exception as e:
            print(f"Uyarı: Yahoo Finance haber servisi kullanılamıyor ({e}).")

        # 2. Yedek Kaynak (Fallback): Yahoo boşsa veya çöktüyse Google News RSS devreye girer
        if not parsed_news:
            print(f"[{self.ticker_symbol}] Yahoo Finance'de haber bulunamadı. Google News RSS yedek kaynağına geçiliyor...")
            return self._fetch_google_news_rss()

        return pd.DataFrame(parsed_news, columns=NEWS_COLUMNS)
