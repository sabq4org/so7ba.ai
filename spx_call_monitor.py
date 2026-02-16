#!/usr/bin/env python3
"""
📊 SPX 6900 Call Monitor — متابعة كل 5 دقائق
"""
import requests
import json
from datetime import datetime

POLYGON_KEY = "pbkeHwxpVSvr6tOr1kUH__UIUZzVlwUy"
SYMBOL = "O:SPXW260213C06900000"

def get_option_quote():
    """Get latest option data from Polygon"""
    # Try snapshot
    url = f"https://api.polygon.io/v3/snapshot/options/{SYMBOL}?apiKey={POLYGON_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if 'results' in data:
                res = data['results']
                day = res.get('day', {})
                greeks = res.get('greeks', {})
                details = res.get('details', {})
                underlying = res.get('underlying_asset', {})
                
                return {
                    'last': day.get('close') or day.get('last_price'),
                    'open': day.get('open'),
                    'high': day.get('high'),
                    'low': day.get('low'),
                    'volume': day.get('volume', 0),
                    'change': day.get('change'),
                    'change_pct': day.get('change_percent'),
                    'iv': res.get('implied_volatility'),
                    'delta': greeks.get('delta'),
                    'gamma': greeks.get('gamma'),
                    'theta': greeks.get('theta'),
                    'vega': greeks.get('vega'),
                    'bid': res.get('last_quote', {}).get('bid'),
                    'ask': res.get('last_quote', {}).get('ask'),
                    'spx_price': underlying.get('price') or underlying.get('last_updated_price'),
                    'strike': details.get('strike_price', 6900),
                }
    except Exception as e:
        pass
    
    # Fallback: last trade
    url2 = f"https://api.polygon.io/v3/trades/{SYMBOL}?limit=1&sort=timestamp&order=desc&apiKey={POLYGON_KEY}"
    try:
        r2 = requests.get(url2, timeout=10)
        if r2.status_code == 200:
            data2 = r2.json()
            if data2.get('results'):
                trade = data2['results'][0]
                return {'last': trade.get('price'), 'volume': trade.get('size')}
    except:
        pass
    
    return None

def format_report(data):
    if not data:
        return "⚠️ ما قدرت أجيب بيانات العقد"
    
    lines = []
    lines.append("📊 **SPXW 6900 Call — 13 Feb (0DTE)**")
    lines.append(f"⏰ {datetime.utcnow().strftime('%H:%M UTC')} ({(datetime.utcnow().hour + 3) % 24}:{datetime.utcnow().strftime('%M')} الرياض)")
    lines.append("")
    
    if data.get('spx_price'):
        diff = data['spx_price'] - 6900
        status = "ITM ✅" if diff > 0 else "OTM ❌" if diff < -5 else "ATM ≈"
        lines.append(f"📈 SPX: **{data['spx_price']:.2f}** ({status}, فرق: {diff:+.1f})")
    
    if data.get('last'):
        lines.append(f"💰 السعر: **${data['last']:.2f}**")
    
    if data.get('bid') and data.get('ask'):
        spread = data['ask'] - data['bid']
        lines.append(f"📊 Bid/Ask: ${data['bid']:.2f} / ${data['ask']:.2f} (spread: ${spread:.2f})")
    
    if data.get('change_pct') is not None:
        emoji = "🟢" if data['change_pct'] >= 0 else "🔴"
        lines.append(f"{emoji} التغيير: {data['change_pct']:+.1f}%")
    
    if data.get('volume'):
        lines.append(f"📦 الفوليوم: {data['volume']:,}")
    
    if data.get('iv'):
        lines.append(f"📐 IV: {data['iv']*100:.1f}%")
    
    if data.get('delta'):
        lines.append(f"🔧 Greeks: Δ{data['delta']:.3f} | Γ{data.get('gamma',0):.4f} | Θ{data.get('theta',0):.2f}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    data = get_option_quote()
    report = format_report(data)
    print(report)
