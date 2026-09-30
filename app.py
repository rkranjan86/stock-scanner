import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Scanner Dashboard", layout="wide")
st.title("📊 Daily Stock Breakout Dashboard")
st.write("আজকের ৩টি কাস্টম শর্তে ফিল্টার হওয়া NSE স্টকসমূহ")

# NSE-এর প্রধান কয়েকটি স্টক লিস্ট
watchlist = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "TATAMOTORS.NS", "ICICIBANK.NS", 
    "SBIN.NS", "AXISBANK.NS", "BHARTIARTL.NS", "HDFCBANK.NS", "LT.NS"
]

selected_stocks = []

with st.spinner('NSE থেকে ডেটা স্ক্যান করা হচ্ছে...'):
    for symbol in watchlist:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d")
            
            if len(df) >= 2:
                today = df.iloc[-1]
                yesterday = df.iloc[-2]

                # আপনার ৩টি শর্ত:
                is_green = today['Close'] > today['Open']
                breaks_prev_high = today['Close'] > yesterday['High']
                higher_volume = today['Volume'] > yesterday['Volume']

                if is_green and breaks_prev_high and higher_volume:
                    vol_increase = ((today['Volume'] - yesterday['Volume']) / yesterday['Volume']) * 100
                    selected_stocks.append({
                        "Stock Name": symbol.replace(".NS", ""),
                        "Close Price (₹)": round(today['Close'], 2),
                        "Yesterday High (₹)": round(yesterday['High'], 2),
                        "Today Open (₹)": round(today['Open'], 2),
                        "Volume Growth (%)": f"+{round(vol_increase, 1)}%",
                        "Status": "✅ Breakout Confirmed"
                    })
        except Exception as e:
            pass

# ড্যাশবোর্ডে টেবিল আকারে দেখানো
if selected_stocks:
    results_df = pd.DataFrame(selected_stocks)
    
    col1, col2 = st.columns(2)
    col1.metric("মোট স্ক্যান করা স্টক", len(watchlist))
    col2.metric("ফর্মুলায় মিল হওয়া স্টক", len(selected_stocks))
    
    st.subheader("📋 নির্বাচিত স্টকের তালিকা")
    st.dataframe(results_df, use_container_width=True)
else:
    st.info("আজকে কোনো স্টকে এই ফর্মুলা মেলেনি।")