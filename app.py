import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

# ---------------------------------------------------------
# ১. পেজ কনফিগারেশন ও হেডিং
# ---------------------------------------------------------
st.set_page_config(
    page_title="stockview12",
    layout="wide",
    page_icon="📈"
)

st.markdown(
    "<h1 style='text-align: center; color: #1f77b4;'>stockview12</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

# ---------------------------------------------------------
# ২. হেল্পার ফাংশন (ইনডেক্স ডেটা নিরাপদভাবে বের করার জন্য)
# ---------------------------------------------------------
def get_live_index_data(ticker_symbol, index_name):
    """
    yfinance থেকে ইনডেক্সের সর্বশেষ দাম ও পরিবর্তন বের করে।
    কোনো সমস্যা হলে 'N/A' ফেরত দেয় যাতে অ্যাপ ক্র্যাশ না করে।
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        # ১ দিনের ডেটা থেকে শেষ ক্লোজিং প্রাইস বের করা
        hist = ticker.history(period="1d")
        if hist.empty:
            return {"price": "N/A", "change": "N/A", "name": index_name}
        
        last_price = hist['Close'].iloc[-1]
        
        # আগের ক্লোজিং প্রাইস বের করা (পরিবর্তন % হিসাবের জন্য)
        prev_hist = ticker.history(period="5d")
        if len(prev_hist) > 1:
            prev_close = prev_hist['Close'].iloc[-2]
            change_pct = ((last_price - prev_close) / prev_close) * 100
        else:
            change_pct = 0.0

        return {
            "price": f"{last_price:,.2f}",
            "change": f"{change_pct:+.2f}%",
            "name": index_name
        }
    except Exception as e:
        return {"price": "N/A", "change": "N/A", "name": index_name}

# ---------------------------------------------------------
# ৩. ইনডেক্স ডেটা স্কোরিং (Marquee টাইপ ডিসপ্লে)
# ---------------------------------------------------------
st.subheader("📊 Live Market Overview")

col1, col2, col3 = st.columns(3)

# ইনডেক্স টিকার সিম্বল (Yahoo Finance স্ট্যান্ডার্ড)
NIFTY_TICKER = "^NSEI"
SENSEX_TICKER = "^BSESN"
BANKNIFTY_TICKER = "^NSEBANK"

nifty_data = get_live_index_data(NIFTY_TICKER, "NIFTY 50")
sensex_data = get_live_index_data(SENSEX_TICKER, "SENSEX")
banknifty_data = get_live_index_data(BANKNIFTY_TICKER, "NIFTY BANK")

with col1:
    st.metric(
        label="NIFTY 50",
        value=nifty_data["price"],
        delta=nifty_data["change"]
    )

with col2:
    st.metric(
        label="SENSEX",
        value=sensex_data["price"],
        delta=sensex_data["change"]
    )

with col3:
    st.metric(
        label="NIFTY BANK",
        value=banknifty_data["price"],
        delta=banknifty_data["change"]
    )

st.markdown("---")

# ---------------------------------------------------------
# ৪. সাইডবার মেনু এবং ওয়াচলিস্ট
# ---------------------------------------------------------
st.sidebar.header("⚙️ Menu")

menu_options = [
    "Add watch List",
    "Intraday stock",
    "Short term stock",
    "Long term stock"
]
menu = st.sidebar.radio("Select Option:", menu_options)

# ওয়াচলিস্ট ডিফল্ট স্টক
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']

# ---------------------------------------------------------
# ৫. ওয়াচলিস্ট ও স্টক স্ক্যানিং লজিক
# ---------------------------------------------------------

# বোলিঙ্গার ব্যান্ড কন্ডিশন চেক করার ফাংশন
def check_bollinger_conditions(symbol, timeframe="1d"):
    """
    শর্ত ১: হ্যামার ক্যান্ডেল নিচের লাইন টাচ করবে না, কিন্তু পরের ক্যান্ডেল মাঝখানে কাটবে।
    শর্ত ২: নিচের লাইনে ফুল বডি গ্রীন ক্যান্ডেল।
    """
    try:
        # yfinance থেকে ডেটা আনা (timeframe অনুযায়ী)
        # দ্রষ্টব্য: yfinance-এ 5m, 15m ইত্যাদি ইন্ট্রাডে ডেটা সর্বোচ্চ 60 দিনের জন্য পাওয়া যায়।
        period_map = {
            "5m": "5d", "10m": "5d", "15m": "5d", "30m": "5d",
            "1h": "1mo", "2h": "1mo", "4h": "1mo",
            "1d": "3mo", "1w": "1y", "1mo": "1y"
        }
        interval_map = {
            "5m": "5m", "10m": "10m", "15m": "15m", "30m": "30m",
            "1h": "1h", "2h": "2h", "4h": "4h",
            "1d": "1d", "1w": "1wk", "1mo": "1mo"
        }
        
        period = period_map.get(timeframe, "3mo")
        interval = interval_map.get(timeframe, "1d")
        
        # yfinance-এ ইন্ট্রাডে ডেটা পাওয়ার সীমাবদ্ধতা আছে
        if interval in ["10m", "2h", "4h"]:
            # yfinance-এ 10m, 2h, 4h সরাসরি সাপোর্ট নেই, তাই resample করতে হবে
            base_interval = "5m" if interval == "10m" else "1h"
            df = yf.download(symbol, period=period, interval=base_interval, progress=False, auto_adjust=False)
            if df.empty:
                return False
            # resampling
            rule = "10min" if interval == "10m" else ("2h" if interval == "2h" else "4h")
            df = df.resample(rule).agg({
                'Open': 'first', 'High': 'max', 'Low': 'min',
                'Close': 'last', 'Volume': 'sum'
            }).dropna()
        else:
            df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)

        if df.empty or len(df) < 20:
            return False

        # কলামের নাম ফ্ল্যাট করা (yfinance কিছু ক্ষেত্রে মাল্টি-লেভেল কলাম দেয়)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # বোলিঙ্গার ব্যান্ড (20, 2) হিসাব
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['STD'] = df['Close'].rolling(window=20).std()
        df['Upper'] = df['MA20'] + (df['STD'] * 2)
        df['Lower'] = df['MA20'] - (df['STD'] * 2)

        # শেষ দুইটি ক্যান্ডেল নেওয়া
        if len(df) < 2:
            return False
        
        prev_candle = df.iloc[-2]
        curr_candle = df.iloc[-1]

        # শর্ত ২: বর্তমান ক্যান্ডেল গ্রীন এবং ফুল বডি, নিচের লাইনকে মাঝখানে কাটে
        is_green = curr_candle['Close'] > curr_candle['Open']
        body_size = abs(curr_candle['Close'] - curr_candle['Open'])
        shadow_upper = curr_candle['High'] - max(curr_candle['Open'], curr_candle['Close'])
        shadow_lower = min(curr_candle['Open'], curr_candle['Close']) - curr_candle['Low']
        
        # ফুল বডি: শ্যাডো বডির ৫০% এর কম
        is_full_body = (shadow_upper < body_size * 0.5) and (shadow_lower < body_size * 0.5)
        
        # নিচের লাইনকে মাঝখানে কাটে (Open নিচে, Close উপরে)
        cuts_lower = (curr_candle['Open'] < curr_candle['Lower']) and (curr_candle['Close'] > curr_candle['Lower'])

        if is_green and is_full_body and cuts_lower:
            return True

        # শর্ত ১: আগের ক্যান্ডেল হ্যামার, বর্তমান ক্যান্ডেল গ্রীন এবং নিচের লাইন কাটে
        is_hammer = (prev_candle['Low'] <= prev_candle['Lower']) and (prev_candle['Close'] > prev_candle['Lower'])
        if is_hammer and is_green and (curr_candle['Close'] > curr_candle['Lower']):
            return True

        return False

    except Exception:
        return False

# ---------------------------------------------------------
# ৬. মেনু অনুযায়ী ডিসপ্লে লজিক
# ---------------------------------------------------------

if menu == "Add watch List":
    st.subheader("📋 Manage Watchlist")
    new_symbol = st.text_input("Enter NSE symbol (e.g., RELIANCE.NS):")
    if st.button("Add to Watchlist"):
        if new_symbol and new_symbol not in st.session_state['watchlist']:
            st.session_state['watchlist'].append(new_symbol)
            st.success(f"Added {new_symbol} to watchlist")
    
    st.write("**Current Watchlist:**")
    for sym in st.session_state['watchlist']:
        try:
            # ওয়াচলিস্টের জন্য লাইভ প্রাইস আনা
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                st.write(f"- {sym}: ₹{price:,.2f}")
            else:
                st.write(f"- {sym}: Data unavailable")
        except:
            st.write(f"- {sym}: Error fetching data")

elif menu in ["Intraday stock", "Short term stock", "Long term stock"]:
    st.subheader(f"🔍 {menu} Scanner")
    
    # টাইমফ্রেম সিলেকশন (শুধুমাত্র স্ক্যানিংয়ের জন্য)
    time_frame = st.selectbox(
        "Select Time Frame for Scanning:",
        ["5m", "10m", "15m", "30m", "1h", "2h", "4h", "1d", "1w", "1mo"]
    )
    
    # স্টক ইউনিভার্স (সিম্পল উদাহরণ - কিছু জনপ্রিয় স্টক)
    # বাস্তবে NIFTY 50, 200, 500 এর সম্পূর্ণ লিস্ট ব্যবহার করতে হবে
    if menu == "Intraday stock":
        universe = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS']
    elif menu == "Short term stock":
        universe = ['SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS', 'LT.NS']
    else: # Long term stock
        universe = ['HINDUNILVR.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'NESTLEIND.NS']

    st.write(f"**Scanning {len(universe)} stocks for Bollinger Band conditions...**")
    
    matching_stocks = []
    progress_bar = st.progress(0)
    
    for idx, symbol in enumerate(universe):
        if check_bollinger_conditions(symbol, time_frame):
            matching_stocks.append(symbol)
        progress_bar.progress((idx + 1) / len(universe))
    
    st.write("---")
    if matching_stocks:
        st.success(f"Found {len(matching_stocks)} matching stocks:")
        for sym in matching_stocks:
            try:
                ticker = yf.Ticker(sym)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                    st.write(f"✅ **{sym}** - ₹{price:,.2f}")
            except:
                st.write(f"✅ **{sym}** - Data fetching error")
    else:
        st.info("No stocks matched the Bollinger Band conditions in the selected timeframe.")

# ---------------------------------------------------------
# ৭. ফুটার - লাইভ ডেট টাইম
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.write("**🕒 Live Date & Time (IST):**")
ist_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
st.sidebar.write(ist_now.strftime("%Y-%m-%d %H:%M:%S"))

# ---------------------------------------------------------
# ৮. রিকোয়ারমেন্টস (এই লাইনগুলো সেভ করার দরকার নেই, শুধু রেফারেন্সের জন্য)
# ---------------------------------------------------------
# requirements.txt:
# streamlit
# yfinance
# pandas
# numpy
