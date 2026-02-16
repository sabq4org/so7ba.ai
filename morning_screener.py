#!/usr/bin/env python3
"""
🔍 Morning Screener v3.0 — صُحبة Trading
Pipeline: Finviz Scanner → UW Options Screener → News → Flow → Spot GEX → Dark Pool → Congress → Contract → Scorecard
"""
import csv
import io
import json
import sys
import requests
import traceback
from datetime import datetime, timedelta

# === إعدادات ===
POLYGON_KEY = 'pbkeHwxpVSvr6tOr1kUH__UIUZzVlwUy'
POLYGON_BASE = 'https://api.polygon.io'
FINVIZ_AUTH = '5465b143-daa4-493b-94a2-dca522d7eea0'
UW_TOKEN = '0673284e-7e64-4d63-8574-fd8cee0f1711'
UW_BASE = 'https://api.unusualwhales.com'
UW_HEADERS = {'Authorization': f'Bearer {UW_TOKEN}', 'Accept': 'application/json'}

FINVIZ_BULLISH_URL = (
    f'https://elite.finviz.com/export.ashx?v=111&f=cap_midover,exch_nasd|nyse,'
    f'sh_avgvol_o2000,sh_instown_o50,sh_opt_option,sh_price_20to300,sh_relvol_o1.5,'
    f'ta_beta_1.2to,ta_change_u1,ta_sma20_pa,ta_volatility_wo3,'
    f'tad_0_close::close:d&ft=4&o=volume&auth={FINVIZ_AUTH}'
)
FINVIZ_BEARISH_URL = (
    f'https://elite.finviz.com/export.ashx?v=111&f=cap_midover,exch_nasd|nyse,'
    f'sh_avgvol_o2000,sh_instown_o50,sh_opt_option,sh_price_20to300,sh_relvol_o1.5,'
    f'ta_beta_1.2to3,ta_change_d1,ta_rsi_to40,ta_sma20_pb,ta_sma50_pb,'
    f'ta_volatility_wo3,tad_0_close::close:d&ft=4&o=volume&auth={FINVIZ_AUTH}'
)

# فلاتر اختيار العقد
DTE_MIN, DTE_MAX = 5, 15
DELTA_MIN, DELTA_MAX = 0.20, 0.40
PRICE_MIN, PRICE_MAX = 0.50, 8.00
MIN_OI, MIN_VOLUME = 500, 100
MAX_SPREAD_PCT = 0.20
MIN_SCORE = 5
TIMEOUT = 15


def log(msg):
    print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] {msg}")


def polygon_get(path, params=None):
    if params is None:
        params = {}
    params['apiKey'] = POLYGON_KEY
    resp = requests.get(f"{POLYGON_BASE}{path}", params=params, timeout=TIMEOUT)
    if resp.status_code == 200:
        return resp.json()
    return None


def uw_get(path, params=None):
    """طلب من Unusual Whales API"""
    resp = requests.get(f"{UW_BASE}{path}", headers=UW_HEADERS, params=params or {}, timeout=TIMEOUT)
    if resp.status_code == 200:
        return resp.json()
    return None


def get_stock_price_yfinance(ticker):
    try:
        import yfinance as yf
        tk = yf.Ticker(ticker)
        return tk.fast_info.last_price
    except:
        return 0


# ─────────────────────────────────────────────
# STEP 1: Finviz Scanner (fallback)
# ─────────────────────────────────────────────
def step1_finviz_scanner():
    results = {'bullish': [], 'bearish': []}
    for direction, url in [('bullish', FINVIZ_BULLISH_URL), ('bearish', FINVIZ_BEARISH_URL)]:
        try:
            log(f"Step 1: Fetching Finviz {direction} scanner...")
            resp = requests.get(url, timeout=TIMEOUT, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code != 200 or '<' in resp.text[:50]:
                log(f"  ⚠️ Finviz {direction}: HTTP {resp.status_code}")
                continue
            reader = csv.DictReader(io.StringIO(resp.text.strip()))
            for row in reader:
                ticker = row.get('Ticker', row.get('ticker', '')).strip()
                if not ticker:
                    continue
                try:
                    price = float(str(row.get('Price', '0')).replace(',', ''))
                except:
                    price = 0
                try:
                    change = float(str(row.get('Change', '0')).replace('%', '').replace(',', ''))
                except:
                    change = 0
                try:
                    volume = int(float(str(row.get('Volume', '0')).replace(',', '')))
                except:
                    volume = 0
                results[direction].append({
                    'ticker': ticker, 'price': price, 'change': change,
                    'volume': volume, 'direction': 'CALL' if direction == 'bullish' else 'PUT',
                })
            log(f"  ✅ Finviz {direction}: {len(results[direction])} tickers")
        except Exception as e:
            log(f"  ❌ Finviz {direction} error: {e}")
    return results


# ─────────────────────────────────────────────
# STEP 1B: UW Options Screener (بديل/مكمل)
# ─────────────────────────────────────────────
def step1b_uw_options_screener():
    results = {'bullish': [], 'bearish': []}
    bullish_params = {
        'type': 'Calls', 'is_otm': 'True', 'vol_greater_oi': 'True',
        'min_premium': 250000, 'min_volume': 500,
        'max_multileg_volume_ratio': 0.1, 'min_ask_perc': 0.7, 'limit': 20,
    }
    bearish_params = {
        'type': 'Puts', 'is_otm': 'True', 'vol_greater_oi': 'True',
        'min_premium': 250000, 'min_volume': 500,
        'max_multileg_volume_ratio': 0.1, 'min_bid_perc': 0.7, 'limit': 20,
    }
    for direction, params in [('bullish', bullish_params), ('bearish', bearish_params)]:
        try:
            log(f"Step 1B: UW Options Screener {direction}...")
            data = uw_get('/api/screener/option-contracts', params)
            if not data:
                log(f"  ⚠️ UW Screener {direction}: no data")
                continue
            contracts = data.get('data', data.get('results', []))
            if not isinstance(contracts, list):
                contracts = []
            seen = set()
            for c in contracts:
                ticker = c.get('underlying_symbol', c.get('ticker', '')).split()[0].replace('_', ' ').split()[0]
                if not ticker or ticker in seen:
                    continue
                seen.add(ticker)
                results[direction].append({
                    'ticker': ticker,
                    'price': float(c.get('underlying_price', 0) or 0),
                    'change': 0,
                    'volume': int(c.get('volume', 0) or 0),
                    'direction': 'CALL' if direction == 'bullish' else 'PUT',
                    'uw_premium': float(c.get('premium', 0) or 0),
                })
            log(f"  ✅ UW Screener {direction}: {len(results[direction])} unique tickers")
        except Exception as e:
            log(f"  ❌ UW Screener {direction} error: {e}")
    return results


# ─────────────────────────────────────────────
# Market Tide (Sentiment)
# ─────────────────────────────────────────────
def fetch_market_tide():
    log("Fetching Market Tide...")
    try:
        data = uw_get('/api/market/market-tide')
        if data:
            tide = data.get('data', data)
            if isinstance(tide, list) and tide:
                tide = tide[-1] if len(tide) > 0 else {}
            log(f"  ✅ Market Tide fetched")
            return tide
        log("  ⚠️ Market Tide: no data")
    except Exception as e:
        log(f"  ❌ Market Tide error: {e}")
    return {}


# ─────────────────────────────────────────────
# STEP 2: News — Benzinga عبر Polygon API
# ─────────────────────────────────────────────
def step2_news_filter(ticker, direction):
    news_items = []
    sentiment_positive = 0
    sentiment_negative = 0
    earnings_risk = False
    try:
        data = polygon_get(f'/v2/reference/news', {'ticker': ticker, 'limit': 5, 'order': 'desc', 'sort': 'published_utc'})
        if data and data.get('results'):
            for article in data['results']:
                title = article.get('title', '')
                desc = article.get('description', '')
                news_items.append(title)
                combined = (title + ' ' + desc).lower()
                pos_words = ['upgrade', 'beat', 'surge', 'rally', 'strong', 'bullish', 'raises', 'record', 'growth']
                neg_words = ['downgrade', 'miss', 'decline', 'weak', 'bearish', 'cut', 'warning', 'loss', 'recall']
                sentiment_positive += sum(1 for w in pos_words if w in combined)
                sentiment_negative += sum(1 for w in neg_words if w in combined)
                if any(kw in combined for kw in ['earnings', 'quarterly results', 'revenue report', 'eps']):
                    pub = article.get('published_utc', '')
                    if pub:
                        try:
                            pub_date = datetime.fromisoformat(pub.replace('Z', '+00:00')).replace(tzinfo=None)
                            if abs((pub_date - datetime.utcnow()).days) <= 5:
                                earnings_risk = True
                        except:
                            pass
    except Exception as e:
        log(f"  ⚠️ News error for {ticker}: {e}")
    if direction == 'CALL':
        news_supports = sentiment_positive >= sentiment_negative
    else:
        news_supports = sentiment_negative >= sentiment_positive
    score = 1 if news_supports else 0
    return score, news_items[:3], earnings_risk


# ─────────────────────────────────────────────
# STEP 3: Flow Analysis (فلاتر أقوى)
# ─────────────────────────────────────────────
def step3_flow_analysis(ticker, direction):
    flow_score = 0
    sweep_score = 0
    details = []
    try:
        params = {
            'ticker': ticker, 'limit': 10,
            'min_premium': 50000, 'size_greater_oi': 'True', 'is_otm': 'True',
        }
        resp = requests.get(f'{UW_BASE}/api/option-trades/flow-alerts',
                            headers=UW_HEADERS, params=params, timeout=TIMEOUT)
        if resp.status_code != 200:
            return 0, 0, [f"Flow API error {resp.status_code}"]
        alerts = resp.json().get('data', [])
        if not isinstance(alerts, list):
            alerts = []
        call_premium = put_premium = ask_side = bid_side = sweeps = 0
        for alert in alerts:
            premium = float(alert.get('total_premium', 0) or 0)
            option_type = str(alert.get('type', alert.get('put_call', ''))).upper()
            if 'CALL' in option_type or option_type == 'C':
                call_premium += premium
            elif 'PUT' in option_type or option_type == 'P':
                put_premium += premium
            if float(alert.get('total_ask_side_prem', 0) or 0) > 0:
                ask_side += 1
            if float(alert.get('total_bid_side_prem', 0) or 0) > 0:
                bid_side += 1
            if alert.get('has_sweep') or 'sweep' in str(alert.get('alert_rule', '')).lower():
                sweeps += 1
        net = call_premium - put_premium
        details.append(f"Call${call_premium/1e6:.1f}M vs Put${put_premium/1e6:.1f}M")
        if direction == 'CALL' and net > 0 and ask_side > bid_side:
            flow_score = 2
            details.append("Flow strongly bullish ✅")
        elif direction == 'PUT' and net < 0 and bid_side >= ask_side:
            flow_score = 2
            details.append("Flow strongly bearish ✅")
        elif (direction == 'CALL' and net > 0) or (direction == 'PUT' and net < 0):
            flow_score = 1
            details.append("Flow mildly supports direction")
        else:
            details.append("Flow does not support direction ❌")
        if sweeps > 0:
            sweep_score = 1
            details.append(f"{sweeps} sweeps detected 🔥")
    except Exception as e:
        details.append(f"Flow error: {e}")
    return flow_score, sweep_score, details


# ─────────────────────────────────────────────
# STEP 4: Spot GEX (محدّث)
# ─────────────────────────────────────────────
def step4_gex():
    info = {'gamma': 'unknown', 'delta': 'unknown', 'supports_calls': False, 'supports_puts': False}
    try:
        log("  Fetching Spot GEX for SPY...")
        resp = requests.get(f'{UW_BASE}/api/stock/SPY/spot-exposures/strike',
                            headers=UW_HEADERS, timeout=TIMEOUT)
        if resp.status_code != 200:
            log(f"  ⚠️ Spot GEX HTTP {resp.status_code}")
            return info
        data_list = resp.json().get('data', [])
        if isinstance(data_list, list) and data_list:
            # Aggregate across strikes
            total_call_gamma = 0
            total_put_gamma = 0
            total_call_delta = 0
            total_put_delta = 0
            for item in data_list:
                total_call_gamma += float(item.get('call_gamma', item.get('call_gex', 0)) or 0)
                total_put_gamma += float(item.get('put_gamma', item.get('put_gex', 0)) or 0)
                total_call_delta += float(item.get('call_delta', item.get('call_dex', 0)) or 0)
                total_put_delta += float(item.get('put_delta', item.get('put_dex', 0)) or 0)
            gamma = total_call_gamma + total_put_gamma
            info['gamma_value'] = gamma
            info['gamma'] = 'negative' if gamma < 0 else 'positive'
            info['call_delta'] = total_call_delta
            info['put_delta'] = total_put_delta
            if abs(total_call_delta) > abs(total_put_delta):
                info['delta'] = 'bullish'
                info['supports_calls'] = True
            else:
                info['delta'] = 'bearish'
                info['supports_puts'] = True
        elif isinstance(data_list, dict):
            gamma = float(data_list.get('gamma', data_list.get('gex', 0)) or 0)
            info['gamma_value'] = gamma
            info['gamma'] = 'negative' if gamma < 0 else 'positive'
        log(f"  GEX: Gamma={info['gamma']}, Delta={info['delta']}")
    except Exception as e:
        log(f"  ❌ GEX error: {e}")
    return info


# ─────────────────────────────────────────────
# Dark Pool Recent
# ─────────────────────────────────────────────
def fetch_darkpool_recent():
    log("Fetching Dark Pool Recent...")
    try:
        data = uw_get('/api/darkpool/recent')
        if data:
            trades = data.get('data', data.get('results', []))
            if isinstance(trades, list):
                # Sort by premium/size descending, take top 5
                for t in trades:
                    t['_size'] = float(t.get('premium', t.get('volume', t.get('size', 0))) or 0)
                trades.sort(key=lambda x: x['_size'], reverse=True)
                top5 = trades[:5]
                log(f"  ✅ Dark Pool: {len(trades)} trades, top 5 selected")
                return top5
        log("  ⚠️ Dark Pool: no data")
    except Exception as e:
        log(f"  ❌ Dark Pool error: {e}")
    return []


# ─────────────────────────────────────────────
# Congress Trades
# ─────────────────────────────────────────────
def fetch_congress_trades():
    log("Fetching Congress Trades...")
    try:
        data = uw_get('/api/congress/recent-trades')
        if data:
            trades = data.get('data', data.get('results', []))
            if isinstance(trades, list):
                top5 = trades[:5]
                log(f"  ✅ Congress Trades: {len(trades)} total, top 5 selected")
                return top5
        log("  ⚠️ Congress Trades: no data")
    except Exception as e:
        log(f"  ❌ Congress Trades error: {e}")
    return []


# ─────────────────────────────────────────────
# STEP 5: IV Rank + Contract Selection
# ─────────────────────────────────────────────
def step5_iv_rank(ticker):
    try:
        resp = requests.get(f'{UW_BASE}/api/stock/{ticker}/iv-rank',
                            headers=UW_HEADERS, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json().get('data', resp.json())
            if isinstance(data, list) and data:
                data = data[-1]
            rank = data.get('iv_rank_1y', data.get('iv_rank', None))
            if rank is not None:
                return float(rank)
    except:
        pass
    return None


def step5_contract_polygon(ticker, direction, price):
    if price <= 0:
        price = get_stock_price_yfinance(ticker)
        if price <= 0:
            return None

    today = datetime.now()
    exp_min = (today + timedelta(days=DTE_MIN)).strftime('%Y-%m-%d')
    exp_max = (today + timedelta(days=DTE_MAX)).strftime('%Y-%m-%d')
    contract_type = 'call' if direction == 'CALL' else 'put'

    if direction == 'CALL':
        strike_min = round(price * 1.00, 2)
        strike_max = round(price * 1.15, 2)
    else:
        strike_min = round(price * 0.85, 2)
        strike_max = round(price * 1.00, 2)

    data = polygon_get(f'/v3/snapshot/options/{ticker}', {
        'strike_price.gte': strike_min, 'strike_price.lte': strike_max,
        'expiration_date.gte': exp_min, 'expiration_date.lte': exp_max,
        'contract_type': contract_type, 'limit': 50, 'order': 'asc', 'sort': 'strike_price',
    })

    if not data or not data.get('results'):
        log(f"  ⚠️ No options data from Polygon for {ticker}")
        return None

    best = None
    best_score = -1

    for opt in data['results']:
        details = opt.get('details', {})
        greeks = opt.get('greeks', {})
        day_data = opt.get('day', {})
        last_quote = opt.get('last_quote', {})

        delta = abs(greeks.get('delta', 0))
        bid = last_quote.get('bid', 0) or 0
        ask = last_quote.get('ask', 0) or 0
        mid = round((bid + ask) / 2, 2) if bid > 0 and ask > 0 else 0
        oi = day_data.get('open_interest', 0) or 0
        volume = day_data.get('volume', 0) or 0
        iv = opt.get('implied_volatility', 0) or 0

        if delta < DELTA_MIN or delta > DELTA_MAX:
            continue
        if mid <= 0 or mid < PRICE_MIN or mid > PRICE_MAX:
            continue
        if oi < MIN_OI:
            continue
        if volume < MIN_VOLUME:
            continue
        spread = ask - bid
        spread_pct = spread / mid if mid > 0 else 999
        if spread_pct >= MAX_SPREAD_PCT:
            continue

        exp_str = details.get('expiration_date', '')
        try:
            dte = (datetime.strptime(exp_str, '%Y-%m-%d') - today).days
        except:
            dte = 0

        score = 0
        if DELTA_MIN <= delta <= DELTA_MAX:
            score += 2
        if spread_pct < MAX_SPREAD_PCT:
            score += 1
        if volume >= MIN_VOLUME:
            score += 1
        if oi >= MIN_OI:
            score += 1
        score += max(0, 1 - abs(delta - 0.30) * 10)

        if score > best_score:
            best_score = score
            best = {
                'symbol': ticker, 'strike': details.get('strike_price'),
                'expiry': exp_str, 'dte': dte,
                'right': 'C' if direction == 'CALL' else 'P',
                'bid': round(bid, 2), 'ask': round(ask, 2), 'mid': mid,
                'spread': round(spread, 2), 'spread_pct': round(spread_pct * 100, 1),
                'delta': round(delta, 3), 'gamma': round(greeks.get('gamma', 0), 4),
                'theta': round(greeks.get('theta', 0), 4), 'vega': round(greeks.get('vega', 0), 4),
                'iv': round(iv, 3), 'volume': int(volume), 'oi': int(oi),
                'direction': direction, 'contract_ticker': details.get('ticker', ''),
                'spread_ok': True,
            }
    return best


# ─────────────────────────────────────────────
# STEP 6: Scorecard
# ─────────────────────────────────────────────
def step6_scorecard(scanner_ok, news_score, flow_score, sweep_score, iv_rank, gex_supports, no_earnings, spread_ok):
    score = 0
    details = []
    if scanner_ok:
        score += 1; details.append("Scanner ✅")
    else:
        details.append("Scanner ❌")
    score += news_score; details.append(f"News {'✅' if news_score else '❌'}")
    score += flow_score
    details.append("Flow ✅✅" if flow_score == 2 else "Flow ✅" if flow_score == 1 else "Flow ❌")
    score += sweep_score; details.append(f"Sweep {'✅' if sweep_score else '❌'}")
    iv_ok = iv_rank is not None and 30 <= iv_rank <= 60
    if iv_ok:
        score += 1; details.append(f"IV Rank ✅ ({iv_rank:.0f}%)")
    else:
        details.append(f"IV Rank ❌ ({iv_rank:.0f}%)" if iv_rank is not None else "IV Rank ❌ (N/A)")
    if gex_supports:
        score += 1; details.append("GEX ✅")
    else:
        details.append("GEX ❌")
    if no_earnings:
        score += 1; details.append("No Earnings ✅")
    else:
        details.append("No Earnings ⚠️")
    if spread_ok:
        score += 1; details.append("Spread ✅")
    else:
        details.append("Spread ❌")
    return score, details


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────
def run_screener():
    log("=" * 50)
    log("🔍 Morning Screener v3.0 — Full Pipeline")
    log("=" * 50)

    # Market Tide
    market_tide = fetch_market_tide()

    # Dark Pool
    darkpool = fetch_darkpool_recent()

    # Congress Trades
    congress = fetch_congress_trades()

    # Step 1: Finviz Scanner (fallback)
    scanner = step1_finviz_scanner()

    # Step 1B: UW Options Screener
    uw_scanner = step1b_uw_options_screener()

    # Merge tickers (UW first, Finviz as fallback)
    all_tickers = []
    seen = set()
    for direction in ['bullish', 'bearish']:
        for t in uw_scanner[direction]:
            key = t['ticker']
            if key not in seen:
                seen.add(key)
                t['source'] = f'uw_{direction}'
                all_tickers.append(t)
        for t in scanner[direction]:
            key = t['ticker']
            if key not in seen:
                seen.add(key)
                t['source'] = f'finviz_{direction}'
                all_tickers.append(t)

    log(f"\nTotal unique tickers: {len(all_tickers)}")

    if not all_tickers:
        log("⚠️ No tickers — using fallback watchlist")
        for sym in ['TSLA', 'NVDA', 'AAPL', 'MSFT', 'AMZN', 'META', 'AMD', 'NFLX']:
            all_tickers.append({'ticker': sym, 'price': 0, 'change': 0, 'volume': 0, 'direction': 'CALL', 'source': 'fallback'})

    # Step 4: Spot GEX
    log("\nStep 4: Spot GEX Analysis...")
    gex_info = step4_gex()

    # Process candidates
    recommendations = []
    all_tickers.sort(key=lambda x: x.get('volume', 0), reverse=True)
    candidates = all_tickers[:20]

    for i, entry in enumerate(candidates):
        ticker = entry['ticker']
        direction = entry['direction']
        price = entry.get('price', 0)
        log(f"\n--- [{i+1}/{len(candidates)}] {ticker} ({direction}) ${price} ---")

        news_score, news_items, earnings_risk = step2_news_filter(ticker, direction)
        no_earnings = not earnings_risk
        log(f"  News: score={news_score}, earnings={earnings_risk}")

        flow_score, sweep_score, flow_details = step3_flow_analysis(ticker, direction)
        log(f"  Flow: {flow_score}/2, Sweep: {sweep_score}")

        iv_rank = step5_iv_rank(ticker)
        log(f"  IV Rank: {iv_rank}")

        contract = step5_contract_polygon(ticker, direction, price)
        spread_ok = contract.get('spread_ok', False) if contract else False

        if contract:
            log(f"  ✅ Contract: ${contract['strike']} {contract['expiry']} Δ{contract['delta']} mid=${contract['mid']}")
        else:
            log(f"  ⚠️ No contract passed filters")

        gex_supports = gex_info.get('supports_calls', False) if direction == 'CALL' else gex_info.get('supports_puts', False)

        score, score_details = step6_scorecard(True, news_score, flow_score, sweep_score, iv_rank, gex_supports, no_earnings, spread_ok)
        log(f"  📊 Score: {score}/9 — {', '.join(score_details)}")

        decision = '✅ دخول' if score >= 7 else '🟡 حجم أصغر' if score >= 5 else '❌ لا تدخل'

        rec = {
            'ticker': ticker, 'price': price, 'change': entry.get('change', 0),
            'direction': direction, 'source': entry.get('source', ''),
            'scorecard': score, 'scorecard_max': 9, 'scorecard_details': score_details,
            'decision': decision, 'news': news_items, 'flow_details': flow_details,
            'iv_rank': iv_rank, 'earnings_risk': earnings_risk, 'contract': contract,
        }

        if contract:
            mid = contract.get('mid', 0)
            if mid > 0:
                rec['tp1'] = round(mid * 1.25, 2)
                rec['tp2'] = round(mid * 1.50, 2)
                rec['sl'] = round(mid * 0.70, 2)
                rec['max_contracts'] = min(3, int(600 / (mid * 100))) if mid > 0 else 0

        recommendations.append(rec)

    recommendations.sort(key=lambda x: x['scorecard'], reverse=True)

    return {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'schedule': '12:00 UTC / 3:00 PM Riyadh',
        'scanner_counts': {
            'finviz_bullish': len(scanner['bullish']), 'finviz_bearish': len(scanner['bearish']),
            'uw_bullish': len(uw_scanner['bullish']), 'uw_bearish': len(uw_scanner['bearish']),
        },
        'market_tide': market_tide,
        'gex': gex_info,
        'darkpool': darkpool,
        'congress': congress,
        'total_candidates': len(candidates),
        'recommendations': recommendations,
    }


def format_morning_report(data):
    recs = data['recommendations']
    gex = data.get('gex', {})
    tide = data.get('market_tide', {})
    darkpool = data.get('darkpool', [])
    congress = data.get('congress', [])
    counts = data.get('scanner_counts', {})
    now = datetime.utcnow().strftime('%Y-%m-%d')

    lines = [
        f"📊 تقرير ما قبل الافتتاح — {now} (v3.0)",
        "",
        "🌡️ حالة السوق (Market Tide):",
    ]

    if tide:
        for key in ['net_call_premium', 'net_put_premium', 'call_premium', 'put_premium',
                     'bearish_premium', 'bullish_premium', 'net_premium', 'sentiment']:
            if key in tide:
                val = tide[key]
                if isinstance(val, (int, float)) and abs(val) > 1000:
                    lines.append(f"• {key}: ${val/1e6:.1f}M")
                else:
                    lines.append(f"• {key}: {val}")
    else:
        lines.append("• غير متوفر")

    lines += [
        "",
        f"📈 SPY Spot GEX: Gamma {gex.get('gamma', '?')} | Delta {gex.get('delta', '?')}",
        f"🔍 Scanners: Finviz {counts.get('finviz_bullish',0)}↑/{counts.get('finviz_bearish',0)}↓ | UW {counts.get('uw_bullish',0)}↑/{counts.get('uw_bearish',0)}↓",
        "",
    ]

    # Dark Pool
    if darkpool:
        lines.append("🏊 Dark Pool (أكبر 5 صفقات):")
        for dp in darkpool[:5]:
            ticker = dp.get('ticker', dp.get('symbol', '?'))
            prem = dp.get('premium', dp.get('volume', dp.get('size', '?')))
            if isinstance(prem, (int, float)) and prem > 1000:
                prem_str = f"${prem/1e6:.1f}M"
            else:
                prem_str = str(prem)
            lines.append(f"• {ticker}: {prem_str}")
        lines.append("")

    # Congress Trades
    if congress:
        lines.append("🏛️ Congress Trades (آخر 5):")
        for ct in congress[:5]:
            ticker = ct.get('ticker', ct.get('asset_description', '?'))
            tx_type = ct.get('transaction_type', ct.get('type', '?'))
            member = ct.get('representative', ct.get('politician', ct.get('member', '?')))
            amount = ct.get('amount', ct.get('range', '?'))
            lines.append(f"• {ticker} — {tx_type} by {member} ({amount})")
        lines.append("")

    # Recommendations
    calls = [r for r in recs if r['direction'] == 'CALL' and r['scorecard'] >= MIN_SCORE]
    puts = [r for r in recs if r['direction'] == 'PUT' and r['scorecard'] >= MIN_SCORE]

    for label, group in [("🟢 فرص CALL:", calls), ("🔴 فرص PUT:", puts)]:
        if not group:
            continue
        lines.append(label)
        for i, r in enumerate(group[:5], 1):
            c = r.get('contract') or {}
            lines.append(f"{i}. {r['ticker']} ${r['price']} | {'Call' if r['direction']=='CALL' else 'Put'} ${c.get('strike','?')} Exp {c.get('expiry','?')} بـ ${c.get('mid','?')}")
            if c:
                lines.append(f"   Greeks: Δ{c.get('delta','?')} Γ{c.get('gamma','?')} Θ{c.get('theta','?')} IV:{c.get('iv','?')}")
                lines.append(f"   OI: {c.get('oi','?')} | Vol: {c.get('volume','?')} | Spread: {c.get('spread_pct','?')}%")
            lines.append(f"   📰 {r['news'][0][:60]}..." if r.get('news') else "   📰 لا أخبار")
            lines.append(f"   📊 Score: {r['scorecard']}/9 — {r['decision']}")
            if r.get('tp1'):
                lines.append(f"   🟢 TP1: ${r['tp1']} | TP2: ${r['tp2']} | 🔴 SL: ${r['sl']}")
            lines.append(f"   {' | '.join(r['scorecard_details'])}")
            lines.append("")

    if not calls and not puts:
        lines.append("❌ لا توجد فرص تستوفي الشروط (Score ≥ 5/9)")

    earnings_tickers = [r['ticker'] for r in recs if r.get('earnings_risk')]
    if earnings_tickers:
        lines.append(f"\n⚠️ أرباح قريبة: {', '.join(earnings_tickers)}")

    return "\n".join(lines)


if __name__ == "__main__":
    data = run_screener()
    report = format_morning_report(data)
    print("\n" + report)
    out_path = '/home/openclaw/.openclaw/workspace/screener_result.json'
    with open(out_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    log(f"\n✅ Saved to {out_path}")
