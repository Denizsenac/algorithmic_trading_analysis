import asyncio
import time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    page_title="QuantAI | Algorithmic Trading & Prediction Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Hareketli & Modern CSS Animasyonları ve Glassmorphism Teması
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes glow {
        0% { box-shadow: 0 0 5px rgba(0, 230, 153, 0.4); }
        50% { box-shadow: 0 0 20px rgba(0, 230, 153, 0.8); }
        100% { box-shadow: 0 0 5px rgba(0, 230, 153, 0.4); }
    }
    
    .live-dot {
        height: 10px;
        width: 10px;
        background-color: #00E699;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 2s infinite;
        margin-right: 8px;
    }
    
    .hero-container {
        background: linear-gradient(135deg, rgba(20, 24, 35, 0.95) 0%, rgba(32, 38, 55, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 35px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .feature-card {
        background: rgba(25, 30, 45, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .feature-card:hover {
        transform: translateY(-5px);
        border-color: rgba(0, 230, 153, 0.5);
        box-shadow: 0 10px 25px -5px rgba(0, 230, 153, 0.2);
    }
    
    .disclaimer-box {
        background: rgba(255, 171, 0, 0.06);
        border-left: 4px solid #FFAB00;
        border-radius: 8px;
        padding: 18px;
        margin: 20px 0;
        font-size: 0.9rem;
        line-height: 1.5;
        color: #E6E8EB;
    }

    .metric-card {
        background: rgba(26, 32, 48, 0.85);
        border-radius: 12px;
        padding: 18px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(74, 144, 226, 0.4);
    }
    
    .badge-positive {
        background-color: rgba(14, 203, 129, 0.18);
        color: #0ECB81;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid rgba(14, 203, 129, 0.3);
    }
    .badge-negative {
        background-color: rgba(246, 70, 93, 0.18);
        color: #F6465D;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid rgba(246, 70, 93, 0.3);
    }
    .badge-neutral {
        background-color: rgba(132, 142, 156, 0.18);
        color: #848E9C;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid rgba(132, 142, 156, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Session state başlatma
if "app_unlocked" not in st.session_state:
    st.session_state["app_unlocked"] = False
if "target_input" not in st.session_state:
    st.session_state["target_input"] = "THYAO.IS"


# =============================================================================
# KATMAN 1: BAŞLANGIÇ / KARŞILAMA VE YASAL UYARI EKRANI (LANDING & GATEWAY)
# =============================================================================
if not st.session_state["app_unlocked"]:
    st.markdown("""
    <div class="hero-container">
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <span class="live-dot"></span>
            <span style="color: #00E699; font-weight: 600; font-size: 0.85rem; letter-spacing: 1.5px;">CANLI HİBRİT PİYASA MOTORU v2.0</span>
        </div>
        <h1 style="font-size: 2.8rem; font-weight: 800; margin: 0; background: linear-gradient(90deg, #FFFFFF 0%, #B4C6EE 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            QuantAI Trading Terminal
        </h1>
        <p style="color: #8E9BAE; font-size: 1.15rem; margin-top: 10px; max-width: 800px; line-height: 1.6;">
            Borsa İstanbul (BIST) ve Global piyasalar için teknik göstergeler, Google News duyarlılık analizi 
            ve makine öğrenmesi destekli yeni nesil algoritmik analiz platformu.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 3'lü Özellik Kartları
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #4A90E2; margin-top: 0;">⚡ Hibrit Sinyal Motoru</h3>
            <p style="color: #A0AEC0; font-size: 0.95rem; line-height: 1.5;">
                Tekil mum yanılgılarını önleyen çift teyitli EMA (9/21) ve SMA 20 trend analizi. 
                RSI momentum filtreleri ve otomatik haber duyarlılık puanlaması.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #00E699; margin-top: 0;">🛡️ Dinamik Risk Yönetimi</h3>
            <p style="color: #A0AEC0; font-size: 0.95rem; line-height: 1.5;">
                Piyasa oynaklığına uyum sağlayan <b>ATR Tabanlı Trailing Stop</b> algoritması. 
                Kârı zirveden itibaren kilitler, sert geri çekilmelerde sermayeyi savunur.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #9B51E0; margin-top: 0;">🧠 Durağan Getiri Modeli</h3>
            <p style="color: #A0AEC0; font-size: 0.95rem; line-height: 1.5;">
                Rastgele yürüyüş (random walk) yanılgısını kıran, ham fiyat yerine <b>yüzdesel getiri</b> 
                tahmini üreten ve yön isabet oranını (Hit Rate) denetleyen ML mimarisi.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Yasal Uyarı Kutusu
    st.markdown("""
    <div class="disclaimer-box">
        <h4 style="color: #FFAB00; margin: 0 0 8px 0; display: flex; align-items: center;">
            ⚖️ ÖNEMLİ YASAL UYARI (SPK & Mevzuat Bilgilendirmesi)
        </h4>
        Bu yazılım ve web terminali; niceliksel finans, makine öğrenmesi ve veri bilimi metodolojilerini 
        göstermek amacıyla <b>yalnızca eğitim, akademik araştırma ve simülasyon amaçlı</b> geliştirilmiştir.<br><br>
        Burada sunulan sinyaller, matematiksel hesaplamalar ve model tahminleri <b>hiçbir şekilde yatırım danışmanlığı (YTD) 
        veya portföy yöneticiliği kapsamında değerlendirilemez.</b> Finansal piyasalarda işlem yapmak yüksek düzeyde 
        sermaye kaybı riski barındırır. Gerçek yatırımlarınızı lisanslı bir finansal kuruluşa danışarak yapınız.
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    col_agree, col_btn = st.columns([1.5, 1])
    with col_agree:
        agree = st.checkbox(
            "Yasal uyarı metnini okudum, anladım ve analiz terminalini eğitim/araştırma amacıyla kullanmayı kabul ediyorum.",
            value=False
        )
    with col_btn:
        start_btn = st.button("🚀 ANALİZ TERMİNALİNİ BAŞLAT", type="primary", use_container_width=True, disabled=not agree)

    if start_btn and agree:
        st.session_state["app_unlocked"] = True
        st.rerun()

    st.stop()


# =============================================================================
# KATMAN 2: CANLI VE HAREKETLİ ANALİZ TERMİNALİ (QUANT TERMINAL)
# =============================================================================

# Yan Panel (Sidebar)
with st.sidebar:
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h3 style="margin:0;">⚡ Terminal Kontrolü</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅️ Başlangıç Ekranına Dön", use_container_width=True):
        st.session_state["app_unlocked"] = False
        st.rerun()

    st.divider()

    st.markdown("##### 📌 Hızlı Hisse Seçimi")
    quick_tickers = ["THYAO.IS", "ASELS.IS", "GARAN.IS", "AAPL", "NVDA", "TSLA"]
    cols_q = st.columns(3)
    for i, q in enumerate(quick_tickers):
        with cols_q[i % 3]:
            if st.button(q, key=f"btn_{q}", use_container_width=True):
                st.session_state["target_input"] = q
                st.rerun()

    target_input = st.text_input(
        "Hisse Sembolü veya Şirket Adı:",
        value=st.session_state.get("target_input", "THYAO.IS")
    )

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        period = st.selectbox("Periyot:", options=["6mo", "1y", "2y", "5y"], index=1)
    with col_s2:
        budget = st.number_input("Bütçe ($/₺):", min_value=1000.0, value=10000.0, step=1000.0)

    st.markdown("##### 🛡️ Risk Parametreleri")
    use_trailing = st.checkbox("ATR Trailing Stop", value=True)
    atr_mult = st.slider("ATR Çarpanı:", 1.5, 4.0, 2.5, 0.1)

    demo_mode = st.checkbox("Demo Modu (Sentetik Haberler)", value=False)
    st.divider()
    analyze_btn = st.button("🔄 Analizi Yenile", type="primary", use_container_width=True)


# Veri Çekme Motoru
@st.cache_data(ttl=300, show_spinner=False)
def load_and_process_data(ticker_symbol, selected_period, is_demo):
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

    processor = DataProcessor(price_data=price_df, news_data=news_df)
    raw_merged = processor.merge_data()
    final_dataset = processor.calculate_indicators(raw_merged)

    return final_dataset, news_df, price_df


# Sembol Çözümleme
search_engine = TickerSearch()
target_ticker = search_engine.search_company(target_input, interactive=False)

if not target_ticker:
    st.error(f"'{target_input}' için borsa sembolü bulunamadı. Lütfen sembolü kontrol edin.")
    st.stop()

# Animasyonlu İlerleme Çubuğu ile Yükleme
progress_placeholder = st.empty()
with progress_placeholder.container():
    p_bar = st.progress(10, text="📡 Piyasa verileri çekiliyor...")
    time.sleep(0.1)
    p_bar.progress(35, text="📰 Haberler ve duyarlılık akışı taranıyor...")
    time.sleep(0.1)
    final_dataset, news_df, raw_prices = load_and_process_data(target_ticker, period, demo_mode)
    p_bar.progress(70, text="🧮 İndikatörler ve sinyaller hesaplanıyor...")
    time.sleep(0.1)
    p_bar.progress(100, text="✨ Analiz tamamlandı!")
    time.sleep(0.2)
progress_placeholder.empty()

if final_dataset is None or final_dataset.empty:
    st.error(f"[{target_ticker}] için yeterli fiyat verisi alınamadı.")
    st.stop()

# Hesaplama Motorları
engine = StrategyEngine(final_dataset)
strategy_results = engine.generate_signals()

simulator = Backtester(
    strategy_results,
    initial_balance=budget,
    use_trailing_stop=use_trailing,
    atr_multiplier=atr_mult
)
final_value, roi = simulator.run_simulation()
metrics = simulator.metrics

predictor = PricePredictor(strategy_results)
predicted_price, target_date = predictor.train_and_predict()

last_actual_date = strategy_results.index[-1]
last_actual_price = float(strategy_results.iloc[-1]['Close'])
price_diff = predicted_price - last_actual_price
pct_change = (price_diff / last_actual_price) * 100.0

target_date_str = target_date.strftime('%Y-%m-%d')
last_actual_date_str = last_actual_date.strftime('%Y-%m-%d')
currency_symbol = "₺" if target_ticker.endswith(".IS") else "$"

# Başlık Bölümü
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
    <div>
        <h2 style="margin: 0; font-size: 2.2rem; font-weight: 800;">{target_ticker}</h2>
        <span style="color: #8E9BAE; font-size: 0.95rem;">Son Güncelleme: {last_actual_date.strftime('%d.%m.%Y')} • Analiz Periyodu: {period.upper()}</span>
    </div>
    <div style="text-align: right;">
        <span style="font-size: 0.85rem; color: #8E9BAE;">Anlık Fiyat</span>
        <div style="font-size: 2rem; font-weight: 800; color: #FFFFFF;">{currency_symbol}{last_actual_price:,.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 4'lü Dinamik Performans Kartları
c1, c2, c3, c4 = st.columns(4)

prev_close = float(strategy_results.iloc[-2]['Close']) if len(strategy_results) > 1 else last_actual_price
day_pct = ((last_actual_price - prev_close) / prev_close) * 100.0
bench_roi = metrics.get('Benchmark_ROI', 0.0)
win_rate = metrics.get('Win_Rate', 0.0)
closed_tr = metrics.get('Closed_Trades', 0)
total_tr = metrics.get('Total_Trades', 0)
direction_str = "📈 YÜKSELİŞ BEKLENTİSİ" if pct_change >= 0 else "📉 DÜŞÜŞ BEKLENTİSİ"

with c1:
    st.metric(
        label="Günlük Değişim",
        value=f"{currency_symbol}{last_actual_price:,.2f}",
        delta=f"{day_pct:+.2f}%"
    )
with c2:
    st.metric(
        label="Strateji Net Kârı",
        value=f"{roi:+.2f}%",
        delta=f"Al & Tut: {bench_roi:+.2f}%",
        delta_color="normal"
    )
with c3:
    st.metric(
        label="Kazanma Oranı (Win Rate)",
        value=f"%{win_rate:.1f}",
        delta=f"{closed_tr} kapanan işlem / {total_tr} toplam"
    )
with c4:
    st.metric(
        label=f"AI Tahmini ({target_date.strftime('%d.%m')})",
        value=f"{currency_symbol}{predicted_price:,.2f}",
        delta=f"{pct_change:+.2f}% ({direction_str})"
    )

st.write("")

# İnteraktif Plotly Mum Grafiği
viz = MarketVisualizer(target_ticker)
viz.create_candlestick_chart(strategy_results)
viz.add_trading_signals(strategy_results)
viz.add_ml_prediction(target_date_str, predicted_price, last_actual_date_str, last_actual_price)

viz.fig.update_layout(
    height=600,
    margin=dict(l=10, r=10, t=30, b=10),
    template="plotly_dark",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(viz.fig, use_container_width=True)

# 4 Detay Sekmesi
tab_bt, tab_ai, tab_news, tab_data = st.tabs([
    "📊 Backtest ve Kâr/Zarar Dökümü",
    "🤖 Yapay Zeka Öznitelik Katkıları",
    "📰 Canlı Haberler & Duyarlılık",
    "📋 Ham Veri Seti & İndir"
])

with tab_bt:
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Başlangıç Sermayesi", f"{currency_symbol}{metrics['Initial_Balance']:,.2f}")
    m_col2.metric("Portföy Değeri", f"{currency_symbol}{metrics['Final_Portfolio']:,.2f}")
    m_col3.metric("Maksimum Düşüş (Max Drawdown)", f"%{metrics['Max_Drawdown']:.2f}")
    m_col4.metric("Kapanan İşlemler", f"{metrics['Closed_Trades']}")

    st.markdown("##### 📜 Kapanan İşlem Detayları")
    closed_trades = [t for t in simulator.trade_history if t['Type'] == 'SELL']
    if closed_trades:
        tdf = pd.DataFrame(closed_trades)
        tdf['Tarih'] = pd.to_datetime(tdf['Date']).dt.strftime('%d.%m.%Y')
        tdf['Satış Fiyatı'] = tdf['Price'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
        tdf['Net Kâr/Zarar'] = tdf['PnL'].apply(lambda x: f"{currency_symbol}{x:+,.2f}")
        tdf['Getiri (%)'] = tdf['PnL_Pct'].apply(lambda x: f"%{x:+.2f}")
        tdf['Çıkış Tipi'] = tdf.get('Reason', 'SIGNAL')
        
        st.dataframe(
            tdf[['Tarih', 'Shares', 'Satış Fiyatı', 'Net Kâr/Zarar', 'Getiri (%)', 'Çıkış Tipi']].rename(columns={'Shares': 'Adet'}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Bu periyotta henüz kapanmış işlem bulunmuyor.")

with tab_ai:
    st.markdown("##### 🔍 Model Hangi Göstergelere Ağırlık Verdi?")
    if predictor.feature_importance:
        fdf = pd.DataFrame(list(predictor.feature_importance.items()), columns=['Öznitelik', 'Model Ağırlığı'])
        fdf = fdf.sort_values(by='Model Ağırlığı', ascending=True)

        fig_b = px.bar(
            fdf, x='Model Ağırlığı', y='Öznitelik', orientation='h',
            color='Model Ağırlığı', color_continuous_scale='RdYlGn'
        )
        fig_b.update_layout(height=350, template="plotly_dark", margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_b, use_container_width=True)

with tab_news:
    st.markdown("##### 🗞️ Çekilen Son Haber Başlıkları ve Duygu Rozetleri")
    if news_df is not None and not news_df.empty:
        dp = DataProcessor(raw_prices, news_df)
        for _, n in news_df.head(10).iterrows():
            title = n.get('Title', 'Başlık Yok')
            pub = n.get('Publisher', 'Bilinmiyor')
            date_s = str(n.get('Date', ''))[:16]
            link = n.get('Link', '')
            score = dp.get_sentiment(title)

            if score > 0.1:
                badge = f'<span class="badge-positive">POZİTİF (+{score:.2f})</span>'
            elif score < -0.1:
                badge = f'<span class="badge-negative">NEGATİF ({score:.2f})</span>'
            else:
                badge = f'<span class="badge-neutral">NÖTR ({score:.2f})</span>'

            link_btn = f'<a href="{link}" target="_blank" style="color: #4A90E2; text-decoration: none; font-weight: 500;">Kaynağa Git ↗</a>' if link else ''

            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="color: #8E9BAE; font-size: 0.85rem;">{pub} • {date_s}</span>
                    {badge}
                </div>
                <div style="color: #FFFFFF; font-size: 1.05rem; font-weight: 500;">{title}</div>
                <div style="margin-top: 8px;">{link_btn}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Bu hisse için güncel haber akışı bulunamadı.")

with tab_data:
    st.markdown("##### 📋 Hesaplanmış İndikatörler ve Sinyaller Tablosu")
    display_cols = [c for c in ['Close', 'SMA_20', 'EMA_9', 'EMA_21', 'RSI_14', 'ATR_14', 'Sentiment_Score', 'Action'] if c in strategy_results.columns]
    st.dataframe(strategy_results[display_cols].tail(25), use_container_width=True)

    csv_d = strategy_results.to_csv().encode('utf-8')
    st.download_button(
        "📥 Tüm Veri Setini İndir (CSV)",
        data=csv_d,
        file_name=f"{target_ticker}_quant_analysis.csv",
        mime="text/csv"
    )

# Footer Yasal Uyarı Notu
st.markdown("""
<div style="text-align: center; color: #6C757D; font-size: 0.8rem; margin-top: 50px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 20px;">
    QuantAI Algorithmic Trading Platform • Bu sistem yatırım tavsiyesi içermez (YTD) • Yalnızca simülasyon ve eğitim amaçlıdır.
</div>
""", unsafe_allow_html=True)
