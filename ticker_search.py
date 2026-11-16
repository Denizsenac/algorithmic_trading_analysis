import re
import requests
from data_fetcher import ensure_ssl_certs


class TickerSearch:
    SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"

    def __init__(self):
        ensure_ssl_certs()
        # API'nin bizi bot olarak engelleyip reddetmemesi için tarayıcı gibi davranıyoruz
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    def search_company(self, company_name, interactive=True):
        raw_input = company_name.strip()
        print(f"\n'{raw_input}' için borsalarda arama yapılıyor...")

        # Basit sembol deseni kontrolü (örn: AAPL, MSFT, THYAO.IS)
        looks_like_ticker = bool(re.match(r'^[A-Za-z0-9\.\-\=]{1,12}$', raw_input))

        try:
            response = requests.get(
                self.SEARCH_URL,
                params={"q": raw_input},  # özel karakterleri requests kendisi kodlar
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as e:
            print("Arama servisi sırasında bir hata oluştu:", e)
            if looks_like_ticker:
                print(f"Uyarı: Arama servisi yanıt vermedi; '{raw_input.upper()}' doğrudan sembol olarak kullanılacak.\n")
                return raw_input.upper()
            return None

        quotes = data.get('quotes', [])

        # Sadece hisse senetlerini (EQUITY) alıp ilk 5 sonucu gösteriyoruz
        valid_quotes = [q for q in quotes if q.get('quoteType') == 'EQUITY'][:5]

        # Liste boşsa ve girdi sembol formatındaysa doğrudan kullan
        if not valid_quotes:
            if looks_like_ticker:
                print(f"Eşleşme listelenemedi ancak '{raw_input.upper()}' sembolü doğrudan deneniyor.\n")
                return raw_input.upper()
            print("Eşleşen bir hisse senedi bulunamadı. Lütfen farklı bir isim deneyin.")
            return None

        # 1. Tam sembol eşleşmesi varsa (örn. kullanıcı zaten 'AAPL' veya 'THYAO.IS' yazdıysa)
        # kullanıcıyı tekrar soruyla bekletmeden doğrudan seç
        exact_matches = [q for q in valid_quotes if q.get('symbol', '').upper() == raw_input.upper()]
        if exact_matches:
            selected_ticker = exact_matches[0]['symbol']
            print(f"Tam sembol eşleşmesi bulundu: {selected_ticker} ({exact_matches[0].get('shortname', '')})\n")
            return selected_ticker

        # 2. Tek bir sonuç varsa doğrudan seç
        if len(valid_quotes) == 1 or not interactive:
            selected_ticker = valid_quotes[0]['symbol']
            print(f"Seçilen Hisse: {selected_ticker} ({valid_quotes[0].get('shortname', '')})\n")
            return selected_ticker

        print("\n--- ARAMA SONUÇLARI ---")
        for i, quote in enumerate(valid_quotes):
            symbol = quote.get('symbol', 'Bilinmiyor')
            name = quote.get('shortname', 'Bilinmiyor')
            exchange = quote.get('exchDisp', 'Bilinmiyor')
            print(f"[{i+1}] Sembol: {symbol: <10} | Şirket: {name} | Borsa: {exchange}")

        while True:
            try:
                choice = input(
                    f"\nAnaliz etmek istediğiniz hissenin numarasını girin (1-{len(valid_quotes)}, iptal için q): "
                ).strip().lower()
            except EOFError:
                # İnteraktif olmayan bir ortamda EOF gelirse varsayılan olarak ilkini seç
                return valid_quotes[0]['symbol']

            if choice == 'q':
                return None
            if choice.isdigit() and 1 <= int(choice) <= len(valid_quotes):
                selected_ticker = valid_quotes[int(choice) - 1]['symbol']
                print(f"Seçilen Hisse: {selected_ticker}\n")
                return selected_ticker
            print("Geçersiz seçim, lütfen listedeki numaralardan birini girin.")
