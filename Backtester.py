class Backtester:
    def __init__(self, data, initial_balance=10000.0):
        self.data = data.copy()
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0  # Elimizdeki hisse adedi

    def run_simulation(self):
        print(f"Starting historical backtest with ${self.initial_balance:,.2f} virtual balance...\n")
        
        for index, row in self.data.iterrows():
            price = row['Close']
            action = row['Action']
            
            # ALIM DURUMU: "BUY" sinyali gelmişse ve paramız hisse almaya yetiyorsa
            if action == 'BUY' and self.balance >= price:
                shares_to_buy = int(self.balance // price) # Alabileceğimiz maksimum hisse adedi
                self.position += shares_to_buy
                self.balance -= shares_to_buy * price
                
            # SATIM DURUMU: "SELL" sinyali gelmişse ve elimizde hisse varsa
            elif action == 'SELL' and self.position > 0:
                self.balance += self.position * price # Hisseleri o günkü fiyattan nakde çevir
                self.position = 0
                
        # Simülasyon bittiğinde elde kalan hisselerin güncel değeri + cepteki nakit para
        final_portfolio_value = self.balance + (self.position * self.data.iloc[-1]['Close'])
        profit_loss_percentage = ((final_portfolio_value - self.initial_balance) / self.initial_balance) * 100
        
        return final_portfolio_value, profit_loss_percentage