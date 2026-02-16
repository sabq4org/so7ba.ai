#!/usr/bin/env python3
"""متابعة سعر مستمرة — streaming من IB Gateway"""
import sys, asyncio, signal
from ib_insync import *

def parse_args():
    if len(sys.argv) < 4:
        print("استخدام: python3 fast_monitor.py SPX 6920P 2026-02-12")
        sys.exit(1)
    symbol = sys.argv[1].upper()
    strike_str = sys.argv[2]
    expiry = sys.argv[3].replace("-", "")
    right = strike_str[-1].upper()
    strike = float(strike_str[:-1])
    return symbol, strike, right, expiry

def make_contract(symbol, strike, right, expiry):
    return Option(symbol, expiry, strike, right, "SMART", currency="USD")

async def main():
    symbol, strike, right, expiry = parse_args()

    ib = IB()
    try:
        await ib.connectAsync("127.0.0.1", 4002, clientId=3, timeout=5)
    except Exception as e:
        print(f"❌ فشل الاتصال: {e}")
        sys.exit(1)

    contract = make_contract(symbol, strike, right, expiry)
    try:
        contracts = await ib.qualifyContractsAsync(contract)
        if not contracts:
            print(f"❌ العقد غير موجود")
            ib.disconnect()
            sys.exit(1)
    except Exception as e:
        print(f"❌ خطأ: {e}")
        ib.disconnect()
        sys.exit(1)

    contract = contracts[0]
    # تفعيل البيانات المؤجلة لو ما في اشتراك
    ib.reqMarketDataType(3)
    # اشتراك في البيانات الحية
    ticker = ib.reqMktData(contract)

    print(f"📡 مراقبة {symbol} {strike}{right} {expiry} — Ctrl+C للإيقاف")
    print("-" * 50)

    # إيقاف نظيف
    stop = asyncio.Event()
    def on_signal(*_): stop.set()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            asyncio.get_event_loop().add_signal_handler(sig, on_signal)
        except NotImplementedError:
            signal.signal(sig, on_signal)

    while not stop.is_set():
        await asyncio.sleep(1)
        ib.sleep(0)  # تحديث البيانات
        bid = f"{ticker.bid:.2f}" if ticker.bid == ticker.bid else "-"
        ask = f"{ticker.ask:.2f}" if ticker.ask == ticker.ask else "-"
        last = f"{ticker.last:.2f}" if ticker.last == ticker.last else "-"
        vol = ticker.volume if ticker.volume == ticker.volume else "-"
        print(f"  Bid: {bid} | Ask: {ask} | Last: {last} | Vol: {vol}")

    ib.cancelMktData(contract)
    ib.disconnect()
    print("\n👋 تم الإيقاف")

if __name__ == "__main__":
    util.run(main())
