# 🚀 QuantAI: Algorithmic Trading & AI Market Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" alt="Scikit-Learn" />
  <img src="https://img.shields.io/badge/GitHub_Actions-CI_Passed-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="CI" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <b>A next-generation quantitative trading and financial analysis terminal</b> designed for <b>Borsa Istanbul (BIST)</b> and <b>Global Markets (US Equities, Tech, Crypto)</b>. It harmonizes multi-timeframe technical momentum indicators, real-time news sentiment NLP, and stationary-return machine learning into a unified decision matrix.
</p>

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quantitative & Mathematical Architecture](#-quantitative--mathematical-architecture)
- [Project Architecture & Directory Structure](#-project-architecture--directory-structure)
- [Installation & Quickstart](#-installation--quickstart)
- [Running Offline Unit Tests](#-running-offline-unit-tests)
- [Development Roadmap](#-development-roadmap)
- [Legal & Regulatory Disclaimer](#-legal--regulatory-disclaimer)
- [Author & Contribution](#-author--contribution)

---

## 💡 Overview

In modern algorithmic trading, relying exclusively on technical indicators leads to severe whipsaws during market regime shifts, while relying solely on news headlines results in delayed trade execution.

**QuantAI** solves this challenge through an asynchronous hybrid pipeline:
1. **Market Data Pipeline:** Asynchronously streams historical OHLCV data via Yahoo Finance.
2. **Real-Time News NLP Stream:** Scrapes live headlines using Yahoo Finance and an automated **Google News RSS Fallback** engine when primary APIs face rate-limits or geographic bans.
3. **Hybrid Decision Engine:** Combines dual-trend confirmation (EMA 9/21 cross + SMA 20 filter) and Wilder's Smoothed RSI (14) with VADER sentiment scores to generate high-probability BUY/SELL signals.
4. **Dynamic Risk Control:** Mitigates drawdowns and locks in floating profits using a volatility-adaptive **ATR Trailing Stop** (`atr_multiplier=2.5`).
5. **Stationary AI Predictor:** Avoids spurious random-walk correlations by predicting **percentage returns** rather than raw price levels.

---

## ⚡ Key Features

- **🌐 Universal Ticker Resolution:** Smart fuzzy search supporting company names (e.g., `Turkish Airlines`, `Apple`, `NVIDIA`) and ticker symbols (`THYAO.IS`, `AAPL`, `NVDA`, `TSLA`).
- **🎨 Layered Modern Fintech UI (Streamlit & Plotly):**
  - **Layer 1 (Gateway & Onboarding):** High-contrast regulatory disclaimer, module previews, and instant access.
  - **Layer 2 (Search & Launchpad):** Clean search interface with one-click popular BIST 30 and US tech chip shortcuts. No unwanted automatic requests.
  - **Layer 3 (Live Terminal):** Interactive Plotly candlestick charts with volume bars, technical overlays, trade markers, backtest performance KPIs, and feature-weight transparency.
- **🛡️ Sentiment Guard Algorithm:** Automatically regularizes NLP sentiment coefficients to `0.0` when news data is sparse, preventing spurious overfitting on zero-sentiment historical windows.
- **⚡ Resilient Google News RSS Fallback:** Zero-configuration, zero-API-key fallback ensuring uninterrupted sentiment analysis even when third-party services are throttled.
- **🧪 Ultra-Fast Offline CI Test Suite:** A comprehensive test suite running in **<0.12 seconds** without network dependencies, verifying models and backtests in GitHub Actions CI across Python 3.11 and 3.12.

---

## 📐 Quantitative & Mathematical Architecture

### 1. Stationary Percentage Return Formulation
Regressing raw non-stationary price series ($Close_t$) against lagged indicators creates spurious correlation and a misleading $R^2 \approx 0.99$ illusion with random directional hit rates (~44%). QuantAI enforces strict statistical stationarity by modeling next-day percentage returns:

$$\text{Target\_Next\_Return}_{t} = \frac{\text{Close}_{t+1} - \text{Close}_t}{\text{Close}_t}$$

### 2. Wilder's Smoothed RSI (14-Period)
QuantAI implements Welles Wilder's original exponential smoothing for Average Gain and Average Loss, eliminating the distortion caused by standard simple moving average implementations:

$$\text{Smoothed Gain}_t = \frac{\text{Smoothed Gain}_{t-1} \times 13 + \text{Gain}_t}{14}$$

$$\text{RSI} = 100 - \left( \frac{100}{1 + \frac{\text{Smoothed Gain}}{\text{Smoothed Loss}}} \right)$$

### 3. Volatility-Adaptive Dynamic ATR Trailing Stop
Rather than using static percentage stops that trigger prematurely during volatile market swings, QuantAI recalculates stop thresholds dynamically based on the 14-day True Range:

$$\text{Stop Level}_t = \max(\text{Stop Level}_{t-1}, \; \text{Peak Price} - [\text{ATR}_{14} \times \alpha])$$

*(where $\alpha$ is the user-configured ATR multiplier, defaulting to $2.5$)*.

---

## 📂 Project Architecture & Directory Structure

```text
algorithmic_trading_analysis/
├── app.py                 # Interactive Streamlit terminal & visualization dashboard
├── main.py                # Command-line interface for headless quantitative execution
├── Backtester.py          # Trade simulator with ATR Trailing Stop, Win Rate, and Max Drawdown
├── strategy_engine.py     # Hybrid signal generator (Dual-EMA, SMA20, RSI, Sentiment)
├── predictor.py           # Machine learning return engine with Sentiment Guard & Ridge regression
├── data_processor.py      # Technical indicator calculation, feature engineering & data alignment
├── data_fetcher.py        # Asynchronous market data fetcher with SSL self-healing
├── news_fetcher.py        # Dual-engine financial news scraper (Yahoo Finance + Google News RSS)
├── ticker_search.py       # Exact and fuzzy symbol resolver with offline fallback
├── visualizer.py          # Plotly interactive candlestick chart builder (HTML export)
├── test_project.py        # Mocked, network-independent offline test suite (runs in 0.1s)
├── requirements.txt       # Environment dependencies with flexible version ranges
└── .github/workflows/     # Automated GitHub Actions CI workflow
```

---

## 🚀 Installation & Quickstart

### Prerequisites
- Python 3.11, 3.12, or 3.14
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Denizsenac/algorithmic_trading_analysis.git
cd algorithmic_trading_analysis
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Launch the Web Trading Terminal (Streamlit)
```bash
streamlit run app.py
```
Your browser will automatically open **`http://localhost:8501`**.

### 5. Run in Console Mode (Optional)
```bash
python main.py
```

---

## 🧪 Running Offline Unit Tests

The repository includes a dedicated unit test suite that validates feature calculation, signal generation, backtesting execution, and machine learning convergence without calling external APIs:

```bash
python test_project.py
```
*Expected execution time: **~0.10s** (All tests green).*

---

## 🗺️ Development Roadmap

- [x] **Step 1: Web Interface & Dashboard (Streamlit):** Multi-layered fintech UI, dynamic Plotly charts, customizable risk parameters, and SPK-compliant disclaimer. *(Completed)*
- [ ] **Step 2: Advanced ML Engine (XGBoost):** Upgrade linear/ridge estimators to gradient-boosted trees (`XGBRegressor`) with hyperparameter tuning, feature importance breakdown, and directional hit-rate optimization. *(In Progress)*
- [ ] **Step 3: Neural Sentiment & RAG (LLM):** Replace lexicon-based VADER scoring with a local vector database and Large Language Model (RAG) assessing nuanced geopolitical and market impact.
- [ ] **Step 4: Cloud Deployment & Alerts:** One-click deployment to Streamlit Community Cloud / Railway and instant signal delivery via Telegram webhook bots.

---

## ⚖️ Legal & Regulatory Disclaimer

> **IMPORTANT NOTICE:** This software and web terminal are developed **strictly for educational, academic research, and simulation purposes**.
>
> Under no circumstances should the signals, indicators, model weights, or predictions generated by this platform be construed as financial advice, investment recommendations, or portfolio management. Trading financial instruments carries substantial risk of capital loss.

---

## 👨‍💻 Author & Contributions

Created by **Deniz Sena**.  
Feel free to open an [Issue](https://github.com/Denizsenac/algorithmic_trading_analysis/issues) or submit a Pull Request to contribute!
