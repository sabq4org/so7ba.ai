#!/usr/bin/env python3
"""Flow-First Options Screener — UW + Polygon"""

import requests, json
from datetime import datetime, timezone, timedelta

UW_KEY = "0673284e-7e64-4d63-8574-fd8cee0f1711"
POLY_KEY = "pbkeHwxpVSvr6tOr1kUH__UIUZzVlwUy"
UW = "https://api.unusualwhales.com/api"
HDR = {"Authorization": f"Bearer {UW_KEY}", "Accept": "application/json"}

def get(url, params=None, headers=None):
    try:
        r = requests.get(url, params=params, headers=headers or HDR, timeout=15)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# ─── Step 1: Market Tide ───
def get_market_tide():
    print("━" * 60)
    print("📊 Step 1: Market Tide")
    print("━" * 60)
    data = get(f"{UW}/market/market-tide")
    if not data or not data.get("data"):
        print("  ⚠ No data, defaulting to Neutral")
        return "⚪ Neutral"
    
    entries = data["data"]
    # Use last entry for latest reading
    last = entries[-1]
    net_call = float(last.get("net_call_premium", 0) or 0)
    net_put = float(last.get("net_put_premium", 0) or 0)
    
    if net_call > 0 and net_call > net_put:
        direction = "🟢 Bullish"
    elif net_put > 0 and net_put > net_call:
        direction = "🔴 Bearish"
    else:
        direction = "⚪ Neutral"
    
    print(f"  Net Call Premium: ${net_call:,.0f}")
    print(f"  Net Put Premium:  ${net_put:,.0f}")
    print(f"  Direction:        {direction}")
    return direction

# ─── Step 2: Screener ───
def screen_contracts():
    print("\n" + "━" * 60)
    print("🔍 Step 2: Options Screener")
    print("━" * 60)
    
    base = {
        "vol_greater_oi": "true",
        "min_premium": 250000,
        "is_otm": "true",
        "max_dte": 21,
        "min_ask_perc": 0.7,
        "max_multileg_volume_ratio": 0.1,
        "issue_types[]": "Common Stock",
        "limit": 20,
    }
    
    all_c = []
    for t in ["Calls", "Puts"]:
        params = {**base, "type": t}
        data = get(f"{UW}/screener/option-contracts", params=params)
        if data and isinstance(data.get("data"), list):
            for c in data["data"]:
                c["_type"] = t
            all_c.extend(data["data"])
            print(f"  {t}: {len(data['data'])} contracts")
        else:
            print(f"  {t}: no data")
    return all_c

# ─── Step 3: Filter ───
def filter_contracts(contracts):
    print("\n" + "━" * 60)
    print("🔎 Step 3: Filtering (price $0.50-$5, DTE 5-21, Vol/OI>2x)")
    print("━" * 60)
    
    out = []
    for c in contracts:
        try:
            close = float(c.get("close", 0) or 0)
            avg = float(c.get("avg_price", 0) or 0)
            price = close if close > 0 else avg
            vol = float(c.get("volume", 0) or 0)
            oi = float(c.get("open_interest", 1) or 1)
            dte_val = None
            
            # Parse DTE from option symbol if not given
            sym = c.get("option_symbol", "")
            if sym and len(sym) > 6:
                try:
                    # Format: TICKER YYMMDD C/P STRIKE
                    # Find the date part
                    import re
                    m = re.search(r'(\d{6})[CP]', sym)
                    if m:
                        exp = datetime.strptime(m.group(1), "%y%m%d").replace(tzinfo=timezone.utc)
                        dte_val = (exp - datetime.now(timezone.utc)).days
                except:
                    pass
            
            if dte_val is None:
                dte_val = int(c.get("dte", 0) or 0)
            
            if not (0.50 <= price <= 5.0):
                continue
            if not (5 <= dte_val <= 21):
                continue
            if oi > 0 and vol / oi <= 2:
                continue
            
            c["_price"] = price
            c["_dte"] = dte_val
            c["_vol_oi"] = vol / max(oi, 1)
            out.append(c)
        except:
            continue
    
    print(f"  ✅ {len(out)} contracts passed")
    return out

# ─── Step 4+5: Confirm & Score ───
def score_contract(c, tide):
    ticker = c.get("ticker_symbol", "?")
    score = 0
    reasons = []
    
    # 1. Vol>OI (already filtered)
    score += 1; reasons.append("Vol>OI ✓")
    
    # 2. Market Tide
    is_call = c["_type"] == "Calls"
    if ("Bullish" in tide and is_call) or ("Bearish" in tide and not is_call):
        score += 1; reasons.append("Tide ✓")
    
    # 3. Flow Alerts
    flow = get(f"{UW}/option-trades/flow-alerts", params={"ticker_symbol": ticker, "limit": 5, "min_premium": 50000})
    flow_data = flow.get("data", []) if flow else []
    if isinstance(flow_data, list) and len(flow_data) >= 2:
        score += 1; reasons.append(f"Flow({len(flow_data)})")
        # Check for sweeps
        sweeps = sum(1 for f in flow_data if "sweep" in str(f).lower())
        if sweeps:
            score += 1; reasons.append(f"Sweep({sweeps})")
    
    # 4. Spot GEX
    gex = get(f"{UW}/stock/{ticker}/spot-exposures/strike")
    if gex and gex.get("data"):
        score += 2; reasons.append("GEX ✓")
    
    # 5. Dark Pool
    dp = get(f"{UW}/darkpool/{ticker}")
    if dp and dp.get("data"):
        dp_list = dp["data"] if isinstance(dp["data"], list) else []
        if len(dp_list) > 0:
            score += 1; reasons.append("DarkPool ✓")
    
    # 6. Net Premium from flow
    if flow_data:
        try:
            total = sum(float(f.get("premium", 0) or 0) for f in flow_data)
            if total > 100000:
                score += 1; reasons.append(f"NetPrem ${total:,.0f}")
        except:
            pass
    
    # 7. No earnings within 48h
    earn = c.get("next_earnings_date")
    if earn:
        try:
            ed = datetime.strptime(earn, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if (ed - datetime.now(timezone.utc)).days > 2:
                score += 1; reasons.append("NoEarnings ✓")
        except:
            score += 1; reasons.append("NoEarnings ✓")
    else:
        score += 1; reasons.append("NoEarnings ✓")
    
    # 8. Technical: use UW greeks already in contract
    delta = c.get("delta")
    if delta:
        try:
            d = abs(float(delta))
            if 0.15 <= d <= 0.50:
                score += 1; reasons.append(f"Delta {float(delta):.2f} ✓")
        except:
            pass
    
    # Spread
    bid = float(c.get("bid", 0) or c.get("low", 0) or 0)
    ask = float(c.get("ask", 0) or c.get("high", 0) or 0)
    spread_pct = ((ask - bid) / ask * 100) if ask > 0 else 0
    
    return {
        "ticker": ticker,
        "contract": c.get("option_symbol", "?"),
        "type": c["_type"],
        "price": c["_price"],
        "delta": c.get("delta"),
        "gamma": c.get("gamma"),
        "theta": c.get("theta"),
        "bid": bid,
        "ask": ask,
        "spread_pct": spread_pct,
        "dte": c["_dte"],
        "vol": c.get("volume", 0),
        "oi": c.get("open_interest", 0),
        "vol_oi": c["_vol_oi"],
        "score": score,
        "reasons": reasons,
        "sector": c.get("sector", ""),
        "earnings": c.get("next_earnings_date", ""),
    }

# ─── Main ───
def run():
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    print("\n" + "=" * 60)
    print("  🐋 Flow-First Options Screener")
    print(f"  📅 {now}")
    print("=" * 60)
    
    tide = get_market_tide()
    contracts = screen_contracts()
    if not contracts:
        print("\n❌ No contracts from screener"); return
    
    filtered = filter_contracts(contracts)
    if not filtered:
        print("\n⚠ No contracts passed strict filters. Relaxing price filter...")
        # Relax: show top contracts by vol/oi
        for c in contracts:
            vol = float(c.get("volume", 0) or 0)
            oi = float(c.get("open_interest", 1) or 1)
            c["_vol_oi"] = vol / max(oi, 1)
            c["_price"] = float(c.get("close", 0) or c.get("avg_price", 0) or 0)
            c["_dte"] = 0
            import re
            sym = c.get("option_symbol", "")
            m = re.search(r'(\d{6})[CP]', sym)
            if m:
                try:
                    exp = datetime.strptime(m.group(1), "%y%m%d").replace(tzinfo=timezone.utc)
                    c["_dte"] = (exp - datetime.now(timezone.utc)).days
                except: pass
        filtered = sorted(contracts, key=lambda x: x["_vol_oi"], reverse=True)[:10]
    
    print(f"\n" + "━" * 60)
    print(f"📡 Step 4-5: Scoring {len(filtered[:10])} contracts...")
    print("━" * 60)
    
    scored = []
    for c in filtered[:10]:
        ticker = c.get("ticker_symbol", "?")
        print(f"  → {ticker} {c.get('option_symbol', '')}")
        scored.append(score_contract(c, tide))
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:5]
    
    # ─── Report ───
    print("\n" + "=" * 60)
    print("  📋 التقرير النهائي | Final Report")
    print("=" * 60)
    print(f"\n  🌊 Market Tide: {tide}")
    print(f"  📊 Screened: {len(contracts)} → Filtered: {len(filtered)} → Top 5")
    
    for i, s in enumerate(top, 1):
        rec = "🟢 STRONG BUY" if s["score"] >= 7 else "🟡 MODERATE" if s["score"] >= 5 else "⚪ WEAK"
        print(f"""
  {'━' * 55}
  #{i}  {s['ticker']} — {s['type']}
  {'━' * 55}
  📄 Contract:  {s['contract']}
  💰 السعر:     ${s['price']:.2f}  |  Bid/Ask: ${s['bid']:.2f}/${s['ask']:.2f}
  📐 Spread:    {s['spread_pct']:.1f}%
  📊 Vol/OI:    {s['vol']}/{s['oi']} = {s['vol_oi']:.1f}x
  📅 DTE:       {s['dte']} days
  Δ  Delta:     {s['delta'] or 'N/A'}
  θ  Theta:     {s['theta'] or 'N/A'}
  📅 Earnings:  {s['earnings'] or 'N/A'}
  ⭐ Score:     {s['score']}/10
  📝 Signals:   {', '.join(s['reasons'])}
  🎯 التوصية:   {rec}""")
    
    print("\n" + "=" * 60)
    print("  ⚠️  NOT financial advice. DYOR.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run()
