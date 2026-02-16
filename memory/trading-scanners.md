# 🔍 Trading Scanners & Strategy — صُحبة × أبو سلمان

تاريخ الإنشاء: 2026-02-10

---

## 📡 الأدوات المتاحة

### 1. Finviz Elite API
- **Auth Token:** `[REDACTED:FINVIZ_AUTH]`
- **Format:** CSV export
- **اشتراك:** أبو سلمان (Elite)

### 2. Massive/Polygon API
- **API Key:** الموجود في MEMORY.md
- **اشتراك:** أبو محمد (Advanced $149/شهر)
- **يشتغل:** أخبار Benzinga (`/v2/reference/news`) + Options Contracts + Last Trade
- **ما يشتغل:** Intraday bars + Benzinga direct endpoint + Snapshots

### 3. yFinance (مجاني)
- بيانات يومية + تاريخية
- Backup لما Polygon يوصل Rate Limit

---

## 🟢 Scanner 1: Bullish Momentum (Call)

**الاسم:** Bullish Momentum Scanner
**الهدف:** أسهم صاعدة بزخم + سيولة عالية = فرص Call

**الفلاتر:**
| الفلتر | القيمة |
|--------|--------|
| Exchange | NASDAQ, NYSE |
| Market Cap | +Mid (2B+) |
| Optionable | Yes |
| Institutional Ownership | Over 50% |
| Volatility Week | Over 3% |
| Change | Up +1% |
| Avg Volume | Over 2M |
| Relative Volume | Over 1.5 |
| Price | $20 - $300 |
| 20-Day SMA | Price above SMA20 |
| Beta | 1.2+ |

**API URL:**
```
https://elite.finviz.com/export.ashx?v=111&f=cap_midover,exch_nasd|nyse,sh_avgvol_o2000,sh_instown_o50,sh_opt_option,sh_price_20to300,sh_relvol_o1.5,ta_beta_1.2to,ta_change_u1,ta_sma20_pa,ta_volatility_wo3,tad_0_close::close:d&ft=4&o=volume&auth=[REDACTED:FINVIZ_AUTH]
```

**نتائج 10 فبراير (11 سهم):**
| Ticker | Company | القطاع | السعر | التغيير | الفوليوم |
|--------|---------|--------|-------|---------|----------|
| DDOG | Datadog | Software | $129.67 | +13.74% | 18.6M |
| CRDO | Credo Tech | Semiconductors | $134.72 | +9.16% | 12.3M |
| ENTG | Entegris | Semiconductors | $133.44 | +9.03% | 7.1M |
| MAS | Masco | Building | $77.82 | +8.67% | 6.7M |
| ESI | Element Solutions | Chemicals | $32.24 | +4.30% | 3.9M |
| VST | Vistra | Utilities/AI | $159.57 | +4.31% | 9M |
| HOG | Harley-Davidson | Vehicles | $20.96 | +4.07% | 9.7M |
| NET | Cloudflare | Software | $180.04 | +3.62% | 9.2M |
| ON | ON Semi | Semiconductors | $67.38 | +3.50% | 19.2M |
| NCLH | Norwegian Cruise | Travel | $23.56 | +3.11% | 29.6M |
| BN | Brookfield | Financial | $47.72 | +1.82% | 7M |

---

## 🔴 Scanner 2: Bearish Breakdown (Put)

**الاسم:** Bearish Breakdown Scanner
**الهدف:** أسهم هابطة بزخم = فرص Put

**الفلاتر المقترحة:**
| الفلتر | القيمة |
|--------|--------|
| Exchange | NASDAQ, NYSE |
| Market Cap | +Mid (2B+) |
| Optionable | Yes |
| Institutional Ownership | Over 50% |
| Volatility Week | Over 3% |
| Change | **Down -1%** |
| Avg Volume | Over 2M |
| Relative Volume | Over 1.5 |
| Price | $20 - $300 |
| 20-Day SMA | **Price below SMA20** |
| Beta | 1.2+ |

**API URL:**
```
https://elite.finviz.com/export.ashx?v=111&f=cap_midover,exch_nasd|nyse,sh_avgvol_o2000,sh_instown_o50,sh_opt_option,sh_price_20to300,sh_relvol_o1.5,ta_beta_1.2to3,ta_change_d1,ta_rsi_to40,ta_sma20_pb,ta_sma50_pb,ta_volatility_wo3,tad_0_close::close:d&ft=4&o=volume&auth=[REDACTED:FINVIZ_AUTH]
```
**تم اختباره:** ✅ يشتغل — سهم واحد (TPG) في يوم أخضر = منطقي

---

## 📰 News API — Benzinga via Polygon

**Endpoint:**
```
GET https://api.polygon.io/v2/reference/news?ticker={TICKER}&limit=5&order=desc&sort=published_utc&apiKey={KEY}
```

**البيانات المتاحة:**
- عنوان الخبر
- Sentiment (positive/negative/neutral)
- Sentiment reasoning
- Tickers المذكورة
- تاريخ النشر

**الاستخدام:**
- فحص كل سهم من السكانر قبل الدخول
- تنبيه لو في خبر سلبي على سهم صاعد (فخ!)
- تنبيه لو في CPI/Fed/Earnings قريب

---

## 📊 Options Chain — Polygon

**Contracts:**
```
GET https://api.polygon.io/v3/reference/options/contracts?underlying_ticker={TICKER}&expiration_date.gte={DATE}&contract_type=call&apiKey={KEY}
```

**Last Trade:**
```
GET https://api.polygon.io/v2/last/trade/{OPTIONS_TICKER}?apiKey={KEY}
```

---

## 🎯 خطة العمل (مقترحة — تحتاج اعتماد)

### الروتين اليومي:
1. **قبل الافتتاح (4:00 عصر بتوقيت الرياض)**
   - تشغيل Bullish + Bearish Scanners
   - سحب أخبار لكل سهم طالع
   - فحص التقويم الاقتصادي (CPI, Fed, Earnings)
   - إرسال تقرير جاهز للقروب

2. **وقت التداول (5:30 - 12:00)**
   - مراقبة أخبار لحظية
   - تحليل Options Chain للأسهم المختارة
   - تنبيه فوري لو في خبر مؤثر

3. **بعد الإقفال**
   - ملخص الأداء
   - تحديث الذاكرة
   - دروس مستفادة

### معايير اختيار العقد:
| المعيار | القيمة |
|---------|--------|
| Delta | 0.20 - 0.30 (من استراتيجية زلاتان) |
| سعر العقد | $2.50 - $6 |
| Take Profit | +25% |
| Stop Loss | -40% |
| الانتهاء | أسبوعي أو أسبوعين |

### تقييم السهم قبل الدخول:
- ✅ Scanner طلعه (Bullish أو Bearish)
- ✅ الأخبار تدعم الاتجاه
- ✅ Options سيولتها عالية (Volume + Open Interest)
- ✅ ما في حدث اقتصادي كبير قريب (أو جاهز له)
- ✅ السبريد معقول

---

## ⚠️ تحذيرات دائمة

1. **CPI / Fed / FOMC** = لا تدخل قبلها أو خفف الحجم
2. **Earnings** = تذبذب عالي، ممكن فرصة أو فخ
3. **Short Squeeze** = مغري بس خطير — حجم صغير فقط
4. **هذا تحليل مو توصية** — القرار دائماً للمتداول

---

## 📰 Finviz News Export API

- **v=3 (أخبار أسهم):** `https://elite.finviz.com/news_export.ashx?v=3&auth=[REDACTED:FINVIZ_AUTH]`
- **v=4 (أخبار إضافية):** `https://elite.finviz.com/news_export.ashx?v=4&auth=[REDACTED:FINVIZ_AUTH]`
- **Format:** CSV (Title, Source, Date, Url, Category, Ticker)
- **v=6:** فاضي ❌ | بدون v: يرجع HTML ❌
- **الاستخدام:** فلترة أخبار بالـ Ticker بعد السكانر
- **تم اختبارها:** ✅ 100 خبر لكل endpoint

---

## 🐋 Unusual Whales API

- **API Key:** `[REDACTED:UW_KEY]`
- **اشتراك:** أبو سلمان
- **Base URL:** `https://api.unusualwhales.com/api`
- **Auth Header:** `Authorization: Bearer {KEY}`
- **تم اختباره:** ✅ يشتغل

### Endpoints المهمة:
| Endpoint | الوصف |
|----------|-------|
| `/option-trades/flow-alerts?limit=10` | Flow Alerts — صفقات كبيرة لحظية |
| `/stock/{TICKER}/greek-exposure` | GEX — Gamma/Delta/Charm/Vanna |
| `/market/economic-calendar` | التقويم الاقتصادي (CPI, Fed, etc) |
| `/stock/{TICKER}/option-contracts?expiry={DATE}` | Options Chain كامل |
| `/darkpool/{TICKER}` | Darkpool trades |
| `/stock/{TICKER}/earnings` | أرباح + expected move |
| `/stock/{TICKER}/flow-per-strike?date={DATE}` | Flow per strike |
| `/stock/{TICKER}/flow-per-expiry?date={DATE}` | Flow per expiry |
| `/stock/{TICKER}/iv-rank` | IV Rank |
| `/market/news?limit=10` | أخبار لحظية |
| `/option-trades/flow-alerts?ticker={TICKER}` | Flow alerts لسهم معين |

### ⚠️ تصحيح CPI:
- **CPI يوم الخميس 13 فبراير** (مو 11 أو 12)
- Core CPI: توقع 2.5% vs سابق 2.6%
- CPI YoY: توقع 2.5% vs سابق 2.7%
- الوقت: 4:30 عصر بتوقيت الرياض

---

## 📝 ملاحظات

- الفلاتر قابلة للتعديل حسب ظروف السوق
- نحتاج نجرب لمدة أسبوع ونقيّم النتائج
- أبو سلمان يسوي الفلترة + أنا أحلل = فريق 🤝
