import requests

class TickerSearch:
    def __init__(self):
        # API'nin bizi bot olarak engelleyip reddetmemesi için tarayıcı gibi davranıyoruz
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    def search_company(self, company_name):
        print(f"\n'{company_name}' için borsalarda arama yapılıyor...")
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}"
        
        try:
            response = requests.get(url, headers=self.headers)
            data = response.json()
            
            quotes = data.get('quotes', [])
            if not quotes:
                print("Eşleşen bir hisse bulunamadı. Lütfen farklı bir isim deneyin.")
                return None
                
            print("\n--- ARAMA SONUÇLARI ---")
            # Sadece hisse senetlerini (EQUITY) alıp ilk 5 sonucu gösteriyoruz
            valid_quotes = [q for q in quotes if q.get('quoteType') == 'EQUITY'][:5]
            
            for i, quote in enumerate(valid_quotes):
                symbol = quote.get('symbol', 'Bilinmiyor')
                name = quote.get('shortname', 'Bilinmiyor')
                exchange = quote.get('exchDisp', 'Bilinmiyor')
                print(f"[{i+1}] Sembol: {symbol: <10} | Şirket: {name} | Borsa: {exchange}")
                
            while True:
                choice = input("\nLütfen analiz etmek istediğiniz hissenin numarasını girin (1-5): ")
                if choice.isdigit() and 1 <= int(choice) <= len(valid_quotes):
                    selected_ticker = valid_quotes[int(choice)-1]['symbol']
                    print(f"Seçilen Hisse: {selected_ticker}\n")
                    return selected_ticker
                else:
                    print("Geçersiz seçim, lütfen listedeki numaralardan birini girin.")
                    
        except Exception as e:
            print("Arama sırasında bir hata oluştu:", e)
            return None