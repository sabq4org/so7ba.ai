#!/usr/bin/env python3
"""تنفيذ صفقة فوري عبر IB Gateway — market order"""
import sys, asyncio, time
from ib_insync import *

def parse_args():
    """تحليل: buy/sell SYMBOL STRIKE+TYPE EXPIRY QTY"""
    if len(sys.argv) < 6:
        print("استخدام: python3 fast_trade.py buy SPX 6920P 2026-02-12 10")
        sys.exit(1)
    action = sys.argv[1].upper()  # BUY أو SELL
    symbol = sys.argv[2].upper()
    strike_str = sys.argv[3]
    expiry = sys.argv[4].replace("-", "")
    qty = int(sys.argv[5])
    right = strike_str[-1].upper()
    strike = float(strike_str[:-1])
    if action not in ("BUY", "SELL"):
        print("❌ الأمر لازم يكون buy أو sell")
        sys.exit(1)
    return action, symbol, strike, right, expiry, qty

def make_contract(symbol, strike, right, expiry):
    return Option(symbol, expiry, strike, right, "SMART", currency="USD")

async def main():
    action, symbol, strike, right, expiry, qty = parse_args()
    start = time.time()

    ib = IB()
    try:
        await ib.connectAsync("127.0.0.1", 4002, clientId=2, timeout=5)
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
    # إرسال أمر سوق فوري
    order = MarketOrder(action, qty)
    order.tif = "IOC"  # فوري أو إلغاء
    trade = ib.placeOrder(contract, order)

    print(f"⚡ {action} {qty}x {symbol} {strike}{right} {expiry} — أمر مرسل...")

    # متابعة التعبئة (أقصى 10 ثواني)
    for _ in range(100):
        await asyncio.sleep(0.1)
        if trade.isDone():
            break

    elapsed = time.time() - start
    status = trade.orderStatus.status

    if trade.fills:
        total_qty = sum(f.execution.shares for f in trade.fills)
        avg_price = sum(f.execution.shares * f.execution.price for f in trade.fills) / total_qty
        print(f"✅ تم التعبئة | الكمية: {total_qty} | السعر: {avg_price:.2f}")
    else:
        print(f"⏳ الحالة: {status}")

    print(f"⏱️ الوقت: {elapsed:.1f} ثانية")
    ib.disconnect()

if __name__ == "__main__":
    util.run(main())
