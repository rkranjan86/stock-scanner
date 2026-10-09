import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# Page Configuration
st.set_page_config(page_title="Stockview12 - Live Bollinger Scanner", layout="wide")

IST = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(IST)

# App Header
st.title("📈 Stockview12 - Standalone Live Scanner")
st.caption(f"📅 Live Market Time (IST): `{now_ist.strftime('%d/%m/%Y | %I:%M:%S %p')}` | ⚡ Powered by yfinance (No API Key Required)")

# ==========================================
# 📌 1. NIFTY 50 STOCKS (Exactly 50)
# ==========================================
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

# ==========================================
# 📌 2. NIFTY NEXT 150 STOCKS (To make NIFTY 200 = 200 Stocks)
# ==========================================
NIFTY_NEXT_150 = [
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
    "UNIONBANK.NS", "UBL.NS", "MCDOWELL-N.NS", "VBL.NS", "VEDL.NS", "IDEA.NS", 
    "VOLTAS.NS", "WIPRO.NS", "YESBANK.NS", "ZEEL.NS", "ZOMATO.NS", "ZYDUSLIFE.NS", "HEG.NS"
]

NIFTY_200 = list(dict.fromkeys(NIFTY_50 + NIFTY_NEXT_150))

# ==========================================
# 📌 3. ADDITIONAL 300 MIDCAP & SMALLCAP STOCKS (To make NIFTY 500 = 500 Stocks)
# ==========================================
NIFTY_MID_SMALL_300 = [
    "3MINDIA.NS", "AARTIDRUGS.NS", "AARTIIND.NS", "AAVAS.NS", "ABSLAMC.NS", "AEGISCHEM.NS",
    "AETHER.NS", "AFFLE.NS", "AJANTPHARM.NS", "AKZOINDIA.NS", "ALEMBICLTD.NS", "ALKYLAMINE.NS",
    "ALLCARGO.NS", "ALOKINDS.NS", "AMERISEL.NS", "ANANTRAJ.NS", "ANGELONE.NS", "ANURAS.NS",
    "APARINDS.NS", "APLLTD.NS", "APOLLO.NS", "APTUS.NS", "ARCHIDPLY.NS", "ARE&M.NS",
    "ASAHIINDIA.NS", "ASTERDM.NS", "ASTRAZEN.NS", "ATUL.NS", "AURIONPRO.NS", "AVANTIFEED.NS",
    "BAJAJELEC.NS", "BAJAJHFL.NS", "BALAMINES.NS", "BALMLAWRIE.NS", "BALRAMCHIN.NS", "BEML.NS",
    "BFINVEST.NS", "BFUTILITIE.NS", "BGRENERGY.NS", "BIKAJI.NS", "BIRLACORPN.NS", "BSOFT.NS",
    "CAMPUS.NS", "CANFINHOME.NS", "CAPLIPOINT.NS", "CARBORUNIV.NS", "CASTROLIND.NS", "CEATLTD.NS",
    "CENTURYPLY.NS", "CENTURYTEX.NS", "CERA.NS", "CESC.NS", "CGCL.NS", "CHAMBLFERT.NS",
    "CHEVIOT.NS", "CHOICEIN.NS", "CLEAN.NS", "COCHINSHIP.NS", "COFFEEDAY.NS", "CRAFTMAN.NS",
    "CREDITACC.NS", "CSBBANK.NS", "CYIENT.NS", "DATAPATTNS.NS", "DCAL.NS", "DCBBANK.NS",
    "DCMSRIRAM.NS", "DEEPAKFERT.NS", "DELTACORP.NS", "DEVYANI.NS", "DHANI.NS", "DHANUKA.NS",
    "ECLERX.NS", "EDELWEISS.NS", "EIDPARRY.NS", "EIHOTEL.NS", "ELECON.NS", "EMAMILTD.NS",
    "ENDURANCE.NS", "ENGINERSIN.NS", "EQUITASBNK.NS", "ERIS.NS", "FACT.NS", "FINEORG.NS",
    "FINPIPE.NS", "FLAIR.NS", "FSL.NS", "GATEWAY.NS", "GHCL.NS", "GMDCLTD.NS",
    "GNFC.NS", "GODFRYPHLP.NS", "GOCOLORS.NS", "GPIL.NS", "GRANULES.NS", "GRAPHITE.NS",
    "GREATTEE.NS", "GRINDWELL.NS", "GSFC.NS", "GSPL.NS", "HEMIPROP.NS", "HFCL.NS",
    "HIKAL.NS", "HIMATSEIDE.NS", "HINDCOPPER.NS", "HONAUT.NS", "HUDCO.NS",
    "IBREALEST.NS", "INDIACEM.NS", "INDIAGLYCO.NS", "INDIGOPNTS.NS", "INFIBEAM.NS", "INOXWIND.NS",
    "INTELLECT.NS", "IOB.NS", "IRB.NS", "IRCON.NS", "ISEC.NS", "ITI.NS", "J&KBANK.NS",
    "JAGRAN.NS", "JAIBALAJI.NS", "JCB.NS", "JINDALSAW.NS", "JKCEMENT.NS", "JKPAPER.NS",
    "JKTYRE.NS", "JMFINANCIL.NS", "JSWINFRA.NS", "JTEKTINDIA.NS", "JUSTDIAL.NS", "JYOTHYLAB.NS",
    "KALPATPOWR.NS", "KALYANI.NS", "KANSAINER.NS", "KARURVYSYA.NS", "KEC.NS", "KPRMILL.NS",
    "KRBL.NS", "KSB.NS", "LATENTVIEW.NS", "LAURUSLABS.NS", "LEMONTREE.NS", "LINDEINDIA.NS",
    "LLOYDSME.NS", "LUMAXIND.NS", "LXCHEM.NS", "MAHABANK.NS", "MAHSEAMLES.NS", "MGL.NS",
    "MAPMYINDIA.NS", "MASTEK.NS", "MAXESTATES.NS", "MEDPLUS.NS", "METROPOLIS.NS", "MFSL.NS",
    "MHRIL.NS", "MINDACORP.NS", "MMTC.NS", "MOIL.NS", "MRPL.NS", "MSUMI.NS", "MTARTECH.NS",
    "MTAG.NS", "NATCOPHARM.NS", "NBCC.NS", "NCC.NS", "NESCO.NS", "NFL.NS", "NLCINDIA.NS",
    "NOCIL.NS", "NUVAMA.NS", "NUVAMACAP.NS", "OLECTRA.NS", "ORIENTELEC.NS", "PCBL.NS",
    "PEL.NS", "PGHL.NS", "PGHH.NS", "PHOENIX.NS", "PNCINFRA.NS", "POLYMED.NS", "POLYPLEX.NS",
    "PRINCEPIPE.NS", "PRSMJOHNSN.NS", "RALLIS.NS", "RAMCOCEM.NS", "RATNAMANI.NS", "RBLBANK.NS",
    "REDINGTON.NS", "RELAXO.NS", "RHIM.NS", "RITES.NS", "ROLEXRINGS.NS", "ROUTE.NS", "RPOWER.NS",
    "RRKABEL.NS", "SANGHIIND.NS", "SAPPHIRE.NS", "SARDAEN.NS", "SAREGAMA.NS", "SBFC.NS",
    "SCHAEFFLER.NS", "SCHNEIDER.NS", "SEAMECLTD.NS", "SHARDACROP.NS", "SHK.NS", "SHOPERSTOP.NS",
    "SHREERAM.NS", "SINDHUTRAD.NS", "SJS.NS", "SKFINDIA.NS", "SOBHA.NS", "SOLARINDS.NS",
    "SOUTHBANK.NS", "SPLPETRO.NS", "STARHEALTH.NS", "SUMICHEM.NS", "SUNDARMFIN.NS", "SUNTECK.NS",
    "SUPRAJIT.NS", "SUPREMEIND.NS", "SUVENPHAR.NS", "SWANENERGY.NS", "TATAINVEST.NS",
    "TATAMTRDVR.NS", "TEAMLEASE.NS", "TECHNOE.NS", "TEJASNET.NS", "THERMAX.NS", "THYROCARE.NS",
    "TIIL.NS", "TIMKEN.NS", "TITAGARH.NS", "TRIDENT.NS", "TRIVENI.NS", "TRITURBINE.NS",
    "TTKPRESTIG.NS", "UCOBANK.NS", "UJJIVANSFB.NS", "USHAMART.NS", "UTIAMC.NS", "VAIBHAVGBL.NS",
    "VARIANCE.NS", "VGUARD.NS", "VINATIORGA.NS", "VIPIND.NS", "VMART.NS", "VSTIND.NS",
    "WABAG.NS", "WELCORP.NS", "WELSPUNLIV.NS", "WESTLIFE.NS", "WHIRLPOOL.NS", "WOCKPHARMA.NS",
    "ZENTEC.NS", "ZFCVINDIA.NS"
]

NIFTY_500 = list(dict.fromkeys(NIFTY_200 + NIFTY_MID_SMALL_300))

# Core Scanner Logic
def scan_stocks(ticker_list, interval, period, strategy):
    selected = []
    if not ticker_list:
        return selected

    try:
        data = yf.download(ticker_list, period=period, interval=interval, group_by='ticker', progress=False)
    except Exception:
        return selected

    for symbol in ticker_list:
        try:
            df = data[symbol].dropna() if symbol in data else None
            if df is None or len(df) < 21:
                continue

            # Bollinger Bands Calculation (20 SMA, 2 STD)
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['Lower_Band'] = df['SMA20'] - (df['STD20'] * 2)

            curr = df.iloc[-1]
            prev = df.iloc[-2]

            body_curr = abs(curr['Close'] - curr['Open'])
            range_curr = curr['High'] - curr['Low']

            if strategy == "Condition 1: Lower Band Cut (Strong Green & Engulfing)":
                is_green = curr['Close'] > curr['Open']
                cuts_lower = curr['Low'] <= curr['Lower_Band'] and curr['Close'] >= curr['Lower_Band']
                bullish_engulfing = (curr['Close'] >= prev['Open']) or (curr['Close'] >= prev['High'] * 0.98)
                strong_body = (body_curr / range_curr) > 0.50 if range_curr > 0 else False

                if is_green and cuts_lower and bullish_engulfing and strong_body:
                    selected.append({
                        "Stock": symbol.replace(".NS", ""),
                        "LTP (₹)": round(curr['Close'], 2),
                        "Open (₹)": round(curr['Open'], 2),
                        "High (₹)": round(curr['High'], 2),
                        "Lower Band (₹)": round(curr['Lower_Band'], 2),
                        "Volume": int(curr['Volume'])
                    })

            elif strategy == "Condition 2: Below Lower Band (Hammer / Morning Star)":
                below_lower = (curr['High'] < curr['Lower_Band']) and (curr['Low'] < curr['Lower_Band'])
                lower_shadow = min(curr['Open'], curr['Close']) - curr['Low']
                upper_shadow = curr['High'] - max(curr['Open'], curr['Close'])
                
                is_hammer = (lower_shadow >= 2 * body_curr) and (upper_shadow <= body_curr * 0.8) if body_curr > 0 else (lower_shadow > 0)
                is_star_body = (body_curr / range_curr) <= 0.30 if range_curr > 0 else True

                if below_lower and (is_hammer or is_star_body):
                    selected.append({
                        "Stock": symbol.replace(".NS", ""),
                        "LTP (₹)": round(curr['Close'], 2),
                        "High (₹)": round(curr['High'], 2),
                        "Low (₹)": round(curr['Low'], 2),
                        "Lower Band (₹)": round(curr['Lower_Band'], 2),
                        "Pattern": "Hammer Below Band" if is_hammer else "Star Base",
                        "Volume": int(curr['Volume'])
                    })
        except Exception:
            continue

    return selected

# UI Options
col1, col2, col3 = st.columns(3)
with col1:
    strategy = st.selectbox("🎯 Select Strategy", [
        "Condition 1: Lower Band Cut (Strong Green & Engulfing)",
        "Condition 2: Below Lower Band (Hammer / Morning Star)"
    ])
with col2:
    timeframe = st.selectbox("⏱️ Select Timeframe", ["5-Min", "15-Min", "1-Hour", "1-Day"], index=3)

with col3:
    segment = st.selectbox("📜 Select Index Segment", [
        f"NIFTY 50 ({len(NIFTY_50)} Stocks)",
        f"NIFTY 200 ({len(NIFTY_200)} Stocks)",
        f"NIFTY 500 ({len(NIFTY_500)} Stocks)"
    ], index=0)

tf_map = {
    "5-Min": ("5m", "5d"),
    "15-Min": ("15m", "5d"),
    "1-Hour": ("60m", "1mo"),
    "1-Day": ("1d", "6mo")
}
interval, period = tf_map[timeframe]

if "NIFTY 50 " in segment:
    stocks_to_scan = NIFTY_50
elif "NIFTY 200 " in segment:
    stocks_to_scan = NIFTY_200
else:
    stocks_to_scan = NIFTY_500

if st.button("🚀 Run Live Scanner", use_container_width=True):
    with st.spinner(f"Scanning {len(stocks_to_scan)} stocks in {timeframe} timeframe..."):
        results = scan_stocks(stocks_to_scan, interval, period, strategy)
        if results:
            st.success(f"Mot {len(results)} ti stock condition match koreche!")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.info("Ei muhurte ekti stock-o selected condition-e match koreni.")
