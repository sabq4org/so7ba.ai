#!/usr/bin/env python3
"""
🤖 Trade Executor v2.0 — صُحبة Trading
- تحقق من Options Last Trade + Quotes من Polygon قبل التنفيذ
- تأكد الـ spread معقول
- سجّل Greeks وقت الدخول
- حد 20% من رأس المال لكل صفقة
- حد 3 صفقات مفتوحة
"""
from ib_insync import *
import requests
import json
import sys
import os
from datetime import datetime

IB_HOST = '127.0.0.1'
IB_PORT = 4002
CLIENT_ID = 80
TRADES_LOG = '/home/openclaw/.openclaw/workspace/trades_log.json'
MAX_POSITION_PCT = 0.20
MAX_OPEN_TRADES = 3
MAX_SPREAD_PCT = 0.20  # أقصى spread مقبول

POLYGON_KEY = 'pbkeHwxpVSvr6tOr1kUH__UIUZzVlwUy'
POLYGON_BASE = 'https://api.polygon.io'
TIMEOUT = 15


def polygon_get(path, params=None):
    if params is None:
        params = {}
    params['apiKey'] = POLYGON_KEY
    resp = requests.get(f"{POLYGON_BASE}{path}", params=params, timeout=TIMEOUT)
    if resp.status_code == 200:
        return resp.json()
    return None


def get_option_ticker(symbol, expiry, strike, right):
    """بناء Option ticker بصيغة Polygon: O:AAPL250221C00230000"""
    r = 'C' if right in ('C', 'CALL') else 'P'
    # expiry: YYYYMMDD → YYMMDD
    if len(expiry) == 8:
        exp_short = expiry[2:]
    elif len(expiry) == 10:  # YYYY-MM-DD
        exp_short = expiry[2:4] + expiry[5:7] + expiry[8:10]
    else:
        exp_short = expiry
    strike_fmt = f"{int(strike * 1000):08d}"
    return f"O:{symbol}{exp_short}{r}{strike_fmt}"


def verify_option_polygon(symbol, expiry, strike, right):
    """تحقق من العقد عبر Polygon: Last Trade + Quotes + Greeks"""
    opt_ticker = get_option_ticker(symbol, expiry, strike, right)
    result = {'verified': False, 'opt_ticker': opt_ticker}

    # Last Trade
    data = polygon_get(f'/v3/trades/{opt_ticker}', {'limit': 1, 'order': 'desc', 'sort': 'timestamp'})
    if data and data.get('results'):
        last = data['results'][0]
        result['last_trade_price'] = last.get('price', 0)
        result['last_trade_size'] = last.get('size', 0)
        result['last_trade_time'] = last.get('sip_timestamp', '')

    # Snapshot للـ Greeks + bid/ask
    # نستخدم snapshot endpoint مباشرة
    snap = polygon_get(f'/v3/snapshot/options/{symbol}', {
        'strike_price': strike,
        'expiration_date': expiry if '-' in str(expiry) else f"{expiry[:4]}-{expiry[4:6]}-{expiry[6:8]}",
        'contract_type': 'call' if right in ('C', 'CALL') else 'put',
        'limit': 1,
    })
    if snap and snap.get('results'):
        opt = snap['results'][0]
        greeks = opt.get('greeks', {})
        quote = opt.get('last_quote', {})
        result['bid'] = quote.get('bid', 0) or 0
        result['ask'] = quote.get('ask', 0) or 0
        result['mid'] = round((result['bid'] + result['ask']) / 2, 2) if result['bid'] > 0 and result['ask'] > 0 else 0
        spread = result['ask'] - result['bid']
        result['spread'] = round(spread, 2)
        result['spread_pct'] = round(spread / result['mid'] * 100, 1) if result['mid'] > 0 else 999

        # Greeks وقت الدخول
        result['greeks'] = {
            'delta': round(greeks.get('delta', 0), 4),
            'gamma': round(greeks.get('gamma', 0), 4),
            'theta': round(greeks.get('theta', 0), 4),
            'vega': round(greeks.get('vega', 0), 4),
        }
        result['iv'] = round(opt.get('implied_volatility', 0), 4)
        result['oi'] = opt.get('day', {}).get('open_interest', 0)

        # تحقق الـ spread معقول
        result['spread_ok'] = result['spread_pct'] < (MAX_SPREAD_PCT * 100)
        result['verified'] = True

    return result


def load_trades():
    if os.path.exists(TRADES_LOG):
        with open(TRADES_LOG, 'r') as f:
            return json.load(f)
    return []


def save_trades(trades):
    with open(TRADES_LOG, 'w') as f:
        json.dump(trades, f, indent=2, default=str)


def get_account_value(ib):
    for item in ib.accountSummary():
        if item.tag == 'NetLiquidation':
            return float(item.value)
    return 0


def count_open_trades():
    trades = load_trades()
    return sum(1 for t in trades if t.get('status') == 'OPEN')


def execute_order(symbol, expiry, strike, right, qty, order_type='MKT', limit_price=None):
    # === تحقق من Polygon أولاً (جديد!) ===
    print(f"🔍 التحقق من العقد عبر Polygon API...")
    verification = verify_option_polygon(symbol, expiry, strike, right)

    if verification.get('verified'):
        print(f"  ✅ Bid: ${verification['bid']} | Ask: ${verification['ask']} | Mid: ${verification['mid']}")
        print(f"  📊 Spread: {verification['spread_pct']}%")
        print(f"  📈 Greeks: Δ{verification['greeks']['delta']} Θ{verification['greeks']['theta']} IV:{verification['iv']}")

        if not verification.get('spread_ok'):
            return {
                "status": "REJECTED",
                "message": f"Spread too wide: {verification['spread_pct']}% > {MAX_SPREAD_PCT*100}%",
                "verification": verification,
            }
    else:
        print(f"  ⚠️ لم يتم التحقق من Polygon — متابعة بدون تأكيد")

    # === تنفيذ عبر IB ===
    ib = IB()
    ib.connect(IB_HOST, IB_PORT, clientId=CLIENT_ID, timeout=15)

    open_count = count_open_trades()
    if open_count >= MAX_OPEN_TRADES:
        ib.disconnect()
        return {"status": "REJECTED", "message": f"Max {MAX_OPEN_TRADES} open trades reached ({open_count} open)"}

    net_liq = get_account_value(ib)
    max_cost = net_liq * MAX_POSITION_PCT

    contract = Option(symbol, expiry, strike, right, 'SMART', '100', 'USD')
    ib.qualifyContracts(contract)

    if contract.conId == 0:
        ib.disconnect()
        return {"status": "ERROR", "message": "عقد غير موجود"}

    ib.reqMarketDataType(3)
    [tk] = ib.reqTickers(contract)
    ib.sleep(2)
    bid = tk.bid if tk.bid and tk.bid > 0 else 0
    ask = tk.ask if tk.ask and tk.ask > 0 else 0
    est_price = (bid + ask) / 2 if bid > 0 and ask > 0 else (tk.last or 0)
    est_cost = est_price * 100 * qty

    if est_cost > max_cost and net_liq > 0:
        max_qty = int(max_cost / (est_price * 100)) if est_price > 0 else 0
        ib.disconnect()
        return {"status": "REJECTED", "message": f"Cost ${est_cost:.0f} exceeds 20% limit (${max_cost:.0f}). Max qty: {max_qty}", "max_qty": max_qty}

    if order_type == 'MKT':
        order = MarketOrder('BUY', qty)
    else:
        order = LimitOrder('BUY', qty, limit_price)

    trade = ib.placeOrder(contract, order)
    for _ in range(15):
        ib.sleep(2)
        if trade.orderStatus.status == 'Filled':
            break

    status = trade.orderStatus.status
    fill_price = trade.orderStatus.avgFillPrice
    filled = trade.orderStatus.filled

    account = {}
    for item in ib.accountSummary():
        if item.tag in ('NetLiquidation', 'TotalCashValue'):
            account[item.tag] = item.value

    ib.disconnect()

    result = {
        "status": status,
        "symbol": symbol,
        "strike": strike,
        "right": "Call" if right == 'C' else "Put",
        "expiry": expiry,
        "qty": int(filled),
        "fill_price": round(fill_price, 2) if fill_price else 0,
        "total_cost": round(fill_price * 100 * filled, 2) if fill_price else 0,
        "tp1_price": round(fill_price * 1.25, 2) if fill_price else 0,
        "tp2_price": round(fill_price * 1.50, 2) if fill_price else 0,
        "sl_price": round(fill_price * 0.70, 2) if fill_price else 0,
        "account": account,
        # === Greeks وقت الدخول (جديد!) ===
        "entry_greeks": verification.get('greeks', {}),
        "entry_iv": verification.get('iv', 0),
        "polygon_verification": verification.get('verified', False),
    }

    # تسجيل الصفقة مع Greeks
    if status == 'Filled' and fill_price:
        trades = load_trades()
        trades.append({
            "id": len(trades) + 1,
            "symbol": symbol,
            "strike": strike,
            "right": right,
            "expiry": expiry,
            "qty": int(filled),
            "qty_remaining": int(filled),
            "entry_price": round(fill_price, 2),
            "total_cost": round(fill_price * 100 * filled, 2),
            "tp1_hit": False,
            "status": "OPEN",
            "open_time": datetime.now().isoformat(),
            # === بيانات Polygon الجديدة ===
            "entry_greeks": verification.get('greeks', {}),
            "entry_iv": verification.get('iv', 0),
            "entry_oi": verification.get('oi', 0),
        })
        save_trades(trades)

    return result


def close_position(symbol, expiry, strike, right, qty):
    ib = IB()
    ib.connect(IB_HOST, IB_PORT, clientId=81, timeout=15)
    contract = Option(symbol, expiry, strike, right, 'SMART', '100', 'USD')
    ib.qualifyContracts(contract)
    order = MarketOrder('SELL', qty)
    trade = ib.placeOrder(contract, order)
    for _ in range(15):
        ib.sleep(2)
        if trade.orderStatus.status == 'Filled':
            break
    fill_price = trade.orderStatus.avgFillPrice
    result = {"status": trade.orderStatus.status, "fill_price": round(fill_price, 2) if fill_price else 0, "qty_sold": int(trade.orderStatus.filled)}
    if trade.orderStatus.status == 'Filled':
        trades = load_trades()
        for t in trades:
            if t.get('symbol') == symbol and t.get('expiry') == expiry and t.get('strike') == strike and t.get('status') == 'OPEN':
                t['status'] = 'CLOSED'
                t['close_price'] = round(fill_price, 2) if fill_price else 0
                t['close_time'] = datetime.now().isoformat()
                t['close_reason'] = 'MANUAL'
                break
        save_trades(trades)
    ib.disconnect()
    return result


def get_portfolio():
    ib = IB()
    ib.connect(IB_HOST, IB_PORT, clientId=82, timeout=15)
    ib.reqMarketDataType(3)
    positions = ib.positions()
    portfolio = []
    for p in positions:
        if p.position != 0:
            [tk] = ib.reqTickers(p.contract)
            ib.sleep(2)
            mid = 0
            if tk.bid and tk.ask and tk.bid > 0 and tk.ask > 0:
                mid = (tk.bid + tk.ask) / 2
            elif tk.last:
                mid = tk.last
            entry = p.avgCost / 100
            pnl_pct = ((mid / entry) - 1) * 100 if entry > 0 and mid > 0 else 0
            pnl_dollar = (mid - entry) * 100 * abs(p.position) if mid > 0 else 0
            portfolio.append({
                "symbol": p.contract.localSymbol, "qty": int(p.position),
                "entry": round(entry, 2), "current": round(mid, 2),
                "pnl_pct": round(pnl_pct, 1), "pnl_dollar": round(pnl_dollar, 2),
            })
    account = {}
    for item in ib.accountSummary():
        if item.tag in ('NetLiquidation', 'TotalCashValue', 'UnrealizedPnL', 'BuyingPower'):
            account[item.tag] = item.value
    ib.disconnect()
    return {"positions": portfolio, "account": account}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: execute_trade.py [buy|sell|portfolio|verify]")
        print("  verify SYMBOL EXPIRY STRIKE RIGHT  — تحقق من العقد بدون تنفيذ")
        sys.exit(1)

    action = sys.argv[1]

    if action == 'verify' and len(sys.argv) >= 6:
        # تحقق فقط بدون تنفيذ
        result = verify_option_polygon(sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5])
        print(json.dumps(result, indent=2))
    elif action == 'portfolio':
        result = get_portfolio()
        print(json.dumps(result, indent=2))
    elif action == 'buy' and len(sys.argv) >= 7:
        result = execute_order(sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5], int(sys.argv[6]))
        print(json.dumps(result, indent=2))
    elif action == 'sell' and len(sys.argv) >= 7:
        result = close_position(sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5], int(sys.argv[6]))
        print(json.dumps(result, indent=2))
    else:
        print("Usage: execute_trade.py [buy|sell|portfolio|verify] ...")
