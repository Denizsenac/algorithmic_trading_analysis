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
# Hareketli & Modern CSS Animasyonları ve Kurumsal Dark Fintech Teması
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Yalnızca Deploy butonunu gizleme (Karanlık Mod / Ayarlar 3 nokta menüsü korunur) */
    .stDeployButton, .stAppDeployButton, [data-testid="stAppDeployButton"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Temel Koyu Tema & Yüksek Kontrast Standartları */
    .stApp {
        background-color: #0B0E14 !important;
        color: #F8FAFC !important;
    }
    
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div {
        color: inherit;
    }

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
        background: linear-gradient(135deg, #131826 0%, #1A2234 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 16px !important;
        padding: 32px 35px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
    }
    
    .feature-card {
        background: #141926 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        padding: 22px !important;
        min-height: 165px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .feature-card:hover {
        transform: translateY(-4px) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 10px 25px rgba(56, 189, 248, 0.15) !important;
    }
    .feature-card h3 {
        margin: 0 0 10px 0 !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
    }
    .feature-card p {
        color: #E2E8F0 !important;
        font-size: 0.94rem !important;
        line-height: 1.55 !important;
        margin: 0 !important;
    }
    
    /* Yasal Uyarı Kutusu ve Metin Kontrastı Garantisi */
    .disclaimer-card {
        background: #101522 !important;
        border: 2px solid #F59E0B !important;
        border-left: 8px solid #F59E0B !important;
        border-radius: 12px !important;
        padding: 22px 26px !important;
        margin: 25px 0 18px 0 !important;
        box-shadow: 0 8px 30px rgba(245, 158, 11, 0.25) !important;
    }
    .disclaimer-card, .disclaimer-card *, .disclaimer-card p, .disclaimer-card span, .disclaimer-card div {
        color: #FFFFFF !important;
    }
    .disclaimer-card h4 {
        color: #FBBF24 !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        margin: 0 0 12px 0 !important;
    }

    /* Buton Tasarımları */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 10px 18px !important;
        transition: all 0.2s ease-in-out !important;
    }

    /* Modül Butonları - Her birine özel şık renk */
    div[data-testid="stColumn"]:nth-child(1) div.stButton > button {
        background: #0F2942 !important;
        border: 1px solid #38BDF8 !important;
        color: #38BDF8 !important;
    }
    div[data-testid="stColumn"]:nth-child(1) div.stButton > button:hover {
        background: #0284C7 !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.5) !important;
    }

    div[data-testid="stColumn"]:nth-child(2) div.stButton > button {
        background: #0D3327 !important;
        border: 1px solid #34D399 !important;
        color: #34D399 !important;
    }
    div[data-testid="stColumn"]:nth-child(2) div.stButton > button:hover {
        background: #059669 !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 15px rgba(52, 211, 153, 0.5) !important;
    }

    div[data-testid="stColumn"]:nth-child(3) div.stButton > button {
        background: #2D1A4E !important;
        border: 1px solid #C084FC !important;
        color: #C084FC !important;
    }
    div[data-testid="stColumn"]:nth-child(3) div.stButton > button:hover {
        background: #7C3AED !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 15px rgba(192, 132, 252, 0.5) !important;
    }

    /* Ana Başlat Butonu */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #00E699 0%, #0284C7 100%) !important;
        border: none !important;
        color: #07090E !important;
        font-size: 1.12rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        padding: 14px 24px !important;
        box-shadow: 0 4px 20px rgba(0, 230, 153, 0.35) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 30px rgba(0, 230, 153, 0.6) !important;
        transform: translateY(-2px) !important;
        color: #000000 !important;
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
    st.session_state["target_input"] = ""


# =============================================================================
# KATMAN 1: BAŞLANGIÇ / KARŞILAMA VE YASAL UYARI EKRANI (LANDING & GATEWAY)
# =============================================================================
if not st.session_state["app_unlocked"]:
    st.markdown("""
    <div class="hero-container" style="padding: 25px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <span class="live-dot"></span>
            <span style="color: #00E699; font-weight: 600; font-size: 0.85rem; letter-spacing: 1.5px;">CANLI HİBRİT PİYASA MOTORU v2.0</span>
        </div>
        <h1 style="font-size: 2.4rem; font-weight: 800; margin: 0; background: linear-gradient(90deg, #FFFFFF 0%, #B4C6EE 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            QuantAI Trading Terminal
        </h1>
        <p style="color: #8E9BAE; font-size: 1.05rem; margin-top: 8px; line-height: 1.5;">
            Borsa İstanbul (BIST) ve Global piyasalar için teknik göstergeler, Google News duyarlılık analizi 
            ve makine öğrenmesi destekli yeni nesil algoritmik analiz platformu.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 3'lü Tıklanabilir Modül Kartları
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-card" style="margin-bottom: 12px;">
            <h3 style="color: #38BDF8 !important;">⚡ Hibrit Sinyal Motoru</h3>
            <p>
                Tekil mum yanılgılarını önleyen çift teyitli <b>EMA (9/21)</b> ve <b>SMA 20</b> trend analizi. 
                RSI momentum filtreleri ve otomatik haber duyarlılık puanlaması.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚡ Sinyal Modülü ile Başlat", key="entry_signals", use_container_width=True):
            st.session_state["app_unlocked"] = True
            st.rerun()

    with c2:
        st.markdown("""
        <div class="feature-card" style="margin-bottom: 12px;">
            <h3 style="color: #34D399 !important;">🛡️ Dinamik Risk Yönetimi</h3>
            <p>
                Piyasa oynaklığına uyum sağlayan <b>ATR Tabanlı Trailing Stop</b> algoritması. 
                Kârı zirveden itibaren kilitler, sert geri çekilmelerde sermayeyi savunur.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🛡️ Risk & Backtest ile Başlat", key="entry_risk", use_container_width=True):
            st.session_state["app_unlocked"] = True
            st.rerun()

    with c3:
        st.markdown("""
        <div class="feature-card" style="margin-bottom: 12px;">
            <h3 style="color: #C084FC !important;">🧠 Durağan Getiri Modeli</h3>
            <p>
                Rastgele yürüyüş yanılgısını kıran, ham fiyat yerine <b>yüzdesel getiri</b> 
                tahmini üreten ve yön isabet oranını (Hit Rate) denetleyen ML mimarisi.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🧠 AI Tahmini ile Başlat", key="entry_ai", use_container_width=True):
            st.session_state["app_unlocked"] = True
            st.rerun()

    # Yasal Uyarı Kutusu (Garantili Bembeyaz & Yüksek Kontrastlı Metin)
    st.markdown("""
    <div class="disclaimer-card">
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <span style="font-size: 1.4rem; margin-right: 10px;">⚖️</span>
            <span style="color: #FBBF24 !important; font-size: 1.15rem; font-weight: 800; letter-spacing: 0.5px;">
                ÖNEMLİ YASAL UYARI (SPK & Mevzuat Bilgilendirmesi)
            </span>
        </div>
        <div style="color: #FFFFFF !important; font-size: 0.98rem; line-height: 1.7; font-weight: 400;">
            Bu platform; niceliksel finans, algoritmik modeller ve makine öğrenmesi algoritmalarını göstermek amacıyla 
            <span style="color: #FBBF24 !important; font-weight: 700; background: rgba(251, 191, 36, 0.2); padding: 2px 7px; border-radius: 4px;">yalnızca eğitim, akademik araştırma ve simülasyon amaçlı</span> geliştirilmiştir.<br><br>
            Platformda üretilen alım-satım sinyalleri, teknik indikatörler ve yapay zeka model tahminleri 
            <span style="color: #FB7185 !important; font-weight: 700; background: rgba(251, 113, 133, 0.2); padding: 2px 7px; border-radius: 4px;">kesinlikle yatırım tavsiyesi (YTD) veya portföy yöneticiliği kapsamında değildir.</span> 
            Finansal piyasalarda işlem yapmak sermaye kaybı riski barındırır. 
            Aşağıdaki butona tıklayarak veya modüllere giriş yaparak kullanım koşullarını kabul etmiş sayılırsınız.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Doğrudan Ana Giriş Butonu
    if st.button("🚀 TÜM TERMİNALİ BAŞLAT (TEK TIKLA GİRİŞ)", key="entry_main", type="primary", use_container_width=True):
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
            if st.button(q, key=f"btn_sb_{q}", use_container_width=True):
                st.session_state["target_input"] = q
                st.rerun()

    typed_ticker = st.text_input(
        "Hisse Sembolü veya Şirket Adı:",
        value=st.session_state.get("target_input", ""),
        placeholder="Örn: THYAO, ASELS, AAPL..."
    )
    if typed_ticker != st.session_state.get("target_input", ""):
        st.session_state["target_input"] = typed_ticker

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
    
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        if st.button("🚀 Analiz Et", type="primary", use_container_width=True):
            st.rerun()
    with col_sb2:
        if st.button("🔄 Sıfırla", use_container_width=True):
            st.session_state["target_input"] = ""
            st.rerun()


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


# Kullanıcının girdiği arama girdisi kontrolü
current_input = st.session_state.get("target_input", "").strip()

if not current_input:
    # Kullanıcı henüz hisse seçmedi: Karşılama ve Arama Ekranı Göster
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(20, 24, 36, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%); 
                border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 16px; padding: 40px 30px; text-align: center; margin-top: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.4);">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 68px; height: 68px; border-radius: 50%; background: rgba(74, 144, 226, 0.15); border: 1px solid rgba(74, 144, 226, 0.4); margin-bottom: 16px;">
            <span style="font-size: 2.2rem;">🔍</span>
        </div>
        <h2 style="margin: 0 0 10px 0; font-size: 2.1rem; font-weight: 800; background: linear-gradient(90deg, #FFFFFF 0%, #B4C6EE 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Hangi Hisseyi Analiz Etmek İstiyorsunuz?
        </h2>
        <p style="color: #94A3B8; font-size: 1.05rem; max-width: 620px; margin: 0 auto 20px auto; line-height: 1.6;">
            Otomatik arama yerine ilk aramayı siz belirleyin. BIST veya Global bir hisse sembolü (veya şirket adı) girerek 
            teknik sinyalleri, risk analizini ve yapay zeka tahminini başlatabilirsiniz.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    
    # Doğrudan Ana Ekranda Arama Çubuğu
    search_col1, search_col2 = st.columns([5, 1])
    with search_col1:
        main_query = st.text_input(
            "Hisse Arama:",
            placeholder="Örn: THYAO, ASELS, GARAN, EREGL, AAPL, NVDA, TSLA...",
            label_visibility="collapsed",
            key="main_search_box"
        )
    with search_col2:
        if st.button("🔎 Analiz Et", type="primary", use_container_width=True, key="btn_main_search"):
            if main_query.strip():
                st.session_state["target_input"] = main_query.strip()
                st.rerun()
            else:
                st.warning("Lütfen bir sembol veya hisse adı yazın.")

    if main_query and main_query.strip() != "":
        if main_query.strip() != st.session_state.get("target_input", ""):
            st.session_state["target_input"] = main_query.strip()
            st.rerun()

    st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
    st.markdown("#### ⚡ Popüler Hisseler (Tek Tıkla Analiz Başlat)")
    
    col_bist, col_global = st.columns(2)
    with col_bist:
        st.markdown("""
        <div style="background: rgba(26, 32, 48, 0.6); padding: 14px 18px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); margin-bottom: 12px;">
            <h5 style="margin: 0; color: #4A90E2; font-weight: 700;">🇹🇷 Borsa İstanbul (BIST 30)</h5>
        </div>
        """, unsafe_allow_html=True)
        bist_chips = [
            ("THYAO.IS", "Türk Hava Yolları"),
            ("ASELS.IS", "Aselsan"),
            ("GARAN.IS", "Garanti BBVA"),
            ("EREGL.IS", "Erdemir"),
            ("KCHOL.IS", "Koç Holding"),
            ("SISE.IS", "Şişecam")
        ]
        b_c1, b_c2 = st.columns(2)
        for idx, (sym, name) in enumerate(bist_chips):
            col_target = b_c1 if idx % 2 == 0 else b_c2
            with col_target:
                if st.button(f"{sym}\n({name})", key=f"chip_bist_{sym}", use_container_width=True):
                    st.session_state["target_input"] = sym
                    st.rerun()

    with col_global:
        st.markdown("""
        <div style="background: rgba(26, 32, 48, 0.6); padding: 14px 18px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); margin-bottom: 12px;">
            <h5 style="margin: 0; color: #00E699; font-weight: 700;">🌍 Global Piyasalar (ABD & Tech)</h5>
        </div>
        """, unsafe_allow_html=True)
        global_chips = [
            ("AAPL", "Apple Inc."),
            ("NVDA", "NVIDIA Corp."),
            ("TSLA", "Tesla Inc."),
            ("MSFT", "Microsoft"),
            ("AMZN", "Amazon"),
            ("GOOGL", "Alphabet")
        ]
        g_c1, g_c2 = st.columns(2)
        for idx, (sym, name) in enumerate(global_chips):
            col_target = g_c1 if idx % 2 == 0 else g_c2
            with col_target:
                if st.button(f"{sym}\n({name})", key=f"chip_global_{sym}", use_container_width=True):
                    st.session_state["target_input"] = sym
                    st.rerun()

    st.stop()


# Sembol Çözümleme
search_engine = TickerSearch()
target_ticker = search_engine.search_company(current_input, interactive=False)

if not target_ticker:
    st.error(f"'{current_input}' için borsa sembolü bulunamadı. Lütfen sembolü kontrol edin.")
    if st.button("⬅️ Yeni Arama Yap", type="primary"):
        st.session_state["target_input"] = ""
        st.rerun()
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
col_header_title, col_header_search = st.columns([5, 1.2])
with col_header_title:
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 15px;">
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
with col_header_search:
    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    if st.button("🔍 Başka Hisse Ara", use_container_width=True):
        st.session_state["target_input"] = ""
        st.rerun()

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
