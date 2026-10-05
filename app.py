import streamlit as st
import pandas as pd
import datetime

# NSE ডেটার জন্য nseindia-data লাইব্রেরি
from nse import NSE

# ---------------------------------------------------------
# ১. পেজ কনফিগারেশন
# ---------------------------------------------------------
st.set_page_config(page_title="stockview12", layout="wide")
st.markdown("<h1 style='text-align: center;'>stockview12</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------------------
# ২. NSE Client (caching সহ)
# ---------------------------------------------------------
@st.cache_resource
def get_nse_client():
    return NSE(download_folder="./data")

nse = get_nse_client()

# ---------------------------------------------------------
# ৩. ইনডেক্স ডেটা (Marquee style)
# ---------------------------------------------------------
st.subheader("📊 Live Market Overview")
col1, col2, col3 = st.columns(3)

def get_index_data(index_name):
    try:
        data = nse.get_equities_data_from_index(index_name)
        if data and len(data) > 0:
            # প্রথম স্টকটির ডেটা থেকেই ইনডেক্স লেভেল বের করা যায়
            # অথবা সরাসরি index quote ব্যবহার করতে হবে
            return data
        return None
    except Exception as e:
        return None

# NIFTY 50, SENSEX, BANK NIFTY এর জন্য nse.indices ব্যবহার
try:
    all_indices = nse.get_all_indices()
    # এখানে আপনার প্রয়োজনীয় ইনডেক্স ডেটা ফিল্টার করে নিন
    st.write("Indices loaded:", len(all_indices) if all_indices else 0)
except:
    st.warning("Index data temporarily unavailable")

st.markdown("---")

# ---------------------------------------------------------
# ৪. সম্পূর্ণ স্টক লিস্ট লোড করা
# ---------------------------------------------------------
@st.cache_data(ttl=3600)  # ১ ঘন্টার জন্য cache
def load_all_stocks():
    """NSE-র সম্পূর্ণ স্টক লিস্ট লোড করে (bhavcopy থেকে অথবা API থেকে)"""
    try:
        # পদ্ধতি ১: সব লিস্টেড সিকিউরিটিজ
        # nseindia-data-তে সরাসরি all_stocks নেই, তাই bhavcopy থেকে নিতে হবে
        # অথবা NIFTY 500 + অন্যান্য ইন্ডেক্স থেকে combine করতে হবে
        
        # NIFTY 500 stocks
        nifty500 = nse.get_equities_data_from_index("NIFTY 500")
        
        # অন্যান্য stocks (BSE, mid-cap, small-cap)
        # BSE-র জন্য bseindia লাইব্রেরি আলাদা
        
        stock_list = []
        if nifty500:
            # data structure অনুযায়ী symbol বের করা
            for item in nifty500:
                if isinstance(item, dict) and 'symbol' in item:
                    stock_list.append(item['symbol'])
                elif isinstance(item, str):
                    stock_list.append(item)
        
        return list(set(stock_list))  # duplicate removal
    except Exception as e:
        st.error(f"Error loading stock list: {e}")
        return []

# ---------------------------------------------------------
# ৫. বোলিঙ্গার ব্যান্ড চেক ফাংশন
# ---------------------------------------------------------
def check_bollinger_condition(symbol, timeframe="1d"):
    """
    আপনার শর্ত:
    1. Hammer candle lower line touch করবে না, পরের green candle মাঝখানে কাটবে।
    2. Green candle full body দিয়ে lower line মাঝখানে কাটবে।
    """
    try:
        # NSE থেকে historical data আনা
        # nseindia-data-তে historical data method আছে
        from nse import NSE
        from nse.cache import SimpleCache
        from pathlib import Path
        
        # সরাসরি quote থেকে দাম বের করা (যদি historical না পাওয়া যায়)
        quote = nse.equityQuote(symbol)
        if not quote:
            return False
        
        # এখানে historical data দরকার হবে Bollinger Band হিসাবের জন্য
        # nseindia-data-তে historical data এর method খুঁজে দেখুন
        # অথবা aynse [citation:3] ব্যবহার করুন stock_df() এর জন্য
        
        return False  # placeholder - আসল লজিক নিচে
    except Exception:
        return False

# ---------------------------------------------------------
# ৬. সাইডবার মেনু
# ---------------------------------------------------------
st.sidebar.header("⚙️ Menu")
menu = st.sidebar.radio("Select:", [
    "Add watch List", "Intraday stock", "Short term stock", "Long term stock"
])

# Watchlist
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']

# ---------------------------------------------------------
# ৭. টাইমফ্রেম সিলেকশন
# ---------------------------------------------------------
st.subheader("Time Frame")
time_frame = st.selectbox("Select timeframe for scanning:", 
    ["5m", "10m", "15m", "30m", "1h", "2h", "4h", "1d", "1w", "1mo"])

# ---------------------------------------------------------
# ৮. মেনু অনুযায়ী ডিসপ্লে
# ---------------------------------------------------------
if menu == "Add watch List":
    st.subheader("📋 Manage Watchlist")
    new_symbol = st.text_input("Enter NSE symbol (e.g., RELIANCE, SBIN):")
    if st.button("Add"):
        if new_symbol and new_symbol.upper() not in st.session_state['watchlist']:
            st.session_state['watchlist'].append(new_symbol.upper())
            st.success(f"Added {new_symbol.upper()}")
    
    st.write("Current Watchlist:")
    for sym in st.session_state['watchlist']:
        try:
            quote = nse.equityQuote(sym)
            if quote:
                price = quote.get('close') or quote.get('lastPrice', 'N/A')
                st.write(f"**{sym}**: ₹{price}")
        except:
            st.write(f"**{sym}**: Data unavailable")

elif menu in ["Intraday stock", "Short term stock", "Long term stock"]:
    st.subheader(f"🔍 {menu} Scanner")
    
    # সম্পূর্ণ স্টক লিস্ট লোড
    with st.spinner("Loading complete NSE stock list..."):
        all_stocks = load_all_stocks()
    
    st.write(f"Total stocks in universe: {len(all_stocks)}")
    
    # স্ক্যানিং progress
    if st.button("Start Scanning"):
        progress = st.progress(0)
        matching = []
        
        for i, symbol in enumerate(all_stocks):
            if check_bollinger_condition(symbol, time_frame):
                matching.append(symbol)
            progress.progress((i + 1) / len(all_stocks))
        
        if matching:
            st.success(f"Found {len(matching)} matching stocks!")
            for sym in matching:
                st.write(f"✅ {sym}")
        else:
            st.info("No stocks matched the conditions.")

# ---------------------------------------------------------
# ৯. লাইভ টাইম
# ---------------------------------------------------------
st.sidebar.markdown("---")
now = datetime.datetime.now()
st.sidebar.write(f"**Time:** {now.strftime('%Y-%m-%d %H:%M:%S')}")
