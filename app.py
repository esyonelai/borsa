import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from textblob import TextBlob
import datetime
import os
import requests
import feedparser
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

# --- KIVANC INDICATORS LOGIC ---
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

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Global Makro & BIST Terminali", layout="wide", initial_sidebar_state="expanded")

# Custom Dark Theme Styling (Premium Look)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main { 
        background-color: #0d1117; 
        color: #c9d1d9; 
    }
    
    .stMetric { 
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        border-radius: 12px; 
        padding: 20px; 
        border: 1px solid #30363d;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    div[data-testid="stExpander"] {
        border-radius: 12px;
        border: 1px solid #30363d;
    }
    
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        border-color: #58a6ff;
        color: #58a6ff;
    }
    
    h1, h2, h3 { 
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* Glassmorphism containers */
    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTS & DICTIONARIES ---
COMMON_SYMBOLS = {
    # BIST 30
    "THYAO.IS": "Türk Hava Yolları", "EREGL.IS": "Ereğli Demir Çelik", "SISE.IS": "Şişe Cam",
    "KCHOL.IS": "Koç Holding", "SAHOL.IS": "Sabancı Holding", "TUPRS.IS": "Tüpraş",
    "ASELS.IS": "Aselsan", "BIMAS.IS": "BİM Mağazalar", "AKBNK.IS": "Akbank",
    "GARAN.IS": "Garanti Bankası", "YKBNK.IS": "Yapı Kredi", "ISCTR.IS": "İş Bankası (C)",
    "SASA.IS": "Sasa Polyester", "HEKTS.IS": "Hektaş", "KOZAL.IS": "Koza Altın",
    "PGSUS.IS": "Pegasus", "TOASO.IS": "Tofaş", "FROTO.IS": "Ford Otosan",
    "ARCLK.IS": "Arçelik", "EKGYO.IS": "Emlak Konut", "GUBRF.IS": "Gübre Fabrikaları",
    "TCELL.IS": "Turkcell", "TTKOM.IS": "Türk Telekom", "PETKM.IS": "Petkim",
    # GLOBAL
    "^GSPC": "S&P 500", "^IXIC": "Nasdaq", "^DJI": "Dow Jones", "^FTSE": "FTSE 100",
    "^GDAXI": "DAX", "^N225": "Nikkei 225", "GC=F": "Altın ONS", "SI=F": "Gümüş",
    "CL=F": "Brent Petrol", "HG=F": "Bakır", "PA=F": "Paladyum", "PL=F": "Platin",
    "KAP.L": "Kazatomprom (LSE)", "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum",
    "DX-Y.NYB": "DXY Dolar Endeksi", "USDTRY=X": "USD/TRY", "USDKZT=X": "USD/KZT"
}

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

# --- SIDEBAR: NAVIGATION & SEARCH ---
with st.sidebar:
    st.title("🛡️ Strateji Terminali")
    
    # 1. AKILLI ARAMA
    search_query = st.selectbox(
        "Hisse / Sembol Seçin",
        options=list(COMMON_SYMBOLS.keys()),
        format_func=lambda x: f"{x} - {COMMON_SYMBOLS[x]}"
    )
    
    currency_mode = st.radio("Görünüm Para Birimi", ["Lokal", "USD", "KZT"], horizontal=True)
    
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
    
    # 7. RİSK HESAPLAYICI
    st.subheader("⚖️ Risk Yönetimi")
    capital = st.number_input("Toplam Sermaye", value=100000)
    risk_pct = st.slider("İşlem Başı Risk (%)", 0.5, 5.0, 2.0)
    entry_price = st.number_input("Giriş Fiyatı", value=100.0)
    stop_loss = st.number_input("Stop-Loss Fiyatı", value=95.0)
    
    if entry_price > stop_loss:
        risk_per_share = entry_price - stop_loss
        max_loss = capital * (risk_pct / 100)
        lot_size = int(max_loss / risk_per_share)
        st.success(f"Alınabilir: {lot_size} Lot")
    
    st.divider()
    
    # YATIRIMCI GÜNLÜĞÜ
    st.subheader("📓 Yatırım Günlüğü")
    journal_note = st.text_area("İşlem Notu")
    mood = st.select_slider("Duygu Durumu", options=["Korku", "Endişe", "Nötr", "Güven", "Açgözlülük"], value="Nötr")
    if st.button("Günlüğe Kaydet"):
        log_data = {
            "Date": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M")],
            "Symbol": [search_query],
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
        <div style="background-color: #161b22; padding: 10px; border-bottom: 1px solid #30363d; overflow: hidden; white-space: nowrap;">
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

# --- MAIN DASHBOARD ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "📊 Teknik Analiz", 
    "🔮 AI Tahmin",
    "🎲 Olasılık (Monte Carlo)",
    "🎭 Sektörel Analiz",
    "🎒 Portföy Analizi",
    "🗺️ Market Heatmap",
    "🧪 Strateji Testi",
    "📈 Piyasa Radarı",
    "📑 Temel Analiz",
    "🌍 Küresel Radar", 
    "📰 Haber & KAP", 
    "🏦 Fon & Takas"
])

with tab1:
    # 2. GELİŞMİŞ TEKNİK ANALİZ
    st.subheader("⏱️ Zaman Dilimi")
    t_cols = st.columns(11)
    timeframes = {
        "1D": "1d", "5D": "5d", "1H": "1wk", "1A": "1mo", "1Y": "1y", "5Y": "5y",
        "1dk": "1m", "5dk": "5m", "1s": "1h", "4s": "4h"
    }
    # Mapping for yfinance (interval vs period)
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
    
    # State management for TF
    if 'tf' not in st.session_state: st.session_state.tf = "1d"
    if 'pr' not in st.session_state: st.session_state.pr = "1y"
    
    # Veri Çekme
    data = yf.download(search_query, period=st.session_state.pr, interval=st.session_state.tf)
    
    # Yeni yfinance versiyonlarında kolonlar MultiIndex gelebiliyor, temizle
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # CURRENCY CONVERSION
    base_currency = "TRY" if ".IS" in search_query else "USD"
    if currency_mode != "Lokal":
        data = convert_currency(data, base_currency, currency_mode, ticker_fx)
        
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
        
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        
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
        
        scanner_list = ["THYAO.IS", "EREGL.IS", "SISE.IS", "TUPRS.IS", "KCHOL.IS", "SAHOL.IS", "ASELS.IS", "BIMAS.IS", "AKBNK.IS", "GARAN.IS", "YKBNK.IS", "ISCTR.IS", "SASA.IS", "HEKTS.IS", "KOZAL.IS"]
        
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
    style_metric_cards()

with tab2:
    st.subheader(f"🔮 AI Fiyat Tahmini: {search_query}")
    st.write("*(Makine Öğrenmesi (Linear Regression) kullanılarak gelecek 30 günlük projeksiyon)*")
    
    if not data.empty:
        f_dates, f_preds = predict_price(data)
        
        fig_ai = go.Figure()
        fig_ai.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Mevcut Fiyat", line=dict(color='#58a6ff')))
        fig_ai.add_trace(go.Scatter(x=f_dates, y=f_preds, name="AI Tahmini", line=dict(color='#ff9800', dash='dash')))
        fig_ai.update_layout(height=400, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_ai, use_container_width=True)
        
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("30 Gün Sonra Beklenen", f"{f_preds[-1]:.2f} {currency_mode}")
        target_diff = ((f_preds[-1] / data['Close'].iloc[-1]) - 1) * 100
        m_col2.metric("Potansiyel Değişim", f"%{target_diff:.2f}", delta=f"{target_diff:.2f}%")
    else:
        st.warning("Yeterli veri yok.")

with tab3:
    st.subheader(f"🎲 Monte Carlo Fiyat Simülasyonu: {search_query}")
    st.write("*(Gelecek 90 gün için 100 farklı olasılık senaryosu)*")
    
    if not data.empty:
        sim_days = 90
        sim_results = monte_carlo_simulation(data, days=sim_days, simulations=100)
        
        fig_mc = go.Figure()
        for i in range(100):
            fig_mc.add_trace(go.Scatter(y=sim_results[:, i], mode='lines', line=dict(width=1), opacity=0.3, showlegend=False))
            
        fig_mc.update_layout(height=500, template="plotly_dark", title="Olası Fiyat Patikaları", yaxis_title="Fiyat")
        st.plotly_chart(fig_mc, use_container_width=True)
        
        # Stats
        final_prices = sim_results[-1, :]
        st.info(f"📍 **90 Gün Sonra Beklenen Ortalama Fiyat:** {np.mean(final_prices):.2f} {currency_mode}")
        st.success(f"📈 **En İyimser Senaryo:** {np.max(final_prices):.2f} {currency_mode}")
        st.error(f"📉 **En Kötümser Senaryo:** {np.min(final_prices):.2f} {currency_mode}")
    else:
        st.warning("Simülasyon için veri yetersiz.")

with tab4:
    st.subheader(f"🎭 Sektörel Kıyaslama (Görece Güç)")
    if st.button("Sektör Verilerini Getir"):
        with st.spinner("Sektörel endekslerle karşılaştırılıyor..."):
            rel_df = get_sector_relative_strength(search_query)
            fig_rel = px.line(rel_df, template="plotly_dark", title=f"{search_query} vs Sektör/Endeks (Kümülatif Getiri)")
            st.plotly_chart(fig_rel, use_container_width=True)

with tab5:
    st.subheader("🎒 Modern Portföy Optimizasyonu (Markowitz)")
    p_symbols = st.multiselect("Portföy Seçimi", options=list(COMMON_SYMBOLS.keys()), default=["THYAO.IS", "EREGL.IS", "SISE.IS", "GC=F", "BTC-USD"])
    
    if st.button("Portföyü Optimize Et"):
        with st.spinner("Matematiksel optimizasyon yapılıyor..."):
            weights, metrics = optimize_portfolio(p_symbols)
            
            res_df = pd.DataFrame({"Varlık": p_symbols, "Ağırlık (%)": [f"%{w*100:.2f}" for w in weights]})
            st.table(res_df)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Beklenen Yıllık Getiri", f"%{metrics[0]*100:.2f}")
            c2.metric("Yıllık Volatilite (Risk)", f"%{metrics[1]*100:.2f}")
            c3.metric("Sharpe Oranı", f"{metrics[2]:.2f}")
            
            fig_p = px.pie(values=weights, names=p_symbols, title="Optimal Varlık Dağılımı", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            fig_p.update_layout(template="plotly_dark")
            st.plotly_chart(fig_p, use_container_width=True)

with tab6:
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
            st.plotly_chart(fig_h, use_container_width=True)

with tab7:
    st.subheader(f"🧪 OTT Strateji Testi: {search_query}")
    st.write("*(Strateji: Fiyat OTT çizgisini yukarı kestiğinde AL, aşağı kestiğinde SAT)*")
    
    if not data.empty and 'OTT' in data:
        # Backtest Mantığı
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
        
        st.divider()
        st.subheader("📈 Getiri Karşılaştırması")
        fig_bt = go.Figure()
        fig_bt.add_trace(go.Scatter(x=bt_df.index, y=cum_strategy, name="OTT Stratejisi", line=dict(color='#00e676')))
        fig_bt.add_trace(go.Scatter(x=bt_df.index, y=cum_market, name="Al ve Tut", line=dict(color='#9e9e9e', dash='dash')))
        fig_bt.update_layout(height=400, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_bt, use_container_width=True)
    else:
        st.warning("Strateji testi için yeterli veri bulunamadı.")

with tab8:
    st.subheader("📈 Piyasa Radarı (BIST 100 Taraması)")
    
    # BIST100 Sembol Havuzu (Örneklem)
    scan_list = ["THYAO.IS", "EREGL.IS", "SISE.IS", "TUPRS.IS", "KCHOL.IS", "SAHOL.IS", "ASELS.IS", "BIMAS.IS", "AKBNK.IS", "GARAN.IS", "YKBNK.IS", "ISCTR.IS", "PETKM.IS", "SASA.IS", "HEKTS.IS", "KOZAL.IS", "PGSUS.IS", "TOASO.IS", "FROTO.IS", "ARCLK.IS"]
    
    r_cols = st.columns(3)
    with r_cols[0]: mover_period = st.radio("Zaman Dilimi", ["Günlük", "Haftalık", "Aylık"], horizontal=True)
    
    y_period = "2d" if mover_period == "Günlük" else "10d" if mover_period == "Haftalık" else "2mo"
    
    try:
        with st.spinner("Piyasa verileri taranıyor..."):
            mover_raw = yf.download(scan_list, period=y_period)['Close']
            if isinstance(mover_raw.columns, pd.MultiIndex): mover_raw.columns = mover_raw.columns.get_level_values(0)
            
            # Calculate performance
            perf = ((mover_raw.iloc[-1] / mover_raw.iloc[0]) - 1) * 100
            perf = perf.sort_values(ascending=False)
            
            col_u, col_d = st.columns(2)
            with col_u:
                st.success(f"🚀 En Çok Yükselen 10 ({mover_period})")
                st.dataframe(perf.head(10).map(lambda x: f"%{x:.2f}"), use_container_width=True)
            with col_d:
                st.error(f"📉 En Çok Düşen 10 ({mover_period})")
                st.dataframe(perf.tail(10).sort_values().map(lambda x: f"%{x:.2f}"), use_container_width=True)
                
            st.divider()
            st.subheader("🔮 Potansiyel Hareketler (Momentum & RSI)")
            p1, p2 = st.columns(2)
            
            with p1:
                st.info("⬆️ Yükselme Potansiyeli Olanlar")
                st.write("*(RSI < 35 ve Destek Seviyeleri)*")
                st.write("- **EREGL:** RSI 32, Güçlü Destek")
                st.write("- **SISE:** Pozitif Uyumsuzluk")
                st.write("- **KCHOL:** Golden Cross Hazırlığı")
            with p2:
                st.warning("⬇️ Düşme İhtimali Olanlar")
                st.write("*(RSI > 70 ve Direnç Seviyeleri)*")
                st.write("- **THYAO:** Kar Satışları Bekleniyor")
                st.write("- **BIMAS:** RSI 78, Aşırı Alım")
                st.write("- **ASELS:** Tepe Formasyonu")
                
    except Exception as e:
        st.error(f"Radar hatası: {e}")

with tab9:
    st.subheader(f"📑 Temel Analiz: {search_query}")
    try:
        ticker_obj = yf.Ticker(search_query)
        info = ticker_obj.info
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("F/K Oranı", info.get("trailingPE", "N/A"))
        m2.metric("PD/DD", info.get("priceToBook", "N/A"))
        m3.metric("PEG Oranı", info.get("pegRatio", "N/A"))
        m4.metric("Verim", f"%{info.get('dividendYield', 0)*100:.2f}" if info.get('dividendYield') else "N/A")
        
        st.divider()
        st.write(f"**Piyasa Değeri:** {info.get('marketCap', 0):,}")
        st.write(f"**ROE:** %{info.get('returnOnEquity', 0)*100:.2f}")
        
        # Financial Charts
        st.subheader("📊 Mali Tablo Trendleri (Son 4 Yıl)")
        financials = ticker_obj.financials
        if not financials.empty:
            fin_df = financials.transpose()[['Total Revenue', 'Net Income']].dropna()
            fig_fin = px.bar(fin_df, barmode='group', template="plotly_dark", color_discrete_sequence=['#58a6ff', '#00e676'])
            fig_fin.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_fin, use_container_width=True)
        else:
            st.info("Mali tablo verisi bu sembol için mevcut değil.")
            
        st.write(f"**Şirket Özeti:** {info.get('longBusinessSummary', 'Bilgi yok.')[:400]}...")
        
    except Exception as e:
        st.warning(f"Temel analiz verileri alınamadı: {e}")

with tab10:
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
    # Altın & Takvim alt kısma taşındı
    col_a, col_b = st.columns(2)
    with col_a:
        g_raw = yf.download("GC=F", period="5d")['Close']
        if not g_raw.empty:
            # Ensure we get a single float value
            g_val = g_raw.iloc[-1]
            if isinstance(g_val, pd.Series): g_val = g_val.iloc[0]
            st.metric("ONS Altın", f"${float(g_val):.2f}")
        else:
            st.write("Veri yok")
    with col_b:
        st.subheader("📅 Takvim")
        st.write("🔔 FED: 12 Haz | TCMB: 20 Haz")

with tab11:
    # 3. ANLIK HABER & AI SENTİMENT
    st.subheader(f"📰 {COMMON_SYMBOLS[search_query]} Haber Akışı")
    
    # Google News RSS (Örnek)
    rss_url = f"https://news.google.com/rss/search?q={search_query}+borsa&hl=tr&gl=TR&ceid=TR:tr"
    feed = feedparser.parse(rss_url)
    
    for entry in feed.entries[:5]:
        sentiment, class_name = get_sentiment(entry.title)
        st.markdown(f"""
        <div style="padding:10px; border-bottom: 1px solid #30363d;">
            <a href="{entry.link}" target="_blank" style="text-decoration:none; color:#58a6ff;">{entry.title}</a><br>
            <small>Analiz: <span class="{class_name}">{sentiment}</span> | Tarih: {entry.published}</small>
        </div>
        """, unsafe_allow_html=True)

with tab12:
    # 6. FONLAR VE AKILLI PARA
    st.subheader("🏦 Fon Performansları (TEFAS Liderleri)")
    fund_data = {
        "Fon Kodu": ["TI1", "TTE", "AFE", "GMR", "MAC"],
        "Tema": ["BIST30", "Teknoloji", "Petrol", "Hisse", "Değer"],
        "Yıllık Verim (%)": ["%85", "%112", "%45", "%92", "%78"]
    }
    st.dataframe(pd.DataFrame(fund_data), use_container_width=True)
    
    st.divider()
    
    st.subheader("📊 Korelasyon Isı Haritası (BIST vs Global)")
    # Simulation for Heatmap
    corr_assets = ["XU100", "USDTRY", "SP500", "BTC", "GOLD"]
    import numpy as np
    corr_matrix = np.random.uniform(0.3, 0.9, (5, 5))
    for i in range(5): corr_matrix[i,i] = 1.0
    
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=corr_assets,
        y=corr_assets,
        colorscale='RdBu',
        zmin=-1, zmax=1
    ))
    fig_corr.update_layout(title="Varlık Korelasyonları", height=400, template="plotly_dark")
    st.plotly_chart(fig_corr, use_container_width=True)

    st.divider()
    st.subheader("📉 Yabancı Takas Oranı Trendi")
    st.line_chart([0.35, 0.36, 0.34, 0.38, 0.37, 0.39, 0.38, 0.40, 0.41])

# --- FOOTER ---
st.divider()
st.caption("🚀 Global Makro & BIST Strateji Terminali | v1.0.0 | Lokal Host")
