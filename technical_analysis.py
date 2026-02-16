#!/usr/bin/env python3
"""
📊 نظام التحليل الفني — صُحبة Trading v2.0
يستخدم Polygon.io API للمؤشرات الفنية + Options Snapshot
yFinance كـ fallback لسعر السهم
"""
import requests
import numpy as np
import json
import sys
import time
from datetime import datetime, timedelta

# === إعدادات ===
POLYGON_KEY = 'pbkeHwxpVSvr6tOr1kUH__UIUZzVlwUy'
POLYGON_BASE = 'https://api.polygon.io'
TIMEOUT = 15


def polygon_get(path, params=None):
    """طلب من Polygon API"""
    if params is None:
        params = {}
    params['apiKey'] = POLYGON_KEY
    url = f"{POLYGON_BASE}{path}"
    resp = requests.get(url, params=params, timeout=TIMEOUT)
    if resp.status_code == 200:
        return resp.json()
    return None


def get_price_yfinance(symbol):
    """سعر السهم من yFinance (fallback)"""
    try:
        import yfinance as yf
        tk = yf.Ticker(symbol)
        info = tk.fast_info
        return {
            'price': info.last_price,
            'prev_close': info.previous_close,
            'high': info.day_high,
            'low': info.day_low,
            'open': info.open,
        }
    except Exception as e:
        return {'price': 0, 'error': str(e)}


def get_technical_indicators(symbol):
    """مؤشرات فنية من Polygon API مباشرة: RSI, EMA9, EMA21, MACD
    ملاحظة: Polygon يحد 5 طلبات/دقيقة — نضيف delay بين الطلبات"""
    indicators = {}

    # نجمع كل الطلبات مع delay بسيط لتجنب rate limit (5 req/min)
    calls = [
        ('rsi', f'/v1/indicators/rsi/{symbol}', {'timespan': 'day', 'limit': 5, 'window': 14}),
        ('ema9', f'/v1/indicators/ema/{symbol}', {'timespan': 'day', 'window': 9, 'limit': 5}),
        ('ema21', f'/v1/indicators/ema/{symbol}', {'timespan': 'day', 'window': 21, 'limit': 5}),
        ('macd', f'/v1/indicators/macd/{symbol}', {'timespan': 'day', 'limit': 5}),
    ]

    for name, path, params in calls:
        data = polygon_get(path, params)
        if data and data.get('results', {}).get('values'):
            val = data['results']['values'][0]
            if name == 'rsi':
                indicators['rsi'] = round(val['value'], 1)
            elif name in ('ema9', 'ema21'):
                indicators[name] = round(val['value'], 2)
            elif name == 'macd':
                indicators['macd'] = round(val.get('value', 0), 4)
                indicators['macd_signal'] = round(val.get('signal', 0), 4)
                indicators['macd_histogram'] = round(val.get('histogram', 0), 4)
        time.sleep(13)  # 5 req/min limit → ~12s بين الطلبات

    return indicators


def get_daily_aggs(symbol, days=20):
    """بيانات يومية من Polygon لحساب Support/Resistance و VWAP"""
    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=days + 5)).strftime('%Y-%m-%d')
    data = polygon_get(f'/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}',
                       {'adjusted': 'true', 'sort': 'asc', 'limit': days})
    if data and data.get('results'):
        return data['results']
    return []


def get_options_snapshot(symbol, price):
    """Options Snapshot — Greeks + IV + OI لأقرب ATM call/put"""
    today = datetime.now()
    exp_min = (today + timedelta(days=5)).strftime('%Y-%m-%d')
    exp_max = (today + timedelta(days=30)).strftime('%Y-%m-%d')
    strike_min = round(price * 0.97, 2)
    strike_max = round(price * 1.03, 2)

    options_data = {'calls': [], 'puts': []}

    for contract_type in ['call', 'put']:
        data = polygon_get(f'/v3/snapshot/options/{symbol}', {
            'strike_price.gte': strike_min,
            'strike_price.lte': strike_max,
            'expiration_date.gte': exp_min,
            'expiration_date.lte': exp_max,
            'contract_type': contract_type,
            'limit': 10,
            'order': 'asc',
            'sort': 'strike_price',
        })
        if data and data.get('results'):
            for opt in data['results']:
                details = opt.get('details', {})
                greeks = opt.get('greeks', {})
                day = opt.get('day', {})
                last_quote = opt.get('last_quote', {})
                options_data[contract_type + 's'].append({
                    'strike': details.get('strike_price'),
                    'expiry': details.get('expiration_date'),
                    'contract_type': contract_type,
                    'delta': round(greeks.get('delta', 0), 4),
                    'gamma': round(greeks.get('gamma', 0), 4),
                    'theta': round(greeks.get('theta', 0), 4),
                    'vega': round(greeks.get('vega', 0), 4),
                    'iv': round(opt.get('implied_volatility', 0), 4),
                    'oi': day.get('open_interest', 0),
                    'volume': day.get('volume', 0),
                    'bid': last_quote.get('bid', 0),
                    'ask': last_quote.get('ask', 0),
                    'mid': round((last_quote.get('bid', 0) + last_quote.get('ask', 0)) / 2, 2) if last_quote.get('bid') and last_quote.get('ask') else 0,
                })

    return options_data


def find_support_resistance(bars):
    """Support/Resistance من البيانات اليومية"""
    if not bars:
        return {'support': 0, 'resistance': 0, 's1': 0, 'r1': 0}
    highs = [b['h'] for b in bars]
    lows = [b['l'] for b in bars]
    return {
        'resistance': round(np.mean(sorted(highs, reverse=True)[:3]), 2),
        'support': round(np.mean(sorted(lows)[:3]), 2),
        'r1': round(max(highs), 2),
        's1': round(min(lows), 2),
    }


def analyze_symbol(symbol):
    """تحليل فني شامل لسهم واحد — Polygon API + yFinance"""

    # === سعر السهم (yFinance لأن Stock snapshot غير مصرح) ===
    price_data = get_price_yfinance(symbol)
    current_price = price_data.get('price', 0)
    prev_close = price_data.get('prev_close', current_price)
    change_pct = ((current_price / prev_close) - 1) * 100 if prev_close else 0

    if current_price == 0:
        return {'symbol': symbol, 'error': 'لا يوجد سعر', 'price': 0}

    # === مؤشرات فنية من Polygon API ===
    indicators = get_technical_indicators(symbol)
    rsi = indicators.get('rsi', 50)
    ema9 = indicators.get('ema9', current_price)
    ema21 = indicators.get('ema21', current_price)
    macd_hist = indicators.get('macd_histogram', 0)
    ema_signal = "BULLISH" if ema9 > ema21 else "BEARISH"

    # === بيانات يومية للـ Support/Resistance ===
    bars = get_daily_aggs(symbol, 20)
    sr = find_support_resistance(bars)

    # === VWAP تقريبي من آخر يوم ===
    vwap = current_price  # تقريب — Polygon ما يعطي intraday VWAP مباشرة
    if bars:
        last = bars[-1]
        vwap = round((last['h'] + last['l'] + last['c']) / 3, 2)
    vwap_signal = "ABOVE" if current_price > vwap else "BELOW"

    # === Options Snapshot — ATM Greeks ===
    options = get_options_snapshot(symbol, current_price)

    # أقرب ATM call
    atm_call = None
    if options['calls']:
        atm_call = min(options['calls'], key=lambda x: abs(x['strike'] - current_price) if x['strike'] else 999)
    atm_put = None
    if options['puts']:
        atm_put = min(options['puts'], key=lambda x: abs(x['strike'] - current_price) if x['strike'] else 999)

    # === حساب النقاط والتوصية ===
    score = 0
    signals = []

    # RSI
    if 30 <= rsi <= 45:
        score += 2
        signals.append(f"RSI {rsi:.0f} — منطقة شراء ✅")
    elif 45 < rsi <= 55:
        score += 1
        signals.append(f"RSI {rsi:.0f} — محايد")
    elif 55 < rsi <= 70:
        signals.append(f"RSI {rsi:.0f} — مرتفع ⚠️")
    elif rsi > 70:
        score -= 2
        signals.append(f"RSI {rsi:.0f} — مشبع شراء 🔴")
    elif rsi < 30:
        score -= 1
        signals.append(f"RSI {rsi:.0f} — مشبع بيع 🟢 (ممكن ارتداد)")

    # EMA
    if ema_signal == "BULLISH":
        score += 1
        signals.append("EMA9 > EMA21 — اتجاه صاعد ✅")
    else:
        score -= 1
        signals.append("EMA9 < EMA21 — اتجاه هابط ⚠️")

    # MACD
    if macd_hist > 0:
        score += 1
        signals.append(f"MACD Histogram إيجابي ({macd_hist:.4f}) ✅")
    elif macd_hist < 0:
        score -= 1
        signals.append(f"MACD Histogram سلبي ({macd_hist:.4f}) ⚠️")

    # VWAP
    if vwap_signal == "ABOVE":
        score += 1
        signals.append(f"فوق VWAP ({vwap:.2f}) — Bullish ✅")
    else:
        score -= 1
        signals.append(f"تحت VWAP ({vwap:.2f}) — Bearish ⚠️")

    # Support/Resistance proximity
    if sr['support'] > 0:
        price_vs_support = ((current_price - sr['support']) / sr['support']) * 100
        if price_vs_support < 0.5:
            score += 2
            signals.append(f"قريب من الدعم ({sr['support']}) — فرصة Call ✅✅")
    if sr['resistance'] > 0:
        price_vs_resistance = ((sr['resistance'] - current_price) / current_price) * 100
        if price_vs_resistance < 0.5:
            score += 2
            signals.append(f"قريب من المقاومة ({sr['resistance']}) — فرصة Put ✅✅")

    # التوصية
    if score >= 3:
        recommendation = "🟢 فرصة قوية — ادخل"
    elif score >= 1:
        recommendation = "🟡 فرصة متوسطة — راقب"
    elif score >= -1:
        recommendation = "⚪ محايد — انتظر"
    else:
        recommendation = "🔴 لا تدخل"

    # الاتجاه
    if ema_signal == "BULLISH" and vwap_signal == "ABOVE" and rsi < 70:
        direction = "CALL ☝️"
    elif ema_signal == "BEARISH" and vwap_signal == "BELOW" and rsi > 30:
        direction = "PUT 👇"
    else:
        direction = "انتظر ⏳"

    return {
        'symbol': symbol,
        'price': round(current_price, 2),
        'change_pct': round(change_pct, 2),
        'day_high': round(price_data.get('high', 0) or 0, 2),
        'day_low': round(price_data.get('low', 0) or 0, 2),
        'rsi': rsi,
        'ema9': ema9,
        'ema21': ema21,
        'ema_signal': ema_signal,
        'macd_histogram': macd_hist,
        'vwap': vwap,
        'vwap_signal': vwap_signal,
        'support': sr['support'],
        'resistance': sr['resistance'],
        's1': sr['s1'],
        'r1': sr['r1'],
        'score': score,
        'direction': direction,
        'recommendation': recommendation,
        'signals': signals,
        # === Options Greeks (جديد) ===
        'atm_call': atm_call,
        'atm_put': atm_put,
    }


def scan_market(symbols=None):
    """مسح السوق — تحليل فني لعدة أسهم"""
    if symbols is None:
        symbols = ['SPY', 'TSLA', 'NVDA', 'AAPL', 'MSFT', 'AMZN', 'META', 'AMD', 'GOOGL', 'NFLX']

    results = []
    for sym in symbols:
        try:
            r = analyze_symbol(sym)
            results.append(r)
            print(f"  ✅ {sym}")
        except Exception as e:
            results.append({'symbol': sym, 'error': str(e)})
            print(f"  ❌ {sym}: {e}")

    return results


def format_report(results):
    """تنسيق التقرير"""
    lines = ["📊 === تحليل فني — صُحبة Trading v2.0 ===\n"]
    opportunities = []

    for r in results:
        if 'error' in r:
            lines.append(f"❌ {r['symbol']}: {r['error']}\n")
            continue

        emoji = "🟢" if r['score'] >= 3 else "🟡" if r['score'] >= 1 else "⚪" if r['score'] >= -1 else "🔴"
        lines.append(f"{emoji} **{r['symbol']}** ${r['price']} ({r['change_pct']:+.1f}%)")
        lines.append(f"   RSI: {r['rsi']} | EMA: {r['ema_signal']} | MACD: {r['macd_histogram']}")
        lines.append(f"   دعم: {r['support']} | مقاومة: {r['resistance']}")
        lines.append(f"   التوصية: {r['recommendation']} — {r['direction']}")

        # عرض Options Greeks لو متوفرة
        if r.get('atm_call'):
            c = r['atm_call']
            lines.append(f"   📞 ATM Call ${c['strike']}: Δ{c['delta']} Θ{c['theta']} IV{c['iv']} OI:{c['oi']}")
        if r.get('atm_put'):
            p = r['atm_put']
            lines.append(f"   📉 ATM Put  ${p['strike']}: Δ{p['delta']} Θ{p['theta']} IV{p['iv']} OI:{p['oi']}")
        lines.append("")

        if r['score'] >= 2:
            opportunities.append(r)

    if opportunities:
        lines.append("\n🎯 === أفضل الفرص ===\n")
        for opp in sorted(opportunities, key=lambda x: x['score'], reverse=True):
            lines.append(f"🔥 {opp['symbol']} — {opp['direction']}")
            for sig in opp['signals']:
                lines.append(f"   • {sig}")
            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    symbols = sys.argv[1:] if len(sys.argv) > 1 else None
    print("🔄 جاري التحليل الفني (Polygon API + yFinance)...\n")
    results = scan_market(symbols)
    report = format_report(results)
    print(report)

    with open('/home/openclaw/.openclaw/workspace/market_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print("✅ تم حفظ النتائج في market_analysis.json")
