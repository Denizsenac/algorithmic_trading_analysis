# 🚀 QuantAI: Algoritmik Ticaret & Yapay Zeka Destekli Piyasa Analiz Platformu

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" alt="Scikit-Learn" />
  <img src="https://img.shields.io/badge/GitHub_Actions-CI_Passed-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="CI" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <b>Borsa İstanbul (BIST)</b> ve <b>Global Piyasalarda (ABD, Kripto)</b> teknik analiz göstergelerini, gerçek zamanlı haber duyarlılık analizini (NLP) ve durağan getiri odaklı makine öğrenmesini birleştiren yeni nesil kantitatif terminal.
</p>

---

## 📌 İçindekiler
- [Genel Bakış](#-genel-bakış)
- [Öne Çıkan Özellikler](#-öne-çıkan-özellikler)
- [Matematiksel ve Finansal Mimari](#-matematiksel-ve-finansal-mimari)
- [Proje Mimarisi ve Dosya Yapısı](#-proje-mimarisi-ve-dosya-yapısı)
- [Ekran Görüntüleri ve Arayüz](#-ekran-görüntüleri-ve-arayüz)
- [Kurulum ve Hızlı Başlangıç](#-kurulum-ve-hızlı-başlangıç)
- [Test Paketinin Çalıştırılması](#-test-paketinin-çalıştırılması)
- [Yol Haritası (Roadmap)](#-yol-haritası-roadmap)
- [Yasal Uyarı (SPK & Mevzuat)](#-yasal-uyarı-spk--mevzuat)

---

## 💡 Genel Bakış

Finansal piyasalarda tek başına teknik göstergeler piyasa gürültüsüne (whipsaw) yakalanırken, yalnızca haber takibi yapmak ise fiyatlama zamanlamasını kaçırmaya yol açar. **QuantAI**, bu iki dünyayı hibrit bir karar matrisiyle birleştirir:

1. **Hisse Fiyat Verileri:** Yahoo Finance üzerinden asenkron veri boru hattı ile çekilir.
2. **Finansal Haber Akışı:** Yahoo Finance ve kesintilere karşı otomatik devreye giren **Google News RSS Fallback** motoru ile anlık taranır.
3. **Hibrit Karar Mekanizması:** Çift teyitli trend analizi (EMA 9/21 + SMA 20) ve Wilder's RSI ile VADER haber duyarlılık puanları filtrelenerek alım-satım sinyalleri üretilir.
4. **Dinamik Risk Yönetimi:** Sermayeyi korumak ve kârı kilitlemek için volatiliteye duyarlı **ATR Tabanlı Trailing Stop** çalışır.
5. **Yapay Zeka & Tahmin Motoru:** Fiyatın rastgele yürüyüş (random walk) yanılgısını kıran, durağan yüzdesel getiri tahmini yapan Ridge regresyon mimarisi.

---

## ⚡ Öne Çıkan Özellikler

- **🌐 Evrensel Hisse Arama Motoru:** Şirket adı (örn. `Türk Hava Yolları`, `Apple`) veya sembol (`THYAO.IS`, `AAPL`, `NVDA`) ile akıllı otomatik tamamlama.
- **🎨 Katmanlı Modern Web Arayüzü (Streamlit):**
  - **Katman 1 (Gateway & Onboarding):** Yasal bilgilendirme, modül özetleri ve tek tıkla başlatma.
  - **Katman 2 (Arama Paneli):** Popüler BIST ve Global hisseler için hızlı seçim butonları.
  - **Katman 3 (Canlı Terminal):** Plotly interaktif mum grafikleri, göstergeler, sinyaller, backtest simülasyonu, ML katsayıları ve duyarlılık rozetleri.
- **🛡️ Sentiment Guard Teknolojisi:** Haber verisi yetersiz olduğunda modelin negatif ya da yanıltıcı ağırlık atamasını engelleyen koruyucu algoritma.
- **⚡ Kesintisiz Google News Fallback:** Yahoo Finance haber API'si kısıtlandığında doğrudan Google News RSS beslemesine geçerek veri akışını kesintisiz sürdürür.
- **🧪 0.1 Saniyede Koşan Çevrimdışı CI Test Paketi:** Harici ağ bağımlılığı olmadan GitHub Actions üzerinde doğrulanan test mimarisi.

---

## 📐 Matematiksel ve Finansal Mimari

### 1. Durağan Getiri Modellemesi (Stationary Returns)
Klasik modellerde ham `Close` fiyatını tahmin etmek sahte korelasyona (spurious correlation) ve $\approx 0.99$ sahte $R^2$ yanılsamasına yol açar. QuantAI, seriyi durağanlaştırarak bir sonraki günün **yüzdesel getirisini** ($\text{Target\_Next\_Return}$) hedefler:

$$\text{Return}_{t+1} = \frac{\text{Close}_{t+1} - \text{Close}_t}{\text{Close}_t}$$

### 2. Wilder's Smoothed RSI (14)
Standart SMA bazlı RSI yerine finansal standart olan Wilder'ın üssel yumuşatma yöntemi uygulanır.

### 3. Dinamik ATR Trailing Stop
Sabit yüzdeli stop-loss yerine piyasa oynaklığını (ATR) izleyen dinamik takip eden zarar durdurma mekanizması:

$$\text{Stop Fiyatı} = \text{Zirve Fiyat} - (\text{ATR}_{14} \times \text{Çarpan})$$

---

## 📂 Proje Mimarisi ve Dosya Yapısı

```bash
algorithmic_trading_analysis/
├── app.py                 # Streamlit web arayüzü ve interaktif terminal
├── main.py                # Konsol tabanlı tam analiz çalıştırıcısı
├── Backtester.py          # ATR Trailing Stop destekli simülasyon ve getiri motoru
├── strategy_engine.py     # Hibrit alım-satım sinyal üretim algoritması
├── predictor.py           # Durağan getiri odaklı makine öğrenmesi tahmin modeli
├── data_processor.py      # Teknik indikatörler, veri birleştirme ve özellik mühendisliği
├── data_fetcher.py        # Asenkron Yahoo Finance piyasa verisi çekicisi
├── news_fetcher.py        # Yahoo Finance + Google News RSS hibrit haber motoru
├── ticker_search.py       # Akıllı hisse senedi ve şirket adı arama motoru
├── visualizer.py          # Plotly interaktif grafik üreticisi (HTML dışa aktarım)
├── test_project.py        # Çevrimdışı çalışan otomatik birim test paketi
├── requirements.txt       # Proje bağımlılıkları
└── .github/workflows/     # GitHub Actions sürekli entegrasyon (CI) yapılandırması
```

---

## 🚀 Kurulum ve Hızlı Başlangıç

### Gereksinimler
- Python 3.11 veya üzeri
- Git

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/Denizsenac/algorithmic_trading_analysis.git
cd algorithmic_trading_analysis
```

### 2. Sanal Ortam (Virtualenv) Oluşturun ve Aktif Edin
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Web Terminalini Başlatın (Streamlit)
```bash
streamlit run app.py
```
Tarayıcınızda otomatik olarak **`http://localhost:8501`** açılacaktır.

### 5. Konsol Modunda Çalıştırma (Opsiyonel)
```bash
python main.py
```

---

## 🧪 Test Paketinin Çalıştırılması

Projede harici internet bağlantısına ihtiyaç duymadan algoritmaları, sinyalleri, backtest hesaplamalarını ve duyarlılık filtrelerini doğrulayan bir test paketi yer alır:

```bash
python test_project.py
```
*Tüm testler ortalama **0.1 saniye** içinde tamamlanır ve yeşil döner.*

---

## 🗺️ Yol Haritası (Roadmap)

- [x] **Adım 1:** Streamlit ile modern, katmanlı ve interaktif web arayüzü tasarımı.
- [ ] **Adım 2:** `predictor.py` içerisine **XGBoost (Extreme Gradient Boosting)** entegrasyonu ile yön isabet oranının (Hit Rate) maksimize edilmesi ve özellik önem derecesi (Feature Importance) analizi.
- [ ] **Adım 3:** Sözlük tabanlı VADER duyarlılığı yerine **Vektör Veritabanı + LLM (RAG)** mimarisiyle finansal haberlerin derin anlamsal etkisinin ölçülmesi.
- [ ] **Adım 4:** Streamlit Cloud / Railway üzerinde canlı dağıtım ve webhook ile anlık Telegram sinyal bildirimleri.

---

## ⚖️ Yasal Uyarı (SPK & Mevzuat)

> **ÖNEMLİ:** Bu yazılım ve analiz terminali; niceliksel finans, algoritmik modeller ve makine öğrenmesi uygulamalarını test etmek amacıyla **yalnızca eğitim, akademik araştırma ve simülasyon amaçlı** geliştirilmiştir.
>
> Burada üretilen alım-satım sinyalleri, teknik indikatörler ve yapay zeka model tahminleri **kesinlikle yatırım tavsiyesi (YTD)** veya portföy yöneticiliği kapsamında değerlendirilemez. Finansal piyasalarda işlem yapmak sermaye kaybı riski barındırır.

---

## 👨‍💻 Geliştirici & Katkı
Geliştirici: **Deniz Sena**  
Sorularınız, hata bildirimleri veya özellik talepleri için bir [Issue](https://github.com/Denizsenac/algorithmic_trading_analysis/issues) açabilir ya da Pull Request gönderebilirsiniz.
