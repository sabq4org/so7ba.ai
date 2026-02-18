from weasyprint import HTML
import pikepdf, PyPDF2, io, subprocess, base64

# Embed Cairo font
with open('/home/openclaw/.local/share/fonts/Cairo.ttf', 'rb') as f:
    CAIRO_B64 = base64.b64encode(f.read()).decode()
CAIRO_URL = f"data:font/truetype;base64,{CAIRO_B64}"

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
.badge { display:block; max-width:120mm; margin:0 auto 4mm auto; border:1px solid rgba(197,160,55,0.5); background:rgba(197,160,55,0.1); color:#c5a037; font-size:9px; font-weight:700; padding:2px 14px; border-radius:20px; letter-spacing:1.5px; }
.main-title { color:#fff; font-size:38px; font-weight:900; line-height:1.15; margin-bottom:3mm; }
.sub-title { color:#c5a037; font-size:20px; font-weight:700; margin-bottom:3mm; }
.year { color:rgba(255,255,255,0.36); font-size:11px; margin-bottom:5mm; }
.divider { width:55mm; height:1.5px; background:linear-gradient(90deg,transparent,#c5a037,transparent); margin:0 auto 5mm auto; }
.cover-desc { color:rgba(255,255,255,0.6); font-size:12px; line-height:2; max-width:140mm; margin:0 auto; }
.cover-icon { font-size:64px; margin-bottom:5mm; }

.pg { width:210mm; height:297mm; page-break-after:always; padding:10mm 12mm 8mm; background:#f9f7f2; display:flex; flex-direction:column; overflow:hidden; }
.pg-last { page-break-after:auto; }
.hdr { display:flex; align-items:center; justify-content:space-between; padding-bottom:2mm; border-bottom:2.5px solid #0d1f3c; margin-bottom:4mm; }
.hdr-brand { font-size:11px; font-weight:900; color:#0d1f3c; }
.hdr-brand span { color:#c5a037; }
.hdr-pg { font-size:10px; color:#999; font-weight:600; }

.sec { margin-bottom:3mm; }
.sec-hd { display:flex; align-items:center; gap:3mm; margin-bottom:3mm; }
.sec-ic { background:linear-gradient(135deg,#0d1f3c,#1a3a5c); color:#c5a037; width:8mm; height:8mm; border-radius:3px; display:flex; align-items:center; justify-content:center; font-size:14px; flex-shrink:0; }
.sec-t { font-size:14px; font-weight:900; color:#0d1f3c; }

.tmpl-card {
  background:#fff; border:1px solid #e0ddd0; border-radius:8px;
  border-top:3px solid #c5a037; padding:3.5mm; margin-bottom:3mm;
}
.tmpl-num { display:inline-block; background:linear-gradient(135deg,#0d1f3c,#1a3a5c); color:#c5a037; font-size:11px; font-weight:900; padding:1.5mm 4mm; border-radius:4px; margin-bottom:2mm; }
.tmpl-title { font-size:14px; font-weight:900; color:#0d1f3c; margin-bottom:1.5mm; }
.tmpl-use { font-size:9.5px; color:#888; margin-bottom:2mm; }
.tmpl-subj { background:#f5f3ed; border-right:4px solid #c5a037; padding:2mm 4mm; font-size:10px; color:#555; border-radius:0 4px 4px 0; margin-bottom:3mm; font-weight:700; }
.tmpl-body { background:#faf9f5; border:1px solid #eee; border-radius:5px; padding:3mm; font-size:10px; color:#333; line-height:1.9; white-space:pre-line; }

.tbl { width:100%; border-collapse:collapse; font-size:11px; background:#fff; }
.tbl thead tr { background:linear-gradient(135deg,#0d1f3c,#1a3a5c); color:#c5a037; }
.tbl th { padding:2.5mm 4mm; font-weight:700; font-size:11px; text-align:right; }
.tbl td { padding:2mm 4mm; border-bottom:1px solid #eee; color:#1a1a2e; font-size:11px; vertical-align:middle; }
.tbl tr:nth-child(even) td { background:#faf8f3; }

.ft { margin-top:auto; padding-top:3mm; border-top:1.5px solid #d0ccc0; display:flex; justify-content:space-between; align-items:center; font-size:9.5px; color:#aaa; }
.ft .br { color:#c5a037; font-weight:700; }

.html-box { background:#0d1f3c; border-radius:6px; padding:3mm; margin-bottom:3mm; direction:ltr; }
.html-box pre { color:#c5a037; font-size:8px; font-family:'Courier New',monospace; line-height:1.5; white-space:pre-wrap; word-break:break-all; }
.html-label { font-size:9px; color:#c5a037; font-weight:700; margin-bottom:1.5mm; text-align:left; }
"""

pages_html = []

# ===== COVER =====
pages_html.append("""<div class="cover">
<div class="gold-bar"></div>
<div class="cr-big">🌙</div><div class="cr-small">🌙</div>
<div class="star" style="top:26mm;right:28mm;font-size:13px;opacity:0.5;">✦</div>
<div class="star" style="top:44mm;right:58mm;font-size:8px;opacity:0.3;">★</div>
<div class="star" style="top:30mm;left:58mm;font-size:9px;opacity:0.3;">★</div>
<div class="frame"></div>
<div class="cover-body">
  <div class="cover-spacer"></div>
  <div class="cover-icon">📧</div>
  <div class="badge">📋 دليل مرجعي — قوالب المراسلات الرسمية</div>
  <div class="main-title">قوالب المراسلات</div>
  <div class="sub-title">صحيفة سبق الإلكترونية</div>
  <div class="year">نماذج موحّدة لكل أنواع المراسلات الرسمية</div>
  <div class="divider"></div>
  <div class="cover-desc">
    6 قوالب جاهزة • تنسيق موحّد • صياغة احترافية<br>
    قرارات إدارية • تكليفات • مخاطبات رسمية • شكر وتقدير
  </div>
  <div class="cover-spacer"></div>
</div>
<div class="gold-bar"></div>
</div>""")

# ===== PAGE 2: FORMAT + TEMPLATES 1-2 =====
pages_html.append("""<div class="pg">
<div class="hdr">
  <div class="hdr-brand">📧 <span>قوالب المراسلات</span> — صحيفة سبق الإلكترونية</div>
  <div class="hdr-pg">الصفحة 1 من 4</div>
</div>

<div class="sec">
  <div class="sec-hd"><div class="sec-ic">🎨</div><div class="sec-t">التنسيق العام</div></div>
  <div class="html-box">
    <div class="html-label">هيكل الإيميل الموحّد</div>
    <pre>ترويسة: صحيفة سبق الإلكترونية — رئيس التحرير
━━━━━━━━━━━━━━━━━━━━━━━
المخاطَب → المحتوى → التحية
━━━━━━━━━━━━━━━━━━━━━━━
التوقيع: علي الحازمي — رئيس التحرير
بصمة: تم إرسالها عن طريق صُحبة ✨</pre>
  </div>
</div>

<div class="tmpl-card">
  <div class="tmpl-num">1️⃣</div>
  <div class="tmpl-title">قرار إداري / اعتماد مالي</div>
  <div class="tmpl-use">صرف رواتب • اعتماد ميزانية • موافقات مالية</div>
  <div class="tmpl-subj">الموضوع: اعتماد [نوع القرار] — [التفاصيل]</div>
  <div class="tmpl-body">الأستاذ [الاسم] — [المنصب]

السلام عليكم ورحمة الله وبركاته،

أرجو اعتماد [تفاصيل القرار] للزميل/الزملاء:
• [اسم 1]  • [اسم 2]

وذلك [السبب]. [شروط التنفيذ]

تحياتي،</div>
</div>

<div class="tmpl-card">
  <div class="tmpl-num">2️⃣</div>
  <div class="tmpl-title">تكليف / تعميم داخلي</div>
  <div class="tmpl-use">تكليف موظف • تعميم إداري • توجيه</div>
  <div class="tmpl-subj">الموضوع: تكليف: [المهمة] — [الاسم]</div>
  <div class="tmpl-body">الزملاء الكرام / الأستاذ [الاسم] — [المنصب]

السلام عليكم ورحمة الله وبركاته،

يُعتمد تكليف [الاسم] بـ[المهمة] اعتباراً من [التاريخ].
• [بند 1]  • [بند 2]

أرجو التنسيق والتنفيذ.
تحياتي،</div>
</div>

<div class="ft"><span class="br">📧 قوالب المراسلات — صحيفة سبق</span><span>دليل مرجعي</span><span>1 / 4</span></div>
</div>""")

# ===== PAGE 3: TEMPLATES 3-4 =====
pages_html.append("""<div class="pg">
<div class="hdr">
  <div class="hdr-brand">📧 <span>قوالب المراسلات</span> — صحيفة سبق الإلكترونية</div>
  <div class="hdr-pg">الصفحة 2 من 4</div>
</div>

<div class="tmpl-card">
  <div class="tmpl-num">3️⃣</div>
  <div class="tmpl-title">مخاطبة جهة خارجية (رسمية)</div>
  <div class="tmpl-use">جهات حكومية • شركات • شراكات</div>
  <div class="tmpl-subj">الموضوع: [الموضوع] — صحيفة سبق الإلكترونية</div>
  <div class="tmpl-body">سعادة / معالي [اللقب] [الاسم]
[المنصب] — [الجهة]

السلام عليكم ورحمة الله وبركاته،
تحية طيبة وبعد،

[نص الرسالة]

وتفضلوا بقبول وافر التحية والتقدير.
علي الحازمي — رئيس التحرير</div>
</div>

<div class="tmpl-card">
  <div class="tmpl-num">4️⃣</div>
  <div class="tmpl-title">شكر وتقدير</div>
  <div class="tmpl-use">شكر موظف • تقدير إنجاز • تهنئة</div>
  <div class="tmpl-subj">الموضوع: شكر وتقدير — [الاسم/المناسبة]</div>
  <div class="tmpl-body">الأستاذ/ة [الاسم]

السلام عليكم ورحمة الله وبركاته،

يسرني أن أتقدم لك بالشكر والتقدير على [السبب].
[تفاصيل إضافية إن وجدت]

وفقك الله وسدد خطاك.
تحياتي،</div>
</div>

<div class="ft"><span class="br">📧 قوالب المراسلات — صحيفة سبق</span><span>دليل مرجعي</span><span>2 / 4</span></div>
</div>""")

# ===== PAGE 4: TEMPLATES 5-6 =====
pages_html.append("""<div class="pg">
<div class="hdr">
  <div class="hdr-brand">📧 <span>قوالب المراسلات</span> — صحيفة سبق الإلكترونية</div>
  <div class="hdr-pg">الصفحة 3 من 4</div>
</div>

<div class="tmpl-card">
  <div class="tmpl-num">5️⃣</div>
  <div class="tmpl-title">متابعة / تذكير</div>
  <div class="tmpl-use">متابعة طلب سابق • تذكير بموعد</div>
  <div class="tmpl-subj">الموضوع: متابعة: [الموضوع الأصلي]</div>
  <div class="tmpl-body">الأستاذ [الاسم]

السلام عليكم ورحمة الله وبركاته،

أود المتابعة بخصوص [الموضوع] المشار إليه بتاريخ [التاريخ].

أرجو التكرم بالإفادة عن المستجدات.
تحياتي،</div>
</div>

<div class="tmpl-card">
  <div class="tmpl-num">6️⃣</div>
  <div class="tmpl-title">اعتذار / إيضاح</div>
  <div class="tmpl-use">تصحيح خطأ • إيضاح موقف</div>
  <div class="tmpl-subj">الموضوع: إيضاح بخصوص [الموضوع]</div>
  <div class="tmpl-body">الأستاذ [الاسم]

السلام عليكم ورحمة الله وبركاته،

بالإشارة إلى [الموضوع]، أود الإيضاح بأن [التوضيح].
[الإجراء التصحيحي إن وجد]

نعتذر عن أي لبس، ونؤكد حرصنا على [الهدف].
تحياتي،</div>
</div>

<div class="ft"><span class="br">📧 قوالب المراسلات — صحيفة سبق</span><span>دليل مرجعي</span><span>3 / 4</span></div>
</div>""")

# ===== PAGE 5: RULES =====
pages_html.append("""<div class="pg pg-last">
<div class="hdr">
  <div class="hdr-brand">📧 <span>قوالب المراسلات</span> — صحيفة سبق الإلكترونية</div>
  <div class="hdr-pg">الصفحة 4 من 4</div>
</div>

<div class="sec">
  <div class="sec-hd"><div class="sec-ic">📌</div><div class="sec-t">القواعد العامة للمراسلات</div></div>
  <table class="tbl">
    <thead><tr><th style="width:30%;">القاعدة</th><th>التفاصيل</th></tr></thead>
    <tbody>
      <tr><td><strong>اللغة</strong></td><td>عربي فصيح مبسط — لا تكلف</td></tr>
      <tr><td><strong>الطول</strong></td><td>مختصر ومباشر — لا حشو</td></tr>
      <tr><td><strong>الخط</strong></td><td>Cairo — 15px للمحتوى، 18px للترويسة</td></tr>
      <tr><td><strong>الألوان</strong></td><td>كحلي #0d1f3c + ذهبي #c5a037</td></tr>
      <tr><td><strong>التوقيع</strong></td><td>ثابت: علي الحازمي — رئيس التحرير</td></tr>
      <tr><td><strong>بصمة صُحبة</strong></td><td>أسفل كل إيميل بخط صغير رمادي</td></tr>
      <tr><td><strong>المخاطبة</strong></td><td>الأستاذ / سعادة / معالي حسب المقام</td></tr>
      <tr><td><strong>الحساب الرسمي</strong></td><td>sabq4u@gmail.com</td></tr>
      <tr><td><strong>حساب صُحبة</strong></td><td>so7ba.ai@gmail.com</td></tr>
    </tbody>
  </table>
</div>

<div class="sec" style="margin-top:4mm;">
  <div class="sec-hd"><div class="sec-ic">⚙️</div><div class="sec-t">طريقة الاستخدام</div></div>
  <div style="background:#fff;border-right:5px solid #c5a037;border-radius:0 7px 7px 0;padding:3mm 5mm;font-size:11px;line-height:2;color:#333;">
    <strong>📌 تلقائي:</strong> صُحبة يختار القالب المناسب حسب نوع الإيميل<br>
    <strong>📌 موحّد:</strong> كل الرسائل تخرج بنفس الشكل والتنسيق<br>
    <strong>📌 مرن:</strong> أي تعديل على القوالب → أبلغ صُحبة ويحدّث فوراً
  </div>
</div>

<div class="ft"><span class="br">📧 قوالب المراسلات — صحيفة سبق</span><span>🌙 صُحبة ✨</span><span>4 / 4</span></div>
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
    page_pdfs.append(pdf_bytes)

out_path = 'email_templates_FINAL.pdf'
with pikepdf.Pdf.new() as out_pdf:
    for pdf_bytes in page_pdfs:
        src = pikepdf.Pdf.open(io.BytesIO(pdf_bytes))
        out_pdf.pages.extend(src.pages)
        src.close()
    out_pdf.save(out_path)

print(f"\n{'✅ تمام!' if all_ok else '⚠️'} {len(page_pdfs)} صفحات → {out_path}")

# Preview all pages
for i in range(len(page_pdfs)):
    subprocess.run(['convert', '-density', '150', f'{out_path}[{i}]', '-resize', '800x', f'email_tmpl_pg{i}.png'], capture_output=True)
    print(f"✅ Preview page {i}")
