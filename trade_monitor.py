#!/usr/bin/env python3
"""
📊 Trade Monitor v2.0 — صُحبة Trading
يستخدم Polygon Options Snapshot لمراقبة العقود المفتوحة
- تابع Greeks (خصوصاً theta decay)
- تابع IV changes
- تنبيه إذا delta تغير بشكل كبير
TP: +25% بيع نصف → +50% بيع الباقي
SL: -30% خروج فوري
DTE ≤ 2 → خروج
"""
from ib_insync import *
import requests
import json
import os
from datetime import datetime

IB_HOST = '127.0.0.1'
IB_PORT = 4002
CLIENT_ID = 50
TRADES_LOG = '/home/openclaw/.openclaw/workspace/trades_log.json'

TP1_PCT = 0.25
TP2_PCT = 0.50
SL_PCT = -0.30
DTE_EXIT = 2
DELTA_ALERT_THRESHOLD = 0.10  # تنبيه إذا delta تغير أكثر من 0.10

POLYGON_KEY = '[REDACTED:POLYGON_KEY]'
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


def get_option_snapshot(symbol, expiry, strike, right):
    """جلب snapshot للعقد من Polygon مع Greeks + IV"""
    # تحويل expiry format
    if len(str(expiry)) == 8:
        exp_fmt = f"{expiry[:4]}-{expiry[4:6]}-{expiry[6:8]}"
    else:
        exp_fmt = str(expiry)

    contract_type = 'call' if right in ('C', 'CALL') else 'put'

    data = polygon_get(f'/v3/snapshot/options/{symbol}', {
        'strike_price': strike,
        'expiration_date': exp_fmt,
        'contract_type': contract_type,
        'limit': 1,
    })

    if data and data.get('results'):
        opt = data['results'][0]
        greeks = opt.get('greeks', {})
        quote = opt.get('last_quote', {})
        day = opt.get('day', {})
        return {
            'found': True,
            'bid': quote.get('bid', 0) or 0,
            'ask': quote.get('ask', 0) or 0,
            'mid': round((quote.get('bid', 0) + quote.get('ask', 0)) / 2, 2) if quote.get('bid') and quote.get('ask') else 0,
            'delta': round(greeks.get('delta', 0), 4),
            'gamma': round(greeks.get('gamma', 0), 4),
            'theta': round(greeks.get('theta', 0), 4),
            'vega': round(greeks.get('vega', 0), 4),
            'iv': round(opt.get('implied_volatility', 0), 4),
            'oi': day.get('open_interest', 0) or 0,
            'volume': day.get('volume', 0) or 0,
        }
    return {'found': False}


def load_trades():
    if os.path.exists(TRADES_LOG):
        with open(TRADES_LOG, 'r') as f:
            return json.load(f)
    return []


def save_trades(trades):
    with open(TRADES_LOG, 'w') as f:
        json.dump(trades, f, indent=2, default=str)


def monitor_all():
    trades = load_trades()
    open_trades = [t for t in trades if t.get('status') == 'OPEN']

    if not open_trades:
        print(json.dumps({"message": "No open trades to monitor"}))
        return

    # === أولاً: جلب بيانات من Polygon لكل عقد ===
    polygon_data = {}
    for trade in open_trades:
        key = f"{trade['symbol']}_{trade['expiry']}_{trade['strike']}_{trade['right']}"
        snap = get_option_snapshot(trade['symbol'], trade['expiry'], trade['strike'], trade['right'])
        polygon_data[key] = snap
        if snap.get('found'):
            print(f"✅ Polygon: {trade['symbol']} ${trade['strike']} — Δ{snap['delta']} Θ{snap['theta']} IV:{snap['iv']}")
        else:
            print(f"⚠️ Polygon: {trade['symbol']} — لا بيانات، نستخدم IB")

    # === ثانياً: IB للتنفيذ والأسعار الحية ===
    ib = IB()
    ib.connect(IB_HOST, IB_PORT, clientId=CLIENT_ID, timeout=15)
    ib.reqMarketDataType(3)

    results = []
    alerts = []  # تنبيهات مهمة

    for trade in open_trades:
        try:
            symbol = trade['symbol']
            expiry = trade['expiry']
            strike = trade['strike']
            right = trade['right']
            entry_price = trade['entry_price']
            qty = trade.get('qty_remaining', trade['qty'])
            tp1_hit = trade.get('tp1_hit', False)
            entry_greeks = trade.get('entry_greeks', {})

            # DTE
            exp_date = datetime.strptime(str(expiry), '%Y%m%d')
            dte = (exp_date - datetime.now()).days

            # بيانات Polygon
            key = f"{symbol}_{expiry}_{strike}_{right}"
            poly = polygon_data.get(key, {})

            # سعر من IB
            contract = Option(symbol, expiry, strike, right, 'SMART', '100', 'USD')
            ib.qualifyContracts(contract)
            [tk] = ib.reqTickers(contract)
            ib.sleep(3)

            bid = tk.bid if tk.bid and tk.bid > 0 else 0
            ask = tk.ask if tk.ask and tk.ask > 0 else 0
            mid = (bid + ask) / 2 if bid > 0 and ask > 0 else (tk.last or 0)
            current = mid if mid > 0 else (tk.last or 0)

            # استخدم Polygon mid لو IB ما عنده سعر
            if current <= 0 and poly.get('found') and poly.get('mid', 0) > 0:
                current = poly['mid']

            pnl_pct = ((current / entry_price) - 1) * 100 if entry_price > 0 and current > 0 else 0
            pnl_dollar = (current - entry_price) * 100 * qty

            # === تتبع تغيّر Greeks (جديد!) ===
            greeks_now = {}
            greeks_change = {}
            if poly.get('found'):
                greeks_now = {
                    'delta': poly['delta'], 'gamma': poly['gamma'],
                    'theta': poly['theta'], 'vega': poly['vega'],
                    'iv': poly['iv'],
                }
                # مقارنة مع Greeks وقت الدخول
                if entry_greeks:
                    for g in ['delta', 'gamma', 'theta', 'vega']:
                        old_val = entry_greeks.get(g, 0)
                        new_val = greeks_now.get(g, 0)
                        greeks_change[g] = round(new_val - old_val, 4)

                    # تنبيه delta
                    delta_change = abs(greeks_change.get('delta', 0))
                    if delta_change > DELTA_ALERT_THRESHOLD:
                        alert_msg = f"⚠️ {symbol} ${strike}: Delta تغير بـ {greeks_change['delta']:+.4f} (من {entry_greeks.get('delta',0)} إلى {greeks_now['delta']})"
                        alerts.append(alert_msg)

                    # تنبيه IV
                    iv_entry = trade.get('entry_iv', 0)
                    iv_now = poly['iv']
                    if iv_entry > 0 and iv_now > 0:
                        iv_change_pct = ((iv_now / iv_entry) - 1) * 100
                        if abs(iv_change_pct) > 15:
                            alerts.append(f"⚠️ {symbol} ${strike}: IV تغير {iv_change_pct:+.1f}% (من {iv_entry} إلى {iv_now})")

            # === قرار البيع ===
            action = "HOLD"
            sell_qty = 0

            if dte <= DTE_EXIT and qty > 0:
                action = "DTE_EXIT"
                sell_qty = qty
            elif current > 0 and pnl_pct <= SL_PCT * 100:
                action = "SL_EXIT"
                sell_qty = qty
            elif not tp1_hit and pnl_pct >= TP1_PCT * 100:
                action = "TP1_SELL_HALF"
                sell_qty = max(1, qty // 2)
            elif tp1_hit and pnl_pct >= TP2_PCT * 100:
                action = "TP2_SELL_REST"
                sell_qty = qty

            # تنفيذ البيع
            fill_price = 0
            if sell_qty > 0 and qty > 0:
                order = MarketOrder('SELL', sell_qty)
                t = ib.placeOrder(contract, order)
                for _ in range(15):
                    ib.sleep(2)
                    if t.orderStatus.status == 'Filled':
                        break
                fill_price = t.orderStatus.avgFillPrice or 0

                if action == "TP1_SELL_HALF":
                    trade['tp1_hit'] = True
                    trade['qty_remaining'] = qty - sell_qty
                elif action in ("TP2_SELL_REST", "SL_EXIT", "DTE_EXIT"):
                    trade['status'] = 'CLOSED'
                    trade['close_reason'] = action
                    trade['close_price'] = fill_price
                    trade['close_time'] = datetime.now().isoformat()
                    trade['qty_remaining'] = 0

            result = {
                "symbol": symbol, "strike": strike, "expiry": expiry,
                "dte": dte, "entry": entry_price, "current": round(current, 2),
                "pnl_pct": round(pnl_pct, 1), "pnl_dollar": round(pnl_dollar, 2),
                "qty": qty, "action": action, "sell_qty": sell_qty,
                "fill_price": round(fill_price, 2),
                # === بيانات Polygon الجديدة ===
                "greeks_now": greeks_now,
                "greeks_change": greeks_change,
            }
            results.append(result)

        except Exception as e:
            results.append({"symbol": trade.get('symbol', '?'), "error": str(e)})

    save_trades(trades)
    ib.disconnect()

    output = {"trades": results, "alerts": alerts}
    print(json.dumps(output, indent=2))

    # طباعة التنبيهات
    if alerts:
        print("\n🚨 === تنبيهات مهمة ===")
        for a in alerts:
            print(a)


if __name__ == "__main__":
    monitor_all()
