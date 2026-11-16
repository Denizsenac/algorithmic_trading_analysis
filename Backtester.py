import pandas as pd
import numpy as np


class Backtester:
    def __init__(self, data, initial_balance=10000.0, commission_fee_pct=0.0005,
                 use_trailing_stop=True, atr_multiplier=2.5):
        self.data = data.copy()
        self.initial_balance = float(initial_balance)
        self.commission_fee_pct = commission_fee_pct
        self.use_trailing_stop = use_trailing_stop
        self.atr_multiplier = atr_multiplier
        self.balance = float(initial_balance)
        self.position = 0  # Elimizdeki hisse adedi
        self.trade_history = []
        self.metrics = {}

    def run_simulation(self):
        print(f"Starting historical backtest with ${self.initial_balance:,.2f} virtual balance (Trailing Stop: {'ON' if self.use_trailing_stop else 'OFF'})...\n")
        
        balance = self.initial_balance
        position = 0
        entry_price = 0.0
        highest_price = 0.0
        equity_curve = []
        closed_trades = []

        for date, row in self.data.iterrows():
            price = float(row['Close'])
            atr = float(row.get('ATR_14', price * 0.02))
            action = row.get('Action', 'HOLD')

            # Trailing Stop & Dinamik Risk Kontrolü:
            is_stop_triggered = False
            if position > 0 and self.use_trailing_stop:
                highest_price = max(highest_price, price)
                # Başlangıç stopu girişin 2.0 ATR altı, takip eden kâr koruma stopu görülen zirvenin atr_multiplier ATR altı
                stop_level = max(entry_price - (2.0 * atr), highest_price - (self.atr_multiplier * atr))
                if price <= stop_level:
                    is_stop_triggered = True

            # SATIM DURUMU: "SELL" sinyali VEYA Trailing Stop tetiklenmesi
            if (action == 'SELL' or is_stop_triggered) and position > 0:
                effective_price = price * (1.0 - self.commission_fee_pct)
                revenue = position * effective_price
                pnl = revenue - (position * entry_price)
                pnl_pct = ((price - entry_price) / entry_price) * 100.0
                balance += revenue
                exit_reason = "TRAILING_STOP" if is_stop_triggered else "SIGNAL_SELL"
                trade_info = {
                    'Date': date, 'Type': 'SELL', 'Price': price, 'Shares': position,
                    'PnL': pnl, 'PnL_Pct': pnl_pct, 'Reason': exit_reason
                }
                self.trade_history.append(trade_info)
                closed_trades.append(trade_info)
                position = 0

            # ALIM DURUMU: "BUY" sinyali ve henüz pozisyonda değilsek (whipsaw / mükerrer alım engeli)
            elif action == 'BUY' and position == 0 and balance >= price:
                effective_price = price * (1.0 + self.commission_fee_pct)
                shares_to_buy = int(balance // effective_price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * effective_price
                    balance -= cost
                    position += shares_to_buy
                    entry_price = price
                    highest_price = price
                    self.trade_history.append({
                        'Date': date, 'Type': 'BUY', 'Price': price, 'Shares': shares_to_buy
                    })

            # Günlük portföy değeri
            current_portfolio_value = balance + (position * price)
            equity_curve.append(current_portfolio_value)

                
        # Simülasyon sonu portföy değeri
        last_price = float(self.data.iloc[-1]['Close'])
        final_portfolio_value = balance + (position * last_price)
        profit_loss_percentage = ((final_portfolio_value - self.initial_balance) / self.initial_balance) * 100.0

        # Benchmark: Buy & Hold (Al ve Tut) Getirisi
        first_price = float(self.data.iloc[0]['Close'])
        benchmark_roi = ((last_price - first_price) / first_price) * 100.0

        # Maksimum Düşüş (Max Drawdown)
        eq_series = pd.Series(equity_curve)
        peak = eq_series.cummax()
        drawdown = (eq_series - peak) / peak.replace(0, np.nan) * 100.0
        max_drawdown = float(drawdown.min()) if not drawdown.empty else 0.0

        # Kazanma Oranı (Win Rate)
        winning_trades = [t for t in closed_trades if t['PnL'] > 0]
        win_rate = (len(winning_trades) / len(closed_trades) * 100.0) if closed_trades else 0.0

        self.metrics = {
            'Initial_Balance': self.initial_balance,
            'Final_Portfolio': final_portfolio_value,
            'Strategy_ROI': profit_loss_percentage,
            'Benchmark_ROI': benchmark_roi,
            'Total_Trades': len(self.trade_history),
            'Closed_Trades': len(closed_trades),
            'Win_Rate': win_rate,
            'Max_Drawdown': max_drawdown
        }
        
        return final_portfolio_value, profit_loss_percentage
