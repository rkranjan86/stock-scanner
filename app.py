<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>StockView12</title>
<script src="https://unpkg.com/lightweight-charts@4.2.0/dist/lightweight-charts.standalone.production.js"></script>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header>
  <div class="brand">StockView12</div>
  <nav>
    <button onclick="showList('watch')">Add Watch List</button>
    <button onclick="showList('intraday')">Intraday Stock</button>
    <button onclick="showList('short')">Short Term Stock</button>
    <button onclick="showList('long')">Long Term Stock</button>
  </nav>
</header>

<div class="ticker">
  <span>NIFTY 50 <b id="nifty">--</b></span>
  <span>SENSEX <b id="sensex">--</b></span>
  <span>NIFTY BANK <b id="bank">--</b></span>
</div>

<section class="toolbar">
  <select id="universe">
    <option>NIFTY50</option><option>NIFTY200</option><option>NIFTY500</option>
    <option>NSE</option><option>BSE</option><option>ALL_NSE_BSE</option>
  </select>
  <select id="timeframe">
    <option>5m</option><option>10m</option><option>15m</option><option>30m</option>
    <option>1h</option><option>2h</option><option>4h</option><option>1D</option><option>1W</option><option>1M</option>
  </select>
  <button onclick="apply()">Scan</button>
  <span id="status" class="status">CONNECTING...</span>
  <span id="clock"></span>
</section>

<section class="settings">
  <details>
    <summary>Scanner Settings</summary>
    <div class="settings-grid">
      <label>BB Period <input id="bb_period" type="number" value="20"></label>
      <label>BB StdDev <input id="bb_std" type="number" step="0.1" value="2"></label>
      <label>Hammer lower/body <input id="hammer_lower" type="number" step="0.1" value="2"></label>
      <label>Hammer upper/body max <input id="hammer_upper" type="number" step="0.05" value="0.35"></label>
      <label>Hammer body/range max <input id="hammer_body_max" type="number" step="0.05" value="0.45"></label>
      <label>Strong body/range min <input id="min_strong_body" type="number" step="0.05" value="0.65"></label>
      <label>Cross body/range min <input id="min_cross_body" type="number" step="0.05" value="0.60"></label>
      <button onclick="apply()">Apply Settings</button>
    </div>
  </details>
</section>

<main>
  <div class="card">
    <div class="card-title">Scanner Results <span id="count">0</span></div>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Stock</th><th>Exchange</th><th>TF</th><th>Signal</th><th>Time</th>
          <th>Price</th><th>Lower BB</th><th>Reason</th>
        </tr></thead>
        <tbody id="results"></tbody>
      </table>
    </div>
  </div>
  <div class="card">
    <div class="card-title">Stock Chart</div>
    <div id="chart"></div>
    <div id="chartTitle">Select a scanner result.</div>
  </div>
</main>

<div id="modal" class="modal hidden">
  <div class="modal-box">
    <button class="close" onclick="closeModal()">×</button>
    <h3 id="listTitle"></h3>
    <input id="symbolInput" placeholder="RELIANCE">
    <button onclick="addList()">Add</button>
    <div id="listItems"></div>
  </div>
</div>

<script src="/static/app.js"></script>
</body>
</html>
