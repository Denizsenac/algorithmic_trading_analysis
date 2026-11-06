import requests


class TickerSearch:
    SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"

    def __init__(self):
        # API'nin bizi bot olarak engelleyip reddetmemesi için tarayıcı gibi davranıyoruz
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    def search_company(self, company_name):
        print(f"\n'{company_name}' için borsalarda arama yapılıyor...")

        try:
            response = requests.get(
                self.SEARCH_URL,
                params={"q": company_name},  # özel karakterleri requests kendisi kodlar
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as e:
            print("Arama sırasında bir hata oluştu:", e)
            return None

        quotes = data.get('quotes', [])

        # Sadece hisse senetlerini (EQUITY) alıp ilk 5 sonucu gösteriyoruz
        valid_quotes = [q for q in quotes if q.get('quoteType') == 'EQUITY'][:5]

        # Liste boşsa seçim döngüsüne hiç girmiyoruz (eski kodda sonsuz döngü oluyordu)
        if not valid_quotes:
            print("Eşleşen bir hisse senedi bulunamadı. Lütfen farklı bir isim deneyin.")
            return None

        print("\n--- ARAMA SONUÇLARI ---")
        for i, quote in enumerate(valid_quotes):
            symbol = quote.get('symbol', 'Bilinmiyor')
            name = quote.get('shortname', 'Bilinmiyor')
            exchange = quote.get('exchDisp', 'Bilinmiyor')
            print(f"[{i+1}] Sembol: {symbol: <10} | Şirket: {name} | Borsa: {exchange}")

        while True:
            choice = input(
                f"\nAnaliz etmek istediğiniz hissenin numarasını girin (1-{len(valid_quotes)}, iptal için q): "
            ).strip().lower()

            if choice == 'q':
                return None
            if choice.isdigit() and 1 <= int(choice) <= len(valid_quotes):
                selected_ticker = valid_quotes[int(choice) - 1]['symbol']
                print(f"Seçilen Hisse: {selected_ticker}\n")
                return selected_ticker
            print("Geçersiz seçim, lütfen listedeki numaralardan birini girin.")