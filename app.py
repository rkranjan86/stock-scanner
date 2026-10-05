import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
from datetime import datetime, time
import pytz

# =========================================================
# ⚙️ PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Stockview12 - Bollinger Band Live Scanner",
    layout="wide",
    page_icon="📈"
)

IST = pytz.timezone('Asia/Kolkata')

# =========================================================
# 🎨 CUSTOM STYLING
# =========================================================
st.markdown("""
    <style>
    .logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }
    .stockview-logo {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #00c6ff 100%);
        color: #ffffff;
        font-weight: 900;
        font-size: 26px;
        padding: 8px 20px;
        border-radius: 10px;
        letter-spacing: 1.5px;
        box-shadow: 0px 4px 12px rgba(0, 198, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stockview-logo span {
        color: #00e676;
    }
    .ext-title {
        font-size: 24px;
        font-weight: 800;
        color: #111111;
        margin: 0;
    }
    .disclaimer-box {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
        padding: 12px 18px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        margin-top: 25px;
        text-align: center;
    }
    .market-open-banner {
        background: linear-gradient(90deg, #00c853 0%, #00e676 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 15px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0, 200, 83, 0.3);
    }
    .market-closed-banner {
        background: linear-gradient(90deg, #d32f2f 0%, #ff5252 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 15px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(211, 47, 47, 0.3);
    }
    .market-pre-banner {
        background: linear-gradient(90deg, #f57c00 0%, #ff9800 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 15px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(245, 124, 0, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# ⏰ MARKET HOURS LOGIC
# =========================================================
def get_market_status():
    """
    ভারতীয় স্টক মার্কেট (NSE/BSE) ওপেন কিনা চেক করে।
    Pre-market: 9:00 AM - 9:15 AM IST
    Live: 9:15 AM - 3:30 PM IST
    সোমবার - শুক্রবার
    """
    now = datetime.now(IST)
    weekday = now.weekday()  # 0=Monday, 6=Sunday

    # NSE ছুটির দিন (প্রয়োজন অনুযায়ী আপডেট করুন)
    NSE_HOLIDAYS = [
        "2026-01-26",  # Republic Day
        "2026-03-04",  # Holi
        "2026-03-17",  # Eid-ul-Fitr (আনুমানিক)
        "2026-03-30",  # Ram Navami
        "2026-04-03",  # Mahavir Jayanti
        "2026-04-14",  # Ambedkar Jayanti
        "2026-05-01",  # Maharashtra Day
        "2026-08-15",  # Independence Day
        "2026-10-02",  # Gandhi Jayanti
        "2026-10-21",  # Dussehra
        "2026-10-22",  # Dussehra (২য় দিন)
        "2026-11-05",  # Diwali (আনুমানিক)
        "2026-12-25",  # Christmas
    ]
    today_str = now.strftime("%Y-%m-%d")

    if weekday >= 5:  # শনি বা রবিবার
        return "closed", "Weekend"
    if today_str in NSE_HOLIDAYS:
        return "closed", "Holiday"

    current_time = now.time()
    pre_open = time(9, 0)
    market_open = time(9, 15)
    market_close = time(15, 30)

    if pre_open <= current_time < market_open:
        return "pre_open", "Pre-Market"
    elif market_open <= current_time <= market_close:
        return "open", "Live"
    else:
        return "closed", "After Hours"


# =========================================================
# 🏷️ HEADER
# =========================================================
st.markdown("""
    <div class="logo-container">
        <div class="stockview-logo">Stockview<span>12</span></div>
        <div class="ext-title">Bollinger Band Live Pro Scanner</div>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# 📈 LIVE INDICES MARQUEE
# =========================================================
@st.cache_data(ttl=30)
def render_live_marquee():
    indices = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "BANK NIFTY": "^NSEBANK",
        "NIFTY 500": "^CRSLDX",
        "INDIA VIX": "^INDIAVIX",
        "DOW JONES": "^DJI",
        "NASDAQ": "^IXIC",
        "NIKKEI 225": "^N225"
    }
    items_html = ""
    for name, ticker in indices.items():
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info
            current_price = info.last_price
            prev_close = info.previous_close
            if current_price is None or prev_close is None:
                continue
            change = current_price - prev_close
            pct_change = (change / prev_close) * 100

            is_pos = change >= 0
            color = "#00e676" if is_pos else "#ff5252"
            sign = "+" if is_pos else ""

            items_html += f"""
            <span style="display: inline-block; margin-right: 40px; font-weight: 600;">
                <span style="color: #cccccc;">{name}:</span> 
                <span style="color: #ffffff;">{current_price:,.2f}</span> 
                <span style="color: {color};">({sign}{change:.2f} | {sign}{pct_change:.2f}%)</span>
            </span>
            """
        except Exception:
            continue

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: transparent;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 14px;
            }}
            .marquee-wrapper {{
                background-color: #1a1e24;
                color: #ffffff;
                padding: 10px 0;
                border-radius: 6px;
                overflow: hidden;
                white-space: nowrap;
            }}
            .marquee-content {{
                display: inline-block;
                white-space: nowrap;
                animation: marquee 35s linear infinite;
            }}
            .marquee-content:hover {{
                animation-play-state: paused;
            }}
            @keyframes marquee {{
                0% {{ transform: translateX(100%); }}
                100% {{ transform: translateX(-100%); }}
            }}
        </style>
    </head>
    <body>
        <div class="marquee-wrapper">
            <div class="marquee-content">
                {items_html}
            </div>
        </div>
    </body>
    </html>
    """
    return html_code

components.html(render_live_marquee(), height=45)

# =========================================================
# 🔄 AUTO REFRESH MARKET STATUS
# =========================================================
@st.fragment(run_every=15)
def auto_refresh_status():
    status, label = get_market_status()
    now = datetime.now(IST)
    time_str = now.strftime('%d/%m/%Y | %I:%M:%S %p IST')

    if status == "open":
        st.markdown(
            f'<div class="market-open-banner">🟢 MARKET LIVE &nbsp;|&nbsp; {time_str} &nbsp;|&nbsp; Auto-refresh: 15s</div>',
            unsafe_allow_html=True
        )
    elif status == "pre_open":
        st.markdown(
            f'<div class="market-pre-banner">🟡 PRE-MARKET &nbsp;|&nbsp; {time_str}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="market-closed-banner">🔴 MARKET CLOSED ({label}) &nbsp;|&nbsp; {time_str} &nbsp;|&nbsp; Showing last closing data</div>',
            unsafe_allow_html=True
        )

auto_refresh_status()

c_time, c_ref = st.columns([4, 1])
with c_ref:
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# =========================================================
# 📌 NAVIGATION MENU
# =========================================================
selected_menu = st.radio(
    "📌 Navigation Menu",
    [
        "📈 Live Scanner",
        "⭐ Live Watchlist",
        "⚡ Intraday Stocks",
        "📅 Short Term Stocks",
        "🏦 Long Term Stocks"
    ],
    horizontal=True
)

st.markdown("---")

# =========================================================
# 📊 STOCK UNIVERSE
# =========================================================
NIFTY_50 = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BEL.NS", "BPCL.NS",
    "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS",
    "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS",
    "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "ITC.NS", "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS",
    "LT.NS", "LTIM.NS", "M&M.NS", "MARUTI.NS", "NTPC.NS",
    "NESTLEIND.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS",
    "SHRIRAMFIN.NS", "SBIN.NS", "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS",
    "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS"
]

NIFTY_200 = NIFTY_50 + [
    "ABB.NS", "ACC.NS", "AUBANK.NS", "ABBOTINDIA.NS", "ABCAPITAL.NS", "ABFRL.NS",
    "ADANIENSOL.NS", "ADANIGREEN.NS", "ADANIPOWER.NS", "ATGL.NS", "AWL.NS", "ALKEM.NS",
    "AMBUJACEM.NS", "APOLLOTYRE.NS", "ASHOKLEY.NS", "ASTRAL.NS", "AUROPHARMA.NS",
    "BALKRISIND.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BANKINDIA.NS", "BERGEPAINT.NS",
    "BDL.NS", "BHARATFORG.NS", "BHEL.NS", "BIOCON.NS", "BOSCHLTD.NS", "CANBK.NS",
    "CGPOWER.NS", "CHOLAFIN.NS", "COFORGE.NS", "COLPAL.NS", "CONCOR.NS", "CROMPTON.NS",
    "CUMMINSIND.NS", "DABUR.NS", "DALBHARAT.NS", "DEEPAKNTR.NS", "DELHIVERY.NS",
    "DIXON.NS", "DLF.NS", "ESCORTS.NS", "EXIDEIND.NS", "FEDERALBNK.NS", "GAIL.NS",
    "GLAND.NS", "GLENMARK.NS", "GMRAIRPORT.NS", "GODREJCP.NS", "GODREJPROP.NS",
    "GUJGASLTD.NS", "HDFCAMC.NS", "HAVELLS.NS", "HINDPETRO.NS", "HINDZINC.NS",
    "ICICIGI.NS", "ICICIPRULI.NS", "IDFCFIRSTB.NS", "INDIAMART.NS", "INDIANB.NS",
    "IEX.NS", "INDHOTEL.NS", "IOC.NS", "IRCTC.NS", "IRFC.NS", "IGL.NS", "INDUSTOWER.NS",
    "NAUKRI.NS", "INDIGO.NS", "IPCALAB.NS", "JSWENERGY.NS", "JINDALSTEL.NS", "JIOFIN.NS",
    "JUBLFOOD.NS", "KPITTECH.NS", "KAJARIACER.NS", "KALYANKJIL.NS", "KEI.NS", "LTF.NS",
    "LTTS.NS", "LICHSGFIN.NS", "LICI.NS", "LUPIN.NS", "MRF.NS", "LODHA.NS", "M&MFIN.NS",
    "MANAPPURAM.NS", "MARICO.NS", "MAXHEALTH.NS", "MAZDOCK.NS", "MPHASIS.NS",
    "MUTHOOTFIN.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", "NHPC.NS", "NMDC.NS", "NYKAA.NS",
    "OBEROIRLTY.NS", "OIL.NS", "PAYTM.NS", "OFSS.NS", "POLICYBZR.NS", "PIIND.NS",
    "PNBHOUSING.NS", "PAGEIND.NS", "PATANJALI.NS", "PERSISTENT.NS", "PETRONET.NS",
    "PFC.NS", "PHOENIXLTD.NS", "PIDILITIND.NS", "POLYCAB.NS", "POONAWALLA.NS",
    "PRESTIGE.NS", "PNB.NS", "REC.NS", "RVNL.NS", "MOTHERSON.NS", "SAIL.NS", "SHREECEM.NS",
    "SIEMENS.NS", "SONACOMS.NS", "SRF.NS", "SBICARD.NS", "SUZLON.NS", "SYNGENE.NS",
    "TVSMOTOR.NS", "TATACOMM.NS", "TATAELXSI.NS", "TATAPOWER.NS", "TATATECH.NS",
    "TIINDIA.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS", "UNOMINDA.NS", "UPL.NS",
    "UNIONBANK.NS", "UBL.NS", "VBL.NS", "VEDL.NS", "IDEA.NS",
    "VOLTAS.NS", "WIPRO.NS", "YESBANK.NS", "ZEEL.NS", "ZOMATO.NS", "ZYDUSLIFE.NS", "HEG.NS"
]

NIFTY_500 = NIFTY_200 + [
    "3MINDIA.NS", "AARTIDRUGS.NS", "AARTIIND.NS", "AAVAS.NS", "ABSLAMC.NS", "AEGISCHEM.NS",
    "AETHER.NS", "AFFLE.NS", "AJANTPHARM.NS", "AKZOINDIA.NS", "ALEMBICLTD.NS", "ALKYLAMINE.NS",
    "ALLCARGO.NS", "ALOKINDS.NS", "AMERISEL.NS", "ANANTRAJ.NS", "ANGELONE.NS", "ANURAS.NS",
    "APARINDS.NS", "APLLTD.NS", "APOLLO.NS", "APTUS.NS", "ARCHIDPLY.NS", "ARE&M.NS",
    "ASAHIINDIA.NS", "ASTERDM.NS", "ASTRAZEN.NS", "ATUL.NS", "AURIONPRO.NS", "AVANTIFEED.NS",
    "BAJAJELEC.NS", "BAJAJHFL.NS", "BALAMINES.NS", "BALMLAWRIE.NS", "BALRAMCHIN.NS", "BEML.NS",
    "BFINVEST.NS", "BFUTILITIE.NS", "BGRENERGY.NS", "BIKAJI.NS", "BIRLACORPN.NS", "BSOFT.NS",
    "CAMPUS.NS", "CANFINHOME.NS", "CAPLIPOINT.NS", "CARBORUNIV.NS", "CASTROLIND.NS", "CEATLTD.NS",
    "CENTURYPLY.NS", "CENTURYTEX.NS", "CERA.NS", "CESC.NS", "CGCL.NS", "CHAMBLFERT.NS",
    "CHEVIOT.NS", "CHOICEIN.NS", "CLEAN.NS", "COCHINSHIP.NS", "COFFEEDAY.NS",
    "CREDITACC.NS", "CSBBANK.NS", "CYIENT.NS", "DATAPATTNS.NS", "DCAL.NS", "DCBBANK.NS",
    "DCMSRIRAM.NS", "DEEPAKFERT.NS", "DELTACORP.NS", "DEVYANI.NS", "DHANUKA.NS",
    "ECLERX.NS", "EDELWEISS.NS", "EIDPARRY.NS", "EIHOTEL.NS", "ELECON.NS", "EMAMILTD.NS",
    "ENDURANCE.NS", "ENGINERSIN.NS", "EQUITASBNK.NS", "ERIS.NS", "FACT.NS", "FINEORG.NS",
    "FINPIPE.NS", "FLAIR.NS", "FSL.NS", "GATEWAY.NS", "GHCL.NS", "GMDCLTD.NS",
    "GNFC.NS", "GODFRYPHLP.NS", "GOCOLORS.NS", "GPIL.NS", "GRANULES.NS", "GRAPHITE.NS",
    "GRINDWELL.NS", "GSFC.NS", "GSPL.NS", "HEMIPROP.NS", "HFCL.NS",
    "HIKAL.NS", "HIMATSEIDE.NS", "HINDCOPPER.NS", "HONAUT.NS", "HUDCO.NS", "ISEC.NS",
    "IBREALEST.NS", "INDIACEM.NS", "INDIAGLYCO.NS", "INDIGOPNTS.NS", "INFIBEAM.NS", "INOXWIND.NS",
    "INTELLECT.NS", "IOB.NS", "IRB.NS", "IRCON.NS", "ITI.NS", "J&KBANK.NS",
    "JAGRAN.NS", "JAIBALAJI.NS", "JINDALSAW.NS", "JKCEMENT.NS", "JKPAPER.NS",
    "JKTYRE.NS", "JMFINANCIL.NS", "JSWINFRA.NS", "JTEKTINDIA.NS", "JUSTDIAL.NS", "JYOTHYLAB.NS",
    "KALPATPOWR.NS", "KANSAINER.NS", "KARURVYSYA.NS", "KEC.NS", "KPRMILL.NS",
    "KRBL.NS", "KSB.NS", "LATENTVIEW.NS", "LAURUSLABS.NS", "LEMONTREE.NS", "LINDEINDIA.NS",
    "LLOYDSME.NS", "LUMAXIND.NS", "LXCHEM.NS", "MAHABANK.NS", "MAHSEAMLES.NS", "MGL.NS",
    "MAPMYINDIA.NS", "MASTEK.NS", "MEDPLUS.NS", "METROPOLIS.NS", "MFSL.NS",
    "MHRIL.NS", "MINDACORP.NS", "MMTC.NS", "MOIL.NS", "MRPL.NS", "MSUMI.NS",
    "MTARTECH.NS", "NATCOPHARM.NS", "NBCC.NS", "NCC.NS", "NESCO.NS",
    "NFL.NS", "NLCINDIA.NS", "NOCIL.NS", "NUVAMA.NS", "OLECTRA.NS", "ORIENTELEC.NS",
    "PCBL.NS", "PEL.NS", "PGHH.NS", "PHOENIX.NS", "PNCINFRA.NS",
    "POLYMED.NS", "POLYPLEX.NS", "PRAJIND.NS", "PRINCEPIPE.NS", "PRSMJOHNSN.NS", "RALLIS.NS",
    "RAMCOCEM.NS", "RATNAMANI.NS", "RBLBANK.NS", "REDINGTON.NS", "RELAXO.NS", "RHIM.NS",
    "RITES.NS", "ROLEXRINGS.NS", "ROUTE.NS", "RPOWER.NS", "RRKABEL.NS",
    "SAPPHIRE.NS", "SARDAEN.NS", "SAREGAMA.NS", "SBFC.NS", "SCHAEFFLER.NS", "SCHNEIDER.NS",
    "SHARDACROP.NS", "SHOPERSTOP.NS", "SJS.NS", "SKFINDIA.NS", "SOBHA.NS", "SOLARINDS.NS", "SOUTHBANK.NS",
    "STARHEALTH.NS", "SUMICHEM.NS", "SUNDARMFIN.NS", "SUNTECK.NS", "SUPRAJIT.NS", "SUPREMEIND.NS",
    "SUVENPHAR.NS", "SWANENERGY.NS", "TATAINVEST.NS", "TEAMLEASE.NS",
    "TECHNOE.NS", "TEJASNET.NS", "THERMAX.NS", "THYROCARE.NS", "TIMKEN.NS",
    "TITAGARH.NS", "TRIDENT.NS", "TRIVENI.NS", "TRITURBINE.NS", "TTKPRESTIG.NS", "UCOBANK.NS",
    "UJJIVANSFB.NS", "USHAMART.NS", "UTIAMC.NS", "VAIBHAVGBL.NS", "VGUARD.NS",
    "VINATIORGA.NS", "VIPIND.NS", "VMART.NS", "VSTIND.NS", "WABAG.NS", "WELCORP.NS",
    "WELSPUNLIV.NS", "WESTLIFE.NS", "WHIRLPOOL.NS", "WOCKPHARMA.NS", "ZENTEC.NS", "ZFCVINDIA.NS"
]

# =========================================================
# 🎯 CORE SCANNER FUNCTION
# =========================================================
def scan_bollinger(stocks, interval, period, strategy_type, tf_name):
    """
    মার্কেট ওপেন থাকলে লাইভ ডেটা, বন্ধ থাকলে শেষ ক্লোজিং ডেটা স্ক্যান করে।
    """
    selected = []
    if not stocks:
        return selected

    market_status, _ = get_market_status()
    is_market_live = (market_status == "open")

    try:
        data = yf.download(
            stocks,
            period=period,
            interval=interval,
            group_by='ticker',
            progress=False,
            auto_adjust=False,
            prepost=False
        )
    except Exception:
        return selected

    for symbol in stocks:
        try:
            if len(stocks) == 1:
                df = data.dropna()
            elif isinstance(data.columns, pd.MultiIndex):
                if symbol in data.columns.get_level_values(0):
                    df = data[symbol].dropna()
                else:
                    continue
            elif symbol in data:
                df = data[symbol].dropna()
            else:
                continue

            if len(df) < 21:
                continue

            # Custom resampling
            if tf_name == "10-Min":
                df = df.resample('10min').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()
            elif tf_name == "2-Hour":
                df = df.resample('2h').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()
            elif tf_name == "4-Hour":
                df = df.resample('4h').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()

            if len(df) < 21:
                continue

            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['Lower_Band'] = df['SMA20'] - (df['STD20'] * 2)

            curr = df.iloc[-1]
            prev = df.iloc[-2]

            body_curr = abs(curr['Close'] - curr['Open'])
            range_curr = curr['High'] - curr['Low']

            clean_symbol = symbol.replace(".NS", "").replace(".BO", "")
            exchange = "BSE" if ".BO" in symbol else "NSE"
            status_tag = "🟢 LIVE" if is_market_live else "🔴 CLOSED"

            # Condition 1
            if strategy_type.startswith("Condition 1"):
                is_green = curr['Close'] > curr['Open']
                cuts_lower = curr['Low'] <= curr['Lower_Band'] and curr['Close'] >= curr['Lower_Band']
                bullish_engulfing = (curr['Close'] >= prev['Open']) or (curr['Close'] >= prev['High'] * 0.98)
                strong_body = (body_curr / range_curr) > 0.50 if range_curr > 0 else False

                if is_green and cuts_lower and bullish_engulfing and strong_body:
                    selected.append({
                        "Stock": clean_symbol,
                        "Exchange": exchange,
                        "Status": status_tag,
                        "LTP (₹)": round(float(curr['Close']), 2),
                        "Open (₹)": round(float(curr['Open']), 2),
                        "High (₹)": round(float(curr['High']), 2),
                        "Lower Band (₹)": round(float(curr['Lower_Band']), 2),
                        "Pattern": "Strong Green Cut",
                        "Volume": int(curr['Volume']) if not pd.isna(curr['Volume']) else 0
                    })

            # Condition 2
            elif strategy_type.startswith("Condition 2"):
                below_lower = (curr['High'] < curr['Lower_Band']) and (curr['Low'] < curr['Lower_Band'])
                lower_shadow = min(curr['Open'], curr['Close']) - curr['Low']
                upper_shadow = curr['High'] - max(curr['Open'], curr['Close'])
                is_hammer = (lower_shadow >= 2 * body_curr) and (upper_shadow <= body_curr * 0.8) if body_curr > 0 else (lower_shadow > 0)
                is_star_body = (body_curr / range_curr) <= 0.30 if range_curr > 0 else True

                if below_lower and (is_hammer or is_star_body):
                    pattern_type = "Hammer Below Band" if is_hammer else "Gap / Morning Star Base"
                    selected.append({
                        "Stock": clean_symbol,
                        "Exchange": exchange,
                        "Status": status_tag,
                        "LTP (₹)": round(float(curr['Close']), 2),
                        "High (₹)": round(float(curr['High']), 2),
                        "Low (₹)": round(float(curr['Low']), 2),
                        "Lower Band (₹)": round(float(curr['Lower_Band']), 2),
                        "Pattern": pattern_type,
                        "Volume": int(curr['Volume']) if not pd.isna(curr['Volume']) else 0
                    })
        except Exception:
            continue

    return selected


# =========================================================
# 📈 PAGE 1: LIVE SCANNER
# =========================================================
if selected_menu == "📈 Live Scanner":
    st.subheader("⚙ Scanner Settings")
    c1, c2, c3 = st.columns(3)

    with c1:
        strategy = st.selectbox(
            "🎯 Select Strategy",
            [
                "Condition 1: Lower Band Cut (Strong Green Candle & Engulfing/Reversal)",
                "Condition 2: Completely Below Lower Band (Hammer / Morning Star Gap)"
            ]
        )

    with c2:
        timeframe = st.selectbox(
            "⏱️ Select Timeframe",
            ["1-Min", "5-Min", "10-Min", "15-Min", "30-Min", "1-Hour", "2-Hour", "4-Hour", "1-Day", "1-Week", "1-Month"],
            index=8
        )

    with c3:
        segment = st.selectbox(
            "📜 Select Stock Segment",
            [
                f"NIFTY 50 ({len(NIFTY_50)} Stocks)",
                f"NIFTY 200 ({len(NIFTY_200)} Stocks)",
                f"NIFTY 500 ({len(NIFTY_500)} Stocks)",
                "🌐 Other Stock View (BSE / SmallCap / Custom)"
            ],
            index=0
        )

    tf_map = {
        "1-Min": ("1m", "1d"),
        "5-Min": ("5m", "5d"),
        "10-Min": ("5m", "5d"),
        "15-Min": ("15m", "5d"),
        "30-Min": ("30m", "5d"),
        "1-Hour": ("60m", "1mo"),
        "2-Hour": ("60m", "1mo"),
        "4-Hour": ("60m", "3mo"),
        "1-Day": ("1d", "6mo"),
        "1-Week": ("1wk", "2y"),
        "1-Month": ("1mo", "10y")
    }
    interval, period = tf_map[timeframe]

    stocks_to_scan = []

    if "NIFTY 50 " in segment:
        stocks_to_scan = NIFTY_50
    elif "NIFTY 200 " in segment:
        stocks_to_scan = NIFTY_200
    elif "NIFTY 500 " in segment:
        stocks_to_scan = NIFTY_500
    elif "Other Stock View" in segment:
        st.markdown("#### 🔍 BSE & Custom Stock Search Portal")
        custom_input = st.text_input(
            "Stock Symbols (Comma Separated, e.g., 500325.BO, SJVN.BO, IREDA, RPOWER):",
            "500325.BO, SJVN.BO, IREDA.NS, RPOWER.NS"
        )
        if custom_input:
            formatted_list = []
            for item in custom_input.split(","):
                sym = item.strip().upper()
                if not sym:
                    continue
                if not (sym.endswith(".NS") or sym.endswith(".BO")):
                    sym = sym + ".NS"
                formatted_list.append(sym)
            stocks_to_scan = formatted_list

    if stocks_to_scan:
        with st.spinner(f"Scanning {len(stocks_to_scan)} stocks in {timeframe} timeframe..."):
            results = scan_bollinger(stocks_to_scan, interval, period, strategy, timeframe)

        if results:
            st.success(f"✅ {len(results)} টি স্টক পাওয়া গেছে ({timeframe} timeframe)!")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.info(f"❌ Selected condition-এ {timeframe} timeframe-এ কোনো স্টক পাওয়া যায়নি।")


# =========================================================
# ⭐ PAGE 2: LIVE WATCHLIST
# =========================================================
elif selected_menu == "⭐ Live Watchlist":
    st.subheader("⭐ Custom Live Watchlist")
    user_symbols = st.text_input(
        "Stock Symbols (Comma Separated, e.g., RELIANCE, SBIN, 500325.BO):",
        "RELIANCE, SBIN, TATAMOTORS, INFY, HDFCBANK"
   
