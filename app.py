import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# Page configuration
st.set_page_config(page_title="Stock Scanner Dashboard", layout="wide")

# Timezone set (IST)
IST = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(IST)

# Top Header Layout
st.title("📈 Daily Stock Breakout Dashboard")
st.caption(f"📅 **Live Time:** `{now_ist.strftime('%d/%m/%Y | %I:%M:%S %p IST')}`")

# 1. Refresh Button Section
if st.button("🔄 Refresh Data / Scan Now"):
    st.cache_data.clear()
    st.rerun()

st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

# 2. Live Market Indices (1 Single Line Compact Display)
st.markdown("##### 📊 Live Market Indices")

@st.cache_data(ttl=60)
def get_live_indices():
    indices = {
        "NIFTY 50": "^NSEI",
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

# 9 columns in a single row
cols = st.columns(9)
idx_names = list(indices_info.keys())

for idx, name in enumerate(idx_names):
    d = indices_info[name]
    with cols[idx]:
        st.metric(label=name, value=d["price"], delta=f"{d['change']} ({d['pct']}%)")

st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

# 3. Stock List (Fallback to reliable list if external URL fails)
@st.cache_data(ttl=3600)
def get_stock_list():
    url = "https://raw.githubusercontent.com/indian-stock-market/nifty-csv/main/ind_nifty200list.csv"
    try:
        df = pd.read_csv(url)
        return [f"{symbol}.NS" for symbol in df['Symbol']]
    except Exception:
        return [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS",
            "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LTIM.NS", "KOTAKBANK.NS", "LT.NS",
            "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "SUNPHARMA.NS", "BAJFINANCE.NS",
            "TATAMOTORS.NS", "TATASTEEL.NS", "NTPC.NS", "POWERGRID.NS", "M&M.NS", "ULTRACEMCO.NS",
            "ADANIENT.NS", "ADANIPORTS.NS", "COALINDIA.NS", "HCLTECH.NS", "ONGC.NS", "WIPRO.NS",
            "BPCL.NS", "IOC.NS", "DLF.NS", "HAL.NS", "BEL.NS", "TATAPOWER.NS", "VBL.NS", "ZOMATO.NS"
        ]

STOCKS_LIST = get_stock_list()

# 4. Stock Scanner Logic
st.markdown("##### 🎯 EOD Breakout Stocks (Close >= Open + ₹10 & Breakout Rules)")

@st.cache_data(ttl=300)
def scan_eod_breakouts():
    selected = []
    data = yf.download(STOCKS_LIST, period="5d", interval="1d", group_by='ticker', progress=False)
    
    for symbol in STOCKS_LIST:
        try:
            df = data[symbol].dropna()
            if len(df) < 2:
                continue
            
            today = df.iloc[-1]
            yesterday = df.iloc[-2]
            
            # Conditions
            is_green = today['Close'] > today['Open']
            price_gain = today['Close'] - today['Open']
            is_10_taka_up = price_gain >= 10
            break_prev_high = today['Close'] > yesterday['High']
            volume_up = today['Volume'] > yesterday['Volume']
            
            if is_green and is_10_taka_up and break_prev_high and volume_up:
                selected.append({
                    "Stock": symbol.replace(".NS", ""),
                    "LTP (₹)": round(today['Close'], 2),
                    "Price Gain (₹)": round(price_gain, 2),
                    "Yesterday High (₹)": round(yesterday['High'], 2),
                    "Volume": int(today['Volume'])
                })
        except Exception:
            continue
            
    return selected

# Trigger Scan
with st.spinner("Scanning Stocks..."):
    results = scan_eod_breakouts()

if results:
    st.success(f"Mot {len(results)} ti stock pawa geche!")
    st.dataframe(pd.DataFrame(results), use_container_width=True)
else:
    st.info("Ajke ei formula-y kono stock meleni. Market close hoyar por (bikel 5-ta) 'Refresh Data' button-e click kore check korun.")
