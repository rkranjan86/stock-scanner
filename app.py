import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Bollinger Band Stock Scanner", layout="wide")

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
st.title("📈 Bollinger Band Lower Cut Scanner")
st.caption(f"📅 **Live Time:** `{now_ist.strftime('%d/%m/%Y | %I:%M:%S %p IST')}`")

# 1. Refresh Button
if st.button("🔄 Refresh Data / Scan Now"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# 2. Live Market Indices (Styled Small Boxes)
st.subheader("📊 Live Market Indices")

@st.cache_data(ttl=60)
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

# Helper function to render styled HTML box
def render_index_card(name, d):
    is_positive = d["change"] >= 0
    change_class = "index-change-pos" if is_positive else "index-change-neg"
    sign = "+" if is_positive else ""
    
    html_code = f"""
    <div class="index-box">
        <div class="index-name">{name}</div>
        <div class="index-price">{d['price']:,}</div>
        <div class="{change_class}">{sign}{d['change']} ({sign}{d['pct']}%)</div>
    </div>
    """
    return html_code

# Row 1: 5 Boxes
cols_row1 = st.columns(5)
for i in range(5):
    name = idx_keys[i]
    d = indices_info[name]
    with cols_row1[i]:
        st.markdown(render_index_card(name, d), unsafe_allow_html=True)

# Row 2: 4 Boxes
cols_row2 = st.columns(4)
for i in range(5, 9):
    name = idx_keys[i]
    d = indices_info[name]
    with cols_row2[i - 5]:
        st.markdown(render_index_card(name, d), unsafe_allow_html=True)

st.markdown("---")

# 3. Automatic & Reliable Stock List Fetcher
@st.cache_data(ttl=86400)
def fetch_nifty200_stocks():
    url_primary = "https://raw.githubusercontent.com/indian-stock-market/nifty-csv/main/ind_nifty200list.csv"
    try:
        df = pd.read_csv(url_primary)
        return [f"{symbol.strip()}.NS" for symbol in df['Symbol']]
    except Exception:
        return [
            "ABB.NS", "ACC.NS", "AAVAS.NS", "ABBOTINDIA.NS", "ABCAPITAL.NS", "ABFRL.NS", "ADANIENSOL.NS", 
            "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "ATGL.NS", "AWL.NS", "APLAPOLLO.NS", 
            "ALKEM.NS", "AMBUJACEM.NS", "ANGELONE.NS", "APOLLOHOSP.NS", "APOLLOTYRE.NS", "ASHOKLEY.NS", 
            "ASIANPAINT.NS", "ASTRAL.NS", "ATUL.NS", "AUROPHARMA.NS", "AUBANK.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", 
            "BAJAJFINSV.NS", "BAJFINANCE.NS", "BALKRISIND.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BANKINDIA.NS", 
            "BATAINDIA.NS", "BERGEPAINT.NS", "BEL.NS", "BHARATFORG.NS", "BHEL.NS", "BPCL.NS", "BHARTIARTL.NS", 
            "BIOCON.NS", "BSOFT.NS", "BOSCHLTD.NS", "BRITANNIA.NS", "CANBK.NS", "CGPOWER.NS", "CHAMBLFERT.NS", 
            "CHOLAFIN.NS", "CIPLA.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", "CONCOR.NS", "COROMANDEL.NS", 
            "CROMPTON.NS", "CUMMINSIND.NS", "DABUR.NS", "DALBHARAT.NS", "DEEPAKNTR.NS", "DELHIVERY.NS", 
            "DIVISLAB.NS", "DIXON.NS", "DLF.NS", "LALPATHLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "ESCORTS.NS", 
            "EXIDEIND.NS", "FEDERALBNK.NS", "FACT.NS", "GAIL.NS", "GLENMARK.NS", "GMRAIRPORT.NS", "GODREJCP.NS", 
            "GODREJPROP.NS", "GRASIM.NS", "GUJGASLTD.NS", "HAL.NS", "HAVELLS.NS", "HCLTECH.NS", "HDFCAMC.NS", 
            "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDCOPPER.NS", "HINDPETRO.NS", 
            "HINDUNILVR.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", "IDFCFIRSTB.NS", "INDIANB.NS", 
            "INDIGO.NS", "INDUSINDBK.NS", "INDUSTOWER.NS", "INFY.NS", "IOC.NS", "IRCTC.NS", "IRFC.NS", 
            "IREDA.NS", "IGL.NS", "NAUKRI.NS", "INOXWIND.NS", "ITC.NS", "JINDALSTEL.NS", "JIOFIN.NS", 
            "JSWENERGY.NS", "JSWSTEEL.NS", "JUBLFOOD.NS", "KALYANKJIL.NS", "KEI.NS", "KOTAKBANK.NS", 
            "KPITTECH.NS", "LTF.NS", "LTTS.NS", "LICHSGFIN.NS", "LICI.NS", "LTIM.NS", "LT.NS", "LUPIN.NS", 
            "M&M.NS", "M&MFIN.NS", "MARICO.NS", "MARUTI.NS", "MAXHEALTH.NS", "MAZDOCK.NS", "METROPOLIS.NS", 
            "MFSL.NS", "MGL.NS", "MSUMI.NS", "MPHASIS.NS", "MRF.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", 
            "NESTLEIND.NS", "NHPC.NS", "NMDC.NS", "NTPC.NS", "NYKAA.NS", "OBEROIRLTY.NS", "ONGC.NS", 
            "OIL.NS", "PAYTM.NS", "OFSS.NS", "POLICYBZR.NS", "PIIND.NS", "PAGEIND.NS", "PERSISTENT.NS", 
            "PETRONET.NS", "PFC.NS", "PIDILITIND.NS", "PNB.NS", "POLYCAB.NS", "POONAWALLA.NS", "POWERGRID.NS", 
            "PRESTAGE.NS", "PVRINOX.NS", "RAMCOCEM.NS", "RCF.NS", "RECLTD.NS", "RELIANCE.NS", "RVNL.NS", 
            "SAIL.NS", "SBICARD.NS", "SBILIFE.NS", "SBIN.NS", "SHREECEM.NS", "SHRIRAMFIN.NS", "SIEMENS.NS", 
            "SJVN.NS", "SONACOMS.NS", "SRF.NS", "SUNPHARMA.NS", "SUNTV.NS", "SUZLON.NS", "SYNGENE.NS", 
            "TATACOMM.NS", "TATACONSUM.NS", "TATAELXSI.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", 
            "TATATECH.NS", "TCS.NS", "TECHM.NS", "TITAN.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS", 
            "TVSMOTOR.NS", "ULTRACEMCO.NS", "UNIONBANK.NS", "UPL.NS", "VBL.NS", "VEDL.NS", "IDEA.NS", 
            "VOLTAS.NS", "WIPRO.NS", "YESBANK.NS", "ZEEL.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"
        ]

STOCKS_LIST = fetch_nifty200_stocks()

# 4. Bollinger Band Lower Band Body Cut Logic
st.subheader("🎯 Bollinger Lower Band Body Cut Stocks")

@st.cache_data(ttl=300)
def scan_bollinger_reversal(stocks):
    selected = []
    if not stocks:
        return selected

    try:
        data = yf.download(stocks, period="30d", interval="1d", group_by='ticker', progress=False)
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
            
            # Bollinger Bands (20 Period, 2 Std Dev)
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['Lower_Band'] = df['SMA20'] - (df['STD20'] * 2)
            
            today = df.iloc[-1]
            
            # 1. Green Candle (Close > Open)
            is_green = today['Close'] > today['Open']
            
            # 2. Open price was BELOW Lower Band
            open_below_band = today['Open'] < today['Lower_Band']
            
            # 3. Close price is ABOVE Lower Band (Body cuts through the band)
            close_above_band = today['Close'] > today['Lower_Band']
            
            if is_green and open_below_band and close_above_band:
                selected.append({
                    "Stock": symbol.replace(".NS", ""),
                    "LTP (₹)": round(today['Close'], 2),
                    "Open (₹)": round(today['Open'], 2),
                    "Lower Band (₹)": round(today['Lower_Band'], 2),
                    "Volume": int(today['Volume'])
                })
        except Exception:
            continue
            
    return selected

with st.spinner("Scanning Stocks..."):
    results = scan_bollinger_reversal(STOCKS_LIST)

if results:
    st.success(f"Mot {len(results)} ti stock pawa geche jekhane Green Candle Body Bollinger Lower Band-ke majhamaji keteiyeche!")
    st.dataframe(pd.DataFrame(results), use_container_width=True)
else:
    st.info("Ajke kono stock-e Green Candle Body Bollinger Lower Band-ke majhamaji kete beroyni. Market close hoyar por (bikel 5-ta) 'Refresh Data' button-e click korun.")
