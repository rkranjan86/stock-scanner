import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Bollinger Band Live Scanner", layout="wide")

IST = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(IST)

# Custom CSS for styling small neat boxes
st.markdown("""
    <style>
    .index-box {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    .index-name {
        font-size: 13px;
        font-weight: 600;
        color: #555555;
        margin-bottom: 2px;
    }
    .index-price {
        font-size: 16px;
        font-weight: bold;
        color: #111111;
    }
    .index-change-pos {
        font-size: 12px;
        font-weight: bold;
        color: #0d8351;
    }
    .index-change-neg {
        font-size: 12px;
        font-weight: bold;
        color: #e53935;
    }
    </style>
""", unsafe_allow_html=True)

# Top Header
st.title("📈 Bollinger Band Advanced Live Scanner")
st.caption(f"📅 **Live Time:** `{now_ist.strftime('%d/%m/%Y | %I:%M:%S %p IST')}`")

# Refresh Control Panel
col_btn, col_auto = st.columns([1, 4])
with col_btn:
    if st.button("🔄 Refresh Data Now"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# 1. Live Market Indices (Styled Small Boxes)
st.subheader("📊 Live Market Indices")

@st.cache_data(ttl=30)
def get_live_indices():
    indices = {
        "NIFTY 50": "^NSEI",
        "NIFTY 500": "^CRSLDX",
        "SENSEX": "^BSESN",
        "BANK NIFTY": "^NSEBANK",
        "INDIA VIX": "^INDIAVIX",
        "DOW JONES": "^DJI",
        "NASDAQ": "^IXIC",
        "DAX": "^GDAXI",
        "SHANGHAI": "000001.SS",
        "NIKKEI 225": "^N225"
    }
    index_data = {}
    for name, ticker in indices.items():
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info
            current_price = info.last_price
            prev_close = info.previous_close
            change = current_price - prev_close
            pct_change = (change / prev_close) * 100
            index_data[name] = {
                "price": round(current_price, 2),
                "change": round(change, 2),
                "pct": round(pct_change, 2)
            }
        except Exception:
            index_data[name] = {"price": 0.0, "change": 0.0, "pct": 0.0}
    return index_data

indices_info = get_live_indices()
idx_keys = list(indices_info.keys())

def render_index_card(name, d):
    is_positive = d["change"] >= 0
    change_class = "index-change-pos" if is_positive else "index-change-neg"
    sign = "+" if is_positive else ""
    return f"""
    <div class="index-box">
        <div class="index-name">{name}</div>
        <div class="index-price">{d['price']:,}</div>
        <div class="{change_class}">{sign}{d['change']} ({sign}{d['pct']}%)</div>
    </div>
    """

cols_row1 = st.columns(5)
for i in range(5):
    name = idx_keys[i]
    d = indices_info[name]
    with cols_row1[i]:
        st.markdown(render_index_card(name, d), unsafe_allow_html=True)

cols_row2 = st.columns(5)
for i in range(5, 10):
    name = idx_keys[i]
    d = indices_info[name]
    with cols_row2[i - 5]:
        st.markdown(render_index_card(name, d), unsafe_allow_html=True)

st.markdown("---")

# 2. Controls / Strategy Selection
st.subheader("⚙️️ Scanner Settings")

c1, c2, c3 = st.columns(3)

with c1:
    strategy = st.selectbox(
        "🎯 Select Condition / Strategy",
        [
            "Condition 1: Lower Band Body Cut (Green Candle)",
            "Condition 2: Completely Below Lower Band (No Touch / Gap)"
        ]
    )

with c2:
    timeframe = st.selectbox(
        "⏱️ Select Timeframe",
        ["5m", "15m", "30m", "1h", "2h", "4h", "1d"],
        index=6
    )

with c3:
    # inline=True er jaygay horizontal=True bebohar kora hoyeche
    segment = st.radio("📜 Stock List Segment", ["NIFTY 50", "NIFTY 500"], horizontal=True)

# Map selected timeframe to yfinance interval & period
tf_map = {
    "5m": ("5m", "5d"),
    "15m": ("15m", "5d"),
    "30m": ("30m", "5d"),
    "1h": ("60m", "1mo"),
    "2h": ("60m", "1mo"),
    "4h": ("60m", "3mo"),
    "1d": ("1d", "3mo")
}
interval, period = tf_map[timeframe]

# Stock Lists
NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS",
    "BHARTIARTL.NS", "LTIM.NS", "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS", "HCLTECH.NS", "BAJFINANCE.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "TATAMOTORS.NS", "NTPC.NS",
    "ONGC.NS", "POWERGRID.NS", "ADANIENT.NS", "ADANIPORTS.NS", "COALINDIA.NS", "BAJAJFINSV.NS", "TATASTEEL.NS",
    "M&M.NS", "NESTLEIND.NS", "GRASIM.NS", "TECHM.NS", "HEROMOTOCO.NS", "CIPLA.NS", "WIPRO.NS", "HDFCLIFE.NS",
    "BPCL.NS", "EICHERMOT.NS", "DRREDDY.NS", "DIVISLAB.NS", "TATACONSUM.NS", "SBILIFE.NS", "BAJAJ-AUTO.NS",
    "BRITANNIA.NS", "INDUSINDBK.NS", "HINDALCO.NS", "JSWSTEEL.NS", "APOLLOHOSP.NS", "UPL.NS"
]

@st.cache_data(ttl=86400)
def fetch_nifty500_stocks():
    url = "https://raw.githubusercontent.com/indian-stock-market/nifty-csv/main/ind_nifty500list.csv"
    try:
        df = pd.read_csv(url)
        return [f"{s.strip()}.NS" for s in df['Symbol'].dropna().unique()]
    except Exception:
        return NIFTY_50

stocks_to_scan = NIFTY_50 if segment == "NIFTY 50" else fetch_nifty500_stocks()

# 3. Scanner Function
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

            if len(df) < 20:
                continue

            # Resample for 2h and 4h if timeframe is selected
            if tf_name == "2h":
                df = df.resample('2h').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()
            elif tf_name == "4h":
                df = df.resample('4h').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()

            if len(df) < 20:
                continue

            # Calculate Bollinger Bands
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['Lower_Band'] = df['SMA20'] - (df['STD20'] * 2)

            candle = df.iloc[-1]

            if strategy_type == "Condition 1: Lower Band Body Cut (Green Candle)":
                is_green = candle['Close'] > candle['Open']
                open_below = candle['Open'] < candle['Lower_Band']
                close_above = candle['Close'] > candle['Lower_Band']

                if is_green and open_below and close_above:
                    selected.append({
                        "Stock": symbol.replace(".NS", ""),
                        "LTP (₹)": round(candle['Close'], 2),
                        "Open (₹)": round(candle['Open'], 2),
                        "High (₹)": round(candle['High'], 2),
                        "Lower Band (₹)": round(candle['Lower_Band'], 2),
                        "Volume": int(candle['Volume'])
                    })

            elif strategy_type == "Condition 2: Completely Below Lower Band (No Touch / Gap)":
                # High is strictly less than Lower Band (No touch)
                completely_below = candle['High'] < candle['Lower_Band']

                if completely_below:
                    selected.append({
                        "Stock": symbol.replace(".NS", ""),
                        "LTP (₹)": round(candle['Close'], 2),
                        "High (₹)": round(candle['High'], 2),
                        "Low (₹)": round(candle['Low'], 2),
                        "Lower Band (₹)": round(candle['Lower_Band'], 2),
                        "Volume": int(candle['Volume'])
                    })
        except Exception:
            continue

    return selected

st.markdown("---")

# 4. Results
with st.spinner(f"Scanning {len(stocks_to_scan)} stocks in {timeframe} timeframe..."):
    results = scan_bollinger(stocks_to_scan, interval, period, strategy, timeframe)

if results:
    st.success(f"Mot {len(results)} ti stock pawa geche selected condition onujayi ({timeframe} timeframe)!")
    st.dataframe(pd.DataFrame(results), use_container_width=True)
else:
    st.info(f"Selected condition-e current live data-te {timeframe} timeframe-e kono stock pawa jayni. Live market-e data auto update hobe.")
