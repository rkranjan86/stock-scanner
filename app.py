import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Stock Scanner Dashboard", layout="wide")

IST = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(IST)

# Top Header
st.title("📈 Daily Stock Breakout Dashboard")
st.caption(f"📅 **Live Time:** `{now_ist.strftime('%d/%m/%Y | %I:%M:%S %p IST')}`")

# 1. Refresh Button
if st.button("🔄 Refresh Data / Scan Now"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# 2. Live Market Indices
st.subheader("📊 Live Market Indices")

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
cols = st.columns(9)
for idx, name in enumerate(indices_info.keys()):
    d = indices_info[name]
    with cols[idx]:
        st.metric(label=name, value=d["price"], delta=f"{d['change']} ({d['pct']}%)")

st.markdown("---")

# 3. Fully Automatic Stock List Fetcher (No manual list)
@st.cache_data(ttl=86400) # Auto refresh stock list once a day
def fetch_automatic_nifty200():
    # Source 1: NSE official CSV repository
    url_primary = "https://raw.githubusercontent.com/indian-stock-market/nifty-csv/main/ind_nifty200list.csv"
    # Source 2: Backup Nifty 200 repository
    url_backup = "https://raw.githubusercontent.com/anandac/nifty200-stocks/main/nifty200.csv"
    
    try:
        df = pd.read_csv(url_primary)
        symbols = [f"{symbol.strip()}.NS" for symbol in df['Symbol']]
        return symbols
    except Exception:
        try:
            df = pd.read_csv(url_backup)
            symbols = [f"{symbol.strip()}.NS" for symbol in df['Symbol']]
            return symbols
        except Exception:
            st.error("Stock list auto-fetch korte somossa hoyeche. Kichu khon por Refresh korun.")
            return []

STOCKS_LIST = fetch_automatic_nifty200()

# 4. Stock Scanner Logic (Exact 4 Rules)
st.subheader(f"🎯 EOD Breakout Stocks (Auto-fetched {len(STOCKS_LIST)} Stocks)")

@st.cache_data(ttl=300)
def scan_eod_breakouts(stocks):
    selected = []
    if not stocks:
        return selected

    data = yf.download(stocks, period="5d", interval="1d", group_by='ticker', progress=False)
    
    for symbol in stocks:
        try:
            df = data[symbol].dropna()
            if len(df) < 2:
                continue
            
            today = df.iloc[-1]
            yesterday = df.iloc[-2]
            
            # Rule 1: Green Candle
            is_green = today['Close'] > today['Open']
            
            # Rule 2: Minimum ₹10 Gain
            price_gain = today['Close'] - today['Open']
            is_10_taka_up = price_gain >= 10
            
            # Rule 3: Today Close > Yesterday High
            break_prev_high = today['Close'] > yesterday['High']
            
            # Rule 4: Today Volume > Yesterday Volume
            volume_up = today['Volume'] > yesterday['Volume']
            
            if is_green and is_10_taka_up and break_prev_high and volume_up:
                selected.append({
                    "Stock": symbol.replace(".NS", ""),
                    "LTP (₹)": round(today['Close'], 2),
                    "Price Gain (₹)": round(price_gain, 2),
                    "Yesterday High (₹)": round(yesterday['High'], 2),
                    "Today Volume": int(today['Volume']),
                    "Yesterday Volume": int(yesterday['Volume'])
                })
        except Exception:
            continue
            
    return selected

with st.spinner("Auto-scanning Nifty 200 Stocks..."):
    results = scan_eod_breakouts(STOCKS_LIST)

if results:
    st.success(f"Mot {len(results)} ti stock pawa geche!")
    st.dataframe(pd.DataFrame(results), use_container_width=True)
else:
    st.info("Ajke ei formula-y kono stock meleni. Market close hoyar por (bikel 5-ta) 'Refresh Data' button-e click korun.")
