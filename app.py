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
st.subheader("⚙️ Scanner Settings")

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

# Complete NIFTY 50 Stock List
NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS",
    "BHARTIARTL.NS", "LTIM.NS", "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS", "HCLTECH.NS", "BAJFINANCE.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "TATAMOTORS.NS", "NTPC.NS",
    "ONGC.NS", "POWERGRID.NS", "ADANIENT.NS", "ADANIPORTS.NS", "COALINDIA.NS", "BAJAJFINSV.NS", "TATASTEEL.NS",
    "M&M.NS", "NESTLEIND.NS", "GRASIM.NS", "TECHM.NS", "HEROMOTOCO.NS", "CIPLA.NS", "WIPRO.NS", "HDFCLIFE.NS",
    "BPCL.NS", "EICHERMOT.NS", "DRREDDY.NS", "DIVISLAB.NS", "TATACONSUM.NS", "SBILIFE.NS", "BAJAJ-AUTO.NS",
    "BRITANNIA.NS", "INDUSINDBK.NS", "HINDALCO.NS", "JSWSTEEL.NS", "APOLLOHOSP.NS", "UPL.NS"
]

# Complete NIFTY 500 Stock List (Stored Directly)
NIFTY_500 = [
    "3MINDIA.NS", "ABB.NS", "ACC.NS", "AAVAS.NS", "ABBOTINDIA.NS", "ABCAPITAL.NS", "ABFRL.NS", "ADANIENSOL.NS", 
    "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "ATGL.NS", "AWL.NS", "AEGISCHEM.NS", 
    "AETHER.NS", "AFFLE.NS", "AJANTPHARM.NS", "APLAPOLLO.NS", "ALKEM.NS", "ALKYLAMIN.NS", "ALLCARGO.NS", 
    "ALOKINDS.NS", "AMBER.NS", "AMBUJACEM.NS", "ANGELONE.NS", "ANURAS.NS", "APARINDS.NS", "APOLLOHOSP.NS", 
    "APOLLOTYRE.NS", "APTUS.NS", "ACI.NS", "ASAHIINDIA.NS", "ASHOKLEY.NS", "ASIANPAINT.NS", "ASTERDM.NS", 
    "ASTRAL.NS", "ATUL.NS", "AUROPHARMA.NS", "AUBANK.NS", "AVANTIFEED.NS", "AXISBANK.NS", "BACIL.NS", 
    "BAJAJ-AUTO.NS", "BAJAJELEC.NS", "BAJAJFINSV.NS", "BAJFINANCE.NS", "BAJAJHLDNG.NS", "BALAMINES.NS", 
    "BALKRISIND.NS", "BALRAMCHIN.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BANKINDIA.NS", "MAHABANK.NS", 
    "BATAINDIA.NS", "BAYERCROP.NS", "BERGEPAINT.NS", "BDL.NS", "BEL.NS", "BHARATFORG.NS", "BHEL.NS", 
    "BPCL.NS", "BHARTIARTL.NS", "BIOCON.NS", "BIRLACORPN.NS", "BSOFT.NS", "BLISSGVS.NS", "BLUEDART.NS", 
    "BLUESTARCO.NS", "BOSCHLTD.NS", "BRIGADE.NS", "BRITANNIA.NS", "MAPMYINDIA.NS", "CAMPUS.NS", "CANFINHOME.NS", 
    "CANBK.NS", "CAPLIPOINT.NS", "CGPOWER.NS", "CARBORUNIV.NS", "CASTROLIND.NS", "CEATLTD.NS", "CENTRALBK.NS", 
    "CDSL.NS", "CENTURYPLY.NS", "CENTURYTEX.NS", "CERA.NS", "CHAMBLFERT.NS", "CHEMSCON.NS", "CHENAITH.NS", 
    "CHOLAHLDNG.NS", "CHOLAFIN.NS", "CIPLA.NS", "CLEAN.NS", "COALINDIA.NS", "COCHINSHIP.NS", "COFORGE.NS", 
    "COLPAL.NS", "CAMS.NS", "CONCOR.NS", "COROMANDEL.NS", "CRAFTSMAN.NS", "CREDITACC.NS", "CROMPTON.NS", 
    "CUMMINSIND.NS", "CYIENT.NS", "DABUR.NS", "DALBHARAT.NS", "DATAPATTE.NS", "DEEPAKFERT.NS", "DEEPAKNTR.NS", 
    "DELHIVERY.NS", "DEVYANI.NS", "DIVISLAB.NS", "DIXON.NS", "DLF.NS", "LALPATHLAB.NS", "DRREDDY.NS", 
    "EIDPARRY.NS", "EIHOTEL.NS", "EASEMYTRIP.NS", "EICHERMOT.NS", "ELGIEQUIP.NS", "EMAMILTD.NS", "ENDURANCE.NS", 
    "ENGINERSIN.NS", "EQUITASBNK.NS", "ERIS.NS", "ESCORTS.NS", "EXIDEIND.NS", "FDC.NS", "FEDERALBNK.NS", 
    "FACT.NS", "FINEORG.NS", "FINCABLES.NS", "FINPIPE.NS", "FSL.NS", "FIVESTAR.NS", "FORTIS.NS", "GRINFRA.NS", 
    "GAIL.NS", "GALAXYSURF.NS", "GARFIBRES.NS", "GMDCLTD.NS", "GATEWAY.NS", "GLAND.NS", "GLAXO.NS", 
    "GLENMARK.NS", "MEDANTA.NS", "GMRAIRPORT.NS", "GOCLCORP.NS", "GODFRYPHLP.NS", "GODREJCP.NS", "GODREJIND.NS", 
    "GODREJPROP.NS", "GRANULES.NS", "GRAPHITE.NS", "GRASIM.NS", "GESHIP.NS", "GREAVESCOT.NS", "GRINDWELL.NS", 
    "GUJGASLTD.NS", "GMDCLTD.NS", "GNFC.NS", "GPPL.NS", "GSFC.NS", "GSPL.NS", "HEG.NS", "HCLTECH.NS", 
    "HDFCAMC.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HFCL.NS", "HAPPSTMNDS.NS", "HAVELLS.NS", "HEROMOTOCO.NS", 
    "HIMATSEIDE.NS", "HINDCOPPER.NS", "HINDPETRO.NS", "HINDUNILVR.NS", "HINDZINC.NS", "POWERGRID.NS", 
    "HOMEFIRST.NS", "HONAUT.NS", "HUDCO.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", "ISEC.NS", 
    "IDBI.NS", "IDFCFIRSTB.NS", "IDFC.NS", "IFCI.NS", "IIFL.NS", "IRB.NS", "IRCON.NS", "ITC.NS", "ITI.NS", 
    "INDIACEM.NS", "INDIAMART.NS", "INDIANB.NS", "IEX.NS", "INDHOTEL.NS", "IOC.NS", "IRCTC.NS", "IRFC.NS", 
    "IREDA.NS", "IGL.NS", "INDUSTOWER.NS", "INDUSINDBK.NS", "NAUKRI.NS", "INFIBEAM.NS", "INFY.NS", "INGERRAND.NS", 
    "INOXWIND.NS", "INTELLECT.NS", "INDIGO.NS", "IPCALAB.NS", "JBCHEPHARM.NS", "JKCEMENT.NS", "JBMA.NS", 
    "JKLAKSHMI.NS", "JKPAPER.NS", "JMFINANCIL.NS", "JSWENERGY.NS", "JSWINFRA.NS", "JSWSTEEL.NS", "JAMNAAUTO.NS", 
    "JINDALSAW.NS", "JSL.NS", "JINDALSTEL.NS", "JIOFIN.NS", "JUBLFOOD.NS", "JUBLINGREA.NS", "JUBLPHARMA.NS", 
    "JUSTDIAL.NS", "JYOTHYLAB.NS", "KPRMILL.NS", "KEI.NS", "KNRCON.NS", "KPITTECH.NS", "KRBL.NS", "KSB.NS", 
    "KAJARIACER.NS", "KPIL.NS", "KALYANKJIL.NS", "KANSAINER.NS", "KARURVYSYA.NS", "KEC.NS", "KIRLOSENG.NS", 
    "KOTAKBANK.NS", "L&TFH.NS", "LTTS.NS", "LICHSGFIN.NS", "LICI.NS", "LTIM.NS", "LT.NS", "LATENTVIEW.NS", 
    "LAURUSLABS.NS", "LXCHEM.NS", "LEMONTREE.NS", "LINDEINDIA.NS", "LUPIN.NS", "MMTC.NS", "MRF.NS", "MTARTECH.NS", 
    "LODHA.NS", "MGL.NS", "MAHSEAMLES.NS", "M&MFIN.NS", "M&M.NS", "MHRIL.NS", "MAHINDCIE.NS", "MANAPPURAM.NS", 
    "MRPL.NS", "MARICO.NS", "MARUTI.NS", "MASTEK.NS", "MAXHEALTH.NS", "MAZDOCK.NS", "MEDPLUS.NS", "METROPOLIS.NS", 
    "MFSL.NS", "MINDACORP.NS", "MSUMI.NS", "MOTILALOFS.NS", "MPHASIS.NS", "MCX.NS", "MUTHOOTFIN.NS", "NATCOPHARM.NS", 
    "NATIONALUM.NS", "NAVINFLUOR.NS", "NAZARA.NS", "NESTLEIND.NS", "NETWORK18.NS", "NHPC.NS", "NLCINDIA.NS", 
    "NMDC.NS", "NTPC.NS", "NH.NS", "NUVAMA.NS", "NYKAA.NS", "OBEROIRLTY.NS", "ONGC.NS", "OIL.NS", "OLECTRA.NS", 
    "PAYTM.NS", "OFSS.NS", "ORIENTELEC.NS", "POLICYBZR.NS", "PCBL.NS", "PIIND.NS", "PNBHOUSING.NS", "PNCINFRA.NS", 
    "PVRINOX.NS", "PAGEIND.NS", "PATANJALI.NS", "PERSISTENT.NS", "PETRONET.NS", "PFC.NS", "PHOENIXLTD.NS", 
    "PIDILITIND.NS", "PEL.NS", "PPLPHARMA.NS", "POLYMED.NS", "POLYCAB.NS", "POONAWALLA.NS", "PFC.NS", 
    "POWERGRID.NS", "PRAJIND.NS", "PRESTIGE.NS", "PRINCEPIPE.NS", "PRSMJOHNSN.NS", "PGHL.NS", "PGHH.NS", 
    "PNB.NS", "QUESS.NS", "RRKABEL.NS", "RBLBANK.NS", "REC.NS", "RITES.NS", "RADICO.NS", "RVNL.NS", "RAILTEL.NS", 
    "RAIN.NS", "RAINBOW.NS", "RAMCOCEM.NS", "RCF.NS", "RATNAMANI.NS", "RAYMOND.NS", "RELIANCE.NS", "RELIGARE.NS", 
    "RITES.NS", "ROSSARI.NS", "ROUTE.NS", "SBFC.NS", "SBICARD.NS", "SBILIFE.NS", "SJVN.NS", "SKFINDIA.NS", 
    "SRF.NS", "SAFARI.NS", "MOTHERSON.NS", "SAPPHIRE.NS", "SARDAEN.NS", "SAREGAMA.NS", "SCHAEFFLER.NS", 
    "SCHNEIDER.NS", "SCI.NS", "SHARDACROP.NS", "SNC.NS", "SHOPERSTOP.NS", "SHREERENUK.NS", "SHREECEM.NS", 
    "SHRIRAMFIN.NS", "SHYAMMETL.NS", "SIEMENS.NS", "SOBHA.NS", "SOLARINDS.NS", "SONACOMS.NS", "SONATSOFTW.NS", 
    "STARHEALTH.NS", "SBIN.NS", "SAIL.NS", "SWSOLAR.NS", "SUMICHEM.NS", "SPARC.NS", "SUNPHARMA.NS", "SUNTV.NS", 
    "SUNDARMFIN.NS", "SUNDRMFAST.NS", "SUNTECK.NS", "SUPRAJIT.NS", "SUPREMEIND.NS", "SUVENPHAR.NS", "SUZLON.NS", 
    "SYNGENE.NS", "SYRMA.NS", "TBOX.NS", "TV18BRDCST.NS", "TVSMOTOR.NS", "TANLA.NS", "TATACOMM.NS", "TATACONSUM.NS", 
    "TATAELXSI.NS", "TATAMTRDVR.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TATATECH.NS", "TTML.NS", 
    "TCS.NS", "TECHM.NS", "TEJASNET.NS", "NIACL.NS", "RAMCOIND.NS", "THERMAX.NS", "THYROCARE.NS", "TIINDIA.NS", 
    "TIMKEN.NS", "TITAN.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS", "TRIDENT.NS", "TRIVENI.NS", 
    "TRITURBINE.NS", "UBOX.NS", "UCOBANK.NS", "UNOMINDA.NS", "UPL.NS", "UTIAMC.NS", "ULTRACEMCO.NS", "UNIONBANK.NS", 
    "UBL.NS", "MCDOWELL-N.NS", "VGUARD.NS", "VMART.NS", "VIPIND.NS", "VAIBHAVGBL.NS", "VTL.NS", "VARROC.NS", 
    "VBL.NS", "MANYAVAR.NS", "VEDL.NS", "VENKEYS.NS", "VIJAYA.NS", "VINATIORGA.NS", "IDEA.NS", "VOLTAS.NS", 
    "WELCORP.NS", "WELSPUNLIV.NS", "WESTLIFE.NS", "WHIRLPOOL.NS", "WIPRO.NS", "WOCKPHARMA.NS", "YESBANK.NS", 
    "ZEEL.NS", "ZENSARTECH.NS", "ZOMATO.NS", "ZYDUSLIFE.NS", "ZYDUSWELL.NS"
]

stocks_to_scan = NIFTY_50 if segment == "NIFTY 50" else NIFTY_500

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
