import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Breakout Scanner", layout="wide")

st.title("📈 Daily Stock Breakout Dashboard")
st.caption("Nifty 200 Stocks Filtered by Price & Volume Rules")

# 1. Automatic Refresh Button
if st.button("🔄 Refresh Data / Scan Now"):
    st.cache_data.clear()

# 2. Fetch Nifty 200 Stock List from GitHub
@st.cache_data(ttl=300)  # 5 minute cache
def get_nifty200_symbols():
    url = "https://raw.githubusercontent.com/indian-stock-market/nifty-csv/main/ind_nifty200list.csv"
    try:
        df = pd.read_csv(url)
        symbols = [f"{symbol}.NS" for symbol in df['Symbol']]
        return symbols
    except Exception as e:
        st.error("Nifty 200 stock list fetch korte somossha hoyeche.")
        return []

symbols = get_nifty200_symbols()

# 3. Main Scanning Function
def scan_stocks():
    selected_stocks = []
    
    if not symbols:
        return selected_stocks
    
    # Download 5 days data for all stocks at once
    data = yf.download(symbols, period="5d", interval="1d", group_by='ticker', progress=False)
    
    for symbol in symbols:
        try:
            df = data[symbol].dropna()
            if len(df) < 2:
                continue
            
            today = df.iloc[-1]
            yesterday = df.iloc[-2]
            
            # ----------------------------------------------------
            # FORMULA / CONDITIONS
            # ----------------------------------------------------
            # 1. Price change +10 taka or more (Close >= Open + 10)
            is_10_taka_up = (today['Close'] - today['Open']) >= 10
            
            # 2. Breakout (Today Close > Yesterday High)
            breaks_prev_high = today['Close'] > yesterday['High']
            
            # 3. Volume confirmation (Today Volume > Yesterday Volume)
            higher_volume = today['Volume'] > yesterday['Volume']
            
            # Filter condition check
            if is_10_taka_up and breaks_prev_high and higher_volume:
                price_diff = today['Close'] - today['Open']
                selected_stocks.append({
                    "Stock": symbol.replace(".NS", ""),
                    "LTP (Taka)": round(today['Close'], 2),
                    "Today Move (Taka)": round(price_diff, 2),
                    "Yesterday High": round(yesterday['High'], 2),
                    "Volume": int(today['Volume'])
                })
        except Exception:
            continue
            
    return selected_stocks

# 4. Display Results
with st.spinner("Scanning Nifty 200 stocks..."):
    results = scan_stocks()

if results:
    st.success(f"Mot {len(results)} ti stock pawa geche!")
    result_df = pd.DataFrame(results)
    st.dataframe(result_df, use_container_width=True)
else:
    st.info("Ajke ei formula-y kono stock meleni. Market cholar shomoy 'Refresh Data' button-e click korun.")
