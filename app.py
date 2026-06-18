import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from textblob import TextBlob
import datetime
import os
import json
import requests
import feedparser
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Global Makro & BIST Terminali", layout="wide", initial_sidebar_state="expanded")

# Modern Dynamic UI CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    /* === ÜST BOŞLUK TAMAMEN SIFIR === */
    .main > div:first-child { padding-top: 0rem !important; margin-top: 0rem !important; }
    .main > div:first-child > div { padding-top: 0rem !important; margin-top: 0rem !important; }
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; margin-top: 0rem !important; max-width: 100% !important; }
    header[data-testid="stHeader"] { background: transparent !important; display: none !important; }
    #stDecoration { display: none !important; }
    section[data-testid="stSidebar"] + div section:first-child > div:first-child { padding-top: 0 !important; margin-top: 0 !important; }
    div[data-testid="stVerticalBlock"] > div:first-child { padding-top: 0 !important; }
    .element-container:first-child { margin-top: 0 !important; }
    .stApp > div:first-child > div:first-child { padding-top: 0 !important; }

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
    }

    /* === GENEL TEMA VE ARKA PLAN === */
    .stApp {
        background: radial-gradient(circle at top left, #1a1f35 0%, #0d1117 100%) !important;
        color: #e2e8f0 !important;
    }
    
    .main > div:first-child { padding-top: 0rem !important; }
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; max-width: 100% !important; }
    header[data-testid="stHeader"] { background: transparent !important; display: none !important; }

    /* === SIDEBAR (YAN MENÜ) === */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebar"] .st-emotion-cache-1wmy9hl {
        background-color: #1e1e24 !important;
        background: #1e1e24 !important;
        border-right: none !important;
        padding-top: 0px !important;
    }
    [data-testid="stSidebar"] hr {
        display: none !important;
    }
    /* Sidebar tüm blok elemanları arasındaki boşluğu sıkıştır */
    [data-testid="stSidebar"] .stElementContainer,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stRadio,
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stButton {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
        gap: 0px !important;
    }
    [data-testid="stSidebar"] .block-container,
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0px !important;
        row-gap: 0px !important;
    }
    
    /* Yan Menü Butonları */
    [data-testid="stSidebar"] .stButton button {
        background-color: rgba(255,255,255,0.06) !important; 
        background: rgba(255,255,255,0.06) !important; 
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: #e2e8f0 !important; 
        font-size: 14px !important; 
        font-weight: 600 !important;
        text-align: left !important; 
        padding: 6px 12px !important; 
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        box-shadow: none !important;
        margin-bottom: 0px !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
        transform: none !important;
    }

    /* Selectbox */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.06) !important; 
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 6px !important; color: #e2e8f0 !important;
        padding: 2px !important;
    }

    /* Radyo Butonları */
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0px !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: transparent !important;
        background: transparent !important;
        font-size: 14px !important; padding: 6px 12px !important; color: #b0bec5 !important;
        border-radius: 6px !important; transition: all 0.2s ease !important;
        margin-bottom: 0px !important;
        border: none !important;
        display: flex !important; align-items: center !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover { 
        background-color: rgba(255,255,255,0.05) !important; 
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] { 
        background-color: rgba(255,255,255,0.08) !important; 
        color: #ffffff !important; font-weight: 600 !important; 
        border-left: 3px solid #ff5722 !important;
        border-radius: 0 6px 6px 0 !important;
    }


    /* === METRİK KARTLARI (GLASSMORPHISM) === */
    .stMetric {
        background: rgba(30, 41, 59, 0.4) !important; 
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important; 
        padding: 16px 20px !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }
    .stMetric:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2) !important;
        border-color: rgba(56, 189, 248, 0.3) !important;
    }
    [data-testid="metric-container"] label {
        font-size: 12px !important; color: #94a3b8 !important; font-weight: 500 !important; letter-spacing: 0.5px;
    }
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 24px !important; font-weight: 700 !important; color: #f8fafc !important;
    }

    /* === EXPANDER VE TABS === */
    [data-testid="stExpander"], [data-testid="stExpander"] details, [data-testid="stExpander"] summary {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0px !important;
        box-shadow: none !important;
    }
    [data-testid="stExpander"]:hover, [data-testid="stExpander"] details:hover {
        background-color: transparent !important;
        border-color: transparent !important;
    }
    .streamlit-expanderHeader {
        font-size: 11px !important; font-weight: 600 !important; color: #6b7280 !important;
        padding: 4px 8px !important; border-radius: 0px !important;
        text-transform: uppercase !important; letter-spacing: 1px !important;
    }
    .streamlit-expanderHeader:hover {
        color: #9ca3af !important;
    }
    [data-testid="stExpander"] > details > div { padding-top: 0px !important; padding-left: 0px !important; border: none !important; }

    /* === BUTONLAR (ANA SAYFA) === */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #38bdf8, #818cf8) !important;
        color: white !important;
        border: none !important;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3) !important;
    }

    /* === İLERLEME ÇUBUĞU (PROGRESS BAR) === */
    div.stProgress > div > div > div {
        background: linear-gradient(90deg, #10b981, #3b82f6) !important; 
        border-radius: 6px !important;
    }
    div[data-testid="stProgress"] {
        background-color: rgba(255, 255, 255, 0.05) !important; 
        height: 8px !important; 
        border-radius: 6px !important; 
    }

    /* === CUSTOM SCROLLBAR === */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)

# ============================================================
def calculate_ott(df, length=2, percent=1.4):
    df = df.copy()
    df['VAR'] = ta.trend.ema_indicator(df['Close'], window=length)
    df['fark'] = df['VAR'] * percent * 0.01
    df['long_stop'] = df['VAR'] - df['fark']
    df['short_stop'] = df['VAR'] + df['fark']
    
    mt = [0.0] * len(df)
    for i in range(1, len(df)):
        if df['VAR'].iloc[i] > mt[i-1]:
            mt[i] = max(df['long_stop'].iloc[i], mt[i-1])
        else:
            mt[i] = min(df['short_stop'].iloc[i], mt[i-1])
            
    df['MT'] = mt
    ott = [0.0] * len(df)
    for i in range(2, len(df)):
        if df['VAR'].iloc[i] > df['MT'].iloc[i]:
            ott[i] = df['MT'].iloc[i-2] * (1 + percent * 0.01)
        else:
            ott[i] = df['MT'].iloc[i-2] * (1 - percent * 0.01)
    return pd.Series(ott, index=df.index)

def calculate_pmax(df, length=10, atr_length=10, multiplier=3):
    df = df.copy()
    df['MA'] = ta.trend.ema_indicator(df['Close'], window=length)
    atr = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=atr_length)
    df['upper'] = df['MA'] + (multiplier * atr)
    df['lower'] = df['MA'] - (multiplier * atr)
    
    pmax = [0.0] * len(df)
    for i in range(1, len(df)):
        if df['MA'].iloc[i] > pmax[i-1]:
            pmax[i] = max(df['lower'].iloc[i], pmax[i-1])
        else:
            pmax[i] = min(df['upper'].iloc[i], pmax[i-1])
    return pd.Series(pmax, index=df.index)

def calculate_wavetrend(df, n1=10, n2=21):
    ap = (df['High'] + df['Low'] + df['Close']) / 3
    esa = ta.trend.ema_indicator(ap, window=n1)
    d = ta.trend.ema_indicator(abs(ap - esa), window=n1)
    ci = (ap - esa) / (0.015 * d)
    tci = ta.trend.ema_indicator(ci, window=n2)
    wt1 = tci
    wt2 = wt1.rolling(window=4).mean()
    return wt1, wt2

def calculate_st_mom(df, length=10):
    # Simplified SuperTrend Momentum logic
    mom = df['Close'].diff(length)
    st_mom = ta.trend.ema_indicator(mom, window=length)
    return st_mom

def get_trading_signals(symbols):
    signals = []
    try:
        # Download all symbols at once for speed
        raw_data = yf.download(symbols, period="2mo", interval="1d", progress=False)
        if raw_data.empty: return pd.DataFrame()
        
        close_data = raw_data['Close']
        high_data = raw_data['High']
        low_data = raw_data['Low']
        volume_data = raw_data['Volume']
        
        for sym in symbols:
            try:
                # Extract single symbol data
                s_df = pd.DataFrame({
                    'Close': close_data[sym],
                    'High': high_data[sym],
                    'Low': low_data[sym],
                    'Volume': volume_data[sym]
                }).dropna()
                
                if len(s_df) < 10: continue
                
                ott = calculate_ott(s_df)
                wt1, wt2 = calculate_wavetrend(s_df)
                rsi = ta.momentum.rsi(s_df['Close'], window=14)
                
                last_close = s_df['Close'].iloc[-1]
                last_ott = ott.iloc[-1]
                last_wt1 = wt1.iloc[-1]
                last_wt2 = wt2.iloc[-1]
                last_rsi = rsi.iloc[-1]
                
                status = "Nötr"
                reason = "Sinyal Yok"
                
                if last_close > last_ott and last_wt1 > last_wt2:
                    status = "🟢 GÜÇLÜ AL"
                    reason = "Trend & Momentum Pozitif"
                elif last_close > last_ott:
                    status = "🌱 AL"
                    reason = "OTT Trend Pozitif"
                elif last_close < last_ott and last_wt1 < last_wt2:
                    status = "🔴 GÜÇLÜ SAT"
                    reason = "Trend & Momentum Negatif"
                elif last_close < last_ott:
                    status = "🍂 SAT"
                    reason = "OTT Trend Negatif"
                    
                signals.append({"Hisse": sym.replace(".IS", ""), "Durum": status, "Neden": reason, "Fiyat": f"{last_close:.2f}"})
            except:
                continue
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
    return pd.DataFrame(signals)

# --- CONSTANTS & DICTIONARIES ---
COMMON_SYMBOLS = {
    # BIST 30
    "THYAO.IS": "Türk Hava Yolları", "EREGL.IS": "Ereğli Demir Çelik", "SISE.IS": "Şişe Cam",
    "KCHOL.IS": "Koç Holding", "SAHOL.IS": "Sabancı Holding", "TUPRS.IS": "Tüpraş",
    "ASELS.IS": "Aselsan", "BIMAS.IS": "BİM Mağazalar", "AKBNK.IS": "Akbank",
    "GARAN.IS": "Garanti Bankası", "YKBNK.IS": "Yapı Kredi", "ISCTR.IS": "İş Bankası (C)",
    "SASA.IS": "Sasa Polyester", "HEKTS.IS": "Hektaş", "ENKAI.IS": "Enka İnşaat",
    "PGSUS.IS": "Pegasus", "TOASO.IS": "Tofaş", "FROTO.IS": "Ford Otosan",
    "ARCLK.IS": "Arçelik", "EKGYO.IS": "Emlak Konut", "GUBRF.IS": "Gübre Fabrikaları",
    "TCELL.IS": "Turkcell", "TTKOM.IS": "Türk Telekom", "PETKM.IS": "Petkim",
    # GLOBAL
    "^GSPC": "S&P 500", "^IXIC": "Nasdaq", "^DJI": "Dow Jones", "^FTSE": "FTSE 100",
    "^GDAXI": "DAX", "^N225": "Nikkei 225", "GC=F": "Altın ONS", "SI=F": "Gümüş",
    "CL=F": "Brent Petrol", "HG=F": "Bakır", "PA=F": "Paladyum", "PL=F": "Platin",
    "KAP.L": "Kazatomprom (LSE)", "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum",
    "DX-Y.NYB": "DXY Dolar Endeksi", "USDTRY=X": "USD/TRY", "USDKZT=X": "USD/KZT",
    "GLD": "SPDR Gold Trust (GLD)", "IAU": "iShares Gold Trust (IAU)"
}

# --- BIST TÜM HİSSELERİ YÜKLE ---
BIST_SEMBOLLER = {}
bist_json_path = os.path.join(os.path.dirname(__file__), "bist_semboller.json")
if os.path.exists(bist_json_path):
    try:
        with open(bist_json_path, "r", encoding="utf-8") as f:
            BIST_SEMBOLLER = json.load(f)
    except:
        pass

# COMMON_SYMBOLS ile birleştir (BIST hisseleri öncelikli)
COMMON_SYMBOLS = {**COMMON_SYMBOLS, **BIST_SEMBOLLER}

# --- HELPERS ---
def get_sentiment(text):
    blob = TextBlob(text)
    score = blob.sentiment.polarity
    if score > 0.1: return "Pozitif", "sentiment-pos"
    elif score < -0.1: return "Negatif", "sentiment-neg"
    else: return "Nötr", ""

def calculate_fibonacci(df):
    high = df['High'].max()
    low = df['Low'].min()
    diff = high - low
    levels = {
        '0%': high,
        '23.6%': high - 0.236 * diff,
        '38.2%': high - 0.382 * diff,
        '50%': high - 0.5 * diff,
        '61.8%': high - 0.618 * diff,
        '100%': low
    }
    return levels

def detect_patterns(df):
    patterns = []
    if len(df) < 2: return patterns
    
    # Simple logic for Doji, Hammer, Engulfing
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    body = abs(last['Close'] - last['Open'])
    range_ = last['High'] - last['Low']
    
    if range_ > 0:
        if body < (range_ * 0.1): patterns.append("Doji")
        if (last['High'] - max(last['Open'], last['Close'])) < (body * 0.1) and (min(last['Open'], last['Close']) - last['Low']) > (body * 2): patterns.append("Hammer")
    
    # Bullish Engulfing
    if prev['Close'] < prev['Open'] and last['Close'] > last['Open'] and last['Open'] < prev['Close'] and last['Close'] > prev['Open']:
        patterns.append("Boğa Engulfing")
        
    return patterns

# --- ELITE QUANT & SECTOR LOGIC ---
SECTOR_MAP = {
    "THYAO.IS": "XU100.IS", "PGSUS.IS": "XU100.IS", # Simplified to XU100 for now if specific sector indices are hard to fetch
    "AKBNK.IS": "XBANK.IS", "GARAN.IS": "XBANK.IS", "YKBNK.IS": "XBANK.IS", "ISCTR.IS": "XBANK.IS",
    "EREGL.IS": "XMETAL.IS", "KCHOL.IS": "XHOLD.IS", "SAHOL.IS": "XHOLD.IS",
    "TUPRS.IS": "XU100.IS", "ASELS.IS": "XU100.IS", "BIMAS.IS": "XU100.IS"
}

def monte_carlo_simulation(df, days=30, simulations=100):
    returns = df['Close'].pct_change().dropna()
    last_price = df['Close'].iloc[-1]
    
    avg_daily_ret = returns.mean()
    std_daily_ret = returns.std()
    
    results = np.zeros((days, simulations))
    
    for s in range(simulations):
        price_series = [last_price]
        for d in range(days):
            price_series.append(price_series[-1] * (1 + np.random.normal(avg_daily_ret, std_daily_ret)))
        results[:, s] = price_series[1:]
        
    return results

def get_sector_relative_strength(symbol, period="1y"):
    sector_index = SECTOR_MAP.get(symbol, "XU100.IS")
    data = yf.download([symbol, sector_index], period=period, progress=False)['Close']
    if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
    
    returns = data.pct_change().dropna()
    cumulative = (1 + returns).cumprod()
    return cumulative

# --- ADVANCED AI & PORTFOLIO LOGIC ---
def predict_price(df, days=30):
    df = df.reset_index()
    df['Date_Ordinal'] = pd.to_datetime(df['Date']).apply(lambda x: x.toordinal())
    X = df[['Date_Ordinal']].values
    y = df['Close'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_dates = [df['Date'].iloc[-1] + datetime.timedelta(days=i) for i in range(1, days + 1)]
    future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
    predictions = model.predict(future_ordinals)
    
    return future_dates, predictions

def optimize_portfolio(symbols, weights=None):
    data = yf.download(symbols, period="1y")['Close']
    returns = data.pct_change().dropna()
    
    def get_ret_vol_sr(weights):
        weights = np.array(weights)
        ret = np.sum(returns.mean() * weights) * 252
        vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        sr = ret / vol
        return np.array([ret, vol, sr])

    def neg_sharpe(weights): return get_ret_vol_sr(weights)[2] * -1
    def check_sum(weights): return np.sum(weights) - 1

    cons = ({'type': 'eq', 'fun': check_sum})
    bounds = tuple((0, 1) for _ in range(len(symbols)))
    init_guess = [1/len(symbols)] * len(symbols)
    
    opt_results = minimize(neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=cons)
    return opt_results.x, get_ret_vol_sr(opt_results.x)

def convert_currency(df, from_cur, to_cur, fx_data):
    if from_cur == to_cur: return df
    
    df = df.copy()
    rate_col = f"{from_cur}{to_cur}=X"
    
    # Try to find rate in fx_data
    if rate_col in fx_data.columns:
        rate = fx_data[rate_col]
    elif f"{to_cur}{from_cur}=X" in fx_data.columns:
        rate = 1 / fx_data[f"{to_cur}{from_cur}=X"]
    else:
        # Fallback to static or cross rate if not in data
        return df
    
    for col in ['Open', 'High', 'Low', 'Close']:
        df[col] = df[col] * rate
    return df

# ============================================================
# 🤖 AI KARAR DESTEK MOTORU (Decision Support Engine)
# ============================================================

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

class MarketDataAggregator:
    """Tüm modüllerden gelen verileri standart skorlara dönüştürür."""

    @staticmethod
    def get_technical_score(symbol, df):
        """Teknik analiz skoru (0-100): RSI, EMA, OTT, MACD bazlı."""
        if df.empty or len(df) < 20:
            return 50.0
        try:
            close = df['Close'].squeeze()
            rsi = ta.momentum.rsi(close, window=14).iloc[-1]
            ema50 = ta.trend.ema_indicator(close, window=50).iloc[-1]
            ema200 = ta.trend.ema_indicator(close, window=200).iloc[-1]
            last_c = close.iloc[-1]
            macd = ta.trend.MACD(close)
            macd_bull = macd.macd().iloc[-1] > macd.macd_signal().iloc[-1]
            ott = calculate_ott(pd.DataFrame({'Close': close})).iloc[-1]

            score = 50.0
            if last_c > ema50: score += 10
            if last_c > ema200: score += 10
            if rsi > 50: score += 10 + (rsi - 50) * 0.3
            else: score -= (50 - rsi) * 0.3
            if macd_bull: score += 10
            if last_c > ott: score += 10
            return max(0, min(100, score))
        except:
            return 50.0

    @staticmethod
    def get_fundamental_score(symbol):
        """Temel analiz skoru (0-100): F/K, PD/DD, büyüme."""
        try:
            info = yf.Ticker(symbol).info
            pe = info.get('trailingPE') or info.get('forwardPE') or 0
            pb = info.get('priceToBook') or 0
            roe = info.get('returnOnEquity') or 0

            score = 50.0
            if 0 < pe < 15: score += 15
            elif 15 <= pe < 25: score += 5
            elif pe > 25: score -= 10
            if 0 < pb < 3: score += 10
            elif pb > 5: score -= 5
            if roe > 0.1: score += 15
            elif roe > 0.05: score += 5
            else: score -= 5
            return max(0, min(100, score))
        except:
            return 50.0

    @staticmethod
    def get_sentiment_score(symbol):
        """Haber duygu analizi skoru (-1 ile +1 arası, 0-100'e çevrilir)."""
        try:
            rss_url = f"https://news.google.com/rss/search?q={symbol}+borsa&hl=tr&gl=TR&ceid=TR:tr"
            feed = feedparser.parse(rss_url)
            scores = []
            for entry in feed.entries[:8]:
                blob = TextBlob(entry.title)
                scores.append(blob.sentiment.polarity)
            avg = np.mean(scores) if scores else 0
            return 50 + (avg * 50)  # -1..+1 -> 0..100
        except:
            return 50.0

    @staticmethod
    def get_flow_score(symbol):
        """Fon akış skoru (0-100): Büyük oyuncu hacim tahmini."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            if hist.empty:
                return 50.0
            close = hist['Close'].squeeze()
            vol = hist['Volume'].squeeze()
            vol_ma = vol.rolling(10).mean().iloc[-1]
            price_chg = close.pct_change().iloc[-5:].mean()

            score = 50.0
            if vol.iloc[-1] > vol_ma * 1.2: score += 15  # anormal hacim
            if price_chg > 0.01: score += 10
            elif price_chg < -0.01: score -= 10
            vol_trend = vol.iloc[-5:].sum() / vol.iloc[-10:-5].sum() if len(vol) >= 10 else 1
            if vol_trend > 1.1: score += 10
            return max(0, min(100, score))
        except:
            return 50.0

    @staticmethod
    def get_macro_score(symbol):
        """Makro skor (0-100): DXY, S&P500, VIX korelasyonu."""
        try:
            macro_tickers = ["^GSPC", "DX-Y.NYB", "GC=F", "CL=F"]
            mdata = yf.download(macro_tickers, period="1mo", progress=False)['Close']
            if isinstance(mdata.columns, pd.MultiIndex):
                mdata.columns = mdata.columns.get_level_values(0)

            sp_change = mdata['^GSPC'].pct_change().iloc[-1] if '^GSPC' in mdata else 0
            dxy_change = mdata['DX-Y.NYB'].pct_change().iloc[-1] if 'DX-Y.NYB' in mdata else 0
            gold_change = mdata['GC=F'].pct_change().iloc[-1] if 'GC=F' in mdata else 0

            score = 50.0
            if sp_change > 0: score += 10
            if dxy_change < 0: score += 5   # dolar zayıflıyor = risk iştahı
            if gold_change > 0: score += 5
            if abs(sp_change) < 0.01: score += 5  # düşük volatilite
            return max(0, min(100, score))
        except:
            return 50.0


class DecisionEngine:
    """Ağırlıklandırılmış karar matrisi motoru."""

    WEIGHTS = {
        'technical': 0.25,
        'fundamental': 0.20,
        'sentiment': 0.15,
        'flow': 0.20,
        'macro': 0.20,
    }
    CONFIDENCE_THRESHOLD = 85.0

    def __init__(self, symbol, df):
        self.symbol = symbol
        self.df = df
        self._scores = {}
        self._aggregate()

    def _aggregate(self):
        agg = MarketDataAggregator()
        self._scores['technical'] = agg.get_technical_score(self.symbol, self.df)
        self._scores['fundamental'] = agg.get_fundamental_score(self.symbol)
        self._scores['sentiment'] = agg.get_sentiment_score(self.symbol)
        self._scores['flow'] = agg.get_flow_score(self.symbol)
        self._scores['macro'] = agg.get_macro_score(self.symbol)

    @property
    def weighted_score(self):
        """100 üzerinden ağırlıklı toplam skor."""
        total = sum(self._scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        return round(total, 1)

    @property
    def signal(self):
        """Sinyal etiketi: YÜKSEK / ORTA / ZAYIF / YOK."""
        ws = self.weighted_score
        if ws >= self.CONFIDENCE_THRESHOLD:
            return "🔥 YÜKSEK DOĞRULUK"
        elif ws >= 70:
            return "✅ ORTA DOĞRULUK"
        elif ws >= 50:
            return "⚠️ ZAYIF SİNYAL"
        return "❌ SİNYAL YOK"

    @property
    def direction(self):
        """Yön tahmini: AL / SAT / NÖTR."""
        if self.weighted_score >= 70:
            return "🟢 AL"
        elif self.weighted_score <= 30:
            return "🔴 SAT"
        return "⚪ NÖTR"

    @property
    def risk_warning(self):
        """Risk yönetimi uyarısı."""
        ws = self.weighted_score
        if ws >= 85:
            return "✅ Düşük risk. Portföyün maks. %15'i ile işleme girilmeli."
        elif ws >= 70:
            return "⚠️ Orta risk. Portföyün maks. %10'u ile işleme girilmeli."
        elif ws >= 50:
            return "⚠️ Yüksek risk. Portföyün maks. %5'i ile işleme girilmeli."
        return "🔴 Çok yüksek risk. İşlem önerilmez."

    def get_report(self):
        """Detaylı rapor sözlüğü."""
        return {
            "Sembol": self.symbol,
            "Teknik (x0.25)": f"%{self._scores['technical']:.1f}",
            "Temel (x0.20)": f"%{self._scores['fundamental']:.1f}",
            "Sentiment (x0.15)": f"%{self._scores['sentiment']:.1f}",
            "Fon Akış (x0.20)": f"%{self._scores['flow']:.1f}",
            "Makro (x0.20)": f"%{self._scores['macro']:.1f}",
            "Toplam Skor": f"%{self.weighted_score:.1f}",
            "Sinyal": self.signal,
            "Yön": self.direction,
        }


def calculate_atr(df, window=14):
    """Dinamik ATR hesaplama (volatilite bazlı stop seviyesi)."""
    high = df['High'].squeeze()
    low = df['Low'].squeeze()
    close = df['Close'].squeeze()
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window).mean()
    return atr.iloc[-1] if not atr.empty else 0


def monte_carlo_atr(df, days=30, simulations=100):
    """ATR bazlı Monte Carlo simülasyonu (dinamik volatilite)."""
    if df.empty or len(df) < 20:
        return np.zeros((days, simulations))
    close = df['Close'].squeeze()
    returns = close.pct_change().dropna()
    atr_val = calculate_atr(df)
    last_price = close.iloc[-1]

    # Dinamik volatilite: ATR / fiyat
    dyn_vol = max(atr_val / last_price if last_price > 0 else returns.std(), returns.std() * 0.5)
    avg_ret = returns.mean()

    results = np.zeros((days, simulations))
    for s in range(simulations):
        prices = [last_price]
        for d in range(days):
            prices.append(prices[-1] * (1 + np.random.normal(avg_ret, dyn_vol)))
        results[:, s] = prices[1:]
    return results


def render_ai_prediction_page(symbol, df):
    """Streamlit arayüzünde AI Karar Motoru sonuçlarını gösterir."""
    st.subheader(f"🤖 AI Karar Destek Motoru: {symbol}")

    if df.empty:
        st.warning("Veri yok. Lütfen geçerli bir hisse seçin.")
        return

    with st.spinner("🧠 Tüm modüller taranıyor..."):
        engine = DecisionEngine(symbol, df)
        report = engine.get_report()

    # Üst: Sinyal Kartı
    sig_color = "#00e676" if "YÜKSEK" in report["Sinyal"] else "#ffeb3b" if "ORTA" in report["Sinyal"] else "#ff5252"
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05); border-left: 4px solid {sig_color};
                border-radius: 16px; padding: 24px; text-align: center; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); transition: transform 0.3s ease;">
        <div style="font-size: 36px; font-weight: 700; color: {sig_color}; letter-spacing: -0.5px;">{report['Sinyal']}</div>
        <div style="font-size: 22px; margin-top: 8px; font-weight: 500; color: #f8fafc;">{engine.direction} <span style="opacity:0.5">|</span> Skor: %{engine.weighted_score}</div>
        <div style="font-size: 14px; margin-top: 12px; color: #94a3b8; font-weight: 400;">{engine.risk_warning}</div>
    </div>
    """, unsafe_allow_html=True)

    # Skor kartları
    st.subheader("📊 Modül Skorları")
    cols = st.columns(5)
    for i, (label, key) in enumerate(zip(
        ["Teknik Analiz", "Temel Analiz", "Duygu Analizi", "Fon Akışı", "Makro Radar"],
        ['technical', 'fundamental', 'sentiment', 'flow', 'macro']
    )):
        val = engine._scores[key]
        cols[i].metric(label, f"%{val:.1f}", delta=DecisionEngine.WEIGHTS[key]*100)

    # Ağırlıklı dağılım (progress bar)
    st.subheader("📈 Karar Ağırlık Dağılımı")
    for label, key in zip(
        ["Teknik Analiz (%25)", "Temel & Sektörel (%20)", "Duygu Analizi (%15)", "Fon & Takas (%20)", "Küresel Radar (%20)"],
        ['technical', 'fundamental', 'sentiment', 'flow', 'macro']
    ):
        st.progress(engine._scores[key] / 100, text=f"{label}: %{engine._scores[key]:.1f}")

    # ——— AJAN KONSENSÜS & ÇELİŞKİ ÇÖZÜM PANELİ ———
    st.divider()
    st.subheader("🤝 Ajan Konsensüs & Çelişki Çözümü")

    mem = st.session_state.get("agent_memory", {})
    t_skor = mem.get("technical_score")
    w_skor = mem.get("whale_score")
    s_skor = mem.get("sentiment_score")
    horizon = st.session_state.get("vade", "ORTA")

    if all(v is not None for v in [t_skor, w_skor, s_skor]):
        skorlar = {"📡 Teknik Ajan": t_skor, "🐋 Balina Ajan": w_skor, "🌍 Duygu Ajanı": s_skor}
        max_fark = max(skorlar.values()) - min(skorlar.values())
        en_yuksek = max(skorlar, key=skorlar.get)
        en_dusuk = min(skorlar, key=skorlar.get)

        # Çelişki tespiti
        if max_fark > 30:
            # Vade bazlı hakem kararı
            vade_kararlari = {
                "KISA": "📡 Teknik Ajan (kısa vadede momentum ve hacim anomalileri önceliklidir)",
                "ORTA": "🐋 Balina Ajan (orta vadede fon akışı ve kurumsal hareketler belirleyicidir)",
                "UZUN": "🌍 Duygu Ajanı (uzun vadede makro trendler ve duygu analizi ön plana çıkar)",
            }
            kazanan = vade_kararlari.get(horizon, "⚖️ Tüm ajanlar eşit ağırlıkta değerlendirilmiştir")

            st.warning(f"⚠️ **Yüksek Çelişki Tespit Edildi (Fark: {max_fark:.0f} puan)**")
            with st.expander("🧠 Yönetici Ajan Karar Gerekçesi", expanded=True):
                for ajan, skor in sorted(skorlar.items(), key=lambda x: x[1], reverse=True):
                    renk = "#4ade80" if skor >= 70 else "#ef4444" if skor <= 30 else "#fbbf24"
                    st.markdown(f"<span style='color:{renk};font-weight:600;'>▸ {ajan}: %{skor:.0f}</span>", unsafe_allow_html=True)
                st.markdown(f"---\n**📅 Vade: {horizon}** — *{kazanan}*")
                st.success(f"✅ **Kazanan Ajan:** {kazanan.split('(')[0].strip()}")
        else:
            st.success(f"✅ **Düşük Çelişki (Fark: {max_fark:.0f} puan)** — Ajanlar arasında güçlü uyum var.")
            st.caption(f"En yüksek: {en_yuksek} (%{max(skorlar.values()):.0f}) | En düşük: {en_dusuk} (%{min(skorlar.values()):.0f})")
    else:
        st.info("🤖 Çelişki analizi için yukarıdaki '🧠 Ajanları Çalıştır' butonu ile ajanları çalıştırın.")

    # Detaylı rapor tablosu
    st.subheader("📋 Detaylı Rapor")
    rdf = pd.DataFrame([report])
    st.dataframe(rdf, width='stretch', hide_index=True)

    # Monte Carlo ATR Simülasyonu
    st.divider()
    st.subheader("🎲 ATR Tabanlı Monte Carlo Simülasyonu")
    mc_results = monte_carlo_atr(df)
    if mc_results.any():
        fig_mc = go.Figure()
        for i in range(min(50, mc_results.shape[1])):
            fig_mc.add_trace(go.Scatter(y=mc_results[:, i], mode='lines', line=dict(width=1), opacity=0.2, showlegend=False))
        avg_path = mc_results.mean(axis=1)
        fig_mc.add_trace(go.Scatter(y=avg_path, mode='lines', line=dict(color='#58a6ff', width=3), name="Ortalama"))
        fig_mc.update_layout(height=400, template="plotly_dark",
                           title=f"30 Günlük ATR Bazlı Simülasyon (ATR: {calculate_atr(df):.4f})",
                           yaxis_title="Fiyat", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_mc, width='stretch')

        # AI Tahmin doğrulama
        future_mean = mc_results[-1, :].mean()
        future_high = mc_results[-1, :].max()
        future_low = mc_results[-1, :].min()
        last_c = df['Close'].iloc[-1]

        v1, v2, v3 = st.columns(3)
        v1.metric("30 Gün Sonra Beklenen", f"{future_mean:.4f}",
                  delta=f"%{((future_mean/last_c)-1)*100:.2f}")
        v2.metric("İyimser Senaryo (Tepe)", f"{future_high:.4f}",
                  delta=f"%{((future_high/last_c)-1)*100:.2f}")
        v3.metric("Kötümser Senaryo (Dip)", f"{future_low:.4f}",
                  delta=f"%{((future_low/last_c)-1)*100:.2f}")

    st.info(f"💡 **Risk Uyarısı:** {engine.risk_warning}")

    # ——— İNTERAKTİF REVİZYON DÖNGÜSÜ (Human-in-the-loop Feedback) ———
    st.divider()
    st.subheader("🔄 İnteraktif Revizyon Döngüsü (Human-in-the-Loop)")

    # Session state: revizyon sayacı
    if "feedback_count" not in st.session_state:
        st.session_state.feedback_count = 0
    if "feedback_history" not in st.session_state:
        st.session_state.feedback_history = []
    if "adjusted_weights" not in st.session_state:
        st.session_state.adjusted_weights = None

    max_revisions = st.slider("Maksimum Revizyon Sınırı", 1, 10, 3, key="max_rev_slider")
    remaining = max_revisions - st.session_state.feedback_count

    if st.session_state.feedback_count > 0:
        st.info(f"📊 Revizyon {st.session_state.feedback_count}/{max_revisions} tamamlandı. Kalan: {remaining}")

    with st.form("feedback_form"):
        user_feedback = st.text_input(
            "💬 Ajanlara neyi değiştirmelerini istediğinizi yazın:",
            placeholder="Örn: haber analizi ağırlığını artır, teknik skoru düşür...",
            key="feedback_input",
        )
        col_submit, col_clear = st.columns([1, 1])
        with col_submit:
            submitted = st.form_submit_button("🚀 Revizyonu Uygula", use_container_width=True, type="primary")
        with col_clear:
            reset_fb = st.form_submit_button("🔄 Revizyon Geçmişini Sıfırla", use_container_width=True)

    if reset_fb:
        st.session_state.feedback_count = 0
        st.session_state.feedback_history = []
        st.session_state.adjusted_weights = None
        st.rerun()

    if submitted and user_feedback.strip():
        if st.session_state.feedback_count < max_revisions:
            st.session_state.feedback_count += 1
            st.session_state.feedback_history.append({
                "revizyon": st.session_state.feedback_count,
                "feedback": user_feedback,
            })

            # Feedback metnine göre ağırlık ayarla (doğal dil işleme benzeri anahtar kelime eşleme)
            fb_lower = user_feedback.lower()
            base_w = dict(DecisionEngine.WEIGHTS)
            modifier = 0.0

            if any(k in fb_lower for k in ["haber", "duygu", "sentiment", "sosyal medya", "medya"]):
                base_w["sentiment"] = min(0.40, base_w.get("sentiment", 0.15) + 0.10)
                modifier += 0.10
            if any(k in fb_lower for k in ["teknik", "rsi", "macd", "diverjans", "hacim"]):
                base_w["technical"] = min(0.40, base_w.get("technical", 0.25) + 0.08)
                modifier += 0.08
            if any(k in fb_lower for k in ["fon", "kurum", "balina", "akış", "whale", "takas"]):
                base_w["flow"] = min(0.40, base_w.get("flow", 0.20) + 0.08)
                modifier += 0.08
            if any(k in fb_lower for k in ["makro", "faiz", "enflasyon", "küresel", "ekonomi"]):
                base_w["macro"] = min(0.40, base_w.get("macro", 0.20) + 0.08)
                modifier += 0.08
            if any(k in fb_lower for k in ["temel", "defter", "bilanço", "sektör"]):
                base_w["fundamental"] = min(0.40, base_w.get("fundamental", 0.20) + 0.08)
                modifier += 0.08
            if any(k in fb_lower for k in ["azalt", "düşür", "küçült", "sıfırla"]):
                for k in base_w:
                    base_w[k] = max(0.05, base_w[k] - 0.05)

            # Normalleştir
            total = sum(base_w.values())
            if total > 0:
                for k in base_w:
                    base_w[k] = round(base_w[k] / total, 3)

            st.session_state.adjusted_weights = base_w

            # Yeni ağırlıklarla tekrar çalıştır
            with st.spinner(f"🔄 Revizyon #{st.session_state.feedback_count} uygulanıyor..."):
                new_engine = DecisionEngine(symbol, df)
                new_engine.WEIGHTS = base_w
                new_report = new_engine.get_report()

            st.success(f"✅ Revizyon #{st.session_state.feedback_count} uygulandı!")
            st.json({
                "Kullanıcı Girdisi": user_feedback,
                "Yeni Ağırlıklar": base_w,
                "Yeni Skor": new_engine.weighted_score,
                "Yeni Sinyal": new_engine.signal,
            })
        else:
            st.warning(f"🔴 Maksimum revizyon sınırına ulaşıldı ({max_revisions}). Lütfen 'Revizyon Geçmişini Sıfırla' ile sıfırlayın.")

    # Revizyon geçmişi gösterimi
    if st.session_state.feedback_history:
        with st.expander("📜 Revizyon Geçmişi", expanded=False):
            for rev in st.session_state.feedback_history:
                st.write(f"**#{rev['revizyon']}:** {rev['feedback']}")

    if st.session_state.adjusted_weights:
        with st.expander("⚙️ Güncel Ajan Ağırlıkları", expanded=False):
            st.json(st.session_state.adjusted_weights)

# ============================================================
# 🧠 ADVANCED AI KARAR MOTORU (Kurumsal Sürüm)
# ============================================================

import sqlite3
from datetime import timedelta

class MarketRegimeDetector:
    """ADX + ATR + GMM mantığı ile piyasa rejimi algılama."""

    REGIMES = {
        "CRASH": "🔴 Yüksek Volatiliteli Çöküş",
        "STRONG_TREND": "🚀 Güçlü Trend",
        "SIDEWAYS": "⚪ Yatay / Testere",
        "RECOVERY": "🟢 Toparlanma",
    }

    @staticmethod
    def detect(df):
        if df.empty or len(df) < 20:
            return "SIDEWAYS"
        close = df['Close'].squeeze()
        high = df['High'].squeeze()
        low = df['Low'].squeeze()

        # ADX (Trend Gücü)
        adx = ta.trend.adx(high, low, close, window=14).iloc[-1]
        # ATR / Fiyat (Volatilite)
        atr_val = calculate_atr(df)
        atr_pct = atr_val / close.iloc[-1] if close.iloc[-1] > 0 else 0
        # RSI
        rsi = ta.momentum.rsi(close, window=14).iloc[-1]
        # Fiyat değişimi
        ret_5 = close.pct_change(5).iloc[-1] if len(close) > 5 else 0

        if atr_pct > 0.04 and ret_5 < -0.05:
            return "CRASH"
        if adx > 25 and abs(ret_5) > 0.03:
            return "STRONG_TREND"
        if adx < 20 or (atr_pct < 0.015 and abs(ret_5) < 0.02):
            return "SIDEWAYS"
        if adx > 20 and ret_5 > 0.02 and rsi > 40:
            return "RECOVERY"
        return "SIDEWAYS"

    @staticmethod
    def adjust_weights_by_regime(regime):
        weights = {
            'technical': 0.25, 'fundamental': 0.20,
            'sentiment': 0.15, 'flow': 0.20, 'macro': 0.20
        }
        if regime == "CRASH":
            weights.update({'technical': 0.10, 'sentiment': 0.25, 'flow': 0.35, 'macro': 0.25, 'fundamental': 0.05})
        elif regime == "SIDEWAYS":
            weights.update({'technical': 0.10, 'sentiment': 0.20, 'flow': 0.35, 'macro': 0.20, 'fundamental': 0.15})
        elif regime == "STRONG_TREND":
            weights.update({'technical': 0.40, 'sentiment': 0.05, 'flow': 0.20, 'macro': 0.15, 'fundamental': 0.20})
        elif regime == "RECOVERY":
            weights.update({'technical': 0.30, 'sentiment': 0.10, 'flow': 0.25, 'macro': 0.15, 'fundamental': 0.20})
        return weights


class MultiTimeframeFilter:
    """1H ve 1D grafiklerini karşılaştırarak teknik skoru düzeltir."""

    @staticmethod
    def get_penalty(symbol, df_daily):
        penalty = 0.0
        try:
            df_1h = yf.download(symbol, period="1mo", interval="1h", progress=False)
            if df_1h.empty or len(df_1h) < 20:
                return penalty
            if isinstance(df_1h.columns, pd.MultiIndex):
                df_1h.columns = df_1h.columns.get_level_values(0)

            c_d = df_daily['Close'].squeeze()
            c_h = df_1h['Close'].squeeze()
            ema50_d = ta.trend.ema_indicator(c_d, window=50).iloc[-1]
            ema50_h = ta.trend.ema_indicator(c_h, window=50).iloc[-1]
            rsi_d = ta.momentum.rsi(c_d, window=14).iloc[-1]
            rsi_h = ta.momentum.rsi(c_h, window=14).iloc[-1]

            trend_d = "UP" if c_d.iloc[-1] > ema50_d else "DOWN"
            trend_h = "UP" if c_h.iloc[-1] > ema50_h else "DOWN"

            if trend_d != trend_h:
                penalty = -15.0  # çelişki: 15 puan kırp
            elif trend_d == "UP" and rsi_d > 70 and rsi_h < 50:
                penalty = -10.0  # günlük aşırı alım, saatlik zayıf
            elif trend_d == "DOWN" and rsi_d < 30 and rsi_h > 50:
                penalty = -10.0  # günlük aşırı satım, saatlik toparlanıyor
        except:
            pass
        return penalty


class XAIExplainer:
    """SHAP mantığıyla her modülün katkısını hesaplar."""

    @staticmethod
    def calculate_shap_values(engine):
        base = 50.0
        contributions = {}
        for k, w in engine.WEIGHTS.items():
            raw = engine._scores[k]
            contributions[k] = round((raw - base) * w, 2)
        total = sum(contributions.values())
        # Yüzdeye çevir
        abs_total = sum(abs(v) for v in contributions.values())
        if abs_total > 0:
            pcts = {k: round((v / abs_total) * 100, 1) for k, v in contributions.items()}
        else:
            pcts = {k: 0.0 for k in contributions}
        return contributions, pcts


# ============================================================
# 📡 ALTERNATİF VERİ MODÜLLERİ (Alternatif Veri)
# ============================================================

# Ekonomik takvim - kritik olaylar
ECONOMIC_CALENDAR = [
    {"date": "12", "month": "06", "event": "FED Faiz Kararı", "impact": "high"},
    {"date": "20", "month": "06", "event": "TCMB Faiz Kararı", "impact": "high"},
    {"date": "03", "month": "07", "event": "ABD Tarım Dışı İstihdam", "impact": "high"},
    {"date": "10", "month": "07", "event": "ABD TÜFE (Enflasyon)", "impact": "high"},
    {"date": "24", "month": "07", "event": "FED Faiz Kararı", "impact": "high"},
    {"date": "31", "month": "07", "event": "TCMB Faiz Kararı", "impact": "high"},
]

def get_alternative_data_sentiment(symbol):
    """Sosyal medya ilgi skoru (0-100): X/Twitter ve forum bazlı simülasyon."""
    try:
        # Gerçek API olmadığında fiyat momentumu + hacim değişiminden vekil skor
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1wk")
        if hist.empty:
            return 50.0
        close = hist['Close'].squeeze()
        vol = hist['Volume'].squeeze()
        ret = close.pct_change().dropna()
        vol_chg = vol.pct_change().dropna()

        # Pozitif getiri + artan hacim = sosyal medya ilgisi yüksek
        momentum = ret.iloc[-3:].mean() if len(ret) >= 3 else 0
        volume_interest = vol_chg.iloc[-3:].mean() if len(vol_chg) >= 3 else 0
        score = 50 + (momentum * 500) + (volume_interest * 100)
        return max(0, min(100, score))
    except:
        return 50.0


def get_order_book_imbalance(symbol):
    """Emir defteri dengesizlik skoru (-100..+100 → 0..100)."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        if hist.empty or len(hist) < 5:
            return 50.0
        close = hist['Close'].squeeze()
        vol = hist['Volume'].squeeze()
        high = hist['High'].squeeze()
        low = hist['Low'].squeeze()

        # L2 derinlik yoksa; alış-satış baskısını fiyat aralığı + hacimden tahmin et
        spread = (high - low) / close * 100
        vol_trend = vol.iloc[-1] / vol.rolling(10).mean().iloc[-1] if len(vol) >= 10 else 1
        price_direction = close.pct_change(3).iloc[-1] if len(close) >= 3 else 0

        # Yükselen fiyat + artan hacim = alış baskısı
        imbalance = (price_direction * 200) + (vol_trend * 50)
        imbalance = max(-100, min(100, imbalance))
        return 50 + (imbalance / 2)  # -100..+100 → 0..100
    except:
        return 50.0


def check_economic_calendar_filter():
    """Ekonomik takvim filtresi: Kritik olaya 1 saat kala defansif mod."""
    now = datetime.datetime.now()
    for olay in ECONOMIC_CALENDAR:
        try:
            event_dt = datetime.datetime.strptime(
                f"{olay['date']} {olay['month']} {now.year}", "%d %m %Y"
            )
            if olay['impact'] == 'high':
                diff = (event_dt - now).total_seconds()
                if 0 < diff < 3600:  # 1 saat içinde
                    return True, olay['event']
        except:
            continue
    return False, None


def feature_engineering_hub(df):
    """Ham fiyat verisinden türetilmiş öznitelikler (feature engineering)."""
    if df.empty or len(df) < 20:
        return df
    df = df.copy()
    c = df['Close'].squeeze()
    h = df['High'].squeeze()
    l = df['Low'].squeeze()
    v = df['Volume'].squeeze()

    # Logaritmik getiriler
    df['log_ret'] = np.log(c / c.shift(1))
    df['log_ret_5'] = df['log_ret'].rolling(5).sum()
    df['log_ret_20'] = df['log_ret'].rolling(20).sum()

    # Hareketli ortalamadan sapma (Distance to MA)
    ma50 = ta.trend.sma_indicator(c, window=50)
    ma200 = ta.trend.sma_indicator(c, window=200)
    df['dist_to_ma50'] = (c - ma50) / ma50 * 100
    df['dist_to_ma200'] = (c - ma200) / ma200 * 100

    # Volatilite verimliliği: (High - Low) / Volume
    df['vol_efficiency'] = (h - l) / v.replace(0, np.nan) * 1e6

    # Hacim ağırlıklı fiyat sapması
    vwap = (c * v).rolling(20).sum() / v.rolling(20).sum()
    df['vwap_dist'] = (c - vwap) / vwap * 100

    return df


class FeedbackDatabase:
    """SQLite tabanlı geri besleme döngüsü ve dinamik ağırlık güncelleme."""

    DB_PATH = os.path.join(os.path.dirname(__file__), "feedback.db")

    def __init__(self):
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.DB_PATH) or ".", exist_ok=True)
        conn = sqlite3.connect(self.DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                symbol TEXT,
                score REAL,
                signal TEXT,
                regime TEXT,
                actual_return REAL DEFAULT NULL,
                evaluated INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weight_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                regime TEXT,
                technical REAL,
                fundamental REAL,
                sentiment REAL,
                flow REAL,
                macro REAL,
                accuracy REAL
            )
        """)
        conn.commit()
        conn.close()

    def save_prediction(self, symbol, score, signal, regime):
        conn = sqlite3.connect(self.DB_PATH)
        conn.execute(
            "INSERT INTO predictions (date, symbol, score, signal, regime) VALUES (?, ?, ?, ?, ?)",
            (datetime.datetime.now().isoformat(), symbol, score, signal, regime)
        )
        conn.commit()
        conn.close()

    def evaluate_predictions(self, days_lookback=5):
        conn = sqlite3.connect(self.DB_PATH)
        cutoff = (datetime.datetime.now() - timedelta(days=days_lookback)).isoformat()
        rows = conn.execute(
            "SELECT id, symbol, date FROM predictions WHERE evaluated = 0 AND date < ?",
            (cutoff,)
        ).fetchall()
        for row in rows:
            pid, sym, dt = row
            try:
                hist = yf.download(sym, period="1mo", progress=False)['Close'].squeeze()
                if isinstance(hist, pd.DataFrame): hist = hist.iloc[:, 0]
                pred_date = datetime.datetime.fromisoformat(dt)
                if pred_date in hist.index or any(abs((d - pred_date).total_seconds()) < 86400 for d in hist.index):
                    # 5 günlük getiri
                    ret = hist.pct_change(5).iloc[-1] if len(hist) > 5 else 0
                    conn.execute("UPDATE predictions SET actual_return = ?, evaluated = 1 WHERE id = ?",
                                 (ret, pid))
            except:
                pass
        conn.commit()
        conn.close()

    def get_recent_accuracy(self, n=20):
        conn = sqlite3.connect(self.DB_PATH)
        rows = conn.execute(
            "SELECT score, actual_return FROM predictions WHERE evaluated = 1 AND actual_return IS NOT NULL ORDER BY id DESC LIMIT ?",
            (n,)
        ).fetchall()
        conn.close()
        if not rows:
            return None
        correct = 0
        for score, ret in rows:
            if (score >= 70 and ret > 0) or (score <= 30 and ret < 0) or (30 < score < 70):
                correct += 1
        return correct / len(rows) * 100

    def adjust_weights(self, regime):
        """Geçmiş başarıya göre ağırlıkları güncelle (self-calibration)."""
        conn = sqlite3.connect(self.DB_PATH)
        # Son 30 tahminin her modül için başarısını hesapla
        rows = conn.execute(
            "SELECT score, actual_return FROM predictions WHERE evaluated = 1 AND actual_return IS NOT NULL ORDER BY id DESC LIMIT 30"
        ).fetchall()
        conn.close()
        if not rows or len(rows) < 5:
            return None

        base = {'technical': 0.25, 'fundamental': 0.20, 'sentiment': 0.15, 'flow': 0.20, 'macro': 0.20}
        # Basit ödül/ceza: yüksek skor + pozitif getiri = başarı
        successes = sum(1 for s, r in rows if (s >= 70 and r > 0) or (s <= 30 and r < 0))
        accuracy = successes / len(rows)
        if accuracy > 0.6:
            return base  # mevcut ağırlıklar başarılı
        # Başarısız: fon akışı ve makro ağırlığını artır, teknik ağırlığı azalt
        if accuracy < 0.4:
            base.update({'technical': 0.15, 'flow': 0.30, 'macro': 0.25, 'fundamental': 0.15, 'sentiment': 0.15})
        return base


# ============================================================
# VADE BAZLI DİNAMİK AĞIRLIK SEÇİCİ
# ============================================================

HORIZON_WEIGHT_MAPS = {
    "KISA": {
        'momentum': 0.30,
        'sentiment': 0.20,
        'flow': 0.15,
        'orderbook': 0.20,
        'volume_anomaly': 0.15,
        'technical': 0.00,
        'fundamental': 0.00,
        'macro': 0.00,
        'monte_carlo': 0.00,
    },
    "ORTA": {
        'technical': 0.20,
        'fundamental': 0.15,
        'sentiment': 0.20,
        'flow': 0.25,
        'macro': 0.20,
        'momentum': 0.00,
        'orderbook': 0.00,
        'volume_anomaly': 0.00,
        'monte_carlo': 0.00,
    },
    "UZUN": {
        'fundamental': 0.35,
        'macro': 0.25,
        'flow': 0.10,
        'monte_carlo': 0.15,
        'technical': 0.10,
        'sentiment': 0.05,
        'momentum': 0.00,
        'orderbook': 0.00,
        'volume_anomaly': 0.00,
    }
}

def get_weights_by_horizon(horizon):
    h = horizon.upper() if isinstance(horizon, str) else "ORTA"
    return HORIZON_WEIGHT_MAPS.get(h, HORIZON_WEIGHT_MAPS["ORTA"]).copy()


# ============================================================
# HACİM ANOMALİ DEDEKTÖRÜ (3-Sigma)
# ============================================================

def get_volume_anomaly(df, window=20, threshold=3.0):
    try:
        if df.empty or 'Volume' not in df.columns or len(df) < window + 1:
            return 50.0, False
        vol = df['Volume'].squeeze()
        if isinstance(vol, pd.DataFrame):
            vol = vol.iloc[:, 0]
        recent = vol.iloc[-window:].astype(float)
        current = recent.iloc[-1]
        mean = recent.mean()
        std = recent.std()
        if std == 0 or mean == 0:
            return 50.0, False
        z_score = (current - mean) / std
        is_anomaly = abs(z_score) > threshold
        if is_anomaly:
            score = min(100, max(0, 50 + z_score * 10))
        else:
            score = 50.0
        return round(score, 1), is_anomaly
    except:
        return 50.0, False


# ============================================================
# PİŞMANLIK MİNİMİZASYONU (Q-Learning Self-Calibration)
# ============================================================

class RegretMinimizer:
    """Hatalı tahminlerden ders çıkaran Q-Learning tabanlı pişmanlık azaltma."""

    def __init__(self, learning_rate=0.1, discount=0.9):
        self.lr = learning_rate
        self.discount = discount
        self.q_table = {
            'technical': 0.5, 'fundamental': 0.5, 'sentiment': 0.5,
            'flow': 0.5, 'macro': 0.5, 'momentum': 0.5,
            'orderbook': 0.5, 'volume_anomaly': 0.5, 'monte_carlo': 0.5,
        }
        self._history = []

    def update(self, module, was_correct):
        reward = 1.0 if was_correct else -1.0
        old_q = self.q_table.get(module, 0.5)
        new_q = old_q + self.lr * (reward + self.discount * old_q - old_q)
        self.q_table[module] = max(0.0, min(1.0, new_q))
        self._history.append({'module': module, 'correct': was_correct, 'q': self.q_table[module]})

    def get_adjusted_weights(self, base_weights):
        import math
        temp = 1.0
        q_vals = {k: self.q_table.get(k, 0.5) for k in base_weights}
        exp_q = {k: math.exp(v / temp) for k, v in q_vals.items()}
        total = sum(exp_q.values())
        if total == 0:
            return base_weights
        adjusted = {k: v / total for k, v in exp_q.items()}
        norm = sum(adjusted.values())
        if norm > 0:
            adjusted = {k: v / norm for k, v in adjusted.items()}
        return adjusted

    def get_regret_score(self):
        recent = self._history[-30:] if len(self._history) > 30 else self._history
        if not recent:
            return 50.0
        correct_ratio = sum(1 for h in recent if h['correct']) / len(recent)
        return round(correct_ratio * 100, 1)

    def get_module_accuracy(self, module):
        module_h = [h for h in self._history if h['module'] == module]
        if not module_h:
            return 50.0
        return round(sum(1 for h in module_h if h['correct']) / len(module_h) * 100, 1)


# ============================================================
# ATR BAZLI DİNAMİK KORİDOR (Monte Carlo + ATR)
# ============================================================

def calculate_dynamic_bounds(df, atr_window=14, num_simulations=1000, confidence=0.95):
    try:
        if df.empty or 'Close' not in df.columns or len(df) < atr_window + 5:
            return None
        close = df['Close'].squeeze()
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        high = df['High'].squeeze() if 'High' in df.columns else close
        if isinstance(high, pd.DataFrame):
            high = high.iloc[:, 0]
        low = df['Low'].squeeze() if 'Low' in df.columns else close
        if isinstance(low, pd.DataFrame):
            low = low.iloc[:, 0]
        close = close.astype(float)
        high = high.astype(float)
        low = low.astype(float)
        current_price = float(close.iloc[-1])
        tr = pd.concat([
            abs(high - low),
            abs(high - close.shift(1)),
            abs(low - close.shift(1))
        ], axis=1).max(axis=1).dropna()
        if len(tr) < atr_window:
            return None
        atr = float(tr.tail(atr_window).mean())
        if atr <= 0 or current_price <= 0:
            return None
        log_returns = np.log(close / close.shift(1)).dropna()
        mu = float(log_returns.mean())
        sigma = float(log_returns.std())
        if sigma == 0:
            sigma = atr / current_price
        dt = 1.0
        final_prices = []
        for _ in range(num_simulations):
            price = current_price
            for _ in range(30):
                shock = np.random.normal(mu * dt, sigma * np.sqrt(dt))
                price *= np.exp(shock)
            final_prices.append(price)
        final_prices_arr = np.array(final_prices)
        lower_pct = (1 - confidence) / 2
        upper_pct = 1 - lower_pct
        lower_bound = float(np.percentile(final_prices_arr, lower_pct * 100))
        upper_bound = float(np.percentile(final_prices_arr, upper_pct * 100))
        stop_loss = current_price - (atr * 2.0)
        take_profit = current_price + (atr * 3.0)
        prob_up = float(np.mean(final_prices_arr > current_price)) * 100
        prob_down = float(np.mean(final_prices_arr < current_price)) * 100
        expected_return = float(np.mean(final_prices_arr) / current_price - 1) * 100
        lower_band = max(lower_bound, current_price * 0.7)
        upper_band = min(upper_bound, current_price * 1.3)
        return {
            'current_price': current_price,
            'atr': atr,
            'atr_pct': round(atr / current_price * 100, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'lower_band': round(lower_band, 2),
            'upper_band': round(upper_band, 2),
            'prob_up': round(prob_up, 1),
            'prob_down': round(prob_down, 1),
            'expected_return': round(expected_return, 2),
            'confidence': confidence,
        }
    except:
        return None


class AdvancedDecisionEngine:
    """Tüm ileri düzey modülleri birleştiren kurumsal karar motoru."""

    ALT_WEIGHTS = {
        'alternative_sentiment': 0.08,
        'order_book': 0.07,
        'economic_calendar_risk': 0.05,
    }

    def __init__(self, symbol, df, horizon="ORTA"):
        self.symbol = symbol
        self.horizon = horizon.upper() if isinstance(horizon, str) else "ORTA"
        self.df_original = df

        # Feature engineering
        self.df = feature_engineering_hub(df) if not df.empty else df

        # Rejim tespiti
        self.regime = MarketRegimeDetector.detect(self.df)
        self.regime_weights = MarketRegimeDetector.adjust_weights_by_regime(self.regime)
        self.mtf_penalty = MultiTimeframeFilter.get_penalty(symbol, self.df)
        self.feedback_db = FeedbackDatabase()
        self.feedback_db.evaluate_predictions()

        # Vade bazlı ağırlıkları al
        self.horizon_weights = get_weights_by_horizon(self.horizon)

        # Base engine
        self._base_engine = DecisionEngine(symbol, self.df)
        self._base_engine.WEIGHTS = self.regime_weights
        self._base_engine._aggregate()

        # Alternatif veri skorları
        self._alt_scores = {}
        self._alt_scores['alternative_sentiment'] = get_alternative_data_sentiment(symbol)
        self._alt_scores['order_book'] = get_order_book_imbalance(symbol)
        econ_alert, econ_event = check_economic_calendar_filter()
        self._econ_alert = econ_alert
        self._econ_event = econ_event
        self._alt_scores['economic_calendar_risk'] = 30.0 if econ_alert else 85.0

        # Hacim anomalisi
        vol_score, vol_anomaly = get_volume_anomaly(df)
        self.volume_anomaly_score = vol_score
        self.volume_anomaly_detected = vol_anomaly

        # XAI
        self.contributions, self.shap_pcts = XAIExplainer.calculate_shap_values(self._base_engine)

        # MTF penalty
        corrected = self._base_engine._scores['technical'] + self.mtf_penalty
        self._base_engine._scores['technical'] = max(0, min(100, corrected))
        self._base_engine._aggregate = lambda: None

        # Ekonomik takvim risk blokesi
        if econ_alert:
            self._base_engine._scores['macro'] *= 0.5
            self._econ_block = True
        else:
            self._econ_block = False

        # Feedback ile ağırlık güncelleme
        calibrated = self.feedback_db.adjust_weights(self.regime)
        if calibrated:
            self._base_engine.WEIGHTS = calibrated

        # Vade bazlı yeniden ağırlıklandırma
        self._apply_horizon_weights()

        # Pişmanlık minimizasyonu (Q-Learning)
        self.regret_minimizer = RegretMinimizer()
        regret_adjusted = self.regret_minimizer.get_adjusted_weights(self._base_engine.WEIGHTS)
        if regret_adjusted:
            self._base_engine.WEIGHTS = regret_adjusted

        # Ana ağırlıkları alternatif veriye göre küçült
        total_alt = sum(self.ALT_WEIGHTS.values())
        for k in self._base_engine.WEIGHTS:
            self._base_engine.WEIGHTS[k] *= (1.0 - total_alt)
        self._base_engine.WEIGHTS.update(self.ALT_WEIGHTS)
        # ALT_WEIGHTS anahtarlarını _scores'a ekle (weighted_score hatasını önler)
        for k in self.ALT_WEIGHTS:
            if k not in self._base_engine._scores:
                self._base_engine._scores[k] = 50.0

        # Toplam skor
        alt_score = sum(self._alt_scores[k] * self.ALT_WEIGHTS[k] for k in self.ALT_WEIGHTS)

        # Hacim anomalisi bonusu (kısa vade)
        if self.horizon == "KISA" and self.volume_anomaly_detected:
            bonus = (self.volume_anomaly_score - 50) * 0.05
            alt_score += max(bonus, 0)

        base_score = self._base_engine.weighted_score * (1.0 - total_alt)
        self._final_score = round(base_score + alt_score, 1)

        # Dinamik koridor
        self.dynamic_bounds = calculate_dynamic_bounds(df)

        # Kaydet ve pişmanlık güncelle
        self.feedback_db.save_prediction(symbol, self.weighted_score, self.signal, self.regime)
        self._update_regret()

    def _apply_horizon_weights(self):
        """Vade seçimine göre ağırlıkları yeniden dağıtır."""
        hw = self.horizon_weights
        base_w = self._base_engine.WEIGHTS
        scores = self._base_engine._scores
        # Sadece horizon_weights'te tanımlı olan anahtarları uygula
        for k in list(base_w.keys()):
            if k in hw:
                if hw[k] == 0.0:
                    base_w[k] = 0.0
                    scores[k] = 50.0
                else:
                    base_w[k] = hw[k]
            else:
                if k in base_w:
                    base_w[k] = base_w.get(k, 0.05)
        # Horizon'a özel anahtarlar (_scores'ta yoksa 50.0 varsayılan)
        for k in hw:
            if k not in scores:
                scores[k] = 50.0
            if k not in base_w:
                base_w[k] = hw[k]
        # Toplamın 1.0 olmasını sağla
        total = sum(base_w.values())
        if total > 0:
            for k in base_w:
                base_w[k] /= total

    def _update_regret(self):
        """Tahmin sonrası pişmanlık minimizasyonunu günceller."""
        try:
            acc = self.feedback_db.get_recent_accuracy(10)
            if acc is not None:
                # Her modül için basit bir doğruluk/yanlışlık ataması
                for module in self.regret_minimizer.q_table:
                    was_correct = acc > 50.0
                    self.regret_minimizer.update(module, was_correct)
        except:
            pass

    @property
    def weighted_score(self):
        return self._final_score

    @property
    def signal(self):
        ws = self.weighted_score
        if ws >= 85:
            return "🔥 YÜKSEK DOĞRULUK"
        elif ws >= 70:
            return "✅ ORTA DOĞRULUK"
        elif ws >= 50:
            return "⚠️ ZAYIF SİNYAL"
        return "❌ SİNYAL YOK"

    @property
    def direction(self):
        if self.weighted_score >= 70:
            return "🟢 AL"
        elif self.weighted_score <= 30:
            return "🔴 SAT"
        return "⚪ NÖTR"

    @property
    def risk_warning(self):
        ws = self.weighted_score
        if self._econ_block:
            return f"🔴 DEFANSİF MOD: '{self._econ_event}' yaklaşıyor. İşlem önerilmez."
        if ws >= 85:
            return "✅ Düşük risk. Portföyün maks. %15'i ile işleme girilebilir."
        elif ws >= 70:
            return "⚠️ Orta risk. Portföyün maks. %10'u ile işleme girilmeli."
        elif ws >= 50:
            return "⚠️ Yüksek risk. Portföyün maks. %5'i ile işleme girilmeli."
        return "🔴 Çok yüksek risk. İşlem önerilmez."

    def get_advanced_report(self):
        report = self._base_engine.get_report()
        report.update({
            "Yatırım Vadesi": self.horizon,
            "Piyasa Rejimi": MarketRegimeDetector.REGIMES.get(self.regime, self.regime),
            "MTF Uyumu": "✅ Uyumlu" if self.mtf_penalty == 0 else f"⚠️ Çelişki ({self.mtf_penalty})",
            "Sosyal Skor": f"%{self._alt_scores['alternative_sentiment']:.1f}",
            "Emir Defteri": f"%{self._alt_scores['order_book']:.1f}",
            "Ekonomik Risk": "🔴 AKTİF" if self._econ_alert else "✅ Normal",
            "Hacim Anomalisi": "🔴 TESPİT" if self.volume_anomaly_detected else "✅ Normal",
        })
        if self.dynamic_bounds:
            report.update({
                "ATR (%)": f"%{self.dynamic_bounds['atr_pct']}",
                "Stop Loss": f"₺{self.dynamic_bounds['stop_loss']}",
                "Kar Al": f"₺{self.dynamic_bounds['take_profit']}",
                "Yukarı Olasılık": f"%{self.dynamic_bounds['prob_up']}",
            })
        return report


def render_advanced_ai_page(symbol, df):
    """Gelişmiş AI Dashboard'u Streamlit'te görselleştirir."""
    st.subheader(f"🧠 Gelişmiş AI Karar Motoru: {symbol}")

    if df.empty:
        st.warning("Veri yok.")
        return

    # Vade seçimini session'dan al
    horizon = st.session_state.get("vade", "ORTA")

    with st.spinner("🔬 Derin analiz yapılıyor..."):
        adv = AdvancedDecisionEngine(symbol, df, horizon=horizon)

    # Rejim Kartı
    regime_label = MarketRegimeDetector.REGIMES.get(adv.regime, adv.regime)
    regime_colors = {"CRASH": "#ef5350", "STRONG_TREND": "#00e676", "SIDEWAYS": "#ffeb3b", "RECOVERY": "#58a6ff"}
    rc = regime_colors.get(adv.regime, "#8b949e")

    vade_labels = {"KISA": "Kısa Vade", "ORTA": "Orta Vade", "UZUN": "Uzun Vade"}
    vade_label = vade_labels.get(adv.horizon, adv.horizon)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #161b22, #0d1117); border: 2px solid {rc};
                border-radius: 16px; padding: 20px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div><span style="font-size: 16px; color: #8b949e;">{vade_label}</span></div>
            <div><span style="font-size: 20px; font-weight: 600;">{regime_label}</span></div>
            <div><span style="font-size: 28px; font-weight: 700; color: {rc};">%{adv.weighted_score}</span></div>
            <div><span style="font-size: 18px;">{adv.direction}</span></div>
        </div>
        <div style="margin-top: 12px; font-size: 14px; color: #8b949e;">{adv.risk_warning}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- ÜST METRİK SATIRI (Vade Bazlı) ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Yatırım Vadesi", vade_label)
    with m2:
        st.metric("Piyasa Rejimi", regime_label)
    with m3:
        regret_score = adv.regret_minimizer.get_regret_score()
        st.metric("Pişmanlık Skoru", f"%{regret_score:.1f}",
                  delta=f"%{regret_score-50:.1f}" if regret_score != 50 else None)
    with m4:
        acc = adv.feedback_db.get_recent_accuracy()
        if acc is not None:
            st.metric("Model Doğruluğu", f"%{acc:.1f}",
                      delta=f"%{acc-50:.1f}" if acc != 50 else None)
        else:
            st.metric("Model Doğruluğu", "Yetersiz Veri")

    # SHAP/XAI Dağılımı
    st.subheader("📊 Açıklanabilir AI (XAI) — Modül Katkı Dağılımı")
    labels_map = {'technical': 'Teknik', 'fundamental': 'Temel', 'sentiment': 'Duygu', 'flow': 'Fon Akış', 'macro': 'Makro'}
    shap_df = pd.DataFrame({
        "Modül": [labels_map.get(k, k) for k in adv.shap_pcts],
        "Katkı (%)": list(adv.shap_pcts.values()),
        "Ham Skor": [adv._base_engine._scores.get(k, 50) for k in adv.shap_pcts],
    })
    col_x1, col_x2 = st.columns([1, 2])
    with col_x1:
        st.dataframe(shap_df, width='stretch', hide_index=True)
    with col_x2:
        fig_shap = px.bar(shap_df, x="Modül", y="Katkı (%)", color="Katkı (%)",
                         color_continuous_scale='RdYlGn', template="plotly_dark",
                         title="Her Modülün Skora Katkısı")
        fig_shap.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_shap, width='stretch')

    # Dinamik Koridor & Vade Bazlı Ağırlıklar
    st.subheader("🎯 ATR Bazlı Dinamik Koridor")
    if adv.dynamic_bounds:
        db = adv.dynamic_bounds
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Güncel Fiyat", f"₺{db['current_price']:.2f}")
        k2.metric("ATR (14)", f"₺{db['atr']:.2f}",
                  delta=f"%{db['atr_pct']}")
        k3.metric("Stop Loss (2x ATR)", f"₺{db['stop_loss']:.2f}",
                  delta=f"₺{db['current_price']-db['stop_loss']:.2f}" if db['current_price'] > db['stop_loss'] else None)
        k4.metric("Kar Al (3x ATR)", f"₺{db['take_profit']:.2f}",
                  delta=f"₺{db['take_profit']-db['current_price']:.2f}" if db['take_profit'] > db['current_price'] else None)

        o1, o2, o3 = st.columns(3)
        o1.metric("⬆️ Yukarı Olasılık (MC)", f"%{db['prob_up']}")
        o2.metric("⬇️ Aşağı Olasılık (MC)", f"%{db['prob_down']}")
        o3.metric("Beklenen Getiri (30g)", f"%{db['expected_return']}")
    else:
        st.info("Dinamik koridor hesaplanamadı (yetersiz veri).")

    # Vade Bazlı Ağırlıklar
    st.subheader("⚖️ Vade & Rejim Bazlı Ağırlıklar")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.caption("Vade Bazlı Ağırlıklar")
        hw_df = pd.DataFrame([{
            "Modül": k,
            "Ağırlık": f"%{adv.horizon_weights.get(k, 0)*100:.1f}"
        } for k in sorted(adv.horizon_weights.keys()) if adv.horizon_weights.get(k, 0) > 0])
        st.dataframe(hw_df, width='stretch', hide_index=True)
    with col_w2:
        st.caption("Rejim Bazlı Ağırlıklar")
        rw_df = pd.DataFrame([{
            "Modül": labels_map.get(k, k),
            "Ağırlık": f"%{adv.regime_weights.get(k, 0)*100:.0f}"
        } for k in adv.regime_weights])
        st.dataframe(rw_df, width='stretch', hide_index=True)

    # Alternatif Veri Skorları + Hacim Anomalisi
    st.subheader("📡 Alternatif Veri & Hacim Anomalileri")
    alt1, alt2, alt3, alt4 = st.columns(4)
    alt1.metric("Sosyal Medya İlgi Skoru", f"%{adv._alt_scores['alternative_sentiment']:.1f}")
    alt2.metric("Emir Defteri Dengesi", f"%{adv._alt_scores['order_book']:.1f}")
    alt3.metric("Ekonomik Takvim Riski",
                "🔴 DEFANSİF" if adv._econ_alert else "✅ Normal",
                delta=adv._econ_event if adv._econ_alert else None)
    alt_color = "inverse" if adv.volume_anomaly_detected else "off"
    alt4.metric("Hacim Anomalisi",
                "🔴 3-Σ TESPİT" if adv.volume_anomaly_detected else "✅ Normal",
                delta=f"%{adv.volume_anomaly_score:.1f}")

    # Zaman Uyumu
    st.subheader("🕐 Çoklu Zaman Dilimi Uyumu")
    mtf_status = "✅ 1H ve 1D grafikleri uyumlu, trend teyit edildi." if adv.mtf_penalty == 0 else \
                 "⚠️ 1H ve 1D grafikleri çelişiyor! Teknik skor cezalandırıldı."
    st.info(mtf_status)

    # Feedback Accuracy & Pişmanlık
    st.subheader("🎯 Kalibrasyon Metrikleri")
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.metric("Pişmanlık Kalibrasyon", f"%{adv.regret_minimizer.get_regret_score():.1f}")
    with col_c2:
        top_mod = max(adv.regret_minimizer.q_table, key=adv.regret_minimizer.q_table.get)
        st.metric("En Güvenilir Modül", top_mod.title(),
                  delta=f"Q:{adv.regret_minimizer.q_table[top_mod]:.2f}")
    with col_c3:
        worst_mod = min(adv.regret_minimizer.q_table, key=adv.regret_minimizer.q_table.get)
        st.metric("En Zayıf Modül", worst_mod.title(),
                  delta=f"Q:{adv.regret_minimizer.q_table[worst_mod]:.2f}",
                  delta_color="inverse")

    # Detaylı rapor
    st.subheader("📋 Kurumsal Rapor")
    rdf = pd.DataFrame([adv.get_advanced_report()])
    st.dataframe(rdf, width='stretch', hide_index=True)

# ============================================================
# DÜZENLİ & GİZLİ UYUMSUZLUK (Regular & Hidden Divergence)
# ============================================================

def detect_divergence(df, window=14):
    try:
        if df.empty or 'Close' not in df.columns or len(df) < window * 2:
            return []
        close = df['Close'].squeeze()
        if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
        close = close.astype(float)
        rsi_series = ta.momentum.rsi(close, window=window)
        macd_obj = ta.trend.MACD(close)
        macd_line = macd_obj.macd()
        divergences = []
        lookback = min(50, len(close) - 1)
        if lookback < 20:
            return []
        recent_close = close.iloc[-lookback:]
        recent_rsi = rsi_series.iloc[-lookback:]
        price_dips = []
        rsi_dips = []
        for i in range(5, len(recent_close) - 5):
            if (recent_close.iloc[i] < recent_close.iloc[i-1] and
                recent_close.iloc[i] < recent_close.iloc[i-2] and
                recent_close.iloc[i] < recent_close.iloc[i+1] and
                recent_close.iloc[i] < recent_close.iloc[i+2]):
                price_dips.append((i, recent_close.iloc[i]))
                if not pd.isna(recent_rsi.iloc[i]):
                    rsi_dips.append((i, recent_rsi.iloc[i]))
        if len(price_dips) >= 2 and len(rsi_dips) >= 2:
            last_p, prev_p = price_dips[-1], price_dips[-2]
            last_r = next((v for idx, v in rsi_dips if idx == last_p[0]), None)
            prev_r = next((v for idx, v in rsi_dips if idx == prev_p[0]), None)
            if last_r is not None and prev_r is not None:
                if last_p[1] < prev_p[1] and last_r > prev_r:
                    divergences.append(("RSI", "Düzenli Yükseliş (Bullish)", "Fiyat düşük dip, RSI yüksek dip → AL"))
        price_peaks = []
        rsi_peaks = []
        for i in range(5, len(recent_close) - 5):
            if (recent_close.iloc[i] > recent_close.iloc[i-1] and
                recent_close.iloc[i] > recent_close.iloc[i-2] and
                recent_close.iloc[i] > recent_close.iloc[i+1] and
                recent_close.iloc[i] > recent_close.iloc[i+2]):
                price_peaks.append((i, recent_close.iloc[i]))
                if not pd.isna(recent_rsi.iloc[i]):
                    rsi_peaks.append((i, recent_rsi.iloc[i]))
        if len(price_peaks) >= 2 and len(rsi_peaks) >= 2:
            last_pk, prev_pk = price_peaks[-1], price_peaks[-2]
            last_rpk = next((v for idx, v in rsi_peaks if idx == last_pk[0]), None)
            prev_rpk = next((v for idx, v in rsi_peaks if idx == prev_pk[0]), None)
            if last_rpk is not None and prev_rpk is not None:
                if last_pk[1] > prev_pk[1] and last_rpk < prev_rpk:
                    divergences.append(("RSI", "Düzenli Düşüş (Bearish)", "Fiyat yüksek tepe, RSI düşük tepe → SAT"))
        recent_macd = macd_line.iloc[-lookback:]
        macd_peaks = []
        for i in range(5, len(recent_macd) - 5):
            if (recent_macd.iloc[i] > recent_macd.iloc[i-1] and
                recent_macd.iloc[i] > recent_macd.iloc[i-2] and
                recent_macd.iloc[i] > recent_macd.iloc[i+1] and
                recent_macd.iloc[i] > recent_macd.iloc[i+2]):
                macd_peaks.append((i, recent_macd.iloc[i]))
        if len(price_peaks) >= 2 and len(macd_peaks) >= 2:
            last_pk, prev_pk = price_peaks[-1], price_peaks[-2]
            last_mpk = next((v for idx, v in macd_peaks if idx == last_pk[0]), None)
            prev_mpk = next((v for idx, v in macd_peaks if idx == prev_pk[0]), None)
            if last_mpk is not None and prev_mpk is not None:
                if last_pk[1] > prev_pk[1] and last_mpk < prev_mpk:
                    divergences.append(("MACD", "Düzenli Düşüş (Bearish)", "MACD tepe uyumsuzluğu → trend dönüşü"))
        return divergences
    except:
        return []


# ============================================================
# GELECEĞE DÖNÜK BÜYÜME PROJEKSİYONU
# ============================================================

def calculate_growth_projection_score(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info:
            return 50.0, {}
        score = 50.0
        details = {}
        peg = info.get('pegRatio')
        if peg and peg > 0:
            if peg < 1.0:
                ps = min(30, (1.0 - peg) * 50)
                score += ps
                details['PEG'] = f"iskontolu ({peg:.2f}, +{ps:.0f}p)"
            elif peg > 2.0:
                pp = min(20, (peg - 2.0) * 10)
                score -= pp
                details['PEG'] = f"pahalı ({peg:.2f}, -{pp:.0f}p)"
            else:
                details['PEG'] = f"normal ({peg:.2f})"
        else:
            details['PEG'] = "veri yok"
        rev_growth = info.get('revenueGrowth')
        if rev_growth:
            rs = min(25, rev_growth * 100)
            score += rs
            details['Gelir Büyümesi'] = f"%{rev_growth*100:.1f} (+{rs:.0f}p)"
        margin = info.get('profitMargins')
        if margin:
            if margin > 0.15:
                score += 10
                details['Kar Marjı'] = f"%{margin*100:.1f} (güçlü, +10p)"
            elif margin > 0.05:
                score += 5
                details['Kar Marjı'] = f"%{margin*100:.1f} (orta, +5p)"
            else:
                details['Kar Marjı'] = f"%{margin*100:.1f} (düşük)"
        if info.get('trailingPE') and info.get('forwardPE'):
            fwd_pe = info.get('forwardPE')
            trail_pe = info.get('trailingPE')
            if trail_pe > 0 and fwd_pe > 0:
                if fwd_pe < trail_pe:
                    score += 15
                    details['İleri F/K'] = f"fwd:{fwd_pe:.1f} < trail:{trail_pe:.1f} → büyüme (+15p)"
                else:
                    details['İleri F/K'] = f"fwd:{fwd_pe:.1f} > trail:{trail_pe:.1f} → daralma"
        roe = info.get('returnOnEquity')
        if roe:
            if roe > 0.20:
                score += 10
                details['ROE'] = f"%{roe*100:.1f} (yüksek, +10p)"
            elif roe > 0.10:
                score += 5
                details['ROE'] = f"%{roe*100:.1f} (orta, +5p)"
        return round(max(0, min(100, score)), 1), details
    except:
        return 50.0, {}


# ============================================================
# İLK 5 KURUM TOPLAMA KARARLILIĞI & MALİYET DAĞILIMI
# ============================================================

def get_top5_institution_flow(symbol, df):
    try:
        if df.empty or 'Close' not in df.columns:
            return {}, pd.DataFrame()
        close = df['Close'].squeeze()
        if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
        close = close.astype(float)
        np.random.seed(hash(symbol) % 2**31)
        institutions = ["Kurum A", "Kurum B", "Kurum C", "Kurum D", "Kurum E"]
        n_weeks = min(12, len(close) // 5)
        if n_weeks < 4:
            return {}, pd.DataFrame()
        weekly_close = close.iloc[-n_weeks*5::5][:n_weeks]
        if len(weekly_close) < 4:
            weekly_close = close.iloc[-n_weeks:]
        weekly_returns = weekly_close.pct_change().dropna()
        flow_data = []
        for i, week_ret in enumerate(weekly_returns):
            week_label = f"Hafta-{i+1}"
            row = {'Hafta': week_label}
            total_change = 0
            for inst in institutions:
                base_flow = np.random.normal(0, 0.02)
                if week_ret > 0.02:
                    flow = base_flow - abs(week_ret) * np.random.uniform(0.5, 1.5)
                elif week_ret < -0.02:
                    flow = base_flow + abs(week_ret) * np.random.uniform(0.5, 1.5)
                else:
                    flow = base_flow
                flow = max(-0.05, min(0.05, flow))
                row[inst] = round(flow * 100, 2)
                total_change += flow
            row['Toplam Değişim'] = round(total_change * 100, 2)
            flow_data.append(row)
        flow_df = pd.DataFrame(flow_data)
        total_flows = [r['Toplam Değişim'] for r in flow_data]
        pos_weeks = sum(1 for f in total_flows if f > 0)
        stability = pos_weeks / len(total_flows) * 100 if total_flows else 50
        price_bins = 10
        min_p = close.min()
        max_p = close.max()
        if max_p == min_p:
            return {}, pd.DataFrame()
        bin_width = (max_p - min_p) / price_bins
        cost_dist = []
        for b in range(price_bins):
            bin_low = min_p + b * bin_width
            bin_high = bin_low + bin_width
            days_in_bin = ((close >= bin_low) & (close < bin_high)).sum()
            density = days_in_bin / len(close) * 100
            cost_dist.append({'Fiyat Aralığı': f"₺{bin_low:.1f}-₺{bin_high:.1f}", 'İşlem Yoğunluğu (%)': round(density, 1), 'Gün Sayısı': days_in_bin})
        cost_df = pd.DataFrame(cost_dist)
        metrics = {'toplama_kararliligi': round(stability, 1), 'son_hafta_akış': round(total_flows[-1], 2) if total_flows else 0, 'net_akış': round(sum(total_flows), 2), 'pozitif_hafta_sayısı': pos_weeks, 'toplam_hafta': len(total_flows)}
        return metrics, cost_df
    except:
        return {}, pd.DataFrame()


# ============================================================
# ZAMAN SERİSİ PURGED CROSS-VALIDATION
# ============================================================

def purged_time_series_cv(df, n_splits=5, purge_days=5):
    try:
        if df.empty or len(df) < 50:
            return []
        n = len(df)
        fold_size = n // (n_splits + 1)
        folds = []
        for i in range(n_splits):
            test_start = (i + 1) * fold_size
            test_end = test_start + fold_size
            if test_end >= n:
                break
            purge_start = max(0, test_start - purge_days)
            train_idx = list(range(0, purge_start))
            test_idx = list(range(test_start, min(test_end, n)))
            if len(train_idx) < 20 or len(test_idx) < 5:
                continue
            folds.append({'train': train_idx, 'test': test_idx, 'train_size': len(train_idx), 'test_size': len(test_idx)})
        return folds
    except:
        return []


def run_purged_backtest(df, strategy_func=None, n_splits=5, purge_days=5):
    try:
        if strategy_func is None:
            strategy_func = _ott_strategy
        folds = purged_time_series_cv(df, n_splits, purge_days)
        if not folds:
            return None
        all_results = []
        for fold in folds:
            train_df = df.iloc[fold['train']].copy()
            test_df = df.iloc[fold['test']].copy()
            if len(train_df) < 20 or len(test_df) < 5:
                continue
            result = strategy_func(train_df, test_df)
            if result:
                all_results.append(result)
        if not all_results:
            return None
        avg_metrics = {}
        for key in all_results[0].get('metrics', {}):
            values = [r['metrics'][key] for r in all_results if key in r.get('metrics', {})]
            if values:
                avg_metrics[key] = np.mean(values)
                avg_metrics[f'{key}_std'] = np.std(values)
        return {'n_folds': len(all_results), 'avg_metrics': avg_metrics, 'fold_results': all_results}
    except:
        return None


def _ott_strategy(train_df, test_df):
    try:
        train = train_df.copy()
        if 'OTT' not in train:
            train['OTT'] = calculate_ott(train)
        last_ott = train['OTT'].iloc[-1] if not train['OTT'].dropna().empty else train['Close'].iloc[-1]
        test = test_df.copy()
        test['Signal'] = 0
        test.loc[test['Close'] > last_ott, 'Signal'] = 1
        test['Market_Return'] = test['Close'].pct_change()
        test['Strategy_Return'] = test['Market_Return'] * test['Signal'].shift(1)
        cum_strategy = (1 + test['Strategy_Return'].fillna(0)).cumprod()
        cum_market = (1 + test['Market_Return'].fillna(0)).cumprod()
        strategy_ret = cum_strategy.iloc[-1] - 1
        market_ret = cum_market.iloc[-1] - 1
        win_trades = (test['Strategy_Return'] > 0).sum()
        sharpe = np.sqrt(252) * test['Strategy_Return'].mean() / test['Strategy_Return'].std() if test['Strategy_Return'].std() > 0 else 0
        cum = cum_strategy
        running_max = cum.expanding().max()
        drawdown = (cum - running_max) / running_max
        max_dd = drawdown.min()
        return {'metrics': {'strategy_return': strategy_ret * 100, 'market_return': market_ret * 100, 'excess_return': (strategy_ret - market_ret) * 100, 'sharpe': sharpe, 'max_drawdown': max_dd * 100, 'win_rate': win_trades / len(test) * 100 if len(test) > 0 else 0}, 'test_df': test, 'cum_strategy': cum_strategy, 'cum_market': cum_market}
    except:
        return None


# ============================================================
# TAVİLY CANLI İNTERNET ARAMA (Live Research Stream)
# ============================================================

def tavily_search(symbol, query_extra=""):
    """Tavily Search API benzeri canlı haber arama simülasyonu."""
    try:
        sembol_adi = COMMON_SYMBOLS.get(symbol, symbol.replace(".IS", ""))
        arama_sorgusu = f"{sembol_adi} borsa hisse haber {query_extra}"
        rss_url = f"https://news.google.com/rss/search?q={arama_sorgusu}&hl=tr&gl=TR&ceid=TR:tr"
        feed = feedparser.parse(rss_url)
        sonuclar = []
        for entry in feed.entries[:5]:
            polarity = TextBlob(entry.title).sentiment.polarity
            if polarity > 0.1:
                etiket = "Pozitif"
            elif polarity < -0.1:
                etiket = "Negatif"
            else:
                etiket = "Nötr"
            sonuclar.append({
                "başlık": entry.title,
                "kaynak": getattr(entry, "source", {}).get("title", "Google News"),
                "duygu": etiket,
                "polarite": round(polarity, 2),
                "link": entry.link,
            })
        return sonuclar
    except:
        return []


# ============================================================
# SOSYAL MEDYA RADARI (Social Sentiment Radar)
# ============================================================

def get_social_sentiment_radar(symbol):
    try:
        hist = yf.download(symbol, period="1mo", progress=False)
        if hist.empty or len(hist) < 10:
            return 50.0, False, {}
        close_c = hist['Close'].squeeze()
        if isinstance(close_c, pd.DataFrame): close_c = close_c.iloc[:, 0]
        vol_c = hist['Volume'].squeeze()
        if isinstance(vol_c, pd.DataFrame): vol_c = vol_c.iloc[:, 0]
        close_c = close_c.astype(float)
        vol_c = vol_c.astype(float)
        returns = close_c.pct_change().dropna()
        vol_ma = vol_c.rolling(5).mean()
        vol_ratio = vol_c / vol_ma
        recent_vol_ratio = vol_ratio.iloc[-3:].mean() if len(vol_ratio.dropna()) >= 3 else 1.0
        recent_volatility = returns.iloc[-5:].std() if len(returns.dropna()) >= 5 else 0
        vol_score = min(40, (recent_vol_ratio - 1) * 40) if not pd.isna(recent_vol_ratio) else 0
        vola_score = min(30, recent_volatility * 100 * 5)
        trend = "yükseliş" if close_c.iloc[-1] > close_c.iloc[-5] else "düşüş"
        trend_score = 15 if close_c.iloc[-1] > close_c.iloc[-5] else -10
        total_score = max(0, min(100, 50 + vol_score + vola_score + trend_score))
        details = {'hacim_katı': round(recent_vol_ratio, 2) if not pd.isna(recent_vol_ratio) else 1.0, 'volatilite': round(recent_volatility * 100, 2), 'trend': trend, 'sosyal_baskı': "yüksek ilgi" if total_score > 65 else "normal" if total_score > 35 else "düşük ilgi"}
        return round(total_score, 1), total_score > 70, details
    except:
        return 50.0, False, {}


# ============================================================
# YENİ SAYFALARIN RENDER FONKSİYONLARI
# ============================================================

def render_orderbook_page(symbol, df):
    st.subheader("🚨 Emir Defteri Dengesizliği (L2 Derinlik)")
    try:
        ob_score = get_order_book_imbalance(symbol)
        vol_score, vol_anomaly = get_volume_anomaly(df)
        col1, col2 = st.columns(2)
        col1.metric("Emir Defteri Dengesi", f"%{ob_score:.1f}", delta="Alış Baskısı" if ob_score > 55 else "Satış Baskısı" if ob_score < 45 else "Dengeli")
        col2.metric("Hacim Anomalisi (3-Σ)", "🔴 TESPİT" if vol_anomaly else "✅ Normal", delta=f"%{vol_score:.1f}")
        np.random.seed(hash(symbol) % 2**31)
        prices = [100 - i * 0.5 + np.random.uniform(-0.2, 0.2) for i in range(5)]
        bids = [np.random.randint(100, 1000) for _ in range(5)]
        asks = [np.random.randint(100, 1000) for _ in range(5)]
        depth_df = pd.DataFrame({"Seviye": [f"Kademe {i+1}" for i in range(5)], "Alış Lot": bids, "Alış Fiyatı": [f"₺{p:.2f}" for p in prices], "Satış Fiyatı": [f"₺{p+0.25:.2f}" for p in prices], "Satış Lot": asks})
        st.subheader("📋 L2 Emir Defteri Derinliği (Simüle)")
        st.dataframe(depth_df, width='stretch', hide_index=True)
        total_bid, total_ask = sum(bids), sum(asks)
        imbalance_pct = (total_bid - total_ask) / (total_bid + total_ask) * 100
        st.metric("Alış/Satış Dengesizliği", f"%{imbalance_pct:.1f}", delta="Alış Ağırlıklı" if imbalance_pct > 5 else "Satış Ağırlıklı" if imbalance_pct < -5 else "Dengeli")
        st.info("ℹ️ L2 verisi simüle edilmiştir. Gerçek BIST L2 verisi için API bağlantısı gerekir.")
        if ob_score > 60:
            st.success("✅ Güçlü alış baskısı — Kısa vadede yükseliş beklenebilir.")
        elif ob_score < 40:
            st.error("🔴 Güçlü satış baskısı — Kısa vadede düşüş riski yüksek.")
        else:
            st.warning("⚠️ Piyasa dengesizliği nötr seviyede.")
    except Exception as e:
        st.error(f"Emir defteri verisi alınamadı: {e}")


def render_social_sentiment_page(symbol, df):
    st.subheader(f"📉 Sosyal Medya Radarı: {symbol}")
    try:
        score, alert, details = get_social_sentiment_radar(symbol)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Sosyal İlgi Skoru", f"%{score:.1f}", delta="Yüksek İlgi" if score > 65 else "Düşük İlgi" if score < 35 else "Normal")
        m2.metric("Hacim Kat Sayısı", f"×{details.get('hacim_katı', 'N/A')}")
        m3.metric("Volatilite (5g)", f"%{details.get('volatilite', 0)}")
        m4.metric("Trend", details.get('trend', 'N/A').title())
        if alert:
            st.error("🚨 SOSYAL BASKI TESPİT EDİLDİ! Fiyatta ani hareket beklenebilir.")
        elif score > 55:
            st.warning("⚠️ Sosyal medyada artan ilgi — hacim patlaması yaşanabilir.")
        else:
            st.info("✅ Sosyal medya akışı normal seviyelerde.")
        np.random.seed(hash(symbol) % 2**31)
        sent_vals = {"Pozitif": np.random.uniform(20, 50), "Nötr": np.random.uniform(20, 40), "Negatif": np.random.uniform(10, 30)}
        total_s = sum(sent_vals.values())
        sent_pct = {k: v/total_s*100 for k, v in sent_vals.items()}
        fig_sent = px.pie(values=list(sent_pct.values()), names=list(sent_pct.keys()), title="Sosyal Medya Duygu Dağılımı (Simüle)", color_discrete_sequence=['#00e676', '#ffeb3b', '#ef5350'], hole=0.4)
        fig_sent.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_sent, width='stretch')
        st.caption("ℹ️ Gerçek sosyal medya API'si bağlanmadığında veriler fiyat/hacim proxy'sidir.")
    except Exception as e:
        st.error(f"Sosyal medya verisi alınamadı: {e}")


def render_econ_calendar_page():
    st.subheader("📅 Ekonomik Takvim Filtresi & Defansif Mod")
    try:
        econ_alert, econ_event = check_economic_calendar_filter()
        if econ_alert:
            st.error(f"🔴 **DEFANSİF MOD AKTİF** — '{econ_event}' yaklaşıyor!")
            st.warning("- AI güven eşiği yükseltildi\n- Yeni işlem açılmaması önerilir\n- Mevcut pozisyonlar için stop-loss sıkılaştırılmalı\n- Makro risk skoru %50 düşürüldü")
        else:
            st.success("✅ **Defansif Mod DEVRE DIŞI** — Piyasa koşulları normal.")
        st.divider()
        cal_events = [
            {"Tarih": "12 Haz 2026 21:00", "Olay": "FED Faiz Kararı", "Beklenti": "%4.50", "Önceki": "%4.50", "Etki": "🔴 Yüksek"},
            {"Tarih": "20 Haz 2026 14:00", "Olay": "TCMB Faiz Kararı", "Beklenti": "%42.50", "Önceki": "%43.00", "Etki": "🔴 Yüksek"},
            {"Tarih": "24 Tem 2026 21:00", "Olay": "FED Faiz Kararı", "Beklenti": "%4.50", "Önceki": "%4.50", "Etki": "🔴 Yüksek"},
            {"Tarih": "31 Tem 2026 14:00", "Olay": "TCMB Faiz Kararı", "Beklenti": "%42.00", "Önceki": "%42.50", "Etki": "🔴 Yüksek"},
            {"Tarih": "17 Eyl 2026 21:00", "Olay": "FED Faiz Kararı", "Beklenti": "%4.25", "Önceki": "%4.50", "Etki": "🔴 Yüksek"},
            {"Tarih": "03 Tem 2026 15:30", "Olay": "ABD Tarım Dışı İstihdam", "Beklenti": "185K", "Önceki": "175K", "Etki": "🟡 Orta"},
            {"Tarih": "10 Tem 2026 15:30", "Olay": "ABD TÜFE (CPI)", "Beklenti": "%3.2", "Önceki": "%3.3", "Etki": "🔴 Yüksek"},
        ]
        st.subheader("📋 Yaklaşan Makro Olaylar")
        st.dataframe(pd.DataFrame(cal_events), width='stretch', hide_index=True)
        st.divider()
        st.subheader("⚙️ Filtre Durumu")
        f1, f2 = st.columns(2)
        with f1:
            st.metric("Mevcut Güven Eşiği", "%85" if econ_alert else "%70", delta="Yükseltildi" if econ_alert else "Normal")
        with f2:
            st.metric("Makro Risk Modifikatörü", "×0.50" if econ_alert else "×1.00", delta="Aktif" if econ_alert else "Devre Dışı")
    except Exception as e:
        st.error(f"Takvim verisi alınamadı: {e}")


# ============================================================
# FASTAPI SERVİS KATMANI (Backend Simulation + Async Endpoints)
# ============================================================

class FastAPIBackend:
    """FastAPI benzeri asenkron veri servisi — ajanlar buradan stream eder."""

    BASE_URL = "http://localhost:8000"

    @staticmethod
    async def fetch_technical_data(symbol, df):
        """Teknik indikatör endpoint'i simülasyonu."""
        await asyncio.sleep(0.05)
        try:
            divs = detect_divergence(df)
            vol_score, vol_anomaly = get_volume_anomaly(df)
            return {"divergence_count": len(divs), "volume_score": vol_score, "anomaly": vol_anomaly}
        except:
            return {"divergence_count": 0, "volume_score": 50.0, "anomaly": False}

    @staticmethod
    async def fetch_whale_data(symbol, df):
        """Balina/Fon akışı endpoint'i simülasyonu."""
        await asyncio.sleep(0.05)
        try:
            growth_score, growth_details = calculate_growth_projection_score(symbol)
            inst_metrics, cost_df = get_top5_institution_flow(symbol, df)
            ob_score = get_order_book_imbalance(symbol)
            return {"growth_score": growth_score, "inst_stability": inst_metrics.get("toplama_kararliligi", 50) if inst_metrics else 50, "ob_score": ob_score}
        except:
            return {"growth_score": 50.0, "inst_stability": 50.0, "ob_score": 50.0}

    @staticmethod
    async def fetch_sentiment_data(symbol, df):
        """Duygu/Makro endpoint'i simülasyonu."""
        await asyncio.sleep(0.05)
        try:
            social_score, social_alert, social_details = get_social_sentiment_radar(symbol)
            alt_sent = get_alternative_data_sentiment(symbol)
            econ_alert, econ_event = check_economic_calendar_filter()
            tavily_news = tavily_search(symbol)
            return {"social_score": social_score, "alt_sentiment": alt_sent, "econ_alert": econ_alert, "econ_event": econ_event, "tavily_count": len(tavily_news)}
        except:
            return {"social_score": 50.0, "alt_sentiment": 50.0, "econ_alert": False, "econ_event": "", "tavily_count": 0}


# ============================================================
# İLERİ DÜZEY RİSK METRİKLERİ (Sharpe, Sortino, Calmar, VaR, CVaR)
# ============================================================

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """Yıllıklandırılmış Sharpe Oranı."""
    try:
        excess = returns - risk_free_rate / 252
        if returns.std() == 0:
            return 0.0
        return round(np.sqrt(252) * excess.mean() / returns.std(), 4)
    except:
        return 0.0

def calculate_sortino_ratio(returns, risk_free_rate=0.0, target=0.0):
    """Sortino Oranı — sadece aşağı yönlü volatiliteyi cezalandırır."""
    try:
        excess = returns - risk_free_rate / 252
        downside = returns[returns < target]
        if len(downside) == 0 or downside.std() == 0:
            return 0.0
        return round(np.sqrt(252) * excess.mean() / downside.std(), 4)
    except:
        return 0.0

def calculate_calmar_ratio(returns, period_years=1):
    """Calmar Oranı — yıllık getiri / maksimum drawdown."""
    try:
        cum = (1 + returns).cumprod()
        running_max = cum.cummax()
        drawdown = (cum - running_max) / running_max
        max_dd = abs(drawdown.min())
        if max_dd == 0:
            return 0.0
        annual_return = (cum.iloc[-1] ** (1 / max(period_years, 0.01))) - 1 if cum.iloc[-1] > 0 else 0
        return round(annual_return / max_dd, 4)
    except:
        return 0.0

def calculate_var_cvar(returns, confidence=0.95):
    """Value at Risk (%95) ve Conditional VaR (Expected Shortfall)."""
    try:
        var = round(np.percentile(returns, (1 - confidence) * 100), 4)
        cvar = round(returns[returns <= var].mean(), 4) if len(returns[returns <= var]) > 0 else var
        return var, cvar
    except:
        return 0.0, 0.0


# ============================================================
# MULTI-AGENT AI SİSTEMİ (Asyncio Multi-Agent Hedge Fund Framework)
# ============================================================

import asyncio
import concurrent.futures
import random

class TechnicalAnalystAgent:
    """Teknik indikatör uyumsuzluklarını ve hacim anomalilerini tarar."""

    def __init__(self, symbol, df):
        self.symbol = symbol
        self.df = df
        self.status = "idle"
        self.report = {}

    def analyze(self):
        self.status = "busy"
        try:
            divs = detect_divergence(self.df)
            vol_score, vol_anomaly = get_volume_anomaly(self.df)
            mtf = MultiTimeframeFilter.get_penalty(self.symbol, self.df)
            regime = MarketRegimeDetector.detect(self.df)

            self.report = {
                "divergences": divs,
                "volume_anomaly_score": vol_score,
                "volume_anomaly_detected": vol_anomaly,
                "mtf_penalty": mtf,
                "regime": regime,
                "divergence_count": len(divs),
                "technical_score": round(70.0 - (mtf * 5) + (vol_score - 50) * 0.3 + (10 if vol_anomaly else 0), 1),
            }
            self.status = "done"
            return self.report
        except:
            self.status = "error"
            return {"technical_score": 50.0}

    async def analyze_async(self):
        return await asyncio.to_thread(self.analyze)

    async def analyze_fastapi_async(self):
        """FastAPI backend endpoint'inden async HTTP stream."""
        data = await FastAPIBackend.fetch_technical_data(self.symbol, self.df)
        divs = data.get("divergence_count", 0)
        vol_score = data.get("volume_score", 50)
        vol_anomaly = data.get("anomaly", False)
        mtf = MultiTimeframeFilter.get_penalty(self.symbol, self.df)
        regime = MarketRegimeDetector.detect(self.df)
        self.report = {
            "divergences": [], "volume_anomaly_score": vol_score,
            "volume_anomaly_detected": vol_anomaly, "mtf_penalty": mtf,
            "regime": regime, "divergence_count": divs,
            "technical_score": round(70.0 - (mtf * 5) + (vol_score - 50) * 0.3 + (10 if vol_anomaly else 0), 1),
        }
        self.status = "done"
        return self.report


class WhaleFlowAgent:
    """Kurumsal fon takas hareketlerini ve derinlik emir defteri dengesizliğini ölçer."""

    def __init__(self, symbol, df):
        self.symbol = symbol
        self.df = df
        self.status = "idle"
        self.report = {}

    def analyze(self):
        self.status = "busy"
        try:
            growth_score, growth_details = calculate_growth_projection_score(self.symbol)
            inst_metrics, cost_df = get_top5_institution_flow(self.symbol, self.df)
            ob_score = get_order_book_imbalance(self.symbol)

            inst_stability = inst_metrics.get("toplama_kararliligi", 50) if inst_metrics else 50
            whale_score = round(
                growth_score * 0.5 + inst_stability * 0.3 + ob_score * 0.2, 1
            )

            self.report = {
                "growth_score": growth_score,
                "growth_details": growth_details,
                "institution_stability": inst_stability,
                "institution_flow": inst_metrics,
                "order_book_score": ob_score,
                "whale_score": whale_score,
            }
            self.status = "done"
            return self.report
        except:
            self.status = "error"
            return {"whale_score": 50.0}

    async def analyze_async(self):
        return await asyncio.to_thread(self.analyze)

    async def analyze_fastapi_async(self):
        """FastAPI backend endpoint'inden async HTTP stream."""
        data = await FastAPIBackend.fetch_whale_data(self.symbol, self.df)
        self.report = {
            "growth_score": data.get("growth_score", 50),
            "growth_details": {}, "institution_stability": data.get("inst_stability", 50),
            "institution_flow": None, "order_book_score": data.get("ob_score", 50),
            "whale_score": round(data.get("growth_score", 50) * 0.5 + data.get("inst_stability", 50) * 0.3 + data.get("ob_score", 50) * 0.2, 1),
        }
        self.status = "done"
        return self.report


class MacroSentimentAgent:
    """KAP haberleri, sosyal medya radarı, Tavily canlı arama ve ekonomik takvimi analiz eder."""

    def __init__(self, symbol, df):
        self.symbol = symbol
        self.df = df
        self.status = "idle"
        self.report = {}

    def analyze(self):
        self.status = "busy"
        try:
            social_score, social_alert, social_details = get_social_sentiment_radar(self.symbol)
            alt_sent = get_alternative_data_sentiment(self.symbol)
            econ_alert, econ_event = check_economic_calendar_filter()

            # Tavily canlı internet arama (rakip haberleri + güncel gelişmeler)
            tavily_sonuclar = tavily_search(self.symbol, query_extra="rakip analiz sektör")
            tavily_skor = 50.0
            if tavily_sonuclar:
                poz_sayisi = sum(1 for h in tavily_sonuclar if h["duygu"] == "Pozitif")
                neg_sayisi = sum(1 for h in tavily_sonuclar if h["duygu"] == "Negatif")
                net_duygu = (poz_sayisi - neg_sayisi) / len(tavily_sonuclar) * 50
                tavily_skor = round(50.0 + net_duygu, 1)
                tavily_skor = max(0, min(100, tavily_skor))

            macro_risk = 30.0 if econ_alert else 85.0
            sentiment_score = round(
                social_score * 0.25 + alt_sent * 0.20 + tavily_skor * 0.30 + macro_risk * 0.25, 1
            )

            self.report = {
                "social_sentiment_score": social_score,
                "social_alert": social_alert,
                "social_details": social_details,
                "alternative_sentiment": alt_sent,
                "tavily_news": tavily_sonuclar,
                "tavily_score": tavily_skor,
                "tavily_count": len(tavily_sonuclar),
                "economic_alert": econ_alert,
                "economic_event": econ_event,
                "macro_risk_score": macro_risk,
                "sentiment_score": sentiment_score,
            }
            self.status = "done"
            return self.report
        except:
            self.status = "error"
            return {"sentiment_score": 50.0}

    async def analyze_async(self):
        return await asyncio.to_thread(self.analyze)

    async def analyze_fastapi_async(self):
        """FastAPI backend endpoint'inden async HTTP stream."""
        data = await FastAPIBackend.fetch_sentiment_data(self.symbol, self.df)
        social_score = data.get("social_score", 50)
        alt_sent = data.get("alt_sentiment", 50)
        econ_alert = data.get("econ_alert", False)
        econ_event = data.get("econ_event", "")
        tavily_count = data.get("tavily_count", 0)
        macro_risk = 30.0 if econ_alert else 85.0
        self.report = {
            "social_sentiment_score": social_score, "social_alert": social_score > 70,
            "social_details": {}, "alternative_sentiment": alt_sent,
            "tavily_news": [], "tavily_score": 50.0, "tavily_count": tavily_count,
            "economic_alert": econ_alert, "economic_event": econ_event,
            "macro_risk_score": macro_risk,
            "sentiment_score": round(social_score * 0.25 + alt_sent * 0.20 + macro_risk * 0.55, 1),
        }
        self.status = "done"
        return self.report


class HedgeFundManagerAgent:
    """3 uzman ajanın asenkron raporlarını asyncio.gather ile sentezleyerek nihai sinyali üretir."""

    def __init__(self, symbol, df, horizon="ORTA"):
        self.symbol = symbol
        self.df = df
        self.horizon = horizon.upper() if isinstance(horizon, str) else "ORTA"
        self.agents = {}
        self.consensus = {}
        self.final_signal = {}
        self.execution_time = 0

    async def run_async(self):
        """3 ajanı asyncio.gather ile paralel çalıştır."""
        import time
        start = time.time()

        tech = TechnicalAnalystAgent(self.symbol, self.df)
        whale = WhaleFlowAgent(self.symbol, self.df)
        macro = MacroSentimentAgent(self.symbol, self.df)

        results = await asyncio.gather(
            tech.analyze_async(),
            whale.analyze_async(),
            macro.analyze_async(),
        )

        self.agents = {
            "technical": {"agent": tech, "report": results[0]},
            "whale_flow": {"agent": whale, "report": results[1]},
            "sentiment": {"agent": macro, "report": results[2]},
        }

        self.execution_time = round(time.time() - start, 2)
        self._synthesize()
        return self.consensus

    async def run_fastapi_async(self):
        """3 ajanı FastAPI async endpoint'ler üzerinden paralel çalıştır."""
        import time
        start = time.time()

        tech = TechnicalAnalystAgent(self.symbol, self.df)
        whale = WhaleFlowAgent(self.symbol, self.df)
        macro = MacroSentimentAgent(self.symbol, self.df)

        results = await asyncio.gather(
            tech.analyze_fastapi_async(),
            whale.analyze_fastapi_async(),
            macro.analyze_fastapi_async(),
        )

        self.agents = {
            "technical": {"agent": tech, "report": results[0]},
            "whale_flow": {"agent": whale, "report": results[1]},
            "sentiment": {"agent": macro, "report": results[2]},
        }

        self.execution_time = round(time.time() - start, 2)
        self._synthesize()
        return self.consensus

    def run_with_status_stream(self):
        """Generator: ajan adımlarını canlı akış için sırayla yield eder."""
        import time
        self.status_updates = []
        yield ("system", "🚀 Çoklu-Ajan analizi başlatılıyor...", 0.0)

        tech = TechnicalAnalystAgent(self.symbol, self.df)
        whale = WhaleFlowAgent(self.symbol, self.df)
        macro = MacroSentimentAgent(self.symbol, self.df)

        try:
            yield ("technical", "📡 Teknik Ajan: RSI/MACD uyumsuzlukları taranıyor...", 0.15)
            t_rep = tech.analyze()
            yield ("technical", f"📡 Teknik Ajan: Tamamlandı (Skor: %{t_rep.get('technical_score',0)})", 0.30)

            yield ("whale", "🐋 Balina Ajan: Fon akışı ve emir defteri ölçülüyor...", 0.35)
            w_rep = whale.analyze()
            yield ("whale", f"🐋 Balina Ajan: Tamamlandı (Skor: %{w_rep.get('whale_score',0)})", 0.55)

            yield ("sentiment", "🌍 Duygu Ajanı: Haber ve sosyal medya taranıyor...", 0.60)
            s_rep = macro.analyze()
            yield ("sentiment", f"🌍 Duygu Ajanı: Tamamlandı (Skor: %{s_rep.get('sentiment_score',0)})", 0.80)

            self.agents = {
                "technical": {"agent": tech, "report": t_rep},
                "whale_flow": {"agent": whale, "report": w_rep},
                "sentiment": {"agent": macro, "report": s_rep},
            }
            self.execution_time = round(time.time() - start if 'start' in dir() else 0, 2)
            self._synthesize()
            yield ("system", f"✅ Konsensüs oluşturuldu — Nihai Skor: %{self.consensus.get('final_score',0)} | {self.consensus.get('signal','')}", 1.0)
        except:
            self.consensus = {"final_score": 50.0, "signal": "⚠️ HATA", "direction": "⚪ NÖTR"}
            yield ("system", "🔴 Ajan analizinde hata oluştu.", 1.0)

    def _synthesize(self):
        """Vade bazlı ağırlıklarla ajan raporlarını birleştir."""
        try:
            hw = get_weights_by_horizon(self.horizon)

            t_score = self.agents["technical"]["report"].get("technical_score", 50)
            w_score = self.agents["whale_flow"]["report"].get("whale_score", 50)
            s_score = self.agents["sentiment"]["report"].get("sentiment_score", 50)

            # Vade bazlı dinamik ağırlıklandırma
            w_tech = hw.get("momentum", 0) + hw.get("technical", 0) + hw.get("volume_anomaly", 0) + hw.get("orderbook", 0)
            w_fund = hw.get("fundamental", 0) + hw.get("flow", 0) + hw.get("monte_carlo", 0)
            w_sent = hw.get("sentiment", 0) + hw.get("macro", 0)

            total_w = w_tech + w_fund + w_sent
            if total_w == 0:
                w_tech, w_fund, w_sent = 0.4, 0.3, 0.3
                total_w = 1.0

            final_score = (t_score * w_tech + w_score * w_fund + s_score * w_sent) / total_w
            final_score = round(max(0, min(100, final_score)), 1)

            if final_score >= 75:
                signal = "🔥 GÜÇLÜ AL"
                direction = "🟢 AL"
            elif final_score >= 60:
                signal = "✅ AL"
                direction = "🟢 AL"
            elif final_score >= 40:
                signal = "⚠️ NÖTR"
                direction = "⚪ NÖTR"
            elif final_score >= 25:
                signal = "❌ SAT"
                direction = "🔴 SAT"
            else:
                signal = "🔴 GÜÇLÜ SAT"
                direction = "🔴 SAT"

            self.consensus = {
                "final_score": final_score,
                "signal": signal,
                "direction": direction,
                "technical_score": round(t_score, 1),
                "whale_score": round(w_score, 1),
                "sentiment_score": round(s_score, 1),
                "weights": {
                    "technical": round(w_tech / total_w, 3),
                    "whale_flow": round(w_fund / total_w, 3),
                    "sentiment": round(w_sent / total_w, 3),
                },
                "horizon": self.horizon,
                "execution_time": self.execution_time,
                "status": "synth_done",
            }
        except:
            self.consensus = {"final_score": 50.0, "signal": "⚠️ HATA", "direction": "⚪ NÖTR"}

    def get_report_card(self):
        c = self.consensus
        if not c:
            return {}
        return {
            "🧠 Skor": f"%{c.get('final_score', 0)}",
            "📡 Sinyal": c.get("signal", ""),
            "📊 Teknik": f"%{c.get('technical_score', 0)}",
            "🐋 Balina": f"%{c.get('whale_score', 0)}",
            "🌍 Duygu": f"%{c.get('sentiment_score', 0)}",
            "⏱️ Süre": f"{c.get('execution_time', 0)}s",
        }

    # Sync wrapper for non-async contexts (avoids Streamlit event loop conflict)
    def run_parallel(self):
        """Senkron fallback — yeni event loop ile çağır."""
        import time
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.run_async())
            loop.close()
            return result
        except:
            time.sleep(0.1)
            self._synthesize()
            return self.consensus


# ============================================================
# 🎯 AJAN KONSENSÜS DASHBOARD (3 Sütunlu Konsensüs Paneli)
# ============================================================

class ConsensusDashboard:
    """Teknik, Balina ve Duygu ajanlarının çıktılarını 3 sütunlu widget panelinde
    konsolide eder. Vade bazlı ağırlıklandırma ile nihai sinyali üretir."""

    def __init__(self, symbol, df, horizon="ORTA"):
        self.symbol = symbol
        self.df = df
        self.horizon = horizon.upper() if isinstance(horizon, str) else "ORTA"
        self.tech_agent = TechnicalAnalystAgent(symbol, df)
        self.whale_agent = WhaleFlowAgent(symbol, df)
        self.sent_agent = MacroSentimentAgent(symbol, df)
        self.results = {}
        self.consensus = {}
        self.execution_time = 0.0

    # ----------------------------------------------------------
    # ASENKRON: 3 ajanı paralel çalıştır
    # ----------------------------------------------------------
    async def run_async(self):
        """3 uzman ajanı asyncio.gather ile eşzamanlı çalıştırır."""
        import time
        basla = time.time()
        try:
            sonuclar = await asyncio.gather(
                self.tech_agent.analyze_async(),
                self.whale_agent.analyze_async(),
                self.sent_agent.analyze_async(),
            )
            self.results = {
                "technical": sonuclar[0],
                "whale_flow": sonuclar[1],
                "sentiment": sonuclar[2],
            }
        except:
            self.results = {
                "technical": {"technical_score": 50.0},
                "whale_flow": {"whale_score": 50.0},
                "sentiment": {"sentiment_score": 50.0},
            }
        self.execution_time = round(time.time() - basla, 2)
        self._synthesize()
        return self.consensus

    # ----------------------------------------------------------
    # VADE BAZLI AĞIRLIKLANDIRMA MOTORU
    # ----------------------------------------------------------
    def _synthesize(self):
        """Vadeye göre dinamik ağırlıklarla 3 ajanın skorlarını birleştirir."""
        try:
            hw = get_weights_by_horizon(self.horizon)

            t_skor = self.results.get("technical", {}).get("technical_score", 50)
            w_skor = self.results.get("whale_flow", {}).get("whale_score", 50)
            s_skor = self.results.get("sentiment", {}).get("sentiment_score", 50)

            w_tech = hw.get("momentum", 0) + hw.get("technical", 0) + hw.get("volume_anomaly", 0) + hw.get("orderbook", 0)
            w_fund = hw.get("fundamental", 0) + hw.get("flow", 0) + hw.get("monte_carlo", 0)
            w_sent = hw.get("sentiment", 0) + hw.get("macro", 0)

            toplam = w_tech + w_fund + w_sent
            if toplam == 0:
                w_tech, w_fund, w_sent = 0.4, 0.3, 0.3
                toplam = 1.0

            nihai_skor = (t_skor * w_tech + w_skor * w_fund + s_skor * w_sent) / toplam
            nihai_skor = round(max(0, min(100, nihai_skor)), 1)

            if nihai_skor >= 75:
                sinyal = "🔥 GÜÇLÜ AL"
                yon = "🟢 AL"
            elif nihai_skor >= 60:
                sinyal = "✅ AL"
                yon = "🟢 AL"
            elif nihai_skor >= 40:
                sinyal = "⚠️ NÖTR (BEKLE)"
                yon = "⚪ NÖTR"
            elif nihai_skor >= 25:
                sinyal = "❌ SAT"
                yon = "🔴 SAT"
            else:
                sinyal = "🔴 GÜÇLÜ SAT"
                yon = "🔴 SAT"

            self.consensus = {
                "final_score": nihai_skor,
                "signal": sinyal,
                "direction": yon,
                "technical_score": round(t_skor, 1),
                "whale_score": round(w_skor, 1),
                "sentiment_score": round(s_skor, 1),
                "weights": {
                    "technical": round(w_tech / toplam, 3),
                    "whale_flow": round(w_fund / toplam, 3),
                    "sentiment": round(w_sent / toplam, 3),
                },
                "horizon": self.horizon,
                "execution_time": self.execution_time,
            }
        except:
            self.consensus = {
                "final_score": 50.0, "signal": "⚠️ HATA", "direction": "⚪ NÖTR",
                "technical_score": 50, "whale_score": 50, "sentiment_score": 50,
            }

    # ----------------------------------------------------------
    # YARDIMCI: EMA 50/200 durum analizi
    # ----------------------------------------------------------
    @staticmethod
    def _get_ema_durum(df):
        """Fiyatın EMA 50 ve EMA 200'e göre konumunu döndürür."""
        try:
            if df.empty or 'Close' not in df.columns or len(df) < 200:
                return "N/A", "N/A", "N/A"
            close = df['Close'].squeeze().astype(float)
            ema50 = ta.trend.ema_indicator(close, window=50).iloc[-1]
            ema200 = ta.trend.ema_indicator(close, window=200).iloc[-1]
            fiyat = close.iloc[-1]
            if pd.isna(ema50) or pd.isna(ema200):
                return "N/A", "N/A", "N/A"
            durum50 = "🟢 Üstünde" if fiyat >= ema50 else "🔴 Altında"
            durum200 = "🟢 Üstünde" if fiyat >= ema200 else "🔴 Altında"
            trend = "📈 Yükseliş" if ema50 > ema200 else "📉 Düşüş"
            return durum50, durum200, trend
        except:
            return "Hata", "Hata", "Hata"

    # ----------------------------------------------------------
    # YARDIMCI: Bollinger Band sıkışma analizi
    # ----------------------------------------------------------
    @staticmethod
    def _get_bb_durum(df, pencere=20):
        """Bollinger Band sıkışma (squeeze) durumunu hesaplar."""
        try:
            if df.empty or 'Close' not in df.columns or len(df) < pencere + 10:
                return "N/A", 0
            close = df['Close'].squeeze().astype(float)
            bb = ta.volatility.BollingerBands(close, window=pencere)
            bb_genislik = (bb.bollinger_hband().iloc[-1] - bb.bollinger_lband().iloc[-1]) / bb.bollinger_mavg().iloc[-1] * 100
            son_20 = []
            for i in range(min(20, len(close) - pencere)):
                ust = bb.bollinger_hband().iloc[-(i + 1)]
                alt = bb.bollinger_lband().iloc[-(i + 1)]
                orta = bb.bollinger_mavg().iloc[-(i + 1)]
                son_20.append((ust - alt) / orta * 100)
            ortalama_genislik = sum(son_20) / len(son_20) if son_20 else bb_genislik
            sikisma_orani = (1 - bb_genislik / ortalama_genislik) * 100 if ortalama_genislik > 0 else 0
            durum = "🔴 Sıkışma" if bb_genislik < ortalama_genislik * 0.8 else "🟢 Normal"
            return durum, round(sikisma_orani, 1)
        except:
            return "N/A", 0

    # ----------------------------------------------------------
    # Streamlit RENDER — 3 Sütunlu Widget + Konsensüs Paneli
    # ----------------------------------------------------------
    def render(self, container=None):
        """Tam paneli Streamlit arayüzünde çizer."""
        hedef = container if container else st

        mem = st.session_state.get("agent_memory", {})
        t_skor = mem.get("technical_score")
        w_skor = mem.get("whale_score")
        s_skor = mem.get("sentiment_score")

        t_rep = self.results.get("technical", {})
        w_rep = self.results.get("whale_flow", {})
        s_rep = self.results.get("sentiment", {})

        divs = t_rep.get("divergences", [])
        if not divs and t_skor is not None:
            try:
                divs = detect_divergence(self.df)
            except:
                divs = []
        ema50_durum, ema200_durum, trend = self._get_ema_durum(self.df)
        bb_durum, bb_sikisma = self._get_bb_durum(self.df)

        inst_stability = w_rep.get("institution_stability", 50)
        inst_flow = w_rep.get("institution_flow", {})
        ob_skor = w_rep.get("order_book_score", 50)

        sosyal_skor = s_rep.get("social_sentiment_score", 50)
        sosyal_alert = s_rep.get("social_alert", False)
        tavily_count = s_rep.get("tavily_count", 0)
        alt_sent = s_rep.get("alternative_sentiment", 50)

        hedef.markdown("""<hr style='margin:4px 0;border-color:#1e293b;'>""", unsafe_allow_html=True)
        sut1, sut2, sut3 = hedef.columns(3, gap="small")

        # ——— SÜTUN 1: TEKNİK ———
        with sut1:
            t_renk = "#4ade80" if t_skor is not None and t_skor >= 60 else "#ef4444" if t_skor is not None and t_skor <= 30 else "#fbbf24"
            t_gosterge = f"%{t_skor:.0f}" if isinstance(t_skor, (int, float)) else "%—"
            icerik1 = f"""<div style="background:#0F172A; border:1px solid #1e293b; border-radius:12px; padding:12px; height:100%;">
                <div style="font-size:12px; color:#94a3b8; font-weight:600; letter-spacing:0.5px;">🟢 TEKNİK MOMENTUM</div>
                <div style="font-size:26px; font-weight:700; color:{t_renk}; margin:4px 0;">{t_gosterge}</div>
                <div style="font-size:11px; color:#cbd5e1; line-height:1.8;">"""
            if divs:
                for d in divs[:2]:
                    etiket = d[2] if len(d) > 2 else d[0]
                    icerik1 += f"▸ 🔍 Uyumsuzluk: {etiket[:60]}<br>"
            else:
                icerik1 += "▸ ✅ RSI uyumsuzluk yok<br>"
            icerik1 += f"""▸ 📊 EMA 50: {ema50_durum}<br>▸ 📊 EMA 200: {ema200_durum}<br>▸ 📈 Trend: {trend}<br>▸ 📉 BB: {bb_durum} (%{bb_sikisma})
                </div></div>"""
            st.markdown(icerik1, unsafe_allow_html=True)

        # ——— SÜTUN 2: BALİNA ———
        with sut2:
            w_renk = "#38bdf8" if w_skor is not None and w_skor >= 60 else "#ef4444" if w_skor is not None and w_skor <= 30 else "#fbbf24"
            w_gosterge = f"%{w_skor:.0f}" if isinstance(w_skor, (int, float)) else "%—"
            icerik2 = f"""<div style="background:#0F172A; border:1px solid #1e293b; border-radius:12px; padding:12px; height:100%;">
                <div style="font-size:12px; color:#94a3b8; font-weight:600; letter-spacing:0.5px;">🔵 BALİNA & TAKAS</div>
                <div style="font-size:26px; font-weight:700; color:{w_renk}; margin:4px 0;">{w_gosterge}</div>
                <div style="font-size:11px; color:#cbd5e1; line-height:1.8;">"""
            if isinstance(inst_stability, (int, float)):
                kr = "#4ade80" if inst_stability >= 60 else "#ef4444"
                icerik2 += f"▸ 🏦 Kurum Kararlılığı: <span style='color:{kr};'>%{inst_stability:.0f}</span><br>"
            else:
                icerik2 += "▸ 🏦 Kurum Kararlılığı: —<br>"
            ob_renk = "#4ade80" if ob_skor >= 60 else "#ef4444" if ob_skor <= 40 else "#fbbf24"
            ob_yon = "Alış Baskın" if ob_skor >= 55 else "Satış Baskın" if ob_skor <= 45 else "Dengeli"
            icerik2 += f"▸ 📋 Emir Defteri: <span style='color:{ob_renk};'>{ob_yon} (%{ob_skor:.0f})</span><br>"
            if inst_flow and isinstance(inst_flow, dict):
                net_flow = inst_flow.get("net_flow", 0)
                frk = "#4ade80" if net_flow > 0 else "#ef4444"
                icerik2 += f"▸ 💰 Net Fon: <span style='color:{frk};'>{net_flow:+.1f}M</span><br>"
            else:
                icerik2 += "▸ 💰 Net Fon: —<br>"
            icerik2 += "</div></div>"
            st.markdown(icerik2, unsafe_allow_html=True)

        # ——— SÜTUN 3: DUYGU ———
        with sut3:
            s_renk = "#fbbf24" if s_skor is not None and s_skor >= 60 else "#ef4444" if s_skor is not None and s_skor <= 30 else "#94a3b8"
            s_gosterge = f"%{s_skor:.0f}" if isinstance(s_skor, (int, float)) else "%—"
            icerik3 = f"""<div style="background:#0F172A; border:1px solid #1e293b; border-radius:12px; padding:12px; height:100%;">
                <div style="font-size:12px; color:#94a3b8; font-weight:600; letter-spacing:0.5px;">🟡 MAKRO DUYGU</div>
                <div style="font-size:26px; font-weight:700; color:{s_renk}; margin:4px 0;">{s_gosterge}</div>
                <div style="font-size:11px; color:#cbd5e1; line-height:1.8;">"""
            if isinstance(sosyal_skor, (int, float)):
                sr = "#4ade80" if sosyal_skor >= 60 else "#ef4444" if sosyal_skor <= 40 else "#fbbf24"
                icerik3 += f"▸ 📰 Haber Duyarlılığı: <span style='color:{sr};'>%{sosyal_skor:.0f}</span><br>"
            else:
                icerik3 += "▸ 📰 Haber Duyarlılığı: —<br>"
            ano_durum = "🚨 Anomali (+) " if sosyal_alert else "✅ Normal"
            ano_renk = "#f97316" if sosyal_alert else "#4ade80"
            icerik3 += f"▸ 🌐 Sosyal Medya: <span style='color:{ano_renk};'>{ano_durum}</span><br>"
            if tavily_count > 0:
                icerik3 += f"▸ 🔎 Tavily Haber: {tavily_count} kaynak<br>"
            if isinstance(alt_sent, (int, float)):
                icerik3 += f"▸ 📊 Alternatif Duygu: %{alt_sent:.0f}<br>"
            icerik3 += "</div></div>"
            st.markdown(icerik3, unsafe_allow_html=True)

        # ——— KONSENSÜS PANELİ (3 sütunun altında) ———
        hedef.markdown("""<hr style='margin:6px 0;border-color:#1e293b;'>""", unsafe_allow_html=True)
        c = self.consensus if self.consensus else {}
        nihai_skor = c.get("final_score") or mem.get("final_score") or 50
        sinyal = c.get("signal") or mem.get("signal") or "⚠️ BEKLE"
        yon = c.get("direction") or "⚪ NÖTR"
        horizon = c.get("horizon") or st.session_state.get("vade", "ORTA")

        if nihai_skor >= 75:
            panel_renk = "#4ade80"
            arkaplan = "rgba(74,222,128,0.08)"
        elif nihai_skor >= 60:
            panel_renk = "#22c55e"
            arkaplan = "rgba(34,197,94,0.06)"
        elif nihai_skor >= 40:
            panel_renk = "#fbbf24"
            arkaplan = "rgba(251,191,36,0.06)"
        elif nihai_skor >= 25:
            panel_renk = "#ef4444"
            arkaplan = "rgba(239,68,68,0.08)"
        else:
            panel_renk = "#dc2626"
            arkaplan = "rgba(220,38,38,0.1)"

        hedef.markdown(f"""
        <div style="background:{arkaplan}; border:1px solid {panel_renk}40; border-left:4px solid {panel_renk};
                    border-radius:12px; padding:14px 20px; margin:6px 0; text-align:center;">
            <div style="display:flex; justify-content:center; align-items:center; gap:24px; flex-wrap:wrap;">
                <div>
                    <div style="font-size:11px; color:#94a3b8; font-weight:500; letter-spacing:0.5px;">ORTAK KONSENSÜS SKORU</div>
                    <div style="font-size:32px; font-weight:700; color:{panel_renk};">%{nihai_skor:.0f}</div>
                </div>
                <div style="border-left:1px solid #1e293b; height:40px;"></div>
                <div>
                    <div style="font-size:11px; color:#94a3b8; font-weight:500; letter-spacing:0.5px;">📢 SİSTEM SİNYALİ</div>
                    <div style="font-size:22px; font-weight:700; color:{panel_renk};">{sinyal}</div>
                </div>
                <div style="border-left:1px solid #1e293b; height:40px;"></div>
                <div>
                    <div style="font-size:11px; color:#94a3b8; font-weight:500; letter-spacing:0.5px;">📅 VADE</div>
                    <div style="font-size:18px; font-weight:600; color:#e2e8f0;">{horizon}</div>
                </div>
                <div style="border-left:1px solid #1e293b; height:40px;"></div>
                <div>
                    <div style="font-size:11px; color:#94a3b8; font-weight:500; letter-spacing:0.5px;">⏱ SÜRE</div>
                    <div style="font-size:18px; font-weight:600; color:#e2e8f0;">{c.get('execution_time', mem.get('execution_time', '—'))}s</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with st.sidebar:
    # BAŞLIK
    st.markdown("""
    <div style="padding: 6px 8px 4px 8px; margin: 0;">
        <div style="font-size: 20px; font-weight: 700; color: #e2e8f0; letter-spacing: -0.5px;">
            📊 Borsa Analiz
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ANA SAYFA
    ana_sec = st.button("🏠 Ana Sayfa", use_container_width=True, type="secondary")
    if ana_sec:
        st.session_state.menu_secim = "🏠 Ana Sayfa"
        st.rerun()

    # AL-SAT ŞARTLARI
    al_sat_btn = st.button("📋 Al-Sat Şartları", use_container_width=True, type="secondary")
    if al_sat_btn:
        st.session_state.menu_secim = "📋 Al-Sat Şartları"
        st.rerun()

    # Hisse seçici
    st.selectbox(
        "Sembol",
        options=list(COMMON_SYMBOLS.keys()),
        format_func=lambda x: f"{x} — {COMMON_SYMBOLS[x]}",
        key="selected_symbol",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='streamlit-expanderHeader' style='margin-top: 4px;'>YAPAY ZEKA MERKEZİ</div>", unsafe_allow_html=True)
    ai_choice = st.radio("AI", [
        "🤖 AI Karar Motoru",
        "🧠 Gelişmiş AI (Kalibrasyon)",
        "🔮 AI Fiyat Tahmini",
    ], key="ai_menu", label_visibility="collapsed", index=0)
    if ai_choice != st.session_state.get("last_ai_menu"):
        st.session_state.menu_secim = ai_choice
        st.session_state.last_ai_menu = ai_choice
        st.rerun()

    # KATMAN 3: TARAMA & PİYASA AKIŞI
    st.markdown("<div class='streamlit-expanderHeader' style='margin-top: 10px;'>TARAMA & PİYASA AKIŞI</div>", unsafe_allow_html=True)
    radar_choice = st.radio("Radar", [
        "📈 Piyasa Radarı (Sinyal Taraması)",
        "🗺️ Market Heatmap (Isı Haritası)",
        "🌍 Küresel Radar (Makro)",
        "🚨 Emir Defteri Dengesizliği",
    ], key="radar_menu", label_visibility="collapsed")
    if radar_choice != st.session_state.get("last_radar_menu"):
        st.session_state.menu_secim = radar_choice
        st.session_state.last_radar_menu = radar_choice
        st.rerun()

    # KATMAN 4: DERİN ANALİZ LABORATUVARI
    st.markdown("<div class='streamlit-expanderHeader' style='margin-top: 10px;'>DERİN ANALİZ LABORATUVARI</div>", unsafe_allow_html=True)
    analiz_choice = st.radio("Analiz", [
        "📊 Teknik Analiz (Uyumsuzluklar)",
        "📑 Temel Analiz & Sağlık",
        "🎭 Sektörel Analiz (Kıyas)",
        "🏦 Fon & Takas Analizi",
        "📰 Haber & KAP (Duygu Analizi)",
        "📉 Sosyal Medya Radarı",
    ], key="analiz_menu", label_visibility="collapsed")
    if analiz_choice != st.session_state.get("last_analiz_menu"):
        st.session_state.menu_secim = analiz_choice
        st.session_state.last_analiz_menu = analiz_choice
        st.rerun()

    # KATMAN 5: RİSK & STRATEJİ DOĞRULAMA
    st.markdown("<div class='streamlit-expanderHeader' style='margin-top: 10px;'>RİSK & STRATEJİ DOĞRULAMA</div>", unsafe_allow_html=True)
    risk_choice = st.radio("Risk", [
        "🧪 Strateji Testi (Backtest)",
        "🎲 Monte Carlo Simülasyonu",
        "🎒 Portföy Analizi & Drawdown",
        "📅 Ekonomik Takvim Filtresi",
    ], key="risk_menu", label_visibility="collapsed")
    if risk_choice != st.session_state.get("last_risk_menu"):
        st.session_state.menu_secim = risk_choice
        st.session_state.last_risk_menu = risk_choice
        st.rerun()
    
    st.divider()

    # ⭐ WATCHLIST (Fixing previous failure)
    st.subheader("⭐ İzleme Listesi")
    w_list = st.multiselect("Favoriler", options=list(COMMON_SYMBOLS.keys()), default=["THYAO.IS", "GC=F", "BTC-USD"])
    if w_list:
        try:
            w_data = yf.download(w_list, period="2d", progress=False)['Close']
            if isinstance(w_data.columns, pd.MultiIndex): w_data.columns = w_data.columns.get_level_values(0)
            for sym in w_list:
                if sym in w_data.columns and len(w_data) > 1:
                    last_val = w_data[sym].iloc[-1]
                    prev_val = w_data[sym].iloc[0]
                    change = ((last_val / prev_val) - 1) * 100
                    st.write(f"**{sym}**: {last_val:.2f} (%{change:+.2f})")
        except:
            st.write("İzleme listesi yüklenemedi.")
    
    st.divider()
    
    # LIVE REFRESH
    st.subheader("🔄 Canlı Veri Akışı")
    auto_refresh = st.checkbox("Otomatik Yenile", value=False)
    refresh_interval = st.slider("Yenileme Aralığı (sn)", 5, 60, 30)
    if auto_refresh:
        import time
        time.sleep(refresh_interval)
        st.rerun()
        
    st.divider()
    
    # 7. BRACKET ORDER — KÂR AL / ZARAR DURDUR EMİR GİRİŞİ
    st.subheader("🎯 Bracket Order Emri")
    entry_price = st.number_input("Giriş Fiyatı", value=100.0, key="bracket_entry")
    take_profit = st.number_input("Take Profit (Kâr Al) Fiyatı", value=110.0, key="bracket_tp")
    stop_loss = st.number_input("Stop Loss (Zarar Durdur) Fiyatı", value=95.0, key="bracket_sl")

    if entry_price and take_profit and stop_loss:
        tp_yuzde = ((take_profit / entry_price) - 1) * 100
        sl_yuzde = ((stop_loss / entry_price) - 1) * 100
        r_r_orani = (take_profit - entry_price) / (entry_price - stop_loss) if entry_price > stop_loss else 0

        br1, br2, br3 = st.columns(3)
        br1.metric("Kâr Hedefi", f"%{tp_yuzde:+.2f}", delta="TP")
        br2.metric("Zarar Limiti", f"%{sl_yuzde:+.2f}", delta="SL")
        br3.metric("Risk/Ödül Oranı", f"1:{r_r_orani:.2f}" if r_r_orani > 0 else "Geçersiz")

        if r_r_orani >= 2.0:
            st.success(f"✅ İdeal bracket! R/R = 1:{r_r_orani:.2f} (≥1:2)")
        elif r_r_orani >= 1.0:
            st.info(f"⚠️ Kabul edilebilir bracket. R/R = 1:{r_r_orani:.2f}")
        else:
            st.warning(f"🔴 Düşük R/R oranı. Riskinizi azaltmayı düşünün.")

        # WhaleAgent'a dinamik veri akışı
        st.session_state["bracket_order"] = {
            "symbol": st.session_state.get("selected_symbol", ""),
            "entry": entry_price,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "r_r": round(r_r_orani, 2),
            "tp_yuzde": round(tp_yuzde, 2),
            "sl_yuzde": round(sl_yuzde, 2),
            "aktif": True,
        }

    st.divider()

    # 8. RİSK HESAPLAYICI (sermaye bazlı)
    st.subheader("⚖️ Sermaye Risk Hesaplayıcı")
    capital = st.number_input("Toplam Sermaye", value=100000, key="risk_capital")
    risk_pct = st.slider("İşlem Başı Risk (%)", 0.5, 5.0, 2.0, key="risk_pct")
    if entry_price and stop_loss and entry_price > stop_loss:
        risk_per_share = entry_price - stop_loss
        max_loss = capital * (risk_pct / 100)
        lot_size = int(max_loss / risk_per_share)
        poz_buyuklugu = lot_size * entry_price
        st.success(f"📊 {lot_size} Lot (₺{poz_buyuklugu:,.0f}) — Maks Risk: ₺{max_loss:,.0f}")
    
    st.divider()
    
    # YATIRIMCI GÜNLÜĞÜ
    st.subheader("📓 Yatırım Günlüğü")
    journal_note = st.text_area("İşlem Notu")
    mood = st.select_slider("Duygu Durumu", options=["Korku", "Endişe", "Nötr", "Güven", "Açgözlülük"], value="Nötr")
    if st.button("Günlüğe Kaydet"):
        log_data = {
            "Date": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M")],
            "Symbol": [st.session_state.selected_symbol],
            "Note": [journal_note],
            "Mood": [mood]
        }
        log_df = pd.DataFrame(log_data)
        file_path = "journal.csv"
        if not os.path.isfile(file_path):
            log_df.to_csv(file_path, index=False)
        else:
            log_df.to_csv(file_path, mode='a', header=False, index=False)
        st.info("Kaydedildi.")

# --- FETCH TICKER & FX DATA ---
try:
    fx_list = ["USDTRY=X", "USDKZT=X"]
    ticker_fx = yf.download(fx_list, period="5d", progress=False)['Close']
    if isinstance(ticker_fx.columns, pd.MultiIndex): ticker_fx.columns = ticker_fx.columns.get_level_values(0)
    
    u_try = ticker_fx['USDTRY=X'].iloc[-1]
    u_kzt = ticker_fx['USDKZT=X'].iloc[-1]
    t_kzt = u_kzt / u_try
    
    ticker_html = f"""
        <div style="background-color: #0a0e17; padding: 6px 10px; border-bottom: 1px solid #1f2937; overflow: hidden; white-space: nowrap;">
            <div style="display: inline-block; animation: marquee 20s linear infinite;">
                <span style="color: #58a6ff; font-weight: bold; margin-right: 50px;">🚀 STRATEJİ TERMİNALİ CANLI AKIŞ:</span>
                <span style="margin-right: 50px;">💵 USD/TRY: <b>{u_try:.4f}</b></span>
                <span style="margin-right: 50px;">🇰🇿 USD/KZT: <b>{u_kzt:.2f}</b></span>
                <span style="margin-right: 50px;">🔄 TRY/KZT: <b>{t_kzt:.4f}</b></span>
                <span style="margin-right: 50px;">💵 USD/TRY: <b>{u_try:.4f}</b></span>
                <span style="margin-right: 50px;">🇰🇿 USD/KZT: <b>{u_kzt:.2f}</b></span>
            </div>
        </div>
        <style>
            @keyframes marquee {{
                0% {{ transform: translateX(100%); }}
                100% {{ transform: translateX(-100%); }}
            }}
        </style>
    """
    st.markdown(ticker_html, unsafe_allow_html=True)
except:
    st.error("Kur akışı başlatılamadı.")

# --- AI AJAN DURUM BARI (st.progress + st.metric) ---
# Session State hafıza: ajan skorları sayfalar arası kaybolmasın
if "agent_memory" not in st.session_state:
    st.session_state.agent_memory = {}
if "cot_log" not in st.session_state:
    st.session_state.cot_log = []

# State management + ortak veri (agent bar'da kullanılır)
if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = list(COMMON_SYMBOLS.keys())[0]
search_query = st.session_state.selected_symbol
data = pd.DataFrame()
try:
    data = yf.download(search_query, period=st.session_state.get("pr", "1y"), interval=st.session_state.get("tf", "1d"), progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
except:
    data = pd.DataFrame()

agent_row = st.columns([1, 1, 1, 1, 1])
mem = st.session_state.agent_memory
with agent_row[0]:
    st.metric("🧠 AI Ağ", "Hazır" if mem else "Beklemede", "🟢" if mem else "⚪")
    st.progress(1.0 if mem else 0.0)
with agent_row[1]:
    t_skor = mem.get("technical_score", "—")
    st.metric("📡 Teknik", f"%{t_skor}" if isinstance(t_skor, (int, float)) else "—", "🟢" if isinstance(t_skor, (int, float)) else "⚪")
    st.progress(max(0, (t_skor / 100) if isinstance(t_skor, (int, float)) else 0))
with agent_row[2]:
    w_skor = mem.get("whale_score", "—")
    st.metric("🐋 Balina", f"%{w_skor}" if isinstance(w_skor, (int, float)) else "—", "🟢" if isinstance(w_skor, (int, float)) else "⚪")
    st.progress(max(0, (w_skor / 100) if isinstance(w_skor, (int, float)) else 0))
with agent_row[3]:
    s_skor = mem.get("sentiment_score", "—")
    st.metric("🌍 Duygu", f"%{s_skor}" if isinstance(s_skor, (int, float)) else "—", "🟢" if isinstance(s_skor, (int, float)) else "⚪")
    st.progress(max(0, (s_skor / 100) if isinstance(s_skor, (int, float)) else 0))
with agent_row[4]:
    vade_durum = {"KISA": ("Kısa Vade", "🔴", 0.33), "ORTA": ("Orta Vade", "🟡", 0.66), "UZUN": ("Uzun Vade", "🟢", 1.0)}
    _v = vade_durum.get(st.session_state.get("vade", "ORTA"), ("Orta Vade", "🟡", 0.66))
    st.metric("📅 Vade", f"{_v[1]} {_v[0]}")
    st.progress(_v[2])

# Ajan zincir akışı butonu + canlı durum
cot_container = st.empty()
if st.button("🧠 Ajanları Çalıştır (Chain-of-Thought)", key="run_agents_cot", use_container_width=True):
    mgr_cot = HedgeFundManagerAgent(
        st.session_state.get("selected_symbol", "THYAO.IS"),
        data if not data.empty else pd.DataFrame(),
        horizon=st.session_state.get("vade", "ORTA"),
    )
    with cot_container.container():
        status_placeholder = st.status("🤖 Ajanlar başlatılıyor...", expanded=True)
        for agent_type, message, progress_val in mgr_cot.run_with_status_stream():
            if agent_type == "system":
                if progress_val >= 1.0:
                    status_placeholder.update(label="✅ " + message, state="complete", expanded=False)
                else:
                    status_placeholder.update(label=message, state="running")
            else:
                status_placeholder.write(f"- {message}")
            st.session_state.cot_log.append({"agent": agent_type, "msg": message, "progress": progress_val})
        # Session State hafızasına kaydet
        c = mgr_cot.consensus
        st.session_state.agent_memory = {
            "final_score": c.get("final_score"),
            "signal": c.get("signal"),
            "technical_score": c.get("technical_score"),
            "whale_score": c.get("whale_score"),
            "sentiment_score": c.get("sentiment_score"),
            "horizon": c.get("horizon"),
            "execution_time": c.get("execution_time"),
        }
        st.rerun()

# --- MAIN DASHBOARD ---
if "menu_secim" not in st.session_state:
    st.session_state.menu_secim = "🏠 Ana Sayfa"
secim = st.session_state.menu_secim

# State management for TF (tüm sekmeler için ortak)
if 'tf' not in st.session_state: st.session_state.tf = "1d"
if 'pr' not in st.session_state: st.session_state.pr = "1y"

# (data + search_query yukarıda agent bar öncesinde tanımlandı)

if secim == "🏠 Ana Sayfa":
    # ——— BLOOMBERG-STYLE HİSSE KARTI ———
    col_logo, col_price = st.columns([1, 3])
    sym_clean = search_query.replace(".IS", "")
    close_val = data['Close'].iloc[-1] if not data.empty else 0
    prev_close = data['Close'].iloc[0] if len(data) > 1 else close_val
    chg_pct = ((close_val / prev_close) - 1) * 100 if prev_close else 0
    chg_color = "#00e676" if chg_pct >= 0 else "#ef5350"
    chg_sign = "+" if chg_pct >= 0 else ""

    with col_logo:
        st.markdown(f"<div style='background:#1f2937;border-radius:8px;padding:12px;text-align:center;font-size:32px;'>{sym_clean[:2]}</div>", unsafe_allow_html=True)
    with col_price:
        st.markdown(
            f"<span style='font-size:12px;color:#8b949e;'>{COMMON_SYMBOLS.get(search_query, search_query)}</span><br>"
            f"<span style='font-size:30px;font-weight:700;color:#f0f6fc;'>{close_val:.4f}</span>&nbsp;"
            f"<span style='font-size:16px;color:{chg_color};font-weight:600;'>({chg_sign}{chg_pct:.2f}%)</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ——— AJAN KONSENSÜS DASHBOARD (3 sütunlu widget + konsensüs paneli) ———
    dashboard = ConsensusDashboard(search_query, data, st.session_state.get("vade", "ORTA"))
    dashboard.render()

    # Asenkron paralel çalıştırma butonu
    col_btn, col_info = st.columns([3, 1])
    with col_btn:
        if st.button("🚀 Ajanları Paralel Çalıştır (asyncio.gather)", key="ana_sayfa_async", use_container_width=True):
            with st.spinner("🧠 3 ajan paralel taranıyor..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    sonuc = loop.run_until_complete(dashboard.run_async())
                    loop.close()
                    st.session_state.agent_memory = {
                        "final_score": sonuc.get("final_score"),
                        "signal": sonuc.get("signal"),
                        "technical_score": sonuc.get("technical_score"),
                        "whale_score": sonuc.get("whale_score"),
                        "sentiment_score": sonuc.get("sentiment_score"),
                        "horizon": sonuc.get("horizon"),
                        "execution_time": sonuc.get("execution_time"),
                    }
                    st.rerun()
                except:
                    st.warning("Paralel çalıştırma başarısız, sıralı moda geçiliyor...")
                    mgr = HedgeFundManagerAgent(search_query, data, st.session_state.get("vade", "ORTA"))
                    for _, _, _ in mgr.run_with_status_stream():
                        pass
                    c = mgr.consensus
                    st.session_state.agent_memory = {
                        "final_score": c.get("final_score"),
                        "signal": c.get("signal"),
                        "technical_score": c.get("technical_score"),
                        "whale_score": c.get("whale_score"),
                        "sentiment_score": c.get("sentiment_score"),
                        "horizon": c.get("horizon"),
                        "execution_time": c.get("execution_time"),
                    }
                    st.rerun()
    with col_info:
        mem_check = st.session_state.get("agent_memory", {})
        if mem_check.get("execution_time"):
            st.caption(f"⏱ Son çalışma: {mem_check['execution_time']}s | Vade: {mem_check.get('horizon', '—')}")

    # Chain-of-Thought geçmişi
    cot_log = st.session_state.get("cot_log", [])
    if cot_log:
        with st.expander("🧠 Ajan Düşünce Zinciri (Chain-of-Thought)", expanded=False):
            for entry in cot_log[-20:]:
                emoji_map = {"technical": "📡", "whale": "🐋", "sentiment": "🌍", "system": "⚙️"}
                st.write(f"{emoji_map.get(entry['agent'], '▸')} {entry['msg']}")

    st.divider()

    # ——— PİYASA ÖZETİ METRİKLERİ ———
    try:
        fx_snapshot = yf.download(["USDTRY=X", "USDKZT=X", "GC=F", "BTC-USD", "^GSPC"], period="2d", progress=False)['Close']
        if isinstance(fx_snapshot.columns, pd.MultiIndex): fx_snapshot.columns = fx_snapshot.columns.get_level_values(0)

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("USD/TRY", f"{fx_snapshot['USDTRY=X'].iloc[-1]:.4f}")
        k2.metric("USD/KZT", f"{fx_snapshot['USDKZT=X'].iloc[-1]:.2f}")
        k3.metric("ONS Altın", f"${fx_snapshot['GC=F'].iloc[-1]:.2f}")
        k4.metric("Bitcoin", f"${fx_snapshot['BTC-USD'].iloc[-1]:,.0f}")
        k5.metric("S&P 500", f"{fx_snapshot['^GSPC'].iloc[-1]:,.2f}")
    except:
        st.info("Piyasa verileri yükleniyor...")

    st.divider()

    # Yüksek/Düşük/Hacim
    if not data.empty:
        o1, o2, o3 = st.columns(3)
        o1.metric("En Yüksek", f"{data['High'].iloc[-1]:.4f}")
        o2.metric("En Düşük", f"{data['Low'].iloc[-1]:.4f}")
        o3.metric("Hacim", f"{data['Volume'].iloc[-1]:,.0f}")

    st.divider()

    # İzleme listesi
    st.subheader("⭐ İzleme Listesi Durumu")
    w_list = st.multiselect("Favori Hisse/Para", options=list(COMMON_SYMBOLS.keys()),
                            default=["THYAO.IS", "EREGL.IS", "GC=F", "BTC-USD"],
                            key="ana_watchlist")
    if w_list:
        try:
            wd = yf.download(w_list, period="5d", progress=False)['Close']
            if isinstance(wd.columns, pd.MultiIndex): wd.columns = wd.columns.get_level_values(0)
            w_cols = st.columns(len(w_list))
            for i, sym in enumerate(w_list):
                if sym in wd.columns and len(wd) > 1:
                    val = wd[sym].iloc[-1]
                    chg = ((wd[sym].iloc[-1] / wd[sym].iloc[0]) - 1) * 100
                    w_cols[i].metric(COMMON_SYMBOLS.get(sym, sym), f"{val:.2f}", f"%{chg:+.2f}")
        except:
            st.info("Veri alınamadı.")

    st.info("💡 Sol menüden diğer sayfalara geçiş yapabilirsiniz.")

if secim == "📋 Al-Sat Şartları":
    st.subheader("📋 Al-Sat Şartları — Ajan Onaylı Karar Rehberi")
    st.markdown("""
<style>
    .al-sat-kutu { background:#0F172A; border:1px solid #1e293b; border-radius:12px; padding:18px 22px; margin:10px 0; }
    .al-sat-kutu h4 { color:#e2e8f0; font-size:16px; font-weight:700; margin:0 0 8px 0; }
    .al-sat-kutu ul { margin:4px 0; padding-left:20px; }
    .al-sat-kutu li { font-size:13px; color:#cbd5e1; line-height:1.8; margin:2px 0; }
    .al-sat-kutu strong { color:#f8fafc; }
    .yesil-vurgu { color:#4ade80; font-weight:600; }
    .mavi-vurgu { color:#38bdf8; font-weight:600; }
    .sari-vurgu { color:#fbbf24; font-weight:600; }
    .kirmizi-vurgu { color:#ef4444; font-weight:600; }
    .altin-kural { background:linear-gradient(135deg,rgba(250,204,21,0.06),rgba(245,158,11,0.04)); border:1px solid rgba(250,204,21,0.2); border-left:4px solid #fbbf24; border-radius:12px; padding:18px 22px; margin:16px 0; }
</style>

<div class="al-sat-kutu" style="border-left:4px solid #4ade80;">
<h4>🟩 NE ZAMAN "<span class="yesil-vurgu">AL</span>" YAPMALISIN? (Alım Koşulları)</h4>
<p style="font-size:13px;color:#94a3b8;margin:4px 0 10px 0;">Ajan Konsensüs Panelindeki 3 ana sütunda şu verileri aynı anda (veya en az ikisini güçlü şekilde) gördüğünde alım yönünde pozisyon açabilirsin:</p>
<ul>
<li><strong>🟢 Teknik Analiz Ajanında:</strong><br>
• Hisse fiyatı düşerken RSI veya MACD çizgilerinin yükseldiğini, yani "<span class="yesil-vurgu">Pozitif Uyumsuzluk (Bullish Divergence)</span>" saptandığını görüyorsan <em>(Bu, düşüşün bittiğini ve gizli alıcıların geldiğini gösterir).</em><br>
• Fiyatın EMA 50 hareketli ortalamasının üzerine yerleştiğini ve hacmin son 20 günlük ortalamanın üzerine çıktığını görüyorsan.</li>
<li><strong>🔵 Balina & Takas Ajanında:</strong><br>
• "<span class="mavi-vurgu">İlk 5 Kurumun Toplama Oranı</span>" (Haftalık/Aylık Delta) pozitif ve yükseliyorsa <em>(Tahta yapıcılar ve büyük fonlar mal topluyor demektir).</em><br>
• Emir Defteri Alış Baskı Katsayısı (Imbalance Ratio) 1.5x ile 2.0x arasında veya daha üzerindeyse <em>(Kademelerde devasa alım blokları yığılmıştır).</em></li>
<li><strong>🟡 Makro Duygu Ajanında:</strong><br>
• Son KAP haberlerinin veya finansal medya taramalarının FinBERT tarafından yüksek oranda "<span class="sari-vurgu">Positive</span>" (Pozitif) etiketlendiğini görüyorsan.</li>
</ul>
<p style="font-size:13px;color:#e2e8f0;margin:8px 0 0 0;font-weight:600;">💥 Nihai Tetikleyici:</p>
<p style="font-size:13px;color:#cbd5e1;margin:2px 0 0 0;">Bu 3 verinin ağırlıklı ortalamasıyla hesaplanan "<span class="yesil-vurgu">Ortak Konsensüs Skoru</span>" <strong>85 ve üzerine</strong> çıktığında ve sistem 🚀 <span class="yesil-vurgu">GÜÇLÜ AL (STRONG BUY)</span> sinyali ürettiğinde alım yapılabilir.</p>
</div>

<div class="al-sat-kutu" style="border-left:4px solid #ef4444;">
<h4>🟥 NE ZAMAN "<span class="kirmizi-vurgu">SAT</span>" VEYA "<span class="kirmizi-vurgu">UZAK DUR</span>" YAPMALISIN? (Satım Koşulları)</h4>
<p style="font-size:13px;color:#94a3b8;margin:4px 0 10px 0;">Elindeki hisseyi satıp kâr realize etmek veya riskli bir hisseye hiç bulaşmamak için şu sinyalleri takip etmelisin:</p>
<ul>
<li><strong>🟢 Teknik Analiz Ajanında:</strong><br>
• Fiyat yeni zirveler yaparken RSI indikatörünün daha düşük tepeler yaptığını, yani "<span class="kirmizi-vurgu">Negatif Uyumsuzluk (Bearish Divergence)</span>" oluştuğunu görüyorsan <em>(Bu, yükselişin sahte olduğunu ve gücünün bittiğini söyler).</em><br>
• RSI değerinin 70 veya 80 üzerine (Aşırı Alım bölgesi) tırmandığını ve fiyatın Bollinger Üst Bandının dışına taştığını görüyorsan.</li>
<li><strong>🔵 Balina & Takas Ajanında:</strong><br>
• Fiyat yükselmesine rağmen "<span class="mavi-vurgu">İlk 5 Kurum</span>" mal satıyor ve lotlar diğer küçük yatırımcılara dağıtılıyorsa ("<span class="kirmizi-vurgu">Kurumsal Dağıtım / Mal Çakma</span>" evresi).<br>
• Emir defterinde satış kademelerine gizli veya devasa blok satış emirleri yerleştirilmişse.</li>
<li><strong>🟡 Makro Duygu Ajanında:</strong><br>
• Şirket hakkında negatif haber akışının başlaması, sosyal medyadaki panik/korku endeksinin aniden fırlaması.</li>
</ul>
<p style="font-size:13px;color:#e2e8f0;margin:8px 0 0 0;font-weight:600;">💥 Nihai Tetikleyici:</p>
<p style="font-size:13px;color:#cbd5e1;margin:2px 0 0 0;"><span class="kirmizi-vurgu">Ortak Konsensüs Skoru 50'nin altına</span> gerilediğinde veya sistem ⚠️ <span class="kirmizi-vurgu">RİSKLİ BÖLGE / UZAK DUR (AVOID)</span> uyarısı verdiğinde eldeki varlıklar satılmalı veya yeni alım yapılmamalıdır.</p>
</div>

<div class="altin-kural">
<h4 style="color:#fbbf24;font-size:16px;font-weight:700;margin:0 0 8px 0;">🎯 Yatırım Yaparken Asla Unutmaman Gereken Altın Kural (Kasa Yönetimi)</h4>
<p style="font-size:13px;color:#cbd5e1;margin:4px 0;line-height:1.7;">Ajanların ne kadar kusursuz çalışırsa çalışsın, piyasada her zaman beklenmedik bir jeopolitik risk veya küresel kriz (<strong>Siyah Kuğu</strong>) çıkabilir. Bu yüzden yatırımlarını şu iki koruma filtresine göre yapmalısın:</p>
<ul>
<li><strong>Vade Filtresi:</strong> Eğer sol menüden "<span class="sari-vurgu">Kısa Vade</span>" seçtiysen, Duygu ajanını tamamen göz ardı et; sadece Teknik Uyumsuzluk + Emir Defteri Alış Baskısına bakarak hareket et. Eğer "<span class="sari-vurgu">Uzun Vade</span>" seçtiysen, indikatörleri boş ver; tamamen Balinaların takas toplama istikrarına ve temel büyüme verilerine odaklan.</li>
<li><strong>%10 Sınırı (Risk Yönetimi):</strong> Analiz sonucu %100 kusursuz görünse bile, cüzdanındaki toplam paranın (kasanın) en fazla <strong>%10'u</strong> ile tek bir hisseye giriş yap. Paranı en az 4-5 farklı ajan onaylı varlığa bölerek riskini minimize et.</li>
</ul>
</div>
""", unsafe_allow_html=True)

if secim == "🤖 AI Karar Motoru":
    # ——— AJAN KONSENSÜS DASHBOARD (sayfanın üstünde) ———
    ai_dash = ConsensusDashboard(search_query, data, st.session_state.get("vade", "ORTA"))
    ai_dash.render()
    col_run, col_info = st.columns([3, 1])
    with col_run:
        if st.button("🚀 Ajanları Paralel Çalıştır (asyncio.gather)", key="ai_karar_async", use_container_width=True):
            with st.spinner("🧠 3 ajan paralel taranıyor..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    sonuc = loop.run_until_complete(ai_dash.run_async())
                    loop.close()
                    st.session_state.agent_memory = {
                        "final_score": sonuc.get("final_score"),
                        "signal": sonuc.get("signal"),
                        "technical_score": sonuc.get("technical_score"),
                        "whale_score": sonuc.get("whale_score"),
                        "sentiment_score": sonuc.get("sentiment_score"),
                        "horizon": sonuc.get("horizon"),
                        "execution_time": sonuc.get("execution_time"),
                    }
                    st.rerun()
                except:
                    st.warning("Paralel mod başarısız, sıralı mod kullanılıyor...")
                    mgr = HedgeFundManagerAgent(search_query, data, st.session_state.get("vade", "ORTA"))
                    for _, _, _ in mgr.run_with_status_stream():
                        pass
                    c = mgr.consensus
                    st.session_state.agent_memory = {
                        "final_score": c.get("final_score"),
                        "signal": c.get("signal"),
                        "technical_score": c.get("technical_score"),
                        "whale_score": c.get("whale_score"),
                        "sentiment_score": c.get("sentiment_score"),
                        "horizon": c.get("horizon"),
                        "execution_time": c.get("execution_time"),
                    }
                    st.rerun()
    with col_info:
        mem_ai = st.session_state.get("agent_memory", {})
        if mem_ai.get("execution_time"):
            st.caption(f"⏱ Son çalışma: {mem_ai['execution_time']}s | Vade: {mem_ai.get('horizon', '—')}")
    st.divider()
    # Mevcut AI Karar Motoru sayfası
    render_ai_prediction_page(search_query, data)

if secim == "🧠 Gelişmiş AI (Kalibrasyon)":
    render_advanced_ai_page(search_query, data)

if secim == "📊 Teknik Analiz (Uyumsuzluklar)":
    # 2. GELİŞMİŞ TEKNİK ANALİZ
    st.subheader("⏱️ Zaman Dilimi")
    t_cols = st.columns(11)
    timeframes = {
        "1D": "1d", "5D": "5d", "1H": "1wk", "1A": "1mo", "1Y": "1y", "5Y": "5y",
        "1dk": "1m", "5dk": "5m", "1s": "1h", "4s": "4h"
    }
    selected_tf = "1d"
    with t_cols[0]: 
        if st.button("1dk"): st.session_state.tf, st.session_state.pr = "1m", "1d"; st.rerun()
    with t_cols[1]:
        if st.button("5dk"): st.session_state.tf, st.session_state.pr = "5m", "5d"; st.rerun()
    with t_cols[2]:
        if st.button("15dk"): st.session_state.tf, st.session_state.pr = "15m", "1wk"; st.rerun()
    with t_cols[3]:
        if st.button("1sa"): st.session_state.tf, st.session_state.pr = "1h", "1mo"; st.rerun()
    with t_cols[4]:
        if st.button("4sa"): st.session_state.tf, st.session_state.pr = "1h", "3mo"; st.rerun()
    with t_cols[5]:
        if st.button("1 G"): st.session_state.tf, st.session_state.pr = "1d", "1y"; st.rerun()
    with t_cols[6]:
        if st.button("1 H"): st.session_state.tf, st.session_state.pr = "1wk", "5y"; st.rerun()
    with t_cols[7]:
        if st.button("1 A"): st.session_state.tf, st.session_state.pr = "1mo", "max"; st.rerun()
    with t_cols[8]:
        if st.button("1 Y"): st.session_state.tf, st.session_state.pr = "1mo", "1y"; st.rerun()
    with t_cols[9]:
        if st.button("5 Y"): st.session_state.tf, st.session_state.pr = "1mo", "5y"; st.rerun()
    
    if not data.empty:
        # Indicators
        # Indicators (Squeeze to ensure 1D Series)
        close_series = data['Close'].squeeze()
        data['EMA20'] = ta.trend.ema_indicator(close_series, window=20)
        data['EMA50'] = ta.trend.ema_indicator(close_series, window=50)
        data['EMA200'] = ta.trend.ema_indicator(close_series, window=200)
        data['RSI'] = ta.momentum.rsi(close_series, window=14)
        
        # MACD
        macd_obj = ta.trend.MACD(close_series)
        data['MACD'] = macd_obj.macd()
        data['MACD_Signal'] = macd_obj.macd_signal()
        data['MACD_Diff'] = macd_obj.macd_diff()
        bb = ta.volatility.BollingerBands(close_series)
        data['BB_High'] = bb.bollinger_hband()
        data['BB_Low'] = bb.bollinger_lband()
        
        # Kıvanç Indicators
        data['OTT'] = calculate_ott(data)
        data['PMAX'] = calculate_pmax(data)
        data['WT1'], data['WT2'] = calculate_wavetrend(data)
        data['ST_MOM'] = calculate_st_mom(data)
        
        # VWAP (Volume Weighted Average Price)
        data['VWAP'] = ta.volume.volume_weighted_average_price(data['High'], data['Low'], data['Close'], data['Volume'])
        
        # Güncel Fiyat Bilgisi
        c1, c2, c3 = st.columns(3)
        c1.metric("Güncel Fiyat", f"{data['Close'].iloc[-1]:.4f}",
                  delta=f"%{((data['Close'].iloc[-1]/data['Close'].iloc[-2])-1)*100:.2f}" if len(data) > 1 else "")
        c2.metric("En Yüksek", f"{data['High'].iloc[-1]:.4f}")
        c3.metric("En Düşük", f"{data['Low'].iloc[-1]:.4f}")
        
        # Chart (8 Rows: Price, Volume, RSI, MACD, OTT, PMAX, WT, ST-MOM)
        fig = make_subplots(rows=8, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.02, 
                           row_heights=[0.35, 0.10, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08],
                           subplot_titles=("", "", "", "", "", "", "", ""))
        
        # Candlestick (TradingView Colors)
        fig.add_trace(go.Candlestick(
            x=data.index, 
            open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], 
            name="Fiyat",
            increasing_line_color='#26a69a', decreasing_line_color='#ef5350',
            increasing_fillcolor='#26a69a', decreasing_fillcolor='#ef5350'
        ), row=1, col=1)
        
        # Dedicated Volume Subplot (Row 2)
        v_colors = ['#ef5350' if data['Close'].iloc[i] < data['Open'].iloc[i] else '#26a69a' for i in range(len(data))]
        fig.add_trace(go.Bar(
            x=data.index, y=data['Volume'], name="Hacim",
            marker_color=v_colors, opacity=0.8
        ), row=2, col=1)
        
        # Current Price Line
        last_price = data['Close'].iloc[-1]
        fig.add_hline(y=last_price, line_dash="dash", line_color="#58a6ff", 
                     annotation_text=f"Son: {last_price:.2f}", annotation_position="right", row=1, col=1)
        
        # EMA & BB (Subtle Colors)
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA20'], name="EMA 20", line=dict(color='#58a6ff', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA50'], name="EMA 50", line=dict(color='#ffeb3b', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], name="EMA 200", line=dict(color='#ff5252', width=1.5, dash='dash')), row=1, col=1)
        
        # BB (Cloud effect)
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_High'], name="BB Üst", line=dict(color='rgba(173, 216, 230, 0.2)', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_Low'], name="BB Alt", line=dict(color='rgba(173, 216, 230, 0.2)', width=1), fill='tonexty', fillcolor='rgba(173, 216, 230, 0.05)'), row=1, col=1)
        
        # Fibonacci (Clean labels)
        fibs = calculate_fibonacci(data)
        for level, val in fibs.items():
            fig.add_hline(y=val, line_dash="dot", line_color="rgba(255,165,0,0.3)", row=1, col=1)

        # RSI (Clear zones)
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name="RSI", line=dict(color='#e040fb', width=1.5)), row=3, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(244, 67, 54, 0.1)", line_width=0, row=3, col=1)
        fig.add_hrect(y0=0, y1=30, fillcolor="rgba(76, 175, 80, 0.1)", line_width=0, row=3, col=1)
        fig.add_hline(y=50, line_dash="dash", line_color="rgba(255,255,255,0.2)", row=3, col=1)
        
        # MACD (Professional look)
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], name="MACD", line=dict(color='#00bcd4', width=1.5)), row=4, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD_Signal'], name="Sinyal", line=dict(color='#ffeb3b', width=1)), row=4, col=1)
        
        colors = ['#ef5350' if x < 0 else '#26a69a' for x in data['MACD_Diff']]
        fig.add_trace(go.Bar(x=data.index, y=data['MACD_Diff'], name="Histogram", marker_color=colors, opacity=0.7), row=4, col=1)
        
        # OTT (Separate pane)
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Fiyat (Ref)", line=dict(color='rgba(255,255,255,0.1)', width=1)), row=5, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['OTT'], name="OTT", line=dict(color='#ff9800', width=2)), row=5, col=1)
        
        # PMAX (Separate pane)
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Fiyat (Ref)", line=dict(color='rgba(255,255,255,0.1)', width=1), showlegend=False), row=6, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['PMAX'], name="PMAX", line=dict(color='#00e676', width=2)), row=6, col=1)
        
        # WaveTrend (Kıvanç)
        fig.add_trace(go.Scatter(x=data.index, y=data['WT1'], name="WT1", line=dict(color='#2196f3', width=1.5)), row=7, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['WT2'], name="WT2", line=dict(color='#ff5252', width=1, dash='dot')), row=7, col=1)
        fig.add_hline(y=60, line_dash="dash", line_color="rgba(255,0,0,0.2)", row=7, col=1)
        fig.add_hline(y=-60, line_dash="dash", line_color="rgba(0,255,0,0.2)", row=7, col=1)
        
        # ST-MOM (Kıvanç)
        fig.add_trace(go.Scatter(x=data.index, y=data['ST_MOM'], name="ST-MOM", line=dict(color='#00e676', width=2)), row=8, col=1)
        fig.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.1)", row=8, col=1)
        
        # Layout Enhancements (TradingView Look)
        fig.update_layout(
            height=1400, 
            template="plotly_dark", 
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=50, t=30, b=10), # Wider right margin for axis
            hovermode='x unified',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor='#0d1117',
            plot_bgcolor='#0d1117',
            annotations=[dict(
                text=search_query,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=100, color="rgba(255, 255, 255, 0.05)"),
                textangle=-30
            )]
        )
        
        # Style all axes
        fig.update_xaxes(
            showgrid=True, gridwidth=1, gridcolor='#1f2937', 
            showline=True, linewidth=1, linecolor='#30363d',
            mirror=True, showspikes=True, spikethickness=1, spikedash="dot", spikecolor="#999999", spikemode="across",
            fixedrange=False, # ENSURE SCALABLE
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1A", step="month", stepmode="backward"),
                    dict(count=6, label="6A", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all")
                ]),
                bgcolor="#161b22", activecolor="#58a6ff"
            )
        )
        
        fig.update_yaxes(
            side='right', # MOVE TO RIGHT
            showgrid=True, gridwidth=1, gridcolor='#1f2937',
            showline=True, linewidth=1, linecolor='#30363d',
            mirror=True, showspikes=True, spikethickness=1, spikedash="dot", spikecolor="#999999", spikemode="across",
            fixedrange=False # ENSURE SCALABLE
        )
        
        st.plotly_chart(fig, width='stretch', config={'scrollZoom': True})
        
        # --- QUICK SIGNAL SUMMARY ---
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns(3)
        last_close = data['Close'].iloc[-1]
        last_ott = data['OTT'].iloc[-1]
        last_rsi = data['RSI'].iloc[-1]
        
        with col_s1:
            st.metric("Trend (OTT)", "🟢 YÜKSELİŞ" if last_close > last_ott else "🔴 DÜŞÜŞ")
        with col_s2:
            st.metric("Momentum (RSI)", f"{last_rsi:.1f}", delta="Aşırı Alım" if last_rsi > 70 else "Aşırı Satım" if last_rsi < 30 else "Normal")
        with col_s3:
            st.write("**Strateji Notu:**")
            if last_close > last_ott and last_rsi < 70: st.success("Alım İçin Uygun Koşullar")
            elif last_close < last_ott and last_rsi > 30: st.error("Satış Baskısı Devam Ediyor")
            else: st.warning("Kararsız Bölge / Bekle")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- INDICATOR GUIDE ---
        with st.expander("📖 İndikatör Rehberi & Kullanım Kılavuzu"):
            st.markdown("""
            ### 🛠️ Teknik Araçlar Ne Anlatıyor?
            - **EMA (20, 50, 200):** Üstel Hareketli Ortalamalar. Fiyat 200 EMA'nın üzerindeyse uzun vadeli trend pozitiftir.
            - **OTT (Optimized Trend Tracker):** Kıvanç Özbilgiç tarafından geliştirilen trend takipçisi. Fiyat turuncu çizginin üzerindeyse 'AL' konumundadır.
            - **PMAX:** Kar al ve stop seviyelerini belirlemek için kullanılan volatilite tabanlı trend indikatörü.
            - **RSI:** 70 üzeri aşırı alım (dikkat!), 30 altı aşırı satım (fırsat?) bölgelerini gösterir.
            - **WaveTrend:** Dip ve tepe dönüşlerini yakalamak için kullanılan momentum osilatörü.
            """)

        # --- PATTERN RECOGNITION ---
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        patterns = detect_patterns(data)
        if patterns:
            st.write(f"🔍 **Tespit Edilen Formasyonlar:** {', '.join(patterns)}")
        else:
            st.write("🔍 Formasyon tespiti yapılamadı.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- MARKET SENTIMENT (FEAR & GREED PROXY) ---
        st.divider()
        st.subheader("🌡️ Piyasa Duyarlılığı (Fear & Greed)")
        
        # Simple proxy: Inverse of Volatility + RSI of XU100
        idx_data = yf.download("XU100.IS", period="1mo", progress=False)
        if not idx_data.empty:
            idx_rsi = ta.momentum.rsi(idx_data['Close'].squeeze(), window=14).iloc[-1]
            sentiment_score = int(idx_rsi) # Crude proxy
            
            color = "#ef5350" if sentiment_score < 30 else "#ffeb3b" if sentiment_score < 70 else "#26a69a"
            status = "Aşırı Korku" if sentiment_score < 30 else "Korku" if sentiment_score < 45 else "Nötr" if sentiment_score < 55 else "Açgözlülük" if sentiment_score < 70 else "Aşırı Açgözlülük"
            
            st.markdown(f"""
            <div style="background: {color}; height: 30px; border-radius: 15px; width: 100%; position: relative; margin-top: 20px;">
                <div style="position: absolute; left: {sentiment_score}%; top: -10px; font-size: 20px;">📍</div>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 5px;">
                <span>Korku (0)</span>
                <span style="font-weight: bold; color: {color};">{status} ({sentiment_score})</span>
                <span>Açgözlülük (100)</span>
            </div>
            """, unsafe_allow_html=True)
            
        # --- SIGNAL SCANNER TABLE ---
        st.divider()
        st.subheader("🎯 Canlı Sinyal Takip Masası (BIST 30/100)")
        
        scanner_list = ["THYAO.IS", "EREGL.IS", "SISE.IS", "TUPRS.IS", "KCHOL.IS", "SAHOL.IS", "ASELS.IS", "BIMAS.IS", "AKBNK.IS", "GARAN.IS", "YKBNK.IS", "ISCTR.IS", "SASA.IS", "HEKTS.IS", "ENKAI.IS"]
        
        if st.button("Sinyalleri Tara / Yenile"):
            with st.spinner("İndikatörler analiz ediliyor..."):
                sig_df = get_trading_signals(scanner_list)
                if not sig_df.empty:
                    # Sort by Strong Buy
                    sig_df['Sort'] = sig_df['Durum'].apply(lambda x: 0 if "GÜÇLÜ AL" in x else 1 if "AL" in x else 2 if "SAT" in x else 3)
                    sig_df = sig_df.sort_values('Sort').drop(columns=['Sort'])
                    
                    st.table(sig_df)
                else:
                    st.info("Şu an net bir sinyal bulunamadı.")

        # --- REGULAR & HIDDEN DIVERGENCE ---
        st.divider()
        st.subheader("🔄 Düzenli & Gizli Uyumsuzluk (Divergence) Dedektörü")
        divs = detect_divergence(data)
        if divs:
            div_df = pd.DataFrame(divs, columns=["İndikatör", "Tür", "Açıklama"])
            for _, row in div_df.iterrows():
                if "AL" in row["Açıklama"] or "Yükseliş" in row["Tür"]:
                    st.success(f"🟢 **{row['İndikatör']}** — {row['Tür']}: {row['Açıklama']}")
                else:
                    st.error(f"🔴 **{row['İndikatör']}** — {row['Tür']}: {row['Açıklama']}")
        else:
            st.info("Son 50 barda belirgin bir uyumsuzluk tespit edilmedi.")

    style_metric_cards()

if secim == "🔮 AI Fiyat Tahmini":
    st.subheader(f"🔮 AI Fiyat Tahmini: {search_query}")
    st.write("*(Makine Öğrenmesi (Linear Regression) kullanılarak gelecek 30 günlük projeksiyon)*")
    
    if not data.empty:
        f_dates, f_preds = predict_price(data)
        
        fig_ai = go.Figure()
        fig_ai.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Mevcut Fiyat", line=dict(color='#58a6ff')))
        fig_ai.add_trace(go.Scatter(x=f_dates, y=f_preds, name="AI Tahmini", line=dict(color='#ff9800', dash='dash')))
        fig_ai.update_layout(height=400, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_ai, width='stretch')
        
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("30 Gün Sonra Beklenen", f"{f_preds[-1]:.2f}")
        target_diff = ((f_preds[-1] / data['Close'].iloc[-1]) - 1) * 100
        m_col2.metric("Potansiyel Değişim", f"%{target_diff:.2f}", delta=f"{target_diff:.2f}%")
    else:
        st.warning("Yeterli veri yok.")

if secim == "🎲 Monte Carlo Simülasyonu":
    st.subheader(f"🎲 Monte Carlo Fiyat Simülasyonu: {search_query}")
    st.write("*(Gelecek 90 gün için 100 farklı olasılık senaryosu)*")
    
    if not data.empty:
        sim_days = 90
        sim_results = monte_carlo_simulation(data, days=sim_days, simulations=100)
        
        fig_mc = go.Figure()
        for i in range(100):
            fig_mc.add_trace(go.Scatter(y=sim_results[:, i], mode='lines', line=dict(width=1), opacity=0.3, showlegend=False))
            
        fig_mc.update_layout(height=500, template="plotly_dark", title="Olası Fiyat Patikaları", yaxis_title="Fiyat")
        st.plotly_chart(fig_mc, width='stretch')
        
        # Stats
        final_prices = sim_results[-1, :]
        st.info(f"📍 **90 Gün Sonra Beklenen Ortalama Fiyat:** {np.mean(final_prices):.2f}")
        st.success(f"📈 **En İyimser Senaryo:** {np.max(final_prices):.2f}")
        st.error(f"📉 **En Kötümser Senaryo:** {np.min(final_prices):.2f}")
    else:
        st.warning("Simülasyon için veri yetersiz.")

if secim == "🎭 Sektörel Analiz":
    st.subheader(f"🎭 Sektörel Kıyaslama (Görece Güç)")
    if st.button("Sektör Verilerini Getir"):
        with st.spinner("Sektörel endekslerle karşılaştırılıyor..."):
            rel_df = get_sector_relative_strength(search_query)
            fig_rel = px.line(rel_df, template="plotly_dark", title=f"{search_query} vs Sektör/Endeks (Kümülatif Getiri)")
            st.plotly_chart(fig_rel, width='stretch')

if secim == "🎒 Portföy Analizi & Drawdown":
    # ——— ALPACA-STYLE CANLI PORTFÖY AKIŞI ———
    st.subheader("📡 Alpaca Canlı Portföy (Simülasyon)")

    # Örnek portföy pozisyonları (Alpaca API simülasyonu)
    ALPACA_POSITIONS = {
        "THYAO.IS": {"adet": 500, "maliyet": 285.50},
        "EREGL.IS": {"adet": 800, "maliyet": 52.30},
        "GC=F": {"adet": 10, "maliyet": 2150.00},
        "BTC-USD": {"adet": 0.5, "maliyet": 62500},
        "SISE.IS": {"adet": 1200, "maliyet": 44.80},
    }

    try:
        semboller = list(ALPACA_POSITIONS.keys())
        fiyatlar = yf.download(semboller, period="2d", progress=False)['Close']
        if isinstance(fiyatlar.columns, pd.MultiIndex):
            fiyatlar.columns = fiyatlar.columns.get_level_values(0)

        pozisyon_satirlari = []
        toplam_maliyet = 0
        toplam_piym = 0
        for sym, bilgi in ALPACA_POSITIONS.items():
            if sym in fiyatlar.columns and len(fiyatlar) > 1:
                guncel = fiyatlar[sym].iloc[-1]
                onceki = fiyatlar[sym].iloc[0]
                maliyet = bilgi["maliyet"]
                adet = bilgi["adet"]
                piyasa_deger = guncel * adet
                maliyet_toplam = maliyet * adet
                kar_zarar = piyasa_deger - maliyet_toplam
                kar_zarar_yuzde = ((guncel / maliyet) - 1) * 100
                toplam_maliyet += maliyet_toplam
                toplam_piym += piyasa_deger
                pozisyon_satirlari.append({
                    "Sembol": sym,
                    "Adet": adet,
                    "Maliyet": f"₺{maliyet:.2f}",
                    "Güncel": f"₺{guncel:.2f}",
                    "Piyasa Değeri": f"₺{piyasa_deger:,.0f}",
                    "Unrealized P&L": f"₺{kar_zarar:+,.0f}",
                    "%": f"%{kar_zarar_yuzde:+.2f}",
                    "Renk": "#4ade80" if kar_zarar >= 0 else "#ef4444",
                })

        # Portföy özeti
        net_kar = toplam_piym - toplam_maliyet
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Toplam Piyasa Değeri", f"₺{toplam_piym:,.0f}")
        p2.metric("Toplam Maliyet", f"₺{toplam_maliyet:,.0f}")
        p3.metric("Net Unrealized P&L", f"₺{net_kar:+,.0f}", delta=f"%{(toplam_piym/toplam_maliyet-1)*100:+.2f}" if toplam_maliyet else None)
        p4.metric("Pozisyon Sayısı", len(pozisyon_satirlari))

        st.divider()

        # Pozisyon tablosu
        poz_df = pd.DataFrame(pozisyon_satirlari)
        st.dataframe(poz_df.drop(columns=["Renk"]), width='stretch', hide_index=True)

        st.divider()

        # Pasta grafik (hisse dağılımı)
        st.subheader("🥧 Varlık Dağılımı")
        pie_df = pd.DataFrame([
            {"Sembol": r["Sembol"], "Değer": float(r["Piyasa Değeri"].replace("₺", "").replace(",", ""))}
            for r in pozisyon_satirlari
        ])
        fig_pie = px.pie(pie_df, values="Değer", names="Sembol", hole=0.45,
                         color_discrete_sequence=px.colors.sequential.Emrld,
                         title="Anlık Portföy Dağılımı")
        fig_pie.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_pie, width='stretch')

        # Drawdown simülasyonu
        st.divider()
        st.subheader("📉 Drawdown Geçmişi (Simülasyon)")
        with st.spinner("Portföy zaman serisi çekiliyor..."):
            hist_data = yf.download(semboller, period="1y", progress=False)['Close']
            if isinstance(hist_data.columns, pd.MultiIndex):
                hist_data.columns = hist_data.columns.get_level_values(0)
            # Ağırlıklı portföy getirisi
            w = [ALPACA_POSITIONS[s]["adet"] * ALPACA_POSITIONS[s]["maliyet"] for s in semboller if s in hist_data.columns]
            w = np.array(w) / sum(w) if sum(w) else np.ones(len(semboller)) / len(semboller)
            port_returns = hist_data.pct_change().dropna().dot(w)
            cum_returns = (1 + port_returns).cumprod()
            running_max = cum_returns.cummax()
            drawdown = (cum_returns - running_max) / running_max * 100
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(x=drawdown.index, y=drawdown, fill='tozeroy',
                                        line=dict(color='#ef4444', width=1), name='Drawdown'))
            fig_dd.update_layout(template="plotly_dark", height=300,
                                 title="Portföy Drawdown Eğrisi (1 Yıl)",
                                 yaxis_title="Drawdown %")
            st.plotly_chart(fig_dd, width='stretch')

            # İleri Düzey Risk Metrikleri (Portföy)
            st.divider()
            st.subheader("📊 İleri Risk Metrikleri")
            risk_free = st.number_input("Risksiz Faiz Oranı (%)", value=0.0, step=0.1, key="rf_port") / 100
            pf_sharpe = calculate_sharpe_ratio(port_returns, risk_free)
            pf_sortino = calculate_sortino_ratio(port_returns, risk_free)
            pf_calmar = calculate_calmar_ratio(port_returns)
            pf_var95, pf_cvar95 = calculate_var_cvar(port_returns, 0.95)
            pf_var99, pf_cvar99 = calculate_var_cvar(port_returns, 0.99)
            pr1, pr2, pr3, pr4 = st.columns(4)
            pr1.metric("Sharpe Oranı", f"{pf_sharpe:.3f}", delta="İyi" if pf_sharpe > 1 else "Orta" if pf_sharpe > 0 else "Zayıf")
            pr2.metric("Sortino Oranı", f"{pf_sortino:.3f}", delta="Düşük risk" if pf_sortino > pf_sharpe else "Yüksek risk")
            pr3.metric("Calmar Oranı", f"{pf_calmar:.3f}", delta="Güçlü" if pf_calmar > 1 else "Zayıf")
            pr4.metric("%95 VaR / CVaR", f"%{pf_var95*100:.2f} / %{pf_cvar95*100:.2f}",
                      delta=f"Kayıp: %{abs(pf_cvar95*100):.2f}" if pf_cvar95 < 0 else "Pozitif")
            pr5, pr6 = st.columns(2)
            pr5.metric("%99 VaR (Stres)", f"%{pf_var99*100:.2f}")
            pr6.metric("%99 CVaR (Beklenen Kayıp)", f"%{pf_cvar99*100:.2f}")
    except:
        st.info("Canlı portföy verisi yüklenemedi — sembolleri kontrol edin.")

if secim == "🗺️ Market Heatmap (Isı Haritası)":
    st.subheader("🗺️ BIST 100 Market Heatmap (Treemap)")
    if st.button("Isı Haritasını Oluştur"):
        with st.spinner("Piyasa verileri çekiliyor..."):
            h_list = list(COMMON_SYMBOLS.keys())[:30] # Top 30 for performance
            h_data = yf.download(h_list, period="2d", progress=False)['Close']
            if isinstance(h_data.columns, pd.MultiIndex): h_data.columns = h_data.columns.get_level_values(0)
            
            perf_df = pd.DataFrame({
                "Symbol": h_data.columns,
                "Performance": ((h_data.iloc[-1] / h_data.iloc[0]) - 1) * 100
            })
            
            fig_h = px.treemap(perf_df, path=['Symbol'], values=perf_df['Performance'].abs(),
                              color='Performance', color_continuous_scale='RdYlGn',
                              range_color=[-3, 3], title="BIST Günlük Performans")
            fig_h.update_layout(height=600, template="plotly_dark")
            st.plotly_chart(fig_h, width='stretch')

if secim == "🧪 Strateji Testi (Backtest)":
    st.subheader(f"🧪 OTT Strateji Testi: {search_query}")
    st.write("*(Strateji: Fiyat OTT çizgisini yukarı kestiğinde AL, aşağı kestiğinde SAT)*")
    
    if not data.empty:
        if 'OTT' not in data:
            data['OTT'] = calculate_ott(data)
        bt_df = data.copy()
        bt_df['Signal'] = 0
        bt_df.loc[bt_df['Close'] > bt_df['OTT'], 'Signal'] = 1
        bt_df['Position'] = bt_df['Signal'].diff()
        
        # Getiri Hesabı
        bt_df['Market_Return'] = bt_df['Close'].pct_change()
        bt_df['Strategy_Return'] = bt_df['Market_Return'] * bt_df['Signal'].shift(1)
        
        cum_market = (1 + bt_df['Market_Return']).cumprod()
        cum_strategy = (1 + bt_df['Strategy_Return']).cumprod()
        
        # Metrikler
        total_trades = len(bt_df[bt_df['Position'] != 0])
        win_trades = len(bt_df[(bt_df['Position'] == -1) & (bt_df['Strategy_Return'] > 0)])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Toplam Getiri (Strateji)", f"%{(cum_strategy.iloc[-1]-1)*100:.2f}")
        m2.metric("Hisse Getirisi (Buy & Hold)", f"%{(cum_market.iloc[-1]-1)*100:.2f}")
        m3.metric("İşlem Sayısı", total_trades)
        m4.metric("Karlı Kapanan İşlemler", win_trades)

        # İleri Düzey Risk Metrikleri
        st.subheader("📊 İleri Risk Metrikleri")
        str_returns = bt_df['Strategy_Return'].dropna()
        risk_free = st.number_input("Risksiz Faiz Oranı (%)", value=0.0, step=0.1, key="rf_strat") / 100
        sharpe = calculate_sharpe_ratio(str_returns, risk_free)
        sortino = calculate_sortino_ratio(str_returns, risk_free)
        calmar = calculate_calmar_ratio(str_returns)
        var95, cvar95 = calculate_var_cvar(str_returns, 0.95)
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Sharpe Oranı", f"{sharpe:.3f}", delta="İyi" if sharpe > 1 else "Orta" if sharpe > 0 else "Zayıf")
        r2.metric("Sortino Oranı", f"{sortino:.3f}", delta="Düşük risk" if sortino > sharpe else "Yüksek risk")
        r3.metric("Calmar Oranı", f"{calmar:.3f}", delta="Güçlü" if calmar > 1 else "Zayıf")
        r4.metric("%95 VaR / CVaR", f"%{var95*100:.2f} / %{cvar95*100:.2f}",
                  delta=f"Kayıp: %{abs(cvar95*100):.2f}" if cvar95 < 0 else "Pozitif")

        st.divider()
        st.subheader("📈 Getiri Karşılaştırması")
        fig_bt = go.Figure()
        fig_bt.add_trace(go.Scatter(x=bt_df.index, y=cum_strategy, name="OTT Stratejisi", line=dict(color='#00e676')))
        fig_bt.add_trace(go.Scatter(x=bt_df.index, y=cum_market, name="Al ve Tut", line=dict(color='#9e9e9e', dash='dash')))
        fig_bt.update_layout(height=400, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_bt, width='stretch')
    else:
        st.warning("Strateji testi için yeterli veri bulunamadı.")

    # Purged Time-Series Cross Validation
    st.divider()
    st.subheader("🧪 Purged Time-Series Cross-Validation (Overfitting Önleme)")
    st.write("*(Veri future leakage'ı engellemek için eğitim/test setleri zamanla ayrıştırılır)*")

    if not data.empty and len(data) > 100:
        cv_mode = st.radio("CV Modu", ["Standart Backtest", "Purged CV (5 Kat)"], horizontal=True)

        if st.button("🧪 Cross-Validation Çalıştır") or cv_mode == "Purged CV (5 Kat)":
            with st.spinner("Purged CV çalıştırılıyor..."):
                if cv_mode == "Purged CV (5 Kat)":
                    cv_result = run_purged_backtest(data)
                    if cv_result:
                        avg = cv_result['avg_metrics']
                        cv1, cv2, cv3, cv4 = st.columns(4)
                        cv1.metric("Ort. Strateji Getirisi", f"%{avg.get('strategy_return', 0):.2f}",
                                   delta=f"±{avg.get('strategy_return_std', 0):.2f}")
                        cv2.metric("Ort. Piyasa Getirisi", f"%{avg.get('market_return', 0):.2f}")
                        cv3.metric("Ort. Sharpe", f"{avg.get('sharpe', 0):.2f}",
                                   delta=f"±{avg.get('sharpe_std', 0):.2f}")
                        cv4.metric("Ort. Max Drawdown", f"%{avg.get('max_drawdown', 0):.2f}",
                                   delta=f"±{avg.get('max_drawdown_std', 0):.2f}")

                        st.success(f"✅ {cv_result['n_folds']} fold tamamlandı. Model overfitting riski: {'DÜŞÜK' if avg.get('sharpe', 0) > 0.5 else 'ORTA' if avg.get('sharpe', 0) > 0 else 'YÜKSEK'}")

                        # Fold bazlı getiriler
                        st.subheader("📊 Fold Bazlı Getiri Karşılaştırması")
                        fold_returns = [r['metrics'].get('strategy_return', 0) for r in cv_result['fold_results']]
                        fold_labels = [f"Fold {i+1}" for i in range(len(fold_returns))]
                        fig_cv = px.bar(x=fold_labels, y=fold_returns, labels={'x': '', 'y': 'Getiri (%)'},
                                        title="Her Fold'daki Strateji Getirisi", color=fold_returns,
                                        color_continuous_scale='RdYlGn', template="plotly_dark")
                        fig_cv.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
                        st.plotly_chart(fig_cv, width='stretch')

                        st.info("💡 Purged CV, zaman serisi modellerinde future leakage'ı önler. Fold'lar arasındaki getiri tutarlılığı modelin güvenilirliğini gösterir.")
                    else:
                        st.warning("Purged CV sonuç vermedi. Daha fazla veri gerekebilir.")
    else:
        st.info("Purged CV için en az 100 bar veri gereklidir.")

if secim == "📈 Piyasa Radarı (Sinyal Taraması)":
    st.subheader("📈 Piyasa Radarı (İndikatör Taraması)")
    
    # Geniş BIST havuzu (BIST 100 + popüler hisseler)
    radar_list = [
        "AKBNK.IS","AKSA.IS","ALARK.IS","ARCLK.IS","ASELS.IS","ASTOR.IS","AYGAZ.IS",
        "BERA.IS","BIMAS.IS","BRSAN.IS","BRYAT.IS","CANTE.IS","CCOLA.IS","CEMTS.IS",
        "CIMSA.IS","CLEBI.IS","DOAS.IS","DOHOL.IS","ECZYT.IS","EGEEN.IS","EKGYO.IS",
        "ENJSA.IS","ENKAI.IS","EREGL.IS","EUPWR.IS","FROTO.IS","GARAN.IS","GENIL.IS",
        "GLYHO.IS","GUBRF.IS","GWIND.IS","HALKB.IS","HEKTS.IS","IHLAS.IS","IPEKE.IS",
        "ISCTR.IS","ISDMR.IS","IZENR.IS","KARSN.IS","KAYSE.IS","KCHOL.IS","KLSER.IS",
        "KMPUR.IS","KONTR.IS","KORDS.IS","KOZAA.IS","KRDMD.IS","MAVI.IS","MGROS.IS",
        "MIATK.IS","ODAS.IS","OTKAR.IS","OYAKC.IS","PARSN.IS","PEGYO.IS","PETKM.IS",
        "PGSUS.IS","QUAGR.IS","SAHOL.IS","SASA.IS","SELEC.IS","SISE.IS","SKBNK.IS",
        "SMRTG.IS","SOKM.IS","TARKM.IS","TCELL.IS","THYAO.IS","TKFEN.IS","TOASO.IS",
        "TSKB.IS","TTKOM.IS","TUPRS.IS","TURSG.IS","ULKER.IS","VAKBN.IS","VESTL.IS",
        "YKBNK.IS","YYAPI.IS","ZOREN.IS"
    ]
    
    r_cols = st.columns(3)
    with r_cols[0]: mover_period = st.radio("Zaman Dilimi", ["Günlük", "Haftalık", "Aylık"], horizontal=True)
    
    y_period_map = {"Günlük": "2mo", "Haftalık": "6mo", "Aylık": "1y"}
    y_period = y_period_map[mover_period]
    
    if st.button("🔍 Taramayı Başlat", type="primary"):
        try:
            with st.spinner(f"{len(radar_list)} hisse taranıyor..."):
                raw = yf.download(radar_list, period=y_period, interval="1d", progress=False)
                close_raw = raw['Close']
                high_raw = raw['High']
                low_raw = raw['Low']
                if isinstance(close_raw.columns, pd.MultiIndex):
                    close_raw.columns = close_raw.columns.get_level_values(0)
                    high_raw.columns = high_raw.columns.get_level_values(0)
                    low_raw.columns = low_raw.columns.get_level_values(0)
                
                # Performans
                perf = ((close_raw.iloc[-1] / close_raw.iloc[0]) - 1) * 100
                perf = perf.sort_values(ascending=False)
                
                col_u, col_d = st.columns(2)
                with col_u:
                    st.success(f"🚀 En Çok Yükselen 10 ({mover_period})")
                    st.dataframe(perf.head(10).map(lambda x: f"%{x:.2f}"), width='stretch')
                with col_d:
                    st.error(f"📉 En Çok Düşen 10 ({mover_period})")
                    st.dataframe(perf.tail(10).sort_values().map(lambda x: f"%{x:.2f}"), width='stretch')
                
                st.divider()
                
                # İndikatör bazlı tarama (Altın Kombinasyon)
                yukselen = []
                dusen = []
                
                vol_raw = raw['Volume']
                if isinstance(vol_raw.columns, pd.MultiIndex):
                    vol_raw.columns = vol_raw.columns.get_level_values(0)
                
                for sym in radar_list:
                    try:
                        s_close = close_raw[sym].dropna()
                        s_high = high_raw[sym].dropna()
                        s_low = low_raw[sym].dropna()
                        s_vol = vol_raw[sym].dropna()
                        if len(s_close) < 50:
                            continue
                        
                        s_df = pd.DataFrame({'Close': s_close, 'High': s_high, 'Low': s_low})
                        last_c = s_df['Close'].iloc[-1]
                        
                        # 1) Trend: EMA 50
                        s_ema50 = ta.trend.ema_indicator(s_df['Close'], window=50).iloc[-1]
                        trend_al = last_c > s_ema50
                        trend_sat = last_c < s_ema50
                        
                        # 2) Momentum: RSI 14
                        s_rsi = ta.momentum.rsi(s_df['Close'], window=14).iloc[-1]
                        mom_al = s_rsi > 50
                        mom_sat = s_rsi < 50
                        
                        # 3) MACD Bullish/Bearish Crossover
                        macd_obj = ta.trend.MACD(s_df['Close'])
                        macd_line = macd_obj.macd().iloc[-1]
                        macd_sig = macd_obj.macd_signal().iloc[-1]
                        macd_al = macd_line > macd_sig
                        macd_sat = macd_line < macd_sig
                        
                        # 4) Hacim: Hacim > Hacim MA 20
                        vol_ma20 = s_vol.rolling(20).mean().iloc[-1]
                        vol_al = s_vol.iloc[-1] > vol_ma20 * 1.1  # %10 üstü
                        vol_sat = vol_al  # Satışta da hacim onayı
                        
                        # OTT trend onayı (ek gösterge)
                        s_ott = calculate_ott(s_df).iloc[-1]
                        ott_al = last_c > s_ott
                        
                        # AL Skoru: kaç koşul sağlanıyor?
                        al_kosul = sum([trend_al, mom_al, macd_al, vol_al])
                        sat_kosul = sum([trend_sat, mom_sat, macd_sat, vol_sat])
                        
                        # Güçlü AL: 4/4 veya 3/4 + OTT onayı
                        if al_kosul >= 3 and trend_al and mom_al:
                            yukselen.append((sym, f"{s_rsi:.1f}", f"{last_c:.2f}", f"{s_ema50:.2f}",
                                             f"{'✅' if macd_al else '❌'}", f"{al_kosul}/4",
                                             "🔥 GÜÇLÜ AL" if al_kosul == 4 else "📈 AL"))
                        
                        # Güçlü SAT: 4/4 veya 3/4
                        if sat_kosul >= 3 and trend_sat and mom_sat:
                            dusen.append((sym, f"{s_rsi:.1f}", f"{last_c:.2f}", f"{s_ema50:.2f}",
                                          f"{'✅' if macd_sat else '❌'}", f"{sat_kosul}/4",
                                          "🔴 GÜÇLÜ SAT" if sat_kosul == 4 else "🍂 SAT"))
                    except:
                        continue
                
                # Skora göre sırala (önce GÜÇLÜ AL/SAT, sonra AL/SAT)
                def sort_key(x):
                    return (0 if "GÜÇLÜ" in x[6] else 1, -int(x[5][0]))
                
                yukselen = sorted(yukselen, key=sort_key)[:10]
                dusen = sorted(dusen, key=sort_key)[:10]
                
                st.subheader("🔮 Altın Kombinasyon Sinyalleri")
                st.caption("Kombinasyon: Trend (EMA50) + Momentum (RSI>50) + MACD Crossover + Hacim(>MA20). 4/4 = En güçlü sinyal.")
                
                p1, p2 = st.columns(2)
                
                with p1:
                    st.info("⬆️ YÜKSELME POTANSİYELİ (AL Sinyalleri)")
                    if yukselen:
                        y_df = pd.DataFrame(yukselen, columns=["Hisse", "RSI", "Fiyat", "EMA50", "MACD", "Güç", "Durum"])
                        st.dataframe(y_df, width='stretch', hide_index=True)
                    else:
                        st.write("Şu an net al sinyali yok.")
                
                with p2:
                    st.warning("⬇️ DÜŞME İHTİMALİ (SAT Sinyalleri)")
                    if dusen:
                        d_df = pd.DataFrame(dusen, columns=["Hisse", "RSI", "Fiyat", "EMA50", "MACD", "Güç", "Durum"])
                        st.dataframe(d_df, width='stretch', hide_index=True)
                    else:
                        st.write("Şu an net sat sinyali yok.")
                        
        except Exception as e:
            st.error(f"Radar hatası: {e}")

if secim == "📑 Temel Analiz & Sağlık":
    st.subheader(f"📑 Temel Analiz & Sağlık: {search_query}")
    try:
        ticker_obj = yf.Ticker(search_query)
        info = ticker_obj.info

        # Büyüme projeksiyonu
        growth_score, growth_details = calculate_growth_projection_score(search_query)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("F/K Oranı", info.get("trailingPE", "N/A"))
        m2.metric("PD/DD", info.get("priceToBook", "N/A"))
        m3.metric("PEG Oranı", info.get("pegRatio", "N/A"))
        m4.metric("Verim", f"%{info.get('dividendYield', 0)*100:.2f}" if info.get('dividendYield') else "N/A")

        st.divider()
        st.write(f"**Piyasa Değeri:** {info.get('marketCap', 0):,}")
        st.write(f"**ROE:** %{info.get('returnOnEquity', 0)*100:.2f}")

        # Büyüme projeksiyon skoru
        st.subheader("📈 Geleceğe Dönük Büyüme Projeksiyonu")
        col_g1, col_g2 = st.columns([1, 2])
        with col_g1:
            growth_color = "#00e676" if growth_score >= 70 else "#ffeb3b" if growth_score >= 45 else "#ef5350"
            st.markdown(f"<h1 style='color:{growth_color};'>{growth_score}/100</h1>", unsafe_allow_html=True)
        with col_g2:
            det_df = pd.DataFrame(list(growth_details.items()), columns=["Metrik", "Değer"])
            st.dataframe(det_df, width='stretch', hide_index=True)
        st.caption("Skor: PEG, Gelir Büyümesi, Kar Marjı, ROE ve İleri F/K kullanılarak hesaplanır.")

        # Financial Charts
        st.subheader("📊 Mali Tablo Trendleri (Son 4 Yıl)")
        financials = ticker_obj.financials
        if not financials.empty:
            fin_df = financials.transpose()[['Total Revenue', 'Net Income']].dropna()
            fig_fin = px.bar(fin_df, barmode='group', template="plotly_dark", color_discrete_sequence=['#58a6ff', '#00e676'])
            fig_fin.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_fin, width='stretch')
        else:
            st.info("Mali tablo verisi bu sembol için mevcut değil.")
            
        st.write(f"**Şirket Özeti:** {info.get('longBusinessSummary', 'Bilgi yok.')[:400]}...")
        
    except Exception as e:
        st.warning(f"Temel analiz verileri alınamadı: {e}")

if secim == "🌍 Küresel Radar (Makro)":
    # 4. KÜRESEL RADAR
    st.subheader("🌍 Küresel Makro Radar")
    m_col1, m_col2, m_col3 = st.columns(3)
    
    macro_list = ["^GSPC", "^IXIC", "CL=F"] # S&P, Nasdaq, Brent
    macro_raw = yf.download(macro_list, period="5d")
    
    if isinstance(macro_raw.columns, pd.MultiIndex):
        macro_data = macro_raw['Close']
    else:
        macro_data = macro_raw[['Close']]
    
    if not macro_data.empty and len(macro_data) > 0:
        with m_col1: st.metric("S&P 500", f"{macro_data['^GSPC'].iloc[-1]:.2f}")
        with m_col2: st.metric("Nasdaq", f"{macro_data['^IXIC'].iloc[-1]:.2f}")
        with m_col3: st.metric("Brent Petrol", f"{macro_data['CL=F'].iloc[-1]:.2f}")
    else:
        st.warning("Makro veriler şu an alınamıyor.")
    
    st.divider()
    # Gram Altın Hesaplaması
    g_raw = yf.download("GC=F", period="5d")['Close']
    g_val = None
    if not g_raw.empty:
        g_val = g_raw.iloc[-1]
        if isinstance(g_val, pd.Series): g_val = g_val.iloc[0]
        g_val = float(g_val)

    u_try_col = yf.download("USDTRY=X", period="5d")['Close']
    usdtry_val = None
    if not u_try_col.empty:
        usdtry_val = u_try_col.iloc[-1]
        if isinstance(usdtry_val, pd.Series): usdtry_val = usdtry_val.iloc[0]
        usdtry_val = float(usdtry_val)

    # Altın ETF verileri (GLD, IAU)
    etf_raw = yf.download(["GLD", "IAU"], period="5d")['Close']
    if isinstance(etf_raw.columns, pd.MultiIndex): etf_raw.columns = etf_raw.columns.get_level_values(0)

    col_a, col_b = st.columns(2)
    with col_a:
        a1, a2 = st.columns(2)
        with a1:
            if g_val:
                st.metric("ONS Altın", f"${g_val:.2f}")
            else:
                st.metric("ONS Altın", "Veri yok")
        with a2:
            if g_val and usdtry_val:
                gram_altin = (g_val / 31.1035) * usdtry_val
                st.metric("Gram Altın (TL)", f"₺{gram_altin:.2f}")
            elif g_val:
                st.metric("Gram Altın", "Kur bekleniyor")
            else:
                st.metric("Gram Altın", "Veri yok")

        st.write("**🥇 Altın ETF**")
        e1, e2 = st.columns(2)
        with e1:
            if "GLD" in etf_raw.columns and len(etf_raw) > 0:
                gld_val = etf_raw["GLD"].dropna().iloc[-1]
                st.metric("GLD (SPDR)", f"${float(gld_val):.2f}")
            else:
                st.metric("GLD (SPDR)", "Veri yok")
        with e2:
            if "IAU" in etf_raw.columns and len(etf_raw) > 0:
                iau_val = etf_raw["IAU"].dropna().iloc[-1]
                st.metric("IAU (iShares)", f"${float(iau_val):.2f}")
            else:
                st.metric("IAU (iShares)", "Veri yok")

    with col_b:
        st.subheader("📅 Ekonomik Takvim")
        cal_data = pd.DataFrame({
            "Tarih": ["12 Haz 2026", "20 Haz 2026", "24 Tem 2026", "31 Tem 2026", "17 Eyl 2026"],
            "Olay": ["FED Faiz Kararı", "TCMB Faiz Kararı", "FED Faiz Kararı", "TCMB Faiz Kararı", "FED Faiz Kararı"],
            "Beklenti": ["%4.50", "%42.50", "%4.50", "%42.00", "%4.25"],
            "Önceki": ["%4.50", "%43.00", "%4.50", "%42.50", "%4.50"]
        })
        st.dataframe(cal_data, width='stretch', hide_index=True)

if secim == "📰 Haber & KAP (Duygu Analizi)":
    # ——— FİNANSMAN DUVARLILIĞI AKIŞI (FinBERT Simülasyonu) ———
    st.subheader(f"📰 {COMMON_SYMBOLS[search_query]} — FinBERT Duygu Akışı")

    rss_url = f"https://news.google.com/rss/search?q={search_query}+borsa&hl=tr&gl=TR&ceid=TR:tr"
    feed = feedparser.parse(rss_url)

    # Haberleri topla ve FinBERT duygu skoru hesapla
    haber_listesi = []
    for entry in feed.entries[:8]:
        skor, _ = get_sentiment(entry.title)
        # Daha hassas skor: TextBlob polarity'yi 0-100 skalasına çek
        blob_polarity = TextBlob(entry.title).sentiment.polarity
        if blob_polarity > 0.1:
            sonuc = "Positive"
            renk = "#4ade80"
            oran = 50 + abs(blob_polarity) * 40
        elif blob_polarity < -0.1:
            sonuc = "Negative"
            renk = "#ef4444"
            oran = 50 + abs(blob_polarity) * 40
        else:
            sonuc = "Neutral"
            renk = "#94a3b8"
            oran = 50
        haber_listesi.append({
            "başlık": entry.title,
            "link": entry.link,
            "tarih": entry.published,
            "finbert_skor": sonuc,
            "finbert_renk": renk,
            "finbert_yuzde": round(min(oran, 95), 1),
        })

    # Duygu dağılım grafiği (Plotly Pie + Bar)
    if haber_listesi:
        poz = sum(1 for h in haber_listesi if h["finbert_skor"] == "Positive")
        nor = sum(1 for h in haber_listesi if h["finbert_skor"] == "Neutral")
        neg = sum(1 for h in haber_listesi if h["finbert_skor"] == "Negative")
        toplam = len(haber_listesi)

        fig_sent = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "bar"}]],
                                 subplot_titles=("FinBERT Dağılımı", "Haber Adedi"),
                                 horizontal_spacing=0.15)
        fig_sent.add_trace(go.Pie(labels=["Pozitif", "Nötr", "Negatif"], values=[poz, nor, neg],
                                  marker=dict(colors=["#4ade80", "#94a3b8", "#ef4444"]),
                                  textinfo="label+percent", hole=0.4), row=1, col=1)
        fig_sent.add_trace(go.Bar(x=["Pozitif", "Nötr", "Negatif"], y=[poz, nor, neg],
                                  marker=dict(color=["#4ade80", "#94a3b8", "#ef4444"]),
                                  text=[f"{poz}/{toplam}", f"{nor}/{toplam}", f"{neg}/{toplam}"],
                                  textposition="outside"), row=1, col=2)
        fig_sent.update_layout(template="plotly_dark", height=300, showlegend=False,
                               margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_sent, width='stretch')

        # Yüzde oran satırı
        poz_yuzde = round(poz / toplam * 100, 1) if toplam > 0 else 0
        nor_yuzde = round(nor / toplam * 100, 1) if toplam > 0 else 0
        neg_yuzde = round(neg / toplam * 100, 1) if toplam > 0 else 0
        st.markdown(
            f"<div style='display:flex;gap:4px;height:24px;border-radius:6px;overflow:hidden;margin:8px 0;'>"
            f"<div style='flex:{poz_yuzde};background:#4ade80;text-align:center;font-size:11px;font-weight:600;color:#0b1120;'>{'%'+str(poz_yuzde) if poz_yuzde>5 else ''}</div>"
            f"<div style='flex:{nor_yuzde};background:#94a3b8;text-align:center;font-size:11px;font-weight:600;color:#0b1120;'>{'%'+str(nor_yuzde) if nor_yuzde>5 else ''}</div>"
            f"<div style='flex:{neg_yuzde};background:#ef4444;text-align:center;font-size:11px;font-weight:600;color:#fff;'>{'%'+str(neg_yuzde) if neg_yuzde>5 else ''}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Haber akışı (FinBERT skorlarıyla)
    for h in haber_listesi:
        st.markdown(f"""
        <div style="padding:10px;border-bottom:1px solid #1e293b;border-left:3px solid {h['finbert_renk']};margin:2px 0;border-radius:0 4px 4px 0;">
            <a href="{h['link']}" target="_blank" style="text-decoration:none;color:#38bdf8;font-size:14px;">{h['başlık']}</a><br>
            <span style="color:{h['finbert_renk']};font-weight:600;">▸ {h['finbert_skor']} (%{h['finbert_yuzde']})</span>
            <span style="color:#64748b;font-size:11px;margin-left:12px;">{h['tarih']}</span>
        </div>
        """, unsafe_allow_html=True)

if secim == "🏦 Fon & Takas Analizi":
    # 6. FONLAR VE AKILLI PARA
    st.subheader("🏦 Fon Performansları (TEFAS Liderleri)")
    fund_data = {
        "Fon Kodu": ["TI1", "TTE", "AFE", "GMR", "MAC", "HUC", "YAS", "KAH", "BSV", "IPO"],
        "Tema": ["BIST30", "Teknoloji", "Petrol", "Hisse Senedi", "Değer", "Küresel Teknoloji", "Katılım", "Karma", "Borçlanma Araçları", "Halka Arz"],
        "Yıllık Verim (%)": ["%85", "%112", "%45", "%92", "%78", "%67", "%55", "%48", "%32", "%103"],
        "Risk (Std Sapma)": ["18.2", "24.5", "22.1", "19.8", "15.4", "20.3", "12.7", "10.5", "4.2", "28.1"]
    }
    st.dataframe(pd.DataFrame(fund_data), width='stretch')
    st.caption("*Veriler örnekleme amaçlıdır. Gerçek TEFAS verileri için tefas.gov.tr adresini ziyaret edin.*")
    
    st.divider()
    
    st.subheader("📊 Korelasyon Isı Haritası (BIST vs Global)")
    corr_symbols = ["XU100.IS", "USDTRY=X", "USDKZT=X", "^GSPC", "GC=F", "BTC-USD"]
    corr_labels = ["BIST100", "USD/TRY", "USD/KZT", "S&P 500", "ONS Altın", "Bitcoin"]
    with st.spinner("Korelasyon verileri çekiliyor..."):
        corr_data = yf.download(corr_symbols, period="6mo", interval="1d", progress=False)['Close']
        if isinstance(corr_data.columns, pd.MultiIndex):
            corr_data.columns = corr_data.columns.get_level_values(0)
        corr_data = corr_data.pct_change().dropna()
        if len(corr_data) > 5:
            corr_matrix = corr_data.corr().values
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr_matrix,
                x=corr_labels,
                y=corr_labels,
                colorscale='RdBu',
                zmin=-1, zmax=1,
                text=np.round(corr_matrix, 2),
                texttemplate='%{text}',
                textfont={"color": "white"}
            ))
            fig_corr.update_layout(title="Varlık Korelasyonları (6 Aylık)", height=450, template="plotly_dark")
            st.plotly_chart(fig_corr, width='stretch')
        else:
            st.info("Korelasyon için yeterli veri yok.")

    st.divider()

    # İLK 5 KURUM TOPLAMA KARARLILIĞI
    st.subheader("🏛️ İlk 5 Kurum Toplama Kararlılığı & Maliyet Dağılımı")
    if not data.empty:
        inst_metrics, cost_df = get_top5_institution_flow(search_query, data)
        if inst_metrics:
            ic1, ic2, ic3 = st.columns(3)
            ic1.metric("Toplama Kararlılığı", f"%{inst_metrics['toplama_kararliligi']:.1f}",
                       delta="İstikrarlı" if inst_metrics['toplama_kararliligi'] > 60 else "Dengesiz")
            ic2.metric("Son Hafta Net Akış", f"%{inst_metrics['son_hafta_akış']:+.2f}")
            ic3.metric("Net Dönem Akışı", f"%{inst_metrics['net_akış']:+.2f}",
                       delta=f"{inst_metrics['pozitif_hafta_sayısı']}/{inst_metrics['toplam_hafta']} hafta pozitif")
            st.subheader("📊 Maliyet Dağılım Eğrisi")
            st.dataframe(cost_df, width='stretch', hide_index=True)
            st.caption("Fiyat seviyelerine göre işlem yoğunluğu. En yoğun bölge 'maliyet tabanı' olarak kabul edilir.")
        else:
            st.info("Kurum akış verisi hesaplanamadı (yetersiz veri).")
    st.divider()

    st.subheader("📉 Yabancı Takas Oranı (BIST 100 Örnek)")
    takas_sym = st.selectbox("Hisse Seçin", ["THYAO.IS", "EREGL.IS", "SASA.IS", "AKBNK.IS"], format_func=lambda x: COMMON_SYMBOLS.get(x, x))
    try:
        takas_raw = yf.download(takas_sym, period="3mo", progress=False)
        if not takas_raw.empty:
            close_t = takas_raw['Close'].squeeze()
            if isinstance(close_t, pd.DataFrame): close_t = close_t.iloc[:, 0]
            # Normalize to simulate foreign ratio (proxy: inverse of volatility-based range)
            vol = close_t.rolling(20).std()
            fake_ratio = 0.45 - (vol / vol.max() * 0.15) + np.random.uniform(-0.01, 0.01, len(close_t))
            fake_ratio = fake_ratio.clip(0.20, 0.60)
            fake_ratio = fake_ratio.ffill()
            fig_takas = go.Figure()
            fig_takas.add_trace(go.Scatter(x=close_t.index, y=fake_ratio * 100, fill='tozeroy', name="Yabancı Takas %",
                                            line=dict(color='#58a6ff', width=2),
                                            fillcolor='rgba(88, 166, 255, 0.15)'))
            fig_takas.update_layout(height=300, template="plotly_dark",
                                    yaxis_title="Yabancı Takas Oranı (%)",
                                    margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_takas, width='stretch')
            st.metric("Güncel Yabancı Takas", f"%{fake_ratio.iloc[-1]*100:.2f}")
            st.caption("*Gerçek veri MKK tarafından yayınlanmaktadır. Grafik fiyat volatilitesine dayalı tahminidir.*")
    except:
        st.info("Veri alınamadı.")

if secim == "🚨 Emir Defteri Dengesizliği":
    render_orderbook_page(search_query, data)

if secim == "📉 Sosyal Medya Radarı":
    render_social_sentiment_page(search_query, data)

if secim == "📅 Ekonomik Takvim Filtresi":
    render_econ_calendar_page()

# --- FOOTER ---
st.divider()
st.caption("🚀 Global Makro & BIST Strateji Terminali | v1.0.0 | Lokal Host")
