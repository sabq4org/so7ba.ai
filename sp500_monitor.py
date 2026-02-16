#!/usr/bin/env python3
import urllib.request
import re
from datetime import datetime, timezone

def get_sp500_data():
    url = "https://www.google.com/finance/quote/.INX:INDEXSP"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        return None
    
    data = {}
    
    # Current price
    price_match = re.search(r'data-last-price="([^"]+)"', html)
    data['price'] = float(price_match.group(1)) if price_match else None
    
    # Previous close and ranges from P6K39c class
    p6k_matches = re.findall(r'class="P6K39c">([^<]+)<', html)
    if len(p6k_matches) >= 1:
        data['prev_close'] = float(p6k_matches[0].replace(',', ''))
    if len(p6k_matches) >= 2:
        day_range = p6k_matches[1].split(' - ')
        if len(day_range) == 2:
            data['day_low'] = float(day_range[0].replace(',', ''))
            data['day_high'] = float(day_range[1].replace(',', ''))
    
    # Calculate changes
    if data.get('price') and data.get('prev_close'):
        data['change'] = data['price'] - data['prev_close']
        data['change_pct'] = (data['change'] / data['prev_close']) * 100
    
    return data

def analyze_market(data):
    """Technical reading"""
    if not data or not data.get('change_pct'):
        return "📊 بيانات غير كافية"
    
    price = data['price']
    change_pct = data['change_pct']
    
    lines = []
    
    # Trend strength
    if change_pct > 1.5:
        lines.append("🚀 **رالي قوي** — زخم شرائي عالي")
    elif change_pct > 0.5:
        lines.append("🟢 **صعود صحي** — المشترون مسيطرون")
    elif change_pct > 0:
        lines.append("🟢 **صعود طفيف** — تماسك إيجابي")
    elif change_pct > -0.5:
        lines.append("🟡 **تراجع طفيف** — جني أرباح محدود")
    elif change_pct > -1.5:
        lines.append("🔴 **ضغط بيعي** — حذر مطلوب")
    else:
        lines.append("🔴 **هبوط حاد** — موجة تصحيح")
    
    # Position in day range
    if data.get('day_high') and data.get('day_low'):
        day_range = data['day_high'] - data['day_low']
        if day_range > 0:
            position = (price - data['day_low']) / day_range * 100
            if position > 80:
                lines.append("📍 قرب أعلى اليوم")
            elif position < 20:
                lines.append("📍 قرب أدنى اليوم")
    
    # Key psychological levels
    if price > 7000:
        lines.append("🎯 اختراق 7000 — مستوى نفسي مهم!")
    elif price > 6900:
        lines.append("🎯 يختبر 7000")
    
    return "\n".join(lines)

def market_status():
    """Check if US market is open"""
    now = datetime.now(timezone.utc)
    hour = now.hour
    weekday = now.weekday()
    
    # Market hours: 14:30-21:00 UTC (9:30-4:00 ET), Mon-Fri
    if weekday >= 5:
        return "🔒 السوق مغلق (عطلة نهاية الأسبوع)"
    elif hour < 14 or (hour == 14 and now.minute < 30):
        return "🔒 السوق لم يفتح بعد"
    elif hour >= 21:
        return "🔒 السوق أغلق"
    else:
        return "🟢 السوق مفتوح"

if __name__ == "__main__":
    data = get_sp500_data()
    
    now = datetime.now(timezone.utc).strftime("%H:%M UTC")
    riyadh_hour = (datetime.now(timezone.utc).hour + 3) % 24
    riyadh_time = f"{riyadh_hour}:{datetime.now(timezone.utc).strftime('%M')} بتوقيت الرياض"
    
    print(f"📊 **S&P 500** — {riyadh_time}")
    print(f"⏰ {market_status()}")
    print()
    
    if data and data.get('price'):
        price = data['price']
        print(f"💰 **{price:,.2f}**")
        
        if data.get('change') is not None:
            change = data['change']
            change_pct = data['change_pct']
            sign = "+" if change >= 0 else ""
            emoji = "🟢" if change >= 0 else "🔴"
            print(f"{emoji} {sign}{change:,.2f} ({sign}{change_pct:.2f}%)")
        
        if data.get('day_low') and data.get('day_high'):
            print(f"📏 نطاق اليوم: {data['day_low']:,.2f} - {data['day_high']:,.2f}")
        
        print()
        print("**📖 القراءة:**")
        print(analyze_market(data))
    else:
        print("⚠️ تعذر جلب البيانات")
