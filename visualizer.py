import plotly.graph_objects as go

class MarketVisualizer:
    def __init__(self, ticker):
        self.ticker = ticker
        self.fig = go.Figure()

    def create_candlestick_chart(self, df):
        # 1. Ana Fiyat Mumlarını (Candlestick) Çizdiriyoruz
        self.fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Market Price'
        ))
        
        # 2. 20 Günlük Hareketli Ortalamayı (SMA) Ekliyoruz
        if 'SMA_20' in df.columns:
            self.fig.add_trace(go.Scatter(
                x=df.index, 
                y=df['SMA_20'], 
                line=dict(color='blue', width=1.5), 
                name='SMA 20'
            ))

    def add_trading_signals(self, df):
        # 3. StrategyEngine'in ürettiği AL (BUY) ve SAT (SELL) Sinyallerini Ekliyoruz
        buy_signals = df[df['Action'] == 'BUY']
        sell_signals = df[df['Action'] == 'SELL']

        # Al (Yeşil Yukarı Ok)
        self.fig.add_trace(go.Scatter(
            x=buy_signals.index,
            y=buy_signals['Close'] * 0.99, # Fiyatın biraz altında görünsün
            mode='markers',
            marker=dict(symbol='triangle-up', color='green', size=12),
            name='BUY Signal'
        ))

        # Sat (Kırmızı Aşağı Ok)
        self.fig.add_trace(go.Scatter(
            x=sell_signals.index,
            y=sell_signals['Close'] * 1.01, # Fiyatın biraz üstünde görünsün
            mode='markers',
            marker=dict(symbol='triangle-down', color='red', size=12),
            name='SELL Signal'
        ))

    def add_ml_prediction(self, target_date_str, predicted_price, last_actual_date, last_actual_price):
        # 4. Yapay Zekanın Tahmin Eğrisini Çiziyoruz (Kesik Çizgi)
        self.fig.add_trace(go.Scatter(
            x=[last_actual_date, target_date_str],
            y=[last_actual_price, predicted_price],
            mode='lines+markers',
            line=dict(color='purple', width=2, dash='dash'),
            marker=dict(symbol='star', size=10),
            name='ML Prediction'
        ))

    def display_chart(self):
        # Grafiğin görsel temasını ayarlayıp tarayıcıda açıyoruz
        self.fig.update_layout(
            title=f"{self.ticker} - Algorithmic Trading Analysis & AI Prediction",
            yaxis_title="Price (USD)",
            xaxis_title="Date",
            template="plotly_dark", # Siyah profesyonel tema
            xaxis_rangeslider_visible=False
        )
        self.fig.show()