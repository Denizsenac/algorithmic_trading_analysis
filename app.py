import asyncio
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from data_fetcher import MarketDataFetcher
from news_fetcher import NewsFetcher
from data_processor import DataProcessor
from ticker_search import TickerSearch
from strategy_engine import StrategyEngine
from Backtester import Backtester
from predictor import PricePredictor
from visualizer import MarketVisualizer

# -----------------------------------------------------------------------------
# Sayfa Konfigürasyonu
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Algorithmic Trading & AI Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel CSS ile kart stilleri ve modern görünüm
st.markdown("""
<style>
    .metric-card {
        background-color: #1E222D;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2A2E39;
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #848E9C;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #EAECEF;
    }
    .badge-positive {
        background-color: rgba(14, 203, 129, 0.2);
        color: #0ECB81;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-negative {
        background-color: rgba(246, 70, 93, 0.2);
        color: #F6465D;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-neutral {
        background-color: rgba(132, 142, 156, 0.2);
        color: #848E9C;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Yan Panel (Sidebar) - Parametreler ve Arama
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Kontrol Paneli")
    st.caption("Algoritmik Ticaret & Yapay Zeka Terminali")
    st.divider()

    # Hızlı Seçim Butonları
    st.subheader("📌 Popüler Hisseler")
    quick_tickers = ["THYAO.IS", "ASELS.IS", "GARAN.IS", "AAPL", "NVDA", "TSLA"]
    cols = st.columns(3)
    selected_quick = None
    for i, t in enumerate(quick_tickers):
        with cols[i % 3]:
            if st.button(t, key=f"quick_{t}", use_container_width=True):
                st.session_state["target_input"] = t

    # Arama Girişi
    target_input = st.text_input(
        "Hisse Adı veya Sembol:",
        value=st.session_state.get("target_input", "THYAO.IS"),
        help="Örn: THYAO.IS, Apple, AAPL, ASELS.IS, MSFT"
    )

    # Parametreler
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        period = st.selectbox("Periyot:", options=["6mo", "1y", "2y", "5y"], index=1)
    with col_p2:
        budget = st.number_input("Bütçe ($/₺):", min_value=1000.0, value=10000.0, step=1000.0)

    st.subheader("🛡️ Risk Yönetimi (Stop-Loss)")
    use_trailing = st.checkbox("ATR Trailing Stop Aktif", value=True, help="Kârı korumak ve zararı kesmek için dinamik takip eden zarar durdur")
    atr_mult = st.slider("ATR Çarpanı:", min_value=1.5, max_value=4.0, value=2.5, step=0.1, help="Görülen zirveden kaç ATR düşüşte stoplanacağı")

    st.subheader("🧪 Test Modu")
    demo_mode = st.checkbox("Demo Modu (Sentetik Haberler)", value=False)

    st.divider()
    run_btn = st.button("🚀 Analizi Çalıştır", type="primary", use_container_width=True)


# -----------------------------------------------------------------------------
# Veri Çekme ve İşleme Fonksiyonu
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def load_and_process_data(ticker_symbol, selected_period, is_demo):
    # Paralel veri ve haber çekimi
    market = MarketDataFetcher(ticker_symbol)
    news = NewsFetcher(ticker_symbol, demo=is_demo)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        price_df, news_df = loop.run_until_complete(asyncio.gather(
            market.fetch_data(period=selected_period),
            asyncio.to_thread(news.fetch_news)
        ))
    finally:
        loop.close()

    if price_df.empty:
        return None, None, None

    # Verileri birleştir ve indikatörleri hesapla
    processor = DataProcessor(price_data=price_df, news_data=news_df)
    raw_merged = processor.merge_data()
    final_dataset = processor.calculate_indicators(raw_merged)

    return final_dataset, news_df, price_df


# -----------------------------------------------------------------------------
# Ana Sayfa Akışı
# -----------------------------------------------------------------------------
st.title("📊 Algoritmik Ticaret & Yapay Zeka Fiyat Tahmin Platformu")

if not target_input:
    st.info("Lütfen sol panelden bir hisse senedi sembolü veya şirket adı girerek 'Analizi Çalıştır' butonuna basın.")
    st.stop()

# Sembol Doğrulama
search_engine = TickerSearch()
target_ticker = search_engine.search_company(target_input, interactive=False)

if not target_ticker:
    st.error(f"'{target_input}' için borsa sembolü bulunamadı. Lütfen sembolü kontrol edin (Örn: THYAO.IS, AAPL).")
    st.stop()

# Veri Yükleme
with st.spinner(f"[{target_ticker}] için piyasa verileri, teknik indikatörler ve haberler analiz ediliyor..."):
    final_dataset, news_df, raw_prices = load_and_process_data(target_ticker, period, demo_mode)

if final_dataset is None or final_dataset.empty:
    st.error(f"[{target_ticker}] için yeterli fiyat verisi alınamadı. Sembolü kontrol edip periyodu uzatmayı deneyin.")
    st.stop()

# 1. Strateji Motoru
engine = StrategyEngine(final_dataset)
strategy_results = engine.generate_signals()

# 2. Backtest Simülatörü
simulator = Backtester(
    strategy_results,
    initial_balance=budget,
    use_trailing_stop=use_trailing,
    atr_multiplier=atr_mult
)
final_value, roi = simulator.run_simulation()
metrics = simulator.metrics

# 3. Yapay Zeka Modeli (Getiri Odaklı Fiyat Tahmini)
predictor = PricePredictor(strategy_results)
predicted_price, target_date = predictor.train_and_predict()

last_actual_date = strategy_results.index[-1]
last_actual_price = float(strategy_results.iloc[-1]['Close'])
price_diff = predicted_price - last_actual_price
pct_change = (price_diff / last_actual_price) * 100.0

target_date_str = target_date.strftime('%Y-%m-%d')
last_actual_date_str = last_actual_date.strftime('%Y-%m-%d')

# -----------------------------------------------------------------------------
# Üst Özet Metrik Kartları
# -----------------------------------------------------------------------------
st.markdown(f"### 🎯 {target_ticker} Özet Performans Göstergeleri")

col1, col2, col3, col4 = st.columns(4)

currency_symbol = "₺" if target_ticker.endswith(".IS") else "$"

with col1:
    prev_close = float(strategy_results.iloc[-2]['Close']) if len(strategy_results) > 1 else last_actual_price
    day_pct = ((last_actual_price - prev_close) / prev_close) * 100.0
    st.metric(
        label=f"Son Kapanış ({last_actual_date.strftime('%d.%m.%Y')})",
        value=f"{currency_symbol}{last_actual_price:,.2f}",
        delta=f"{day_pct:+.2f}% (1G)"
    )

with col2:
    bench_roi = metrics.get('Benchmark_ROI', 0.0)
    st.metric(
        label="Strateji Net Kâr / Zarar",
        value=f"{roi:+.2f}%",
        delta=f"Benchmark (Al & Tut): {bench_roi:+.2f}%",
        delta_color="normal"
    )

with col3:
    win_rate = metrics.get('Win_Rate', 0.0)
    closed_tr = metrics.get('Closed_Trades', 0)
    total_tr = metrics.get('Total_Trades', 0)
    st.metric(
        label="Kazanma Oranı (Win Rate)",
        value=f"%{win_rate:.1f}",
        delta=f"{closed_tr} kapanan işlem / {total_tr} toplam"
    )

with col4:
    direction_emoji = "📈 YÜKSELİŞ" if pct_change >= 0 else "📉 DÜŞÜŞ"
    st.metric(
        label=f"AI Tahmini ({target_date.strftime('%A %d.%m')})",
        value=f"{currency_symbol}{predicted_price:,.2f}",
        delta=f"{pct_change:+.2f}% | {direction_emoji}"
    )

st.divider()

# -----------------------------------------------------------------------------
# İnteraktif Plotly Grafik
# -----------------------------------------------------------------------------
st.subheader("📈 İnteraktif Mum Grafiği, İndikatörler ve AI Tahmini")

viz = MarketVisualizer(target_ticker)
viz.create_candlestick_chart(strategy_results)
viz.add_trading_signals(strategy_results)
viz.add_ml_prediction(target_date_str, predicted_price, last_actual_date_str, last_actual_price)

# Plotly düzenini Streamlit'e göre uyarla
viz.fig.update_layout(
    height=600,
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(viz.fig, use_container_width=True)

# -----------------------------------------------------------------------------
# Detay Sekmeleri (Tabs)
# -----------------------------------------------------------------------------
tab_backtest, tab_ai, tab_news, tab_data = st.tabs([
    "📊 Backtest & İşlem Geçmişi",
    "🤖 Yapay Zeka & Öznitelikler",
    "📰 Haberler & Sentiment",
    "📋 Veri Seti & İndikatörler"
])

# ----------------- TAB 1: BACKTEST -----------------
with tab_backtest:
    st.markdown("#### 💼 Portföy ve Simülasyon Detayları")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Başlangıç Bütçesi", f"{currency_symbol}{metrics['Initial_Balance']:,.2f}")
    c2.metric("Nihai Portföy Değeri", f"{currency_symbol}{metrics['Final_Portfolio']:,.2f}")
    c3.metric("Maksimum Düşüş (Max DD)", f"%{metrics['Max_Drawdown']:.2f}")
    c4.metric("Kapanan İşlem Sayısı", f"{metrics['Closed_Trades']}")

    st.markdown("#### 📜 Kapanan İşlem Listesi")
    closed_trades = [t for t in simulator.trade_history if t['Type'] == 'SELL']
    if closed_trades:
        trades_df = pd.DataFrame(closed_trades)
        trades_df['Tarih'] = pd.to_datetime(trades_df['Date']).dt.strftime('%Y-%m-%d')
        trades_df['Fiyat'] = trades_df['Price'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
        trades_df['Kâr/Zarar'] = trades_df['PnL'].apply(lambda x: f"{currency_symbol}{x:+,.2f}")
        trades_df['Getiri (%)'] = trades_df['PnL_Pct'].apply(lambda x: f"%{x:+.2f}")
        trades_df['Çıkış Nedeni'] = trades_df.get('Reason', 'SIGNAL')

        st.dataframe(
            trades_df[['Tarih', 'Shares', 'Fiyat', 'Kâr/Zarar', 'Getiri (%)', 'Çıkış Nedeni']].rename(columns={'Shares': 'Adet'}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Bu periyotta henüz kapanmış bir işlem bulunmuyor (Pozisyon beklemede veya alım seviyesinde).")

# ----------------- TAB 2: AI ÖZNİTELİKLERİ -----------------
with tab_ai:
    st.markdown("#### 🧠 Model Öznitelik Katkıları (Feature Coefficients on Next Return)")
    st.write(
        "Aşağıdaki grafik, modelin yarınki getiriyi tahmin ederken hangi göstergelere ne kadar ağırlık verdiğini gösterir. "
        "Pozitif değerler getiriyi yukarı, negatif değerler aşağı çeker."
    )

    if predictor.feature_importance:
        feat_df = pd.DataFrame(list(predictor.feature_importance.items()), columns=['Öznitelik', 'Katsayı (Ağırlık)'])
        feat_df = feat_df.sort_values(by='Katsayı (Ağırlık)', ascending=True)

        fig_coef = px.bar(
            feat_df,
            x='Katsayı (Ağırlık)',
            y='Öznitelik',
            orientation='h',
            color='Katsayı (Ağırlık)',
            color_continuous_scale='RdYlGn',
            title=f"{target_ticker} İçin Öznitelik Ağırlık Dağılımı"
        )
        fig_coef.update_layout(height=350, template="plotly_dark")
        st.plotly_chart(fig_coef, use_container_width=True)

    # Geçmiş Tahmin Kayıtları
    past_logs = [l for l in PricePredictor._load_log() if l.get('Ticker') == target_ticker]
    if past_logs:
        st.markdown("#### 📜 Bu Hisse İçin Kaydedilmiş Geçmiş AI Tahminleri")
        past_df = pd.DataFrame(past_logs)[['Prediction_Date', 'Target_Date', 'Predicted_Close', 'Actual_Close_Today']]
        past_df.columns = ['Tahmin Tarihi', 'Hedef Tarih', 'Tahmin Fiyatı', 'O Günkü Kapanış']
        st.dataframe(past_df.tail(5), use_container_width=True, hide_index=True)

# ----------------- TAB 3: HABERLER -----------------
with tab_news:
    st.markdown("#### 📰 Çekilen Son Haberler ve Duyarlılık Skorları")
    if news_df is not None and not news_df.empty:
        for _, n in news_df.head(10).iterrows():
            title = n.get('Title', 'Başlık Yok')
            pub = n.get('Publisher', 'Bilinmiyor')
            date_str = str(n.get('Date', ''))[:16]
            link = n.get('Link', '')

            # Duygu puanı hesapla
            dp = DataProcessor(raw_prices, news_df)
            score = dp.get_sentiment(title)

            if score > 0.1:
                badge = f'<span class="badge-positive">POZİTİF (+{score:.2f})</span>'
            elif score < -0.1:
                badge = f'<span class="badge-negative">NEGATİF ({score:.2f})</span>'
            else:
                badge = f'<span class="badge-neutral">NÖTR ({score:.2f})</span>'

            link_html = f'<a href="{link}" target="_blank" style="color: #4A90E2; text-decoration: none;">Haberi Oku ↗</a>' if link else ''

            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <span style="font-size: 0.8rem; color: #848E9C;">{pub} • {date_str}</span>
                    {badge}
                </div>
                <div style="font-size: 1rem; color: #EAECEF; font-weight: 500;">{title}</div>
                <div style="margin-top: 5px;">{link_html}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Bu hisse için haber akışı bulunamadı. Duygu skoru nötr (0.0) kabul ediliyor.")

# ----------------- TAB 4: VERİ SETİ -----------------
with tab_data:
    st.markdown("#### 📋 Hesaplanmış İndikatörler Tablosu (Son 20 Gün)")
    display_cols = [c for c in ['Close', 'SMA_20', 'EMA_9', 'EMA_21', 'RSI_14', 'ATR_14', 'Sentiment_Score', 'Action'] if c in strategy_results.columns]
    st.dataframe(strategy_results[display_cols].tail(20), use_container_width=True)

    csv_data = strategy_results.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Tüm Veri Setini İndir (CSV)",
        data=csv_data,
        file_name=f"{target_ticker}_algorithmic_analysis.csv",
        mime="text/csv"
    )
