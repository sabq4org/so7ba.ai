from weasyprint import HTML
from PIL import Image, ImageDraw, ImageFont
import pikepdf, PyPDF2, io, subprocess, base64

# ===== Volleyball icon (circle with lines) =====
size = 420
img = Image.new('RGBA', (size, size), (0,0,0,0))
draw = ImageDraw.Draw(img)
# White ball
draw.ellipse((10,10,size-10,size-10), fill=(255,255,255,240))
# Lines on ball
draw.arc((10,10,size-10,size-10), 0, 360, fill=(180,180,180,200), width=4)
draw.arc((60,10,size-60,size-10), 30, 150, fill=(180,180,180,180), width=3)
draw.arc((10,60,size-10,size-60), 120, 240, fill=(180,180,180,180), width=3)
draw.line((size//2, 10, size//2, size-10), fill=(180,180,180,150), width=3)
draw.line((10, size//2, size-10, size//2), fill=(180,180,180,150), width=3)

# Gold border
bs = size + 28
result = Image.new('RGBA', (bs, bs), (0,0,0,0))
bd = Image.new('RGBA', (bs, bs), (0,0,0,0))
ImageDraw.Draw(bd).ellipse((0,0,bs-1,bs-1), fill=(197,160,55,200))
ImageDraw.Draw(bd).ellipse((9,9,bs-10,bs-10), fill=(0,0,0,0))
result.paste(bd,(0,0),bd)
result.paste(img,(14,14),img)
buf = io.BytesIO()
result.save(buf,'PNG')
ball_url = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

# ===== Embed Cairo =====
with open('/home/openclaw/.local/share/fonts/Cairo.ttf','rb') as f:
    CAIRO_B64 = base64.b64encode(f.read()).decode()
CAIRO_URL = f"data:font/truetype;base64,{CAIRO_B64}"

# ===== Schedule =====
# Double round-robin: 4 teams
schedule = [
    # Day, Date, Match1, Match2
    ("اليوم 1", "الخميس — ٢ رمضان", (1,2), (3,4)),
    ("اليوم 2", "الاثنين — ٦ رمضان", (1,3), (2,4)),
    ("اليوم 3", "الخميس — ٩ رمضان", (1,4), (2,3)),
    ("اليوم 4", "الاثنين — ١٣ رمضان", (2,1), (4,3)),
    ("اليوم 5", "الخميس — ١٦ رمضان", (3,1), (4,2)),
    ("اليوم 6", "الاثنين — ٢٠ رمضان", (4,1), (3,2)),
]

FONT_CSS = f"@font-face {{ font-family: 'Cairo'; src: url('{CAIRO_URL}') format('truetype'); font-weight: 100 900; font-style: normal; }}\n"

CSS = FONT_CSS + """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Cairo', 'Arial', sans-serif; direction: rtl; background: #fff; color: #1a1a2e; }
.cover { width: 210mm; height: 297mm; overflow: hidden;
  background: linear-gradient(160deg, #07111f 0%, #0f2540 38%, #1a3a5c 62%, #0a1c32 100%);
  display: flex; flex-direction: column; position: relative; }
.gold-bar { height: 8mm; background: linear-gradient(90deg,#7a5510,#c5a037,#f0d060,#c5a037,#7a5510); flex-shrink:0; position:relative; z-index:10; }
.cr-big { position:absolute; top:14mm; left:5mm; font-size:80px; color:#c5a037; opacity:0.28; z-index:2; line-height:1; transform:rotate(15deg); }
.cr-small { position:absolute; bottom:24mm; right:8mm; font-size:48px; color:#c5a037; opacity:0.16; z-index:2; line-height:1; transform:rotate(-15deg); }
.star { position:absolute; color:#f0d060; z-index:3; }
.frame { position:absolute; top:14mm; left:11mm; right:11mm; bottom:14mm; border:1.5px solid rgba(197,160,55,0.4); border-radius:6px; z-index:4; }
.cover-body { position:relative; z-index:10; flex:1; display:flex; flex-direction:column; align-items:stretch; padding:0 18mm; }
.cover-body > * { width:100%; text-align:center; margin-right:0; margin-left:0; }
.cover-spacer { flex:1; min-height:0; }
.cover-game-img { display:block; width:44mm; height:44mm; margin:0 auto 4mm auto; object-fit:contain; }
.badge { display:block; max-width:100mm; margin:0 auto 4mm auto; border:1px solid rgba(197,160,55,0.5); background:rgba(197,160,55,0.1); color:#c5a037; font-size:9px; font-weight:700; padding:2px 14px; border-radius:20px; letter-spacing:1.5px; }
.org-lbl { color:rgba(197,160,55,0.6); font-size:11px; font-weight:600; letter-spacing:4px; margin-bottom:2mm; }
.main-title { color:#fff; font-size:36px; font-weight:900; line-height:1.15; margin-bottom:2mm; }
.sub-title { color:#c5a037; font-size:20px; font-weight:700; margin-bottom:2mm; }
.year { color:rgba(255,255,255,0.36); font-size:11px; margin-bottom:4mm; }
.divider { width:55mm; height:1.5px; background:linear-gradient(90deg,transparent,#c5a037,transparent); margin:0 auto 4mm auto; }
.stats { width:100%; display:flex; justify-content:center; align-items:center; margin-bottom:5mm; }
.st { text-align:center; padding:0 7mm; }
.st-n { font-size:34px; font-weight:900; color:#c5a037; line-height:1; display:block; }
.st-l { font-size:10px; color:rgba(255,255,255,0.5); margin-top:1.5mm; display:block; }
.st-sep { width:1px; height:11mm; background:rgba(197,160,55,0.3); }
.pills { width:100%; display:flex; justify-content:center; gap:2.5mm; margin-bottom:4mm; flex-wrap:wrap; }
.pill { border:1px solid rgba(197,160,55,0.3); background:rgba(255,255,255,0.06); color:rgba(255,255,255,0.75); font-size:10px; padding:3px 11px; border-radius:20px; }
.tagline { color:rgba(255,255,255,0.3); font-size:10px; }

.pg { width:210mm; page-break-after:always; padding:12mm 13mm 10mm; background:#f9f7f2; display:flex; flex-direction:column; }
.pg-last { page-break-after:auto; }
.hdr { display:flex; align-items:center; justify-content:space-between; padding-bottom:3mm; border-bottom:2.5px solid #0d1f3c; margin-bottom:5mm; }
.hdr-brand { font-size:11px; font-weight:900; color:#0d1f3c; }
.hdr-brand span { color:#c5a037; }
.hdr-pg { font-size:10px; color:#999; font-weight:600; }
.sec { margin-bottom:5mm; }
.sec-hd { display:flex; align-items:center; gap:3mm; margin-bottom:3mm; }
.sec-ic { background:linear-gradient(135deg,#0d1f3c,#1a3a5c); color:#c5a037; width:8mm; height:8mm; border-radius:3px; display:flex; align-items:center; justify-content:center; font-size:14px; flex-shrink:0; }
.sec-t { font-size:14px; font-weight:900; color:#0d1f3c; }
.info { background:#fff; border-right:5px solid #c5a037; border-radius:0 7px 7px 0; padding:4mm 5mm; font-size:12px; line-height:2; color:#333; }
.srow { display:flex; gap:3mm; margin-bottom:4mm; }
.sc { flex:1; background:linear-gradient(135deg,#0d1f3c,#1a3a5c); border-radius:7px; padding:4mm 2mm; text-align:center; color:#fff; }
.sc-n { font-size:28px; font-weight:900; color:#c5a037; line-height:1; }
.sc-l { font-size:10px; opacity:0.6; margin-top:1.5mm; }
.ph3 { display:flex; gap:3mm; }
.pc { flex:1; background:#fff; border:1px solid #e0ddd0; border-radius:7px; padding:4mm; }
.pc-t { font-size:12px; font-weight:900; margin-bottom:3mm; }
.pc li { list-style:none; font-size:11px; color:#555; margin-bottom:1.5mm; }

.tbl { width:100%; border-collapse:collapse; background:#fff; margin-bottom:3mm; }
.tbl thead tr { background:linear-gradient(135deg,#0d1f3c,#1a3a5c); color:#c5a037; }
.tbl th { padding:3mm 4mm; font-weight:700; font-size:12px; text-align:right; }
.tbl th.c { text-align:center; }
.tbl td { padding:2.5mm 4mm; border-bottom:1px solid #eee; color:#1a1a2e; font-size:13px; vertical-align:middle; font-weight:700; }
.tbl td.c { text-align:center; }
.tbl tr:nth-child(even) td { background:#faf8f3; }
.vs { color:#c5a037; font-weight:900; font-size:14px; text-align:center; }

.pts3 { display:flex; gap:3mm; margin-bottom:4mm; }
.pt3 { flex:1; border-radius:7px; padding:4mm; text-align:center; color:#fff; }
.pt3.w1 { background:linear-gradient(135deg,#1a5c2a,#27ae60); }
.pt3.w2 { background:linear-gradient(135deg,#2d6b1a,#6bae27); }
.pt3.l1 { background:linear-gradient(135deg,#8b6914,#c5a037); }
.pt3.l2 { background:linear-gradient(135deg,#8b1a1a,#c0392b); }
.pt3 .e { font-size:18px; }
.pt3 .l { font-size:11px; font-weight:700; margin:1.5mm 0; }
.pt3 .n { font-size:28px; font-weight:900; line-height:1; }
.pt3 .u { font-size:9px; opacity:0.8; }

.note { background:#fffbf0; border:1px solid #f0d070; border-radius:7px; padding:3mm 4mm; font-size:11.5px; color:#6b5200; line-height:1.8; margin-bottom:4mm; }
.note strong { color:#8B6914; }
.champ { background:linear-gradient(135deg,#8B6914,#c5a037,#f0d060,#c5a037,#8B6914); border-radius:9px; padding:5mm; text-align:center; color:#0d1f3c; margin-top:4mm; }
.champ .ci { font-size:30px; }
.champ .ct { font-size:14px; font-weight:900; margin:2mm 0; }
.champ .cl { background:rgba(255,255,255,0.4); border-radius:5px; padding:2.5mm 10mm; display:inline-block; font-size:12px; min-width:65mm; }
.ft { margin-top:auto; padding-top:3mm; border-top:1.5px solid #d0ccc0; display:flex; justify-content:space-between; align-items:center; font-size:9.5px; color:#aaa; }
.ft .br { color:#c5a037; font-weight:700; }
.db { display:inline-block; font-size:10px; font-weight:900; padding:2.5px 7px; border-radius:3px; text-align:center; line-height:1.6; }
.db.navy { border-right:4px solid #c5a037; background:#fff; color:#0d1f3c; }
.db.gold { background:linear-gradient(135deg,#8B6914,#c5a037); color:#fff; }
.db.green { background:#1a5c2a; color:#a0e8b0; }
"""

pages_html = []

# ===== PAGE 1: COVER =====
pages_html.append(f"""<div class="cover">
<div class="gold-bar"></div>
<div class="cr-big">🌙</div><div class="cr-small">🌙</div>
<div class="star" style="top:26mm;right:28mm;font-size:13px;opacity:0.5;">✦</div>
<div class="star" style="top:44mm;right:58mm;font-size:8px;opacity:0.3;">★</div>
<div class="star" style="top:30mm;left:58mm;font-size:9px;opacity:0.3;">★</div>
<div class="star" style="bottom:58mm;right:32mm;font-size:9px;opacity:0.3;">★</div>
<div class="frame"></div>
<div class="cover-body">
  <div class="cover-spacer"></div>
  <img class="cover-game-img" src="{ball_url}" alt="كرة طائرة">
  <div class="badge">🗂️ مقترح رسمي — للمراجعة والاعتماد</div>
  <div class="org-lbl">ت ح ت &nbsp; م ظ ل ة</div>
  <div class="main-title">البطولة الرمضانية</div>
  <div class="sub-title">لصفوة المهيدب لكرة الطائرة</div>
  <div class="year">رمضان المبارك ١٤٤٨ هـ</div>
  <div class="divider"></div>
  <div class="stats">
    <div class="st"><span class="st-n">4</span><span class="st-l">فرق متنافسة</span></div>
    <div class="st-sep"></div>
    <div class="st"><span class="st-n">14</span><span class="st-l">مباراة</span></div>
    <div class="st-sep"></div>
    <div class="st"><span class="st-n">7</span><span class="st-l">أيام لعب</span></div>
  </div>
  <div class="pills">
    <div class="pill">🏐 دوري مزدوج + نهائيات</div>
    <div class="pill">📅 الخميس والاثنين</div>
    <div class="pill">👥 5 لاعبين/فريق</div>
  </div>
  <div class="tagline">ليالي رمضان × حماس الطائرة × منافسة حقيقية 🏐🔥</div>
  <div class="cover-spacer"></div>
</div>
<div class="gold-bar"></div>
</div>""")

# ===== PAGE 2: INFO + SCHEDULE =====
sched_rows = ""
for i, (day, date, m1, m2) in enumerate(schedule):
    style = ''
    day_class = 'navy'
    sched_rows += f"""<tr {style}>
      <td rowspan="2" style="border-right:4px solid #c5a037;background:#fff;text-align:center;vertical-align:middle;font-size:11px;font-weight:900;color:#0d1f3c;padding:2mm;">
        {day}<br><span style="font-size:9px;color:#888;">{date}</span>
      </td>
      <td style="font-size:14px;">فريق {m1[0]}</td>
      <td class="vs" style="font-size:15px;">⚔️</td>
      <td style="font-size:14px;">فريق {m1[1]}</td>
    </tr>
    <tr><td style="font-size:14px;border-bottom:1px solid #eee;">فريق {m2[0]}</td>
      <td class="vs" style="font-size:15px;border-bottom:1px solid #eee;">⚔️</td>
      <td style="font-size:14px;border-bottom:1px solid #eee;">فريق {m2[1]}</td>
    </tr>
    <tr><td colspan="4" style="height:1.5px;background:#e0e0e0;padding:0;"></td></tr>
"""

pages_html.append(f"""<div class="pg">
<div class="hdr">
  <div class="hdr-brand">🏐 <span>البطولة الرمضانية لصفوة المهيدب</span> لكرة الطائرة</div>
  <div class="hdr-pg">الصفحة 1 من 4</div>
</div>
<div class="sec">
  <div class="sec-hd"><div class="sec-ic">📊</div><div class="sec-t">أرقام البطولة</div></div>
  <div class="srow">
    <div class="sc"><div class="sc-n">4</div><div class="sc-l">فرق</div></div>
    <div class="sc"><div class="sc-n">20</div><div class="sc-l">لاعب</div></div>
    <div class="sc"><div class="sc-n">14</div><div class="sc-l">مباراة</div></div>
    <div class="sc"><div class="sc-n">7</div><div class="sc-l">أيام لعب</div></div>
    <div class="sc"><div class="sc-n">3.5</div><div class="sc-l">أسبوع</div></div>
  </div>
</div>
<div class="sec">
  <div class="sec-hd"><div class="sec-ic">🏗️</div><div class="sec-t">هيكل المراحل</div></div>
  <div class="ph3">
    <div class="pc" style="border-top:4px solid #1a3a5c;">
      <div class="pc-t" style="color:#0d1f3c;">🔵 مرحلة الدوري<br><small style="font-weight:400;color:#888;">6 أيام لعب</small></div>
      <ul>
        <li>📅 الخميس + الاثنين</li>
        <li>🔄 كل فريق يلعب ضد الجميع مرتين</li>
        <li>🏐 مباراتان كل يوم لعب</li>
        <li>✅ أفضل 2 للنهائي</li>
      </ul>
    </div>
    <div class="pc" style="border-top:4px solid #c5a037;">
      <div class="pc-t" style="color:#8B6914;">🏆 يوم التتويج<br><small style="font-weight:400;color:#888;">الخميس ٢٣ رمضان</small></div>
      <ul>
        <li>🥉 المركز 3 vs المركز 4</li>
        <li>🔥 الأول vs الثاني — النهائي</li>
        <li>👑 تتويج البطل</li>
        <li>🎁 توزيع الجوائز</li>
      </ul>
    </div>
  </div>
</div>
<div class="ft"><span class="br">🏐 البطولة الرمضانية لصفوة المهيدب لكرة الطائرة</span><span>مقترح رسمي</span><span>1 / 4</span></div>
</div>""")

# ===== PAGE 3: SCHEDULE =====
pages_html.append(f"""<div class="pg">
<div class="hdr">
  <div class="hdr-brand">🏐 <span>البطولة الرمضانية لصفوة المهيدب</span> — جدول الدوري</div>
  <div class="hdr-pg">الصفحة 2 من 4</div>
</div>
<div class="sec">
  <div class="sec-hd"><div class="sec-ic">📅</div><div class="sec-t">جدول الدوري — 6 أيام لعب (دوري مزدوج)</div></div>
  <table class="tbl"><thead><tr>
    <th style="width:22%;text-align:center;">اليوم</th>
    <th style="width:33%;">الفريق الأول</th>
    <th class="c" style="width:8%;">VS</th>
    <th style="width:33%;">الفريق الثاني</th>
  </tr></thead><tbody>
  {sched_rows}
  </tbody></table>
</div>
<div class="ft"><span class="br">🏐 البطولة الرمضانية لصفوة المهيدب لكرة الطائرة</span><span>مقترح رسمي</span><span>2 / 4</span></div>
</div>""")

# ===== PAGE 4: FINALS + RULES =====
pages_html.append(f"""<div class="pg pg-last">
<div class="hdr">
  <div class="hdr-brand">🏐 <span>البطولة الرمضانية لصفوة المهيدب</span> — النهائيات والقواعد</div>
  <div class="hdr-pg">الصفحة 3 من 4</div>
</div>
<div class="sec">
  <div class="sec-hd"><div class="sec-ic">🏆</div><div class="sec-t">يوم التتويج — الخميس ٢٣ رمضان</div></div>
  <table class="tbl"><thead><tr>
    <th style="width:8%;text-align:center;">#</th>
    <th style="width:32%;">المتنافس الأول</th>
    <th class="c" style="width:8%;">VS</th>
    <th style="width:32%;">المتنافس الثاني</th>
    <th class="c" style="width:18%;">الهدف</th>
  </tr></thead><tbody>
  <tr><td class="c">1</td><td style="font-size:14px;">🥉 المركز الثالث</td><td class="vs">⚔️</td><td style="font-size:14px;">المركز الرابع</td><td class="c" style="font-size:11px;color:#8B6914;font-weight:700;">المركز 3 🥉</td></tr>
  <tr style="background:rgba(197,160,55,0.08);"><td class="c" style="font-weight:900;">2</td><td style="font-size:14px;font-weight:900;">🥇 المركز الأول</td><td class="vs" style="font-size:16px;">⚔️</td><td style="font-size:14px;font-weight:900;">المركز الثاني 🥈</td><td class="c" style="font-size:12px;color:#8B6914;font-weight:900;">البطل 🏆</td></tr>
  </tbody></table>
</div>
<div class="sec">
  <div class="sec-hd"><div class="sec-ic">📊</div><div class="sec-t">نظام النقاط (FIVB)</div></div>
  <div class="pts3">
    <div class="pt3 w1"><div class="e">🟢</div><div class="l">فوز 3-0 / 3-1</div><div class="n">3</div><div class="u">نقاط</div></div>
    <div class="pt3 w2"><div class="e">🟡</div><div class="l">فوز 3-2</div><div class="n">2</div><div class="u">نقاط</div></div>
    <div class="pt3 l1"><div class="e">🟠</div><div class="l">خسارة 2-3</div><div class="n">1</div><div class="u">نقطة</div></div>
    <div class="pt3 l2"><div class="e">🔴</div><div class="l">خسارة 0-3 / 1-3</div><div class="n">0</div><div class="u">نقطة</div></div>
  </div>
  <div class="note">⚠️ <strong>نظام الأشواط:</strong> كل مباراة من 5 أشواط — الفائز من يحقق 3 أشواط أولاً (Best of 5).<br>
  <strong>⚖️ التساوي في النقاط:</strong> ١. نسبة الأشواط &nbsp;•&nbsp; ٢. نسبة النقاط &nbsp;•&nbsp; ٣. المواجهة المباشرة</div>
</div>
<div class="sec">
  <div class="sec-hd"><div class="sec-ic">📋</div><div class="sec-t">قوانين اللعب</div></div>
  <div class="info">
    <strong>👥 التشكيلة:</strong> 5 لاعبين أساسيين في الملعب<br>
    <strong>🔄 التبديل:</strong> حسب قوانين الكرة الطائرة المعتمدة<br>
    <strong>🏐 الأشواط:</strong> الشوط من 25 نقطة (الخامس من 15 نقطة) — بفارق نقطتين<br>
    <strong>⏰ التوقيت:</strong> مباراتان كل يوم لعب — الخميس والاثنين
  </div>
</div>
<div class="champ"><div class="ci">🏆</div>
<div class="ct">بطل البطولة الرمضانية لصفوة المهيدب لكرة الطائرة 1448هـ</div>
<div class="cl">يُكتب هنا اسم البطل بعد النهائي الكبير</div></div>
<div class="ft"><span class="br">🏐 البطولة الرمضانية لصفوة المهيدب لكرة الطائرة</span><span>🌙 رمضان كريم 1448هـ</span><span>3 / 4</span></div>
</div>""")

# ===== RENDER =====
page_pdfs = []
all_ok = True
for idx, page_html in enumerate(pages_html):
    full = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<style>{CSS}@page{{size:210mm 297mm;margin:0;}}</style></head><body>{page_html}</body></html>"""
    pdf_bytes = HTML(string=full).write_pdf()
    tmp_r = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    n = len(tmp_r.pages)
    print(f"  صفحة {idx+1}: {n} {'✅' if n==1 else '❌'}")
    if n != 1: all_ok = False
    tmp_path = f'/tmp/vball_page_{idx}.pdf'
    with open(tmp_path, 'wb') as f:
        f.write(pdf_bytes)
    page_pdfs.append(tmp_path)

out_path = 'volleyball_FINAL.pdf'
with pikepdf.Pdf.new() as out_pdf:
    for pg_path in page_pdfs:
        src = pikepdf.Pdf.open(pg_path)
        out_pdf.pages.extend(src.pages)
        src.close()
    out_pdf.save(out_path)

print(f"\n{'✅ تمام!' if all_ok else '⚠️'} {len(page_pdfs)} صفحات → {out_path}")
subprocess.run(['convert','-density','120',f'{out_path}[0]','-resize','500x','vball_cover.png'], capture_output=True)
print("✅ Preview ready")
