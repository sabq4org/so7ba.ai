from weasyprint import HTML
from PIL import Image, ImageDraw
import PyPDF2, pikepdf, io, subprocess, base64

# Embed Cairo font
with open('/home/openclaw/.local/share/fonts/Cairo.ttf', 'rb') as _f:
    CAIRO_B64 = base64.b64encode(_f.read()).decode()
CAIRO_URL = f"data:font/truetype;base64,{CAIRO_B64}"

# ===== Dice image =====
img = Image.open('dice_ai.png').convert('RGBA')
size = 420
img = img.resize((size, size), Image.LANCZOS)
mask = Image.new('L', (size, size), 0)
ImageDraw.Draw(mask).ellipse((0,0,size-1,size-1), fill=255)
img.putalpha(mask)
bs = size + 28
result = Image.new('RGBA', (bs, bs), (0,0,0,0))
bd = Image.new('RGBA', (bs, bs), (0,0,0,0))
ImageDraw.Draw(bd).ellipse((0,0,bs-1,bs-1), fill=(197,160,55,200))
ImageDraw.Draw(bd).ellipse((9,9,bs-10,bs-10), fill=(0,0,0,0))
result.paste(bd,(0,0),bd)
result.paste(img,(14,14),img)
buf = io.BytesIO()
result.save(buf,'PNG')
dice_url = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

# ===== Schedule =====
rounds = [
    [(1,10),(2,9),(3,8),(4,7),(5,6)],
    [(1,9),(10,8),(2,7),(3,6),(4,5)],
    [(1,8),(9,7),(10,6),(2,5),(3,4)],
    [(1,7),(8,6),(9,5),(10,4),(2,3)],
    [(1,6),(7,5),(8,4),(9,3),(10,2)],
    [(1,5),(6,4),(7,3),(8,2),(9,10)],
    [(1,4),(5,3),(6,2),(7,10),(8,9)],
    [(1,3),(4,2),(5,10),(6,9),(7,8)],
    [(1,2),(3,10),(4,9),(5,8),(6,7)],
]
all_matches = [m for r in rounds for m in r]
# 10 days × 4 matches + day 11 × 5 matches = 45 total
play_days_matches = [all_matches[i:i+4] for i in range(0, 40, 4)] + [all_matches[40:45]]

day_names = [
    "الأربعاء — ١ رمضان","الجمعة — ٣ رمضان","الأحد — ٥ رمضان",
    "الثلاثاء — ٧ رمضان","الخميس — ٩ رمضان","السبت — ١١ رمضان",
    "الاثنين — ١٣ رمضان","الأربعاء — ١٥ رمضان","الجمعة — ١٧ رمضان",
    "الأحد — ١٩ رمضان","الثلاثاء — ٢١ رمضان",
]

def match_rows(day_idx):
    matches = play_days_matches[day_idx]
    rows = ""
    for i, (a,b) in enumerate(matches):
        rows += f'<tr><td class="c">{i+1}</td><td>فريق {a}</td><td class="vs">⚔️</td><td>فريق {b}</td></tr>\n'
    return rows

def sched_table(start, end, label):
    html = f'<div class="sec-hd" style="margin-bottom:4mm;"><div class="sec-ic">📅</div><div class="sec-t">{label}</div></div>\n'
    html += '<table class="tbl"><thead><tr><th style="width:22%">اليوم</th><th class="c" style="width:5%">#</th><th style="width:32%">الفريق الأول</th><th class="c" style="width:8%">VS</th><th style="width:32%">الفريق الثاني</th></tr></thead><tbody>\n'
    for d in range(start, end):
        n = len(play_days_matches[d])
        label_class = 'gold' if d == 11 else ''
        special = ' 🌟<br><small>مباراة الحسم</small>' if d == 11 else f'<br><small>الجولة {d+1}</small>'
        html += f'<tr><td rowspan="{n}"><span class="db {label_class}">اليوم {d+1}{special}<br><small style="opacity:0.8;font-size:8px;">{day_names[d]}</small></span></td>'
        for i, (a,b) in enumerate(play_days_matches[d]):
            prefix = "" if i == 0 else "<tr>"
            suffix = "</tr>"
            if i == 0:
                html += f'<td class="c">{i+1}</td><td>فريق {a}</td><td class="vs">⚔️</td><td>فريق {b}</td></tr>\n'
            else:
                bg = 'style="background:rgba(197,160,55,0.05);"' if d == 11 else ''
                html += f'<tr {bg}><td class="c">{i+1}</td><td>فريق {a}</td><td class="vs">⚔️</td><td>فريق {b}</td></tr>\n'
    html += '</tbody></table>\n'
    return html

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
.main-title { color:#fff; font-size:38px; font-weight:900; line-height:1.15; margin-bottom:2mm; }
.sub-title { color:#c5a037; font-size:19px; font-weight:700; margin-bottom:2mm; }
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
.hdr { display:flex; align-items:center; justify-content:space-between; padding-bottom:3mm; border-bottom:2.5px solid #0d1f3c; margin-bottom:6mm; }
.hdr-brand { font-size:11px; font-weight:900; color:#0d1f3c; }
.hdr-brand span { color:#c5a037; }
.hdr-pg { font-size:10px; color:#999; font-weight:600; }
.sec { margin-bottom:5mm; }
.sec-hd { display:flex; align-items:center; gap:3mm; margin-bottom:4mm; }
.sec-ic { background:linear-gradient(135deg,#0d1f3c,#1a3a5c); color:#c5a037; width:8mm; height:8mm; border-radius:3px; display:flex; align-items:center; justify-content:center; font-size:14px; flex-shrink:0; }
.sec-t { font-size:14px; font-weight:900; color:#0d1f3c; }
.info { background:#fff; border-right:5px solid #c5a037; border-radius:0 7px 7px 0; padding:4mm 5mm; font-size:12px; line-height:2; color:#333; }
.grid2 { display:flex; flex-wrap:wrap; gap:3mm; }
.rc { flex:1 1 calc(50% - 3mm); background:#fff; border:1px solid #e8e3d8; border-radius:7px; padding:4mm; border-top:3.5px solid #c5a037; }
.rc-n { font-size:20px; font-weight:900; color:#c5a037; line-height:1; }
.rc-t { font-size:11.5px; color:#444; margin-top:2mm; line-height:1.65; }
.srow { display:flex; gap:3mm; margin-bottom:4mm; }
.sc { flex:1; background:linear-gradient(135deg,#0d1f3c,#1a3a5c); border-radius:7px; padding:3.5mm 2mm; text-align:center; color:#fff; }
.sc-n { font-size:26px; font-weight:900; color:#c5a037; line-height:1; }
.sc-l { font-size:9.5px; opacity:0.6; margin-top:1.5mm; }
.ph3 { display:flex; gap:3mm; }
.pc { flex:1; background:#fff; border:1px solid #e0ddd0; border-radius:7px; padding:4mm; }
.pc-t { font-size:12px; font-weight:900; margin-bottom:3mm; }
.pc li { list-style:none; font-size:11px; color:#555; margin-bottom:1.5mm; }
.tbl { width:100%; border-collapse:collapse; font-size:11.5px; background:#fff; margin-bottom:3mm; }
.tbl thead tr { background:linear-gradient(135deg,#0d1f3c,#1a3a5c); color:#c5a037; }
.tbl th { padding:2.5mm 3mm; font-weight:700; font-size:11.5px; text-align:right; }
.tbl th.c { text-align:center; }
.tbl td { padding:1.5mm 3mm; border-bottom:1px solid #eee; color:#1a1a2e; font-size:11px; vertical-align:middle; }
.tbl td.c { text-align:center; }
.tbl tr:nth-child(even) td { background:#faf8f3; }
.db { display:inline-block; background:#0d1f3c; color:#c5a037; font-size:9px; font-weight:700; padding:2.5px 7px; border-radius:3px; text-align:center; line-height:1.6; }
.db.gold { background:linear-gradient(135deg,#8B6914,#c5a037); color:#fff; }
.db.green { background:#1a5c2a; color:#a0e8b0; }
.vs { color:#c5a037; font-weight:900; font-size:13px; text-align:center; }
.pts2 { display:flex; gap:4mm; margin-bottom:4mm; }
.pt2 { flex:1; border-radius:7px; padding:4mm; text-align:center; color:#fff; }
.pt2.win { background:linear-gradient(135deg,#1a5c2a,#27ae60); }
.pt2.loss { background:linear-gradient(135deg,#8b1a1a,#c0392b); }
.pt2 .e { font-size:20px; }
.pt2 .l { font-size:13px; font-weight:700; margin:2mm 0; }
.pt2 .n { font-size:32px; font-weight:900; line-height:1; }
.pt2 .u { font-size:10px; opacity:0.8; }
.tl { position:relative; padding-right:8mm; }
.tl::before { content:''; position:absolute; right:3.5mm; top:2mm; bottom:2mm; width:1.5px; background:linear-gradient(to bottom,#c5a037,rgba(197,160,55,0.1)); }
.tl-item { display:flex; gap:4mm; margin-bottom:4mm; position:relative; }
.tl-dot { position:absolute; right:-6mm; top:1.5mm; width:5mm; height:5mm; border-radius:50%; background:#c5a037; }
.tl-dot.g { background:linear-gradient(135deg,#c5a037,#f0d060); }
.tl-dot.s { background:#1a5c2a; }
.tl-day { font-size:12px; font-weight:900; color:#0d1f3c; margin-bottom:1mm; }
.tl-desc { font-size:11px; color:#666; }
.note { background:#fffbf0; border:1px solid #f0d070; border-radius:7px; padding:3mm 4mm; font-size:11.5px; color:#6b5200; line-height:1.8; margin-bottom:4mm; }
.note strong { color:#8B6914; }
.champ { background:linear-gradient(135deg,#8B6914,#c5a037,#f0d060,#c5a037,#8B6914); border-radius:9px; padding:5mm; text-align:center; color:#0d1f3c; margin-top:4mm; }
.champ .ci { font-size:30px; }
.champ .ct { font-size:14px; font-weight:900; margin:2mm 0; }
.champ .cl { background:rgba(255,255,255,0.4); border-radius:5px; padding:2.5mm 10mm; display:inline-block; font-size:12px; min-width:65mm; }
.ft { margin-top:auto; padding-top:3mm; border-top:1.5px solid #d0ccc0; display:flex; justify-content:space-between; align-items:center; font-size:9.5px; color:#aaa; }
.ft .br { color:#c5a037; font-weight:700; }
.pg-last .sec { margin-bottom:3mm; }
.pg-last .tl-item { margin-bottom:2.5mm; }
.pg-last .note { padding:2mm 3mm; margin-bottom:2.5mm; }
.pg-last .champ { padding:3.5mm; margin-top:2.5mm; }
.pg-last .pts2 { margin-bottom:2.5mm; }
.pg-last .tl { padding-right:7mm; }
"""

# Build schedule rows for pages
def sched_rows(start, end):
    html = ""
    for d in range(start, end):
        matches = play_days_matches[d]
        n = len(matches)
        is_last = (d == 10)
        if is_last:
            day_cell = f'<td rowspan="{n}" style="background:linear-gradient(135deg,#8B6914,#c5a037);color:#0d1f3c;font-size:9.5px;font-weight:900;padding:1.5mm 3mm;text-align:center;vertical-align:middle;border-bottom:2px solid #c5a037;">اليوم {d+1} 🌟<br><span style="font-size:8px;font-weight:600;">{day_names[d]}</span></td>'
        else:
            day_cell = f'<td rowspan="{n}" style="border-right:4px solid #c5a037;background:#fff;color:#0d1f3c;font-size:10px;font-weight:900;padding:1.5mm 2.5mm;text-align:center;vertical-align:middle;border-bottom:1px solid #eee;">اليوم {d+1}<br><span style="font-size:8px;color:#888;font-weight:600;">{day_names[d]}</span></td>'
        for i, (a, b) in enumerate(matches):
            alt = 'background:#faf8f3;' if i % 2 == 1 else 'background:#fff;'
            row_open = f'<tr style="{alt}">{day_cell}' if i == 0 else f'<tr style="{alt}">'
            html += (f'{row_open}'
                     f'<td style="font-size:12.5px;font-weight:700;padding:1.5mm 3mm;border-bottom:1px solid #eee;vertical-align:middle;">فريق {a}</td>'
                     f'<td style="text-align:center;font-size:14px;font-weight:900;color:#c5a037;border-bottom:1px solid #eee;vertical-align:middle;">⚔️</td>'
                     f'<td style="font-size:12.5px;font-weight:700;padding:1.5mm 3mm;border-bottom:1px solid #eee;vertical-align:middle;">فريق {b}</td>'
                     f'</tr>\n')
        html += f'<tr><td colspan="4" style="height:1.5px;background:#e0e0e0;padding:0;"></td></tr>\n'
    return html

sched_header = '''<table style="width:100%;border-collapse:collapse;background:#fff;margin-bottom:3mm;"><thead><tr>
<th style="width:19%;background:linear-gradient(135deg,#0d1f3c,#1a3a5c);color:#c5a037;padding:2.5mm 3mm;font-size:11px;font-weight:700;text-align:center;">اليوم</th>
<th style="width:37%;background:linear-gradient(135deg,#0d1f3c,#1a3a5c);color:#c5a037;padding:2.5mm 3mm;font-size:11px;font-weight:700;text-align:right;">الفريق الأول</th>
<th style="width:7%;background:linear-gradient(135deg,#0d1f3c,#1a3a5c);color:#c5a037;padding:2.5mm;font-size:11px;font-weight:700;text-align:center;">VS</th>
<th style="width:37%;background:linear-gradient(135deg,#0d1f3c,#1a3a5c);color:#c5a037;padding:2.5mm 3mm;font-size:11px;font-weight:700;text-align:right;">الفريق الثاني</th>
</tr></thead><tbody>'''

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
  <img class="cover-game-img" src="{dice_url}" alt="نرد">
  <div class="badge">🗂️ مقترح رسمي — للمراجعة والاعتماد</div>
  <div class="org-lbl">ت ح ت &nbsp; م ظ ل ة</div>
  <div class="main-title">صفوة المهيدب</div>
  <div class="sub-title">البطولة الرمضانية للشيش</div>
  <div class="year">رمضان المبارك ١٤٤٨ هـ</div>
  <div class="divider"></div>
  <div class="stats">
    <div class="st"><span class="st-n">10</span><span class="st-l">فرق متنافسة</span></div>
    <div class="st-sep"></div>
    <div class="st"><span class="st-n">45</span><span class="st-l">مباراة</span></div>
    <div class="st-sep"></div>
    <div class="st"><span class="st-n">13</span><span class="st-l">يوم لعب</span></div>
  </div>
  <div class="pills">
    <div class="pill">🏆 دوري + نهائيات</div>
    <div class="pill">⏰ ١٢ منتصف الليل</div>
    <div class="pill">📅 يوم ورى يوم</div>
  </div>
  <div class="tagline">ليالي رمضان × حرارة المنافسة × شيش أصيل 🎲🔥</div>
  <div class="cover-spacer"></div>
</div>
<div class="gold-bar"></div>
</div>""")

# ===== PAGE 2: PROPOSAL =====
pages_html.append(f"""<div class="pg">
<div class="hdr">
  <div class="hdr-brand">🎲 <span>بطولة صفوة المهيدب</span> الرمضانية للشيش</div>
  <div class="hdr-pg">الصفحة 1 من 4</div>
</div>
<div class="sec">
  <div class="sec-hd"><div class="sec-ic">📊</div><div class="sec-t">أرقام البطولة</div></div>
  <div class="srow">
    <div class="sc"><div class="sc-n">10</div><div class="sc-l">فريق</div></div>
    <div class="sc"><div class="sc-n">45</div><div class="sc-l">مباراة</div></div>
    <div class="sc"><div class="sc-n">4-5</div><div class="sc-l">مباريات/يوم</div></div>
    <div class="sc"><div class="sc-n">11</div><div class="sc-l">يوم دوري</div></div>
    <div class="sc"><div class="sc-n">2</div><div class="sc-l">أيام نهائي</div></div>
    <div class="sc"><div class="sc-n">13</div><div class="sc-l">المجموع</div></div>
  </div>
</div>
<div class="sec">
  <div class="sec-hd"><div class="sec-ic">🏗️</div><div class="sec-t">هيكل المراحل</div></div>
  <div class="ph3">
    <div class="pc" style="border-top:4px solid #1a3a5c;">
      <div class="pc-t" style="color:#0d1f3c;">🔵 مرحلة الدوري<br><small style="font-weight:400;color:#888;">الأيام 1 → 11</small></div>
      <ul>
        <li>📅 يوم ورى يوم</li>
        <li>⏰ الساعة 12 منتصف الليل</li>
        <li>⚽ 4-5 مباريات/يوم</li>
        <li>✅ أفضل 4 يتأهلون</li>
      </ul>
    </div>
    <div class="pc" style="border-top:4px solid #1a5c2a;">
      <div class="pc-t" style="color:#1a5c2a;">🟢 نصف النهائي<br><small style="font-weight:400;color:#888;">السبت ٢٥ رمضان</small></div>
      <ul>
        <li>⚔️ الأول ضد الرابع</li>
        <li>⚔️ الثاني ضد الثالث</li>
        <li>🏆 الفائزان للنهائي</li>
        <li>🥉 الخاسران يتنافسان</li>
      </ul>
    </div>
    <div class="pc" style="border-top:4px solid #c5a037;">
      <div class="pc-t" style="color:#8B6914;">🏆 النهائيات<br><small style="font-weight:400;color:#888;">الثلاثاء ٢٨ رمضان</small></div>
      <ul>
        <li>🥉 مباراة المركز الثالث</li>
        <li>🔥 النهائي الكبير</li>
        <li>👑 تتويج البطل</li>
        <li>🎁 توزيع الجوائز</li>
      </ul>
    </div>
  </div>
</div>
<div class="ft"><span class="br">🎲 بطولة صفوة المهيدب الرمضانية للشيش</span><span>مقترح رسمي</span><span>1 / 4</span></div>
</div>""")

# ===== PAGE 3: SCHEDULE DAYS 1-6 =====
pages_html.append(f"""<div class="pg">
<div class="hdr">
  <div class="hdr-brand">🎲 <span>بطولة صفوة المهيدب</span> — جدول الدوري</div>
  <div class="hdr-pg">الصفحة 2 من 4</div>
</div>
<div class="sec-hd" style="margin-bottom:3mm;"><div class="sec-ic">📅</div><div class="sec-t">جدول الدوري — الأيام 1 إلى 6</div></div>
{sched_header}
{sched_rows(0, 6)}
</tbody></table>
<div class="ft"><span class="br">🎲 بطولة صفوة المهيدب الرمضانية للشيش</span><span>مقترح رسمي</span><span>2 / 4</span></div>
</div>""")

# ===== PAGE 4: SCHEDULE DAYS 7-12 =====
pages_html.append(f"""<div class="pg">
<div class="hdr">
  <div class="hdr-brand">🎲 <span>بطولة صفوة المهيدب</span> — جدول الدوري</div>
  <div class="hdr-pg">الصفحة 3 من 4</div>
</div>
<div class="sec-hd" style="margin-bottom:3mm;"><div class="sec-ic">📅</div><div class="sec-t">جدول الدوري — الأيام 7 إلى 11</div></div>
{sched_header}
{sched_rows(6, 11)}
</tbody></table>
<div class="ft"><span class="br">🎲 بطولة صفوة المهيدب الرمضانية للشيش</span><span>مقترح رسمي</span><span>3 / 4</span></div>
</div>""")

# ===== PAGE 5: FINALS + RULES =====
pages_html.append(f"""<div class="pg pg-last">
<div class="hdr">
  <div class="hdr-brand">🎲 <span>بطولة صفوة المهيدب</span> — النهائيات والقواعد</div>
  <div class="hdr-pg">الصفحة 4 من 4</div>
</div>
<div class="sec">
  <div class="sec-hd"><div class="sec-ic">🏅</div><div class="sec-t">جدول النهائيات — السبت 25 والثلاثاء 28 رمضان</div></div>
  <table class="tbl"><thead><tr>
    <th style="width:20%">اليوم</th><th class="c" style="width:5%">#</th>
    <th style="width:28%">المتنافس الأول</th><th class="c" style="width:7%">VS</th>
    <th style="width:28%">المتنافس الثاني</th><th class="c" style="width:12%">الهدف</th>
  </tr></thead><tbody>
  <tr><td rowspan="2"><span class="db green">السبت<br>٢٥ رمضان<br>نصف نهائي</span></td>
    <td class="c">1</td><td>🥇 المركز الأول</td><td class="vs">⚔️</td><td>المركز الرابع</td><td class="c" style="font-size:10px;color:#1a5c2a;font-weight:700;">للنهائي ✅</td></tr>
  <tr><td class="c">2</td><td>🥈 المركز الثاني</td><td class="vs">⚔️</td><td>المركز الثالث</td><td class="c" style="font-size:10px;color:#1a5c2a;font-weight:700;">للنهائي ✅</td></tr>
  <tr style="border-top:2.5px solid #c5a037;"><td rowspan="2"><span class="db gold">الثلاثاء<br>٢٨ رمضان<br>🔥 النهائيات</span></td>
    <td class="c">1</td><td>🥉 الخاسر الأول</td><td class="vs">⚔️</td><td>الخاسر الثاني</td><td class="c" style="font-size:10px;color:#8B6914;font-weight:700;">المركز 3 🥉</td></tr>
  <tr style="background:rgba(197,160,55,0.08);"><td class="c">2</td><td><strong>🏆 الفائز الأول</strong></td><td class="vs">⚔️</td><td><strong>الفائز الثاني</strong></td><td class="c" style="font-size:11px;color:#8B6914;font-weight:900;">البطل 🏆</td></tr>
  </tbody></table>
</div>
<div class="sec">
  <div class="sec-hd"><div class="sec-ic">📊</div><div class="sec-t">نظام النقاط</div></div>
  <div class="pts2">
    <div class="pt2 win"><div class="e">🟢</div><div class="l">فوز</div><div class="n">3</div><div class="u">نقاط</div></div>
    <div class="pt2 loss"><div class="e">🔴</div><div class="l">خسارة</div><div class="n">0</div><div class="u">نقطة</div></div>
  </div>
  <div class="note">⚠️ <strong>لا يوجد تعادل في الشيش</strong> — كل مباراة تنتهي بفائز واحد فقط.<br>
  <strong>⚖️ الفصل عند التساوي في النقاط:</strong> ١. المواجهة المباشرة &nbsp;•&nbsp; ٢. فارق النقاط &nbsp;•&nbsp; ٣. القرعة</div>
</div>
<div class="sec">
  <div class="sec-hd"><div class="sec-ic">🗓️</div><div class="sec-t">الخط الزمني</div></div>
  <div class="tl">
    <div class="tl-item"><div class="tl-dot"></div><div>
      <div class="tl-day">الأيام 1 → 11 · مرحلة الدوري</div>
      <div class="tl-desc">يوم ورى يوم — الأربعاء 1 رمضان حتى الثلاثاء 21 رمضان ⏰ 12 ليلاً</div>
    </div></div>
    <div class="tl-item"><div class="tl-dot s"></div><div>
      <div class="tl-day">السبت 25 رمضان · نصف النهائي</div>
      <div class="tl-desc">أفضل 4 فرق — مباراتان حاسمتان ⏰ 12 ليلاً</div>
    </div></div>
    <div class="tl-item"><div class="tl-dot g"></div><div>
      <div class="tl-day">الثلاثاء 28 رمضان · يوم التتويج 🏆</div>
      <div class="tl-desc">مباراة المركز الثالث ثم النهائي الكبير — تتويج بطل صفوة المهيدب 🎲🔥</div>
    </div></div>
  </div>
</div>
<div class="note" style="background:#f0f8ff;border-color:#b0d4f0;color:#1a3a5c;">
  <strong>⏰ التوقيت:</strong> الساعة 12 منتصف الليل كل يوم لعب &nbsp;&nbsp;
  <strong>💡 ملاحظة:</strong> بعد الاعتماد يُضاف أسماء الفرق ويُطلق الجدول التفصيلي.
</div>
<div class="champ"><div class="ci">🏆</div>
<div class="ct">بطل بطولة صفوة المهيدب الرمضانية 1448هـ</div>
<div class="cl">يُكتب هنا اسم البطل بعد النهائي الكبير</div></div>
<div class="ft"><span class="br">🎲 بطولة صفوة المهيدب الرمضانية للشيش</span><span>🌙 رمضان كريم 1448هـ</span><span>4 / 4</span></div>
</div>""")

# ===== RENDER with pikepdf =====
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
    # Save to temp file for pikepdf
    tmp_path = f'/tmp/shish_page_{idx}.pdf'
    with open(tmp_path, 'wb') as f:
        f.write(pdf_bytes)
    page_pdfs.append(tmp_path)

# Merge with pikepdf (clean merge, no cross-reference issues)
out_path = 'shish_FINAL_v8.pdf'
with pikepdf.Pdf.new() as out_pdf:
    for pg_path in page_pdfs:
        src = pikepdf.Pdf.open(pg_path)
        out_pdf.pages.extend(src.pages)
        src.close()
    out_pdf.save(out_path)

print(f"\n{'✅ تمام!' if all_ok else '⚠️'} {len(page_pdfs)} صفحات → {out_path}")
subprocess.run(['convert','-density','120',f'{out_path}[0]','-resize','500x','cover_v8.png'], capture_output=True)
print("✅ Preview ready")
