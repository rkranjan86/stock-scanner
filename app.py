import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, time
import pytz

# Page configuration
st.set_page_config(page_title="EOD Stock Analysis Dashboard", layout="wide")

# Timezone set (IST)
IST = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(IST)

# Header Section: Live Date & Time
st.markdown(f"### 📅 **Live Date & Time:** `{now_ist.strftime('%d/%m/%Y | %I:%M:%S %p IST')}`")

# 1. Live Index Tracker (Nifty 50, Sensex, Bank Nifty)
st.subheader("📊 Live Market Indices")

@st.cache_data(ttl=60) # Live Indices update every 60s
def get_live_indices():
    indices = {
        "Nifty 50": "^NSEI",
        "Sensex": "^BSESN",
        "Bank Nifty": "^NSEBANK"
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
col1, col2, col3 = st.columns(3)

with col1:
    d = indices_info["Nifty 50"]
    st.metric(label="NIFTY 50", value=d["price"], delta=f"{d['change']} ({d['pct']}%)")

with col2:
    d = indices_info["Sensex"]
    st.metric(label="SENSEX", value=d["price"], delta=f"{d['change']} ({d['pct']}%)")

with col3:
    d = indices_info["Bank Nifty"]
    st.metric(label="BANK NIFTY", value=d["price"], delta=f"{d['change']} ({d['pct']}%)")

st.markdown("---")

# 2. Hardcoded Nifty 200 / Major Stocks List (To prevent fetch errors)
STOCKS_LIST = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS",
    "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LTIM.NS", "KOTAKBANK.NS", "LT.NS",
    "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "SUNPHARMA.NS", "BAJFINANCE.NS",
    "TATAMOTORS.NS", "TATASTEEL.NS", "NTPC.NS", "POWERGRID.NS", "M&M.NS", "ULTRACEMCO.NS",
    "ADANIENT.NS", "ADANIPORTS.NS", "COALINDIA.NS", "HCLTECH.NS", "ONGC.NS", "WIPRO.NS",
    "BPCL.NS", "IOC.NS", "DLF.NS", "HAL.NS", "BEL.NS", "TATAPOWER.NS", "VBL.NS", "ZOMATO.NS",
    "JIOFIN.NS", "PFC.NS", "RECLTD.NS", "IRFC.NS", "SUZLON.NS", "BHEL.NS", "BANKBARODA.NS"
]

# 3. Stock Scanner Logic
st.subheader("🎯 EOD Breakout Stock Analysis (Filter: Close >= Open + 10)")

@st.cache_data(ttl=1800) # Data cached for 30 mins
def scan_eod_breakouts():
    selected = []
    # Fetch 5 days daily candles
    data = yf.download(STOCKS_LIST, period="5d", interval="1d", group_by='ticker', progress=False)
    
    for symbol in STOCKS_LIST:
        try:
            df = data[symbol].dropna()
            if len(df) < 2:
                continue
            
            today = df.iloc[-1]
            yesterday = df.iloc[-2]
            
            # Formulate Rules
            # Rule 1: Green Candle (Today Close > Today Open)
            is_green = today['Close'] > today['Open']
            
            # Rule 2: Minimum 10 Taka Movement (Close - Open >= 10)
            price_gain = today['Close'] - today['Open']
            is_10_taka_up = price_gain >= 10
            
            # Rule 3: Today Close > Yesterday High
            break_prev_high = today['Close'] > yesterday['High']
            
            # Rule 4: Today Volume > Yesterday Volume
            volume_up = today['Volume'] > yesterday['Volume']
            
            if is_green and is_10_taka_up and break_prev_high and volume_up:
                selected.append({
                    "Stock": symbol.replace(".NS", ""),
                    "Close Price (₹)": round(today['Close'], 2),
                    "Price Gain (₹)": round(price_gain, 2),
                    "Yesterday High (₹)": round(yesterday['High'], 2),
                    "Volume": int(today['Volume'])
                })
        except Exception:
            continue
            
    return selected

# Trigger Scan & Display Data
with st.spinner("Processing Market EOD Data..."):
    results = scan_eod_breakouts()

if results:
    st.success(f"Mot {len(results)} ti Stock eey Formula-y Select Hoyeche:")
    res_df = pd.DataFrame(results)
    st.dataframe(res_df, use_container_width=True)
else:
    st.info("Shesher Market Data Anushare Ei Formula-y Kono Stock Meleni.")
