import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import numpy as np
from indian_stock_market import NSE

# 1. INITIALIZATION & CONFIG
st.set_page_config(page_title="stockview12", layout="wide")
st.markdown("<h1 style='text-align: center;'>stockview12</h1>", unsafe_allow_html=True)

nse = NSE()

# 2. SIDEBAR MENU (Watchlist, Intraday, etc.)
st.sidebar.header("Menu")
menu_options = ["Add watch List", "Intraday stock", "Short term stock", "Long term stock"]
menu = st.sidebar.radio("Select a menu:", menu_options)

# Placeholder for storing watchlist (simple session state)
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = ['RELIANCE', 'TCS', 'INFY']

# 3. TICKER (Marquee) for Nifty, Sensex, Nifty Bank
st.markdown("---")
col1, col2, col3 = st.columns(3)
# Example: Fetching indices - Note: Indices are usually accessed via NSE
nifty_data = nse.get_trade_info("NIFTY 50")
sensex_data = nse.get_trade_info("SENSEX") # Or via BSE
bank_nifty = nse.get_trade_info("BANKNIFTY")

with col1:
    st.markdown(f"**NIFTY:** {nifty_data['lastPrice']} (Change: {nifty_data['change']}%)")
with col2:
    st.markdown(f"**SENSEX:** {sensex_data['lastPrice']} (Change: {sensex_data['change']}%)")
with col3:
    st.markdown(f"**NIFTY BANK:** {bank_nifty['lastPrice']} (Change: {bank_nifty['change']}%)")
st.markdown("---")

# 4. TIME FRAME SELECTOR
st.subheader("Time Frame")
time_frame = st.selectbox("Select time frame:", 
                          ["5m", "10m", "15m", "30m", "1h", "2h", "4h", "1d", "1w", "1mo"])

# 5. SCANNING LOGIC
# This function calculates the indicators and checks conditions.
def check_bollinger_conditions(symbol, timeframe):
    # Fetch OHLC data from the library
    # Note: The NSE library has get_ohlc_data method
    df = nse.get_ohlc_data(symbol, timeframe=timeframe, is_index=False)
    
    if df is None or df.empty:
        return False
    
    # Calculate Bollinger Bands (20 period, 2 standard deviations)
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['std'] = df['close'].rolling(window=20).std()
    df['Upper'] = df['MA20'] + (df['std'] * 2)
    df['Lower'] = df['MA20'] - (df['std'] * 2)
    
    # --- Conditions (The logic for your screenshots) ---
    
    # Condition 1: Hammer candle does not touch the lower line, 
    # and the next green candle fully cuts the lower line in the middle.
    # Condition 2: A green candle with a full body cuts the lower line in the middle.
    
    # Example of logic to implement:
    prev_candle = df.iloc[-2]
    current_candle = df.iloc[-1]
    
    # Condition 2 Check: Body cuts the lower line in the middle
    # Green candle: close > open. Full body: high is close, low is open (or minimal shadows).
    # "cuts the lower line in the middle" means the candle's body (or the wick if a hammer) 
    # extends from below to above the lower band.
    is_green_candle = current_candle['close'] > current_candle['open']
    has_minimal_shadows = (current_candle['high'] - max(current_candle['open'], current_candle['close'])) < (abs(current_candle['close'] - current_candle['open'])) * 0.5
    cuts_lower_band = (current_candle['low'] < current_candle['Lower']) and (current_candle['close'] > current_candle['Lower'])
    
    if is_green_candle and cuts_lower_band and has_minimal_shadows:
        return True
    
    # Condition 1 Check: Hammer near lower band
    # The hammer's low should be near the lower band, but the close should be above the band.
    # The next candle (current) should be a green candle whose body cuts the band.
    if (current_candle['close'] > current_candle['open']) and (prev_candle['low'] <= prev_candle['Lower']) and (prev_candle['close'] > prev_candle['Lower']):
        return True
    
    return False

# 6. STOCK UNIVERSE & DISPLAY
# You need a function to get NIFTY 50, 200, 500 stocks, plus BSE stocks.
# The library provides this: nse.get_equities_data_from_index("NIFTY 50")
# For a full list, you can combine multiple indices and use BSE data.

if menu in ["Intraday stock", "Short term stock", "Long term stock"]:
    st.subheader(f"Results for {menu}")
    
    # Define stock universe based on selection (simple example)
    universe = []
    if menu == "Intraday stock":
         # Fetch list of NIFTY 50 stocks as a placeholder
        universe = nse.get_equities_data_from_index("NIFTY 50")
    elif menu == "Short term stock":
        universe = nse.get_equities_data_from_index("NIFTY 200")
    elif menu == "Long term stock":
        universe = nse.get_equities_data_from_index("NIFTY 500")
    
    # Scan the universe
    matching_stocks = []
    for symbol in universe:
        # This loop would hit rate limits if you do it all at once.
        # In a real app, you should cache or run this in a background process.
        if check_bollinger_conditions(symbol, time_frame):
            matching_stocks.append(symbol)
            # Add LTP data
            ltp = nse.get_trade_info(symbol)
            st.write(f"{symbol}: {ltp['lastPrice']} - Change: {ltp['change']}%")

elif menu == "Add watch List":
    st.subheader("Manage Watchlist")
    symbol_to_add = st.text_input("Enter NSE/BSE symbol to add:")
    if st.button("Add"):
        if symbol_to_add and symbol_to_add not in st.session_state['watchlist']:
            st.session_state['watchlist'].append(symbol_to_add)
            st.success(f"Added {symbol_to_add}")
    
    st.write("Current Watchlist:")
    # Display watchlist with real-time prices
    for symbol in st.session_state['watchlist']:
        ltp = nse.get_trade_info(symbol)
        st.write(f"{symbol}: {ltp['lastPrice']} - Change: {ltp['change']}%")

# 7. LIVE DATE AND TIME
st.sidebar.markdown("---")
st.sidebar.write("**Live Date & Time:**")
st.sidebar.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
