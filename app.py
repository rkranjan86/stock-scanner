from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf

from scanner import scan
from stocks import N200, N500

IST = timezone(timedelta(hours=5, minutes=30))
st.set_page_config(page_title="stock২minit – AI Stock Scanner", page_icon="📈", layout="wide")

st.markdown("""
<style>
header[data-testid="stHeader"], footer, #MainMenu {display:none}
.block-container {padding-top: .6rem; max-width: 1250px}
.idx {display:flex; gap:12px; flex-wrap:wrap; margin:8px 0 14px}
.idx > div {flex:1; min-width:230px; background:#fff; color:#14231c; border:1px solid #d9dfda;
            border-radius:8px; padding:10px 14px; font-variant-numeric:tabular-nums}
.idx .n {font-weight:700}
.idx .p {font-size:20px; margin:0 10px}
.up {color:#0a8f4e} .dn {color:#d6342c}
</style>""", unsafe_allow_html=True)

# ---------- ১. হেডার + মেনু বার + লাইভ date/time ----------
components.html("""
<style>
body{margin:0;font-family:'Segoe UI','Noto Sans Bengali',sans-serif}
.h{display:flex;align-items:center;gap:20px;padding:10px 18px;background:#0b5d46;color:#fff;border-radius:8px;flex-wrap:wrap}
.logo{font:800 24px Georgia,serif}.logo small{display:block;font:500 11px sans-serif;opacity:.8}
nav{flex:1;display:flex;gap:6px;flex-wrap:wrap}
nav a{color:#fff;text-decoration:none;padding:6px 12px;border-radius:6px;font-weight:600;font-size:14px}
nav a:first-child,nav a:hover{background:rgba(255,255,255,.2)}
.c{text-align:right;font-variant-numeric:tabular-nums}.c b{font-size:20px;display:block}.c span{font-size:12px;opacity:.9}
</style>
<div class="h"><div class="logo">stock২minit<small>AI Stock Scanner</small></div>
<nav><a href="#">হোম</a><a href="#">স্ক্যানার</a><a href="#">Nifty 200</a><a href="#">Nifty 500</a><a href="#">সম্পর্কে</a></nav>
<div class="c"><b id="t">--:--:--</b><span id="d"></span> · <span id="m"></span></div></div>
<script>
function tick(){const n=new Date(),o={timeZone:'Asia/Kolkata'};
document.getElementById('t').textContent=n.toLocaleTimeString('en-GB',o);
document.getElementById('d').textContent=n.toLocaleDateString('bn-IN',{...o,weekday:'short',day:'numeric',month:'long',year:'numeric'});
const p=new Intl.DateTimeFormat('en-GB',{...o,weekday:'short',hour:'2-digit',minute:'2-digit',hour12:false}).formatToParts(n).reduce((a,x)=>(a[x.type]=x.value,a),{});
const m=+p.hour*60+ +p.minute;const open=!['Sat','Sun'].includes(p.weekday)&&m>=555&&m<=930;
document.getElementById('m').textContent=open?'মার্কেট খোলা':'মার্কেট বন্ধ'}
tick();setInterval(tick,1000)
</script>""", height=82)


def market_open():
    n = datetime.now(IST)
    m = n.hour * 60 + n.minute
    return n.weekday() < 5 and 555 <= m <= 935


# ---------- ২. Nifty / Sensex / Bank Nifty ----------
@st.cache_data(ttl=60, show_spinner=False)
def get_indices():
    out = []
    for name, t in [("NIFTY 50", "^NSEI"), ("SENSEX", "^BSESN"), ("BANK NIFTY", "^NSEBANK")]:
        try:
            d = yf.Ticker(t).history(period="5d", interval="1d")["Close"].dropna()
            out.append((name, float(d.iloc[-1]), float(d.iloc[-2])))
        except Exception:
            out.append((name, None, None))
    return out


@st.fragment(run_every="60s")
def indices_row():
    html = '<div class="idx">'
    for name, v, b in get_indices():
        if v is None:
            html += f'<div><span class="n">{name}</span> <span class="p">—</span></div>'
            continue
        ch = v - b
        cls, ar = ("up", "▲") if ch >= 0 else ("dn", "▼")
        html += (f'<div class="{cls}"><span class="n" style="color:#14231c">{name}</span>'
                 f'<span class="p">{v:,.2f}</span>{ar} {abs(ch):,.2f} ({ch / b * 100:+.2f}%)</div>')
    st.markdown(html + "</div>", unsafe_allow_html=True)


indices_row()


# ---------- ডেটা লোড (Yahoo Finance, ৫ মিনিটের candle) ----------
@st.cache_data(ttl=300, show_spinner=False, max_entries=2)
def load(symbols: tuple):
    out = {}
    for i in range(0, len(symbols), 100):
        batch = symbols[i:i + 100]
        tk = [s + ".NS" for s in batch]
        try:
            df = yf.download(tk, period="5d", interval="5m", group_by="ticker",
                             threads=True, progress=False, auto_adjust=False)
        except Exception:
            continue
        for s, t in zip(batch, tk):
            try:
                d = df[t].dropna(subset=["Close"])
                if len(d) >= 30:
                    out[s] = d[["Open", "High", "Low", "Close", "Volume"]]
            except Exception:
                pass
    return out


# ---------- ৩. কন্ডিশন dropdown + Search ----------
COND = {
    "১. Lower BB-তে Green candle (মাঝামাঝি body) + Volume": "A",
    "২. Lower BB-এর নিচে Hammer / Morning Star (touch ছাড়া)": "B",
}
WIN = {"শেষ candle": "last", "গত ১ ঘণ্টা": "hour", "আজকের পুরো দিন": "day"}

c1, c2, c3, c4 = st.columns([1.1, 2.6, 1.3, 0.8], vertical_alignment="bottom")
uni = c1.selectbox("স্টক ইউনিভার্স", ["Nifty 200", "Nifty 500"])
cond_label = c2.selectbox("কন্ডিশন", list(COND))
win_label = c3.selectbox("সিগন্যাল কখনকার", list(WIN), index=2)
go = c4.button("🔍 Search", type="primary", use_container_width=True)
with st.expander("অ্যাডভান্সড"):
    volx = st.number_input("Volume কত গুণ বেশি হলে (কন্ডিশন ১)", 1.0, 10.0, 1.5, 0.1)
    auto = st.checkbox("মার্কেট খোলা থাকলে প্রতি ১ মিনিটে অটো রিফ্রেশ", value=True)

if go:
    st.session_state.q = dict(uni=uni, cond=COND[cond_label], win=WIN[win_label], volx=volx)
    st.session_state.cond_label = cond_label


def results():
    q = st.session_state.get("q")
    if not q:
        st.info("ইউনিভার্স ও কন্ডিশন বেছে **Search** চাপুন। প্রথমবার ডেটা আনতে ১–২ মিনিট লাগতে পারে।")
        return
    syms = tuple(N200 if q["uni"] == "Nifty 200" else N500)
    with st.spinner(f"{len(syms)}টি স্টকের ডেটা আনা হচ্ছে…"):
        data = load(syms)
    if not data:
        st.error("Yahoo Finance থেকে ডেটা আসেনি। কিছুক্ষণ পর আবার Search চাপুন।")
        return
    df = scan(data, q["cond"], q["win"], q["volx"])
    st.subheader(f"{st.session_state.get('cond_label', '')} · {q['uni']}")
    if df.empty:
        st.warning("এই মুহূর্তে কোনো স্টক কন্ডিশনে মেলেনি। 'আজকের পুরো দিন' বেছে আবার দেখুন।")
    else:
        sty = df.style.format({"Signal Price": "{:,.2f}", "LTP": "{:,.2f}", "Lower BB": "{:,.2f}",
                               "Change %": "{:+.2f}%", "Volume ×": "{:.1f}×"})
        paint = getattr(sty, "map", None) or sty.applymap
        sty = paint(lambda x: "color:#0a8f4e;font-weight:600" if x > 0 else "color:#d6342c;font-weight:600"
                    if x < 0 else "", subset=["Change %"])
        st.caption(f"✅ {len(df)}টি স্টক পাওয়া গেছে")
        st.dataframe(sty, hide_index=True, use_container_width=True,
                     column_config={"Chart": st.column_config.LinkColumn("চার্ট", display_text="📈 খুলুন")})
    last = max(d.index[-1] for d in data.values())
    st.caption(f"ডেটা: Yahoo Finance · শেষ candle {last:%d %b, %H:%M} · স্ক্যান {len(data)}/{len(syms)} স্টক "
               f"({'মার্কেট খোলা' if market_open() else 'মার্কেট বন্ধ, শেষ সেশনের ডেটা'})")


every = "60s" if (market_open() and st.session_state.get("q") and auto) else None
st.fragment(results, run_every=every)()
st.caption("⚠ শুধু শিক্ষামূলক টুল, বিনিয়োগ পরামর্শ নয়। Yahoo ডেটায় ১৫ মিনিট পর্যন্ত delay থাকতে পারে।")
