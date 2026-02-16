#!/usr/bin/env python3
"""جلب سعر لحظي من IB Gateway — سريع ومباشر"""
import sys, asyncio
from ib_insync import *

def parse_args():
    """تحليل الأوامر: SYMBOL STRIKE+TYPE EXPIRY"""
    if len(sys.argv) < 4:
        print("استخدام: python3 fast_quote.py SPX 6920P 2026-02-12")
        sys.exit(1)
    symbol = sys.argv[1].upper()
    strike_str = sys.argv[2]
    expiry = sys.argv[3].replace("-", "")
    # فصل السعر عن النوع (P/C)
    right = strike_str[-1].upper()
    strike = float(strike_str[:-1])
    return symbol, strike, right, expiry

def make_contract(symbol, strike, right, expiry):
    """بناء العقد — يدعم SPX و SPY وأي سهم"""
    if symbol in ("SPX", "NDX", "RUT", "VIX"):
        return Option(symbol, expiry, strike, right, "SMART", currency="USD")
    elif symbol in ("SPY", "QQQ", "IWM", "AAPL", "TSLA", "AMZN", "MSFT", "GOOG", "META", "NVDA"):
        return Option(symbol, expiry, strike, right, "SMART", currency="USD")
    else:
        # محاولة كخيار على سهم
        return Option(symbol, expiry, strike, right, "SMART", currency="USD")

async def main():
    symbol, strike, right, expiry = parse_args()
    ib = IB()
    try:
        await ib.connectAsync("127.0.0.1", 4002, clientId=1, timeout=5)
    except Exception as e:
        print(f"❌ فشل الاتصال بـ IB Gateway: {e}")
        sys.exit(1)

    contract = make_contract(symbol, strike, right, expiry)
    # تأهيل العقد
    try:
        contracts = await ib.qualifyContractsAsync(contract)
        if not contracts:
            print(f"❌ العقد غير موجود: {symbol} {strike}{right} {expiry}")
            ib.disconnect()
            sys.exit(1)
    except Exception as e:
        print(f"❌ خطأ في تأهيل العقد: {e}")
        ib.disconnect()
        sys.exit(1)

    contract = contracts[0]
    # تفعيل البيانات المؤجلة لو ما في اشتراك
    ib.reqMarketDataType(3)  # 3 = delayed
    # طلب السعر
    ticker = ib.reqMktData(contract, genericTickList="", snapshot=True, regulatorySnapshot=False)
    # انتظار البيانات (أقصى 3 ثواني)
    for _ in range(30):
        await asyncio.sleep(0.1)
        if ticker.last == ticker.last or ticker.bid == ticker.bid:  # not NaN
            break

    bid = ticker.bid if ticker.bid == ticker.bid else "-"
    ask = ticker.ask if ticker.ask == ticker.ask else "-"
    last = ticker.last if ticker.last == ticker.last else "-"
    mid = ""
    if isinstance(bid, (int, float)) and isinstance(ask, (int, float)) and bid > 0 and ask > 0:
        mid = f" | Mid: {(bid + ask) / 2:.2f}"

    print(f"📊 {symbol} {strike}{right} {expiry}")
    print(f"   Bid: {bid} | Ask: {ask} | Last: {last}{mid}")

    ib.disconnect()

if __name__ == "__main__":
    util.run(main())
