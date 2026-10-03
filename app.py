import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# Page Configuration
st.set_page_config(page_title="Stockview12 - Bollinger Band Live Scanner", layout="wide")

IST = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(IST)

# Custom Styling (Stockview12 Logo, Marquee, Buttons, Disclaimer)
st.markdown("""
    <style>
    /* Stockview12 Logo Styling */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }
    .stockview-logo {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #00c6ff 100%);
        color: #ffffff;
        font-weight: 900;
        font-size: 26px;
        padding: 8px 20px;
        border-radius: 10px;
        letter-spacing: 1.5px;
        box-shadow: 0px 4px 12px rgba(0, 198, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stockview-logo span {
        color: #00e676; /* Accent color for '12' */
    }
    .ext-title {
        font-size: 24px;
        font-weight: 800;
        color: #111111;
        margin: 0;
    }
    
    /* Marquee Ticker Styling */
    .marquee-wrapper {
        background-color: #1a1e24;
        color: #ffffff;
        padding: 8px 0;
        border-radius: 6px;
        overflow: hidden;
        white-space: nowrap;
        box-shadow: inset 0 0 5px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .marquee-content {
        display: inline-block;
        animation: marquee 30s linear infinite;
    }
    @keyframes marquee {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-item {
        display: inline-block;
        margin-right: 35px;
        font-size: 14px;
        font-weight: 600;
    }
    .ticker-pos { color: #00e676; }
    .ticker-neg { color: #ff5252; }
    
    /* Disclaimer Box */
    .disclaimer-box {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
        padding: 12px 18px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        margin-top: 25px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 1. Header with Stockview12 Dynamic Logo
st.markdown(f"""
    <div class="logo-container">
        <div class="stockview-logo">Stockview<span>12</span></div>
        <div class="ext-title">Bollinger Band Live Pro Scanner</div>
    </div>
""", unsafe_allow_html=True)

# 2. Live Indices Fetching for Marquee
@st.cache_data(ttl=30)
def get_live_indices():
    indices = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "BANK NIFTY": "^NSEBANK",
        "NIFTY 500": "^CRSLDX",
        "INDIA VIX": "^INDIAVIX",
        "DOW JONES": "^DJI",
        "NASDAQ": "^IXIC",
        "NIKKEI 225": "^N225"
    }
    items_html = ""
    for name, ticker in indices.items():
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info
            current_price = info.last_price
            prev_close = info.previous_close
            change = current_price - prev_close
            pct_change = (change / prev_close) * 100
            
            is_pos = change >= 0
            cls = "ticker-pos" if is_pos else "ticker-neg"
            sign = "+" if is_pos else ""
            
            items_html += f"""
            <div class="ticker-item">
                <span>{name}:</span> <b>{current_price:,.2f}</b> 
                <span class="{cls}">({sign}{change:.2f} | {sign}{pct_change:.2f}%)</span>
            </div>
            """
        except Exception:
            continue
    return items_html

marquee_html = get_live_indices()

# Display Marquee Bar
if marquee_html:
    st.markdown(f"""
        <div class="marquee-wrapper">
            <div class="marquee-content">
                {marquee_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

# Refresh Control & Live Time
c_time, c_ref = st.columns([4, 1])
with c_time:
    st.caption(f"📅 **Live Market Time:** `{now_ist.strftime('%d/%m/%Y | %I:%M:%S %p IST')}`")
with c_ref:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# 3. Navigation Menu Bar
selected_menu = st.radio(
    "📌 Navigation Menu",
    [
        "📈 Live Scanner", 
        "⭐ Live Watchlist", 
        "⚡ Intraday Stocks", 
        "📅 Short Term Stocks", 
        "🏦 Long Term Stocks"
    ],
    horizontal=True
)

st.markdown("---")

# Stock Lists Definition
NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS",
    "BHARTIARTL.NS", "LTIM.NS", "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS", "HCLTECH.NS", "BAJFINANCE.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "TATAMOTORS.NS", "NTPC.NS",
    "ONGC.NS", "POWERGRID.NS", "ADANIENT.NS", "ADANIPORTS.NS", "COALINDIA.NS", "BAJAJFINSV.NS", "TATASTEEL.NS",
    "M&M.NS", "NESTLEIND.NS", "GRASIM.NS", "TECHM.NS", "HEROMOTOCO.NS", "CIPLA.NS", "WIPRO.NS", "HDFCLIFE.NS",
    "BPCL.NS", "EICHERMOT.NS", "DRREDDY.NS", "DIVISLAB.NS", "TATACONSUM.NS", "SBILIFE.NS", "BAJAJ-AUTO.NS",
    "BRITANNIA.NS", "INDUSINDBK.NS", "HINDALCO.NS", "JSWSTEEL.NS", "APOLLOHOSP.NS", "UPL.NS"
]

NIFTY_500 = NIFTY_50 + [
    "ABB.NS", "ACC.NS", "AUBANK.NS", "BEL.NS", "BHEL.NS", "BPCL.NS", "GAIL.NS", "IDFCFIRSTB.NS", 
    "IRCTC.NS", "IRFC.NS", "JIOFIN.NS", "LICHSGFIN.NS", "NHPC.NS", "NMDC.NS", "POLYCAB.NS", "RECLTD.NS", 
    "PFC.NS", "SAIL.NS", "TATACOMM.NS", "TATAPOWER.NS", "VOLTAS.NS", "ZEEL.NS", "ZOMATO.NS"
]

# Core Scanner Function
@st.cache_data(ttl=60)
def scan_bollinger(stocks, interval, period, strategy_type, tf_name):
    selected = []
    if not stocks:
        return selected

    try:
        data = yf.download(stocks, period=period, interval=interval, group_by='ticker', progress=False)
    except Exception:
        return selected

    for symbol in stocks:
        try:
            if symbol in data:
                df = data[symbol].dropna()
            else:
                continue

            if len(df) < 21:
                continue

            # Resampling Logic
            if tf_name == "10m":
                df = df.resample('10min').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()
            elif tf_name == "2h":
                df = df.resample('2h').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()
            elif tf_name == "4h":
                df = df.resample('4h').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()

            if len(df) < 21:
                continue

            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['Lower_Band'] = df['SMA20'] - (df['STD20'] * 2)

            curr = df.iloc[-1]
            prev = df.iloc[-2]

            body_curr = abs(curr['Close'] - curr['Open'])
            range_curr = curr['High'] - curr['Low']

            if strategy_type == "Condition 1: Lower Band Cut (Strong Green Candle & Engulfing/Reversal)":
                is_green = curr['Close'] > curr['Open']
                cuts_lower = curr['Low'] <= curr['Lower_Band'] and curr['Close'] >= curr['Lower_Band']
                bullish_engulfing = (curr['Close'] >= prev['Open']) or (curr['Close'] >= prev['High'] * 0.98)
                strong_body = (body_curr / range_curr) > 0.50 if range_curr > 0 else False

                if is_green and cuts_lower and bullish_engulfing and strong_body:
                    selected.append({
                        "Stock": symbol.replace(".NS", ""),
                        "LTP (₹)": round(curr['Close'], 2),
                        "Open (₹)": round(curr['Open'], 2),
                        "High (₹)": round(curr['High'], 2),
                        "Lower Band (₹)": round(curr['Lower_Band'], 2),
                        "Pattern": "Strong Green Cut",
                        "Volume": int(curr['Volume'])
                    })

            elif strategy_type == "Condition 2: Completely Below Lower Band (Hammer / Morning Star Gap)":
                below_lower = curr['High'] <= curr['Lower_Band']
                lower_shadow = min(curr['Open'], curr['Close']) - curr['Low']
                upper_shadow = curr['High'] - max(curr['Open'], curr['Close'])
                
                is_hammer = (lower_shadow >= 2 * body_curr) and (upper_shadow <= body_curr * 1.2) if body_curr > 0 else (lower_shadow > 0)
                is_small_body = (body_curr / range_curr) < 0.35 if range_curr > 0 else True

                if below_lower and (is_hammer or is_small_body):
                    pattern_type = "Hammer Below Band" if is_hammer else "Gap / Morning Star Base"
                    selected.append({
                        "Stock": symbol.replace(".NS", ""),
                        "LTP (₹)": round(curr['Close'], 2),
                        "High (₹)": round(curr['High'], 2),
                        "Low (₹)": round(curr['Low'], 2),
                        "Lower Band (₹)": round(curr['Lower_Band'], 2),
                        "Pattern": pattern_type,
                        "Volume": int(curr['Volume'])
                    })
        except Exception:
            continue

    return selected

# Page 1: Main Live Scanner
if selected_menu == "📈 Live Scanner":
    st.subheader("⚙️ Scanner Settings")
    c1, c2, c3 = st.columns(3)

    with c1:
        strategy = st.selectbox(
            "🎯 Select Strategy",
            [
                "Condition 1: Lower Band Cut (Strong Green Candle & Engulfing/Reversal)",
                "Condition 2: Completely Below Lower Band (Hammer / Morning Star Gap)"
            ]
        )

    with c2:
        timeframe = st.selectbox(
            "⏱️ Select Timeframe",
            ["5m", "10m", "15m", "30m", "1h", "2h", "4h", "1d", "1w", "1m"],
            index=7
        )

    with c3:
        segment = st.radio("📜 Stock List Segment", ["NIFTY 50", "NIFTY 500"], horizontal=True)

    tf_map = {
        "5m": ("5m", "5d"),
        "10m": ("5m", "5d"),
        "15m": ("15m", "5d"),
        "30m": ("30m", "5d"),
        "1h": ("60m", "1mo"),
        "2h": ("60m", "1mo"),
        "4h": ("60m", "3mo"),
        "1d": ("1d", "6mo"),
        "1w": ("1wk", "2y"),
        "1m": ("1mo", "5y")
    }
    interval, period = tf_map[timeframe]
    stocks_to_scan = NIFTY_50 if segment == "NIFTY 50" else NIFTY_500

    with st.spinner(f"Scanning {len(stocks_to_scan)} stocks in {timeframe} timeframe..."):
        results = scan_bollinger(stocks_to_scan, interval, period, strategy, timeframe)

    if results:
        st.success(f"Mot {len(results)} ti stock pawa geche selected condition onujayi ({timeframe} timeframe)!")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info(f"Selected condition-e current live data-te {timeframe} timeframe-e kono stock pawa jayni.")

# Page 2: Live Watchlist
elif selected_menu == "⭐ Live Watchlist":
    st.subheader("⭐ Custom Live Watchlist")
    user_symbols = st.text_input("Stock Symbols Type Korun (Comma Separated):", "RELIANCE, SBIN, TATAMOTORS, INFY, HDFCBANK")
    
    if user_symbols:
        symbol_list = [s.strip().upper() + ".NS" for s in user_symbols.split(",") if s.strip()]
        watchlist_data = []
        for sym in symbol_list:
            try:
                t = yf.Ticker(sym)
                info = t.fast_info
                p = info.last_price
                pc = info.previous_close
                chg = p - pc
                pct = (chg / pc) * 100
                watchlist_data.append({
                    "Stock Symbol": sym.replace(".NS", ""),
                    "LTP (₹)": round(p, 2),
                    "Change (₹)": round(chg, 2),
                    "Change (%)": f"{pct:+.2f}%",
                    "Prev Close (₹)": round(pc, 2)
                })
            except Exception:
                continue
        if watchlist_data:
            st.dataframe(pd.DataFrame(watchlist_data), use_container_width=True)

# Page 3: Intraday Stocks
elif selected_menu == "⚡ Intraday Stocks":
    st.subheader("⚡ Intraday Focus Stocks (High Liquidity & Volatility)")
    st.caption("Intraday trading-er jonno suitable high-volume stock scanning (15m timeframe):")
    intraday_list = ["RELIANCE.NS", "TATAMOTORS.NS", "SBIN.NS", "ICICIBANK.NS", "AXISBANK.NS", "BAJFINANCE.NS"]
    results = scan_bollinger(intraday_list, "15m", "5d", "Condition 1: Lower Band Cut (Strong Green Candle & Engulfing/Reversal)", "15m")
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info("Current Intraday timeframe-e (15m) kono setup toiri hoyni.")

# Page 4: Short Term Stocks
elif selected_menu == "📅 Short Term Stocks":
    st.subheader("📅 Short Term / Swing Trading Stocks")
    st.caption("Daily timeframe-e breakout ba reversal pattern scan kora hocche:")
    results = scan_bollinger(NIFTY_50, "1d", "6mo", "Condition 1: Lower Band Cut (Strong Green Candle & Engulfing/Reversal)", "1d")
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info("Daily timeframe-e kono Short-term setup pawa jayni.")

# Page 5: Long Term Stocks
elif selected_menu == "🏦 Long Term Stocks":
    st.subheader("🏦 Long Term Fundamental Wealth Creators")
    st.caption("Weekly timeframe-e deep value zone-e thaka stocks:")
    results = scan_bollinger(NIFTY_50[:15], "1wk", "2y", "Condition 2: Completely Below Lower Band (Hammer / Morning Star Gap)", "1w")
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info("Weekly timeframe-e kono long-term value setup pawa jayni.")

# Footer Disclaimer Note
st.markdown("""
    <div class="disclaimer-box">
        ⚠️ <b>কাজের সতর্কতা ও ডিসক্লেইমার:</b> এখানে কোনো শেয়ার বা স্টক বাই (Buy) অথবা সেল (Sell) করার অনুমতি বা পরামর্শ দেয়া হয় না। এই পোর্টালটি সম্পূর্ণ শিক্ষার উদ্দেশ্যে (Educational Purpose) প্রণীত।
    </div>
""", unsafe_allow_html=True)
