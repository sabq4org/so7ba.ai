#!/usr/bin/env python3
"""
📈 SPX Update v2.0 — صُحبة Trading
يستخدم Polygon minute aggs + Technical Indicators API
yFinance كـ fallback
"""
import requests
import json
from datetime import datetime, timezone, timedelta

POLYGON_KEY = '[REDACTED:POLYGON_KEY]'
POLYGON_BASE = 'https://api.polygon.io'
TIMEOUT = 15

riyadh = timezone(timedelta(hours=3))
now = datetime.now(riyadh)


def polygon_get(path, params=None):
    if params is None:
        params = {}
    params['apiKey'] = POLYGON_KEY
    try:
        resp = requests.get(f"{POLYGON_BASE}{path}", params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None


def get_spx_from_polygon():
    """بيانات SPY من Polygon minute aggs + تحويل تقريبي لـ SPX"""
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # SPY minute aggs لآخر يوم تداول
    data = polygon_get(f'/v2/aggs/ticker/SPY/range/1/minute/{yesterday}/{today}',
                       {'adjusted': 'true', 'sort': 'desc', 'limit': 5})
    if data and data.get('results'):
        bar = data['results'][0]
        return {
            'spy_price': bar['c'],
            'spy_high': bar['h'],
            'spy_low': bar['l'],
            'spy_open': bar['o'],
            'source': 'polygon_minute',
        }

    # Fallback: daily aggs
    data = polygon_get(f'/v2/aggs/ticker/SPY/range/1/day/{yesterday}/{today}',
                       {'adjusted': 'true', 'sort': 'desc', 'limit': 2})
    if data and data.get('results'):
        bar = data['results'][0]
        return {
            'spy_price': bar['c'],
            'spy_high': bar['h'],
            'spy_low': bar['l'],
            'spy_open': bar['o'],
            'source': 'polygon_daily',
        }
    return None


def get_indicators():
    """مؤشرات فنية لـ SPY من Polygon API مباشرة"""
    indicators = {}

    # RSI
    data = polygon_get('/v1/indicators/rsi/SPY', {'timespan': 'day', 'limit': 3, 'window': 14})
    if data and data.get('results', {}).get('values'):
        indicators['rsi'] = round(data['results']['values'][0]['value'], 1)

    # EMA 9
    data = polygon_get('/v1/indicators/ema/SPY', {'timespan': 'day', 'window': 9, 'limit': 3})
    if data and data.get('results', {}).get('values'):
        indicators['ema9'] = round(data['results']['values'][0]['value'], 2)

    # EMA 21
    data = polygon_get('/v1/indicators/ema/SPY', {'timespan': 'day', 'window': 21, 'limit': 3})
    if data and data.get('results', {}).get('values'):
        indicators['ema21'] = round(data['results']['values'][0]['value'], 2)

    # MACD
    data = polygon_get('/v1/indicators/macd/SPY', {'timespan': 'day', 'limit': 3})
    if data and data.get('results', {}).get('values'):
        macd_val = data['results']['values'][0]
        indicators['macd'] = round(macd_val.get('value', 0), 4)
        indicators['macd_signal'] = round(macd_val.get('signal', 0), 4)
        indicators['macd_histogram'] = round(macd_val.get('histogram', 0), 4)

    return indicators


def get_yfinance_fallback():
    """yFinance كـ fallback"""
    try:
        import yfinance as yf
        spy = yf.Ticker('SPY')
        si = spy.fast_info
        try:
            spx = yf.Ticker('^GSPC')
            xi = spx.fast_info
            return {
                'price': xi.last_price, 'prev': xi.previous_close,
                'high': xi.day_high, 'low': xi.day_low, 'open': xi.open,
                'spy': si.last_price, 'source': 'yfinance_spx',
            }
        except:
            ratio = 10.028
            return {
                'price': si.last_price * ratio, 'prev': si.previous_close * ratio,
                'high': si.day_high * ratio, 'low': si.day_low * ratio,
                'open': si.open * ratio,
                'spy': si.last_price, 'source': 'yfinance_spy_converted',
            }
    except Exception as e:
        return {'error': str(e)}


# === Main ===
result = {}

# محاولة Polygon أولاً
polygon_data = get_spx_from_polygon()
indicators = get_indicators()

if polygon_data:
    spy_price = polygon_data['spy_price']
    ratio = 10.028  # SPX/SPY تقريبي

    # نحاول نجيب SPX مباشرة من yFinance للسعر الدقيق
    yf_data = get_yfinance_fallback()
    if yf_data and 'price' in yf_data:
        price = yf_data['price']
        prev = yf_data['prev']
        high = yf_data['high']
        low = yf_data['low']
        opn = yf_data['open']
    else:
        price = spy_price * ratio
        prev = polygon_data.get('spy_open', spy_price) * ratio  # تقريب
        high = polygon_data['spy_high'] * ratio
        low = polygon_data['spy_low'] * ratio
        opn = polygon_data['spy_open'] * ratio
else:
    # Fallback كامل لـ yFinance
    yf_data = get_yfinance_fallback()
    if 'error' in yf_data:
        print(json.dumps({"error": yf_data['error']}, ensure_ascii=False))
        exit(1)
    price = yf_data['price']
    prev = yf_data['prev']
    high = yf_data['high']
    low = yf_data['low']
    opn = yf_data['open']
    spy_price = yf_data.get('spy', 0)

chg = price - prev
pct = (chg / prev) * 100 if prev else 0

# VIX
try:
    import yfinance as yf
    vix = yf.Ticker('^VIX')
    vix_price = vix.fast_info.last_price
    vix_prev = vix.fast_info.previous_close
    vix_chg = ((vix_price - vix_prev) / vix_prev) * 100
    vix_str = f"{vix_price:.2f} ({vix_chg:+.2f}%)"
except:
    vix_str = "غير متاح"

# Direction
if pct > 0.3:
    direction = "🟢🟢"
elif pct > 0:
    direction = "🟢"
elif pct > -0.3:
    direction = "🔴"
else:
    direction = "🔴🔴"

output = {
    "price": round(price, 2),
    "prev": round(prev, 2),
    "change": round(chg, 2),
    "change_pct": round(pct, 2),
    "high": round(high, 2),
    "low": round(low, 2),
    "open": round(opn, 2),
    "vix": vix_str,
    "direction": direction,
    "time": now.strftime("%I:%M %p"),
    "spy": round(spy_price, 2) if spy_price else 0,
    # === مؤشرات فنية من Polygon (جديد!) ===
    "indicators": indicators,
    "source": polygon_data.get('source', 'yfinance') if polygon_data else 'yfinance',
}

print(json.dumps(output, ensure_ascii=False))
