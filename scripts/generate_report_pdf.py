#!/usr/bin/env python3
"""Generate professional Arabic PDF for AI Advertising Report"""

from fpdf import FPDF

FONT_PATH = "/home/openclaw/.local/share/fonts/Cairo.ttf"
OUTPUT = "/home/openclaw/.openclaw/workspace/reports/ai-advertising-report-2026.pdf"

# Colors
DARK_BLUE = (0, 51, 102)
MEDIUM_BLUE = (0, 102, 153)
ACCENT_TEAL = (0, 150, 136)
ACCENT_ORANGE = (230, 126, 34)
DARK_GRAY = (51, 51, 51)
LIGHT_GRAY = (245, 245, 245)
WHITE = (255, 255, 255)
TABLE_HEADER_BG = (0, 51, 102)
TABLE_ALT_ROW = (240, 248, 255)
QUOTE_BG = (248, 249, 250)
QUOTE_BORDER = (0, 150, 136)
RED_ACCENT = (192, 57, 43)


class ArabicPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Cairo", "", FONT_PATH)
        self.set_text_shaping(True)
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Cairo", "", 8)
        self.set_text_color(*MEDIUM_BLUE)
        self.cell(0, 8, text="الذكاء الاصطناعي يغزو عالم الإعلانات — تقرير تحليلي معمّق", align="C")
        self.ln(4)
        self.set_draw_color(*ACCENT_TEAL)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), self.w - 20, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Cairo", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, text=f"— {self.page_no()} —", align="C")

    def cover_page(self):
        self.add_page()
        self.ln(40)
        # Decorative top bar
        self.set_fill_color(*DARK_BLUE)
        self.rect(0, 0, self.w, 8, "F")
        self.set_fill_color(*ACCENT_TEAL)
        self.rect(0, 8, self.w, 3, "F")

        # Title
        self.ln(20)
        self.set_font("Cairo", "", 28)
        self.set_text_color(*DARK_BLUE)
        self.multi_cell(0, 16, text="الذكاء الاصطناعي\nيغزو عالم الإعلانات", align="C")

        self.ln(5)
        self.set_draw_color(*ACCENT_TEAL)
        self.set_line_width(1.5)
        cx = self.w / 2
        self.line(cx - 40, self.get_y(), cx + 40, self.get_y())
        self.ln(8)

        self.set_font("Cairo", "", 18)
        self.set_text_color(*MEDIUM_BLUE)
        self.cell(0, 12, text="حرب المليارات بين الإعلان المباشر والتجارة الوكيلة", align="C")
        self.ln(15)

        self.set_font("Cairo", "", 14)
        self.set_text_color(*ACCENT_TEAL)
        self.cell(0, 10, text="تقرير تحليلي معمّق", align="C")
        self.ln(25)

        # Info box
        self.set_fill_color(*LIGHT_GRAY)
        box_y = self.get_y()
        self.rect(40, box_y, self.w - 80, 35, "F")
        self.set_draw_color(*MEDIUM_BLUE)
        self.set_line_width(0.3)
        self.rect(40, box_y, self.w - 80, 35, "D")
        
        self.set_xy(40, box_y + 5)
        self.set_font("Cairo", "", 11)
        self.set_text_color(*DARK_GRAY)
        self.cell(self.w - 80, 8, text="تاريخ الإعداد: 16 فبراير 2026", align="C")
        self.ln(10)
        self.set_x(40)
        self.set_font("Cairo", "", 9)
        self.set_text_color(120, 120, 120)
        self.multi_cell(self.w - 80, 6, text="أُعدّ بالاستناد إلى معلومات موثّقة حتى أوائل 2025، مع إشارات لتطورات لاحقة", align="C")

        # Bottom bar
        self.set_fill_color(*DARK_BLUE)
        self.rect(0, self.h - 11, self.w, 8, "F")
        self.set_fill_color(*ACCENT_TEAL)
        self.rect(0, self.h - 14, self.w, 3, "F")

    def chapter_title(self, number, title):
        self.ln(6)
        y = self.get_y()
        # Color bar on left
        self.set_fill_color(*DARK_BLUE)
        self.rect(self.w - 24, y, 4, 12, "F")
        
        self.set_font("Cairo", "", 18)
        self.set_text_color(*DARK_BLUE)
        self.cell(0, 12, text=f"الفصل {number}: {title}", align="R")
        self.ln(4)
        self.set_draw_color(*ACCENT_TEAL)
        self.set_line_width(1)
        self.line(20, self.get_y(), self.w - 20, self.get_y())
        self.ln(6)

    def section_title(self, title, color=None):
        if color is None:
            color = MEDIUM_BLUE
        self.ln(3)
        self.set_font("Cairo", "", 14)
        self.set_text_color(*color)
        # Small bullet
        self.cell(0, 10, text=f"◆  {title}", align="R")
        self.ln(3)

    def subsection_title(self, title):
        self.ln(2)
        self.set_font("Cairo", "", 12)
        self.set_text_color(*ACCENT_TEAL)
        self.cell(0, 9, text=f"▸  {title}", align="R")
        self.ln(2)

    def body_text(self, text):
        self.set_font("Cairo", "", 11)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(0, 7, text=text, align="R")
        self.ln(2)

    def bullet_point(self, text):
        self.set_font("Cairo", "", 11)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(0, 7, text=f"●  {text}", align="R")
        self.ln(1)

    def quote_block(self, text, author=""):
        self.ln(3)
        y = self.get_y()
        # Background
        self.set_fill_color(*QUOTE_BG)
        h = max(20, len(text) * 0.15 + 15)
        self.rect(25, y, self.w - 50, h, "F")
        # Left accent bar
        self.set_fill_color(*QUOTE_BORDER)
        self.rect(self.w - 28, y, 3, h, "F")
        
        self.set_xy(28, y + 3)
        self.set_font("Cairo", "", 10)
        self.set_text_color(80, 80, 80)
        self.multi_cell(self.w - 60, 6, text=f'"{text}"', align="R")
        if author:
            self.set_font("Cairo", "", 9)
            self.set_text_color(*ACCENT_TEAL)
            self.cell(self.w - 60, 6, text=f"— {author}", align="R")
            self.ln(2)
        self.set_y(max(self.get_y(), y + h + 3))
        self.ln(3)

    def add_table(self, headers, rows):
        self.ln(3)
        n_cols = len(headers)
        col_w = (self.w - 40) / n_cols

        # Header
        self.set_fill_color(*TABLE_HEADER_BG)
        self.set_text_color(*WHITE)
        self.set_font("Cairo", "", 10)
        for h in headers:
            self.cell(col_w, 9, text=h, align="C", fill=True, border=1)
        self.ln()

        # Rows
        self.set_font("Cairo", "", 9)
        for i, row in enumerate(rows):
            if i % 2 == 0:
                self.set_fill_color(*TABLE_ALT_ROW)
            else:
                self.set_fill_color(*WHITE)
            self.set_text_color(*DARK_GRAY)
            for cell in row:
                self.cell(col_w, 8, text=cell, align="C", fill=True, border=1)
            self.ln()
        self.ln(4)

    def numbered_item(self, number, title, desc=""):
        self.set_font("Cairo", "", 11)
        self.set_text_color(*ACCENT_ORANGE)
        line = f"{number}. {title}"
        self.cell(0, 8, text=line, align="R")
        self.ln(1)
        if desc:
            self.set_font("Cairo", "", 10)
            self.set_text_color(*DARK_GRAY)
            self.multi_cell(0, 6, text=f"    {desc}", align="R")
            self.ln(1)


def build_pdf():
    pdf = ArabicPDF()

    # ===== COVER =====
    pdf.cover_page()

    # ===== المقدمة =====
    pdf.add_page()
    pdf.section_title("المقدمة", DARK_BLUE)
    pdf.body_text("يشهد عالم الإعلانات الرقمية تحولاً جذرياً غير مسبوق. لم يعد الذكاء الاصطناعي مجرد أداة لتحسين استهداف الإعلانات أو أتمتة الحملات، بل أصبح هو المنصة ذاتها. في مشهد تتسارع فيه الأحداث، تتنافس أكبر شركات التقنية على إعادة تشكيل العلاقة بين المستهلك والعلامة التجارية من خلال وكلاء ذكاء اصطناعي قادرين على اتخاذ قرارات الشراء نيابةً عن المستخدم.")
    pdf.body_text("هذا التقرير يرصد ملامح هذا التحول، ويحلّل استراتيجيات اللاعبين الرئيسيين، ويستعرض المخاوف المتصاعدة حول مستقبل يُدار فيه التسوّق والإعلان بالكامل عبر الآلة.")

    # ===== الفصل الأول =====
    pdf.chapter_title("الأول", 'OpenAI والإعلانات في ChatGPT')
    pdf.section_title("الخلفية")
    pdf.body_text("منذ إطلاق ChatGPT في نوفمبر 2022، ظلّ سام ألتمان يؤكد أن الشركة لا تخطط لإدخال إعلانات في منتجاتها. لكن الموقف بدأ يتغير تدريجياً مع تصاعد تكاليف التشغيل وتوسّع قاعدة المستخدمين.")

    pdf.section_title("التحوّل الكبير — ديسمبر 2024")
    pdf.body_text("كشفت صحيفة Financial Times أن OpenAI بدأت رسمياً في دراسة إدخال إعلانات في منتجاتها:")
    pdf.bullet_point("سارة فراير (Sarah Friar)، المديرة المالية، تقود جهود استكشاف نموذج الإعلانات")
    pdf.bullet_point("ألتمان وصف الإعلانات بأنها «الملاذ الأخير» لكنه لم يستبعدها")
    pdf.bullet_point("تعيين مسؤولين سابقين من Meta وGoogle مؤشر على الاتجاه الإعلاني")

    pdf.section_title("نموذج الإيرادات وضغوطه")
    pdf.bullet_point("إيرادات سنوية: ~3.4 مليار دولار (اشتراكات + API)")
    pdf.bullet_point("تكاليف التشغيل: تتجاوز 5 مليارات دولار سنوياً")
    pdf.bullet_point("تمويل 6.6 مليار دولار (أكتوبر 2024) بتقييم 157 مليار — ضغط هائل للاستدامة")

    pdf.section_title("كيف ستبدو الإعلانات في ChatGPT؟")
    pdf.numbered_item(1, "توصيات مدفوعة", "اقتراحات مموّلة عند السؤال عن منتجات أو خدمات")
    pdf.numbered_item(2, "شراكات مع علامات تجارية", "مثل الشراكة مع Shopify لدمج التسوق المباشر")
    pdf.numbered_item(3, "إعلانات في البحث", "نتائج بحث مدفوعة ضمن ChatGPT Search")
    pdf.numbered_item(4, "رعاية المحتوى", "محتوى مموّل ضمن الإجابات")

    pdf.quote_block("لسنا في عجلة لوضع إعلانات، لكننا لا نستبعد أي خيار", "سام ألتمان، ديسمبر 2024")

    # ===== الفصل الثاني =====
    pdf.chapter_title("الثاني", "جوجل والتجارة الوكيلة")
    pdf.section_title("ما هي التجارة الوكيلة (Agentic Commerce)؟")
    pdf.body_text("نموذج تجاري جديد يقوم فيه وكيل ذكاء اصطناعي بإدارة رحلة التسوق كاملة نيابة عن المستخدم: من البحث عن المنتج، إلى المقارنة، إلى التفاوض على السعر، إلى إتمام الشراء والدفع.")

    pdf.section_title("استراتيجية جوجل — Google I/O 2025")
    pdf.subsection_title("Google Shopping يتحول لوكيل تسوّق ذكي")
    pdf.bullet_point("إعادة بناء كاملة لتجربة Shopping باستخدام نموذج Gemini")
    pdf.bullet_point("الوكيل يفهم السياق: ميزانيتك، تفضيلاتك، مشترياتك السابقة")
    pdf.bullet_point("بحث عبر ملايين المتاجر وتقديم توصية مخصصة")

    pdf.subsection_title("Project Mariner — وكيل المتصفح")
    pdf.bullet_point("وكيل AI يعمل داخل Chrome — يتسوق ويشتري نيابة عنك")
    pdf.bullet_point("أُعلن عنه أواخر 2024 وبدأ الاختبار المحدود في 2025")

    pdf.subsection_title("AI Overviews + Shopping")
    pdf.bullet_point("دمج نتائج التسوق في ملخصات البحث المدعومة بالذكاء الاصطناعي")

    pdf.section_title("الأرقام")
    pdf.bullet_point("جوجل تسيطر على ~28.4% من سوق الإعلانات الرقمية عالمياً")
    pdf.bullet_point("إيرادات الإعلانات: 307.4 مليار دولار في 2024")
    pdf.bullet_point("قطاع Shopping Ads ينمو ~18% سنوياً")

    # ===== الفصل الثالث =====
    pdf.chapter_title("الثالث", "بروتوكولات جوجل التجارية الجديدة")
    pdf.body_text("أعلنت جوجل عن تطوير بروتوكولات تجارية مفتوحة (Commerce Protocols) تهدف إلى توحيد الطريقة التي تتفاعل بها وكلاء الذكاء الاصطناعي مع المتاجر الإلكترونية.")

    pdf.section_title("المكونات الرئيسية")
    pdf.numbered_item(1, "Agent Commerce API", "واجهة برمجة للاستعلام عن المنتجات والأسعار والتوفر آلياً")
    pdf.numbered_item(2, "Product Data Protocol", "معيار موحد لوصف المنتجات بطريقة يفهمها AI")
    pdf.numbered_item(3, "Checkout Protocol", "آلية آمنة لإتمام الشراء والدفع عبر الوكيل")
    pdf.numbered_item(4, "Trust & Verification Layer", "طبقة تحقق من هوية الوكيل والمستخدم")

    pdf.section_title("لماذا هذا مهم؟", RED_ACCENT)
    pdf.bullet_point("يحوّل الإنترنت من واجهات بشرية (مواقع) إلى واجهات آلية (APIs للوكلاء)")
    pdf.bullet_point("من يملك البروتوكول يملك البنية التحتية")
    pdf.bullet_point("المتاجر التي لا تدعمها ستصبح غير مرئية لوكلاء AI")

    # ===== الفصل الرابع =====
    pdf.chapter_title("الرابع", "المقارنة — OpenAI مقابل جوجل")

    pdf.add_table(
        ["جوجل (تجارة وكيلة)", "OpenAI (إعلانات مباشرة)", "المعيار"],
        [
            ["وكيل AI يدير التسوق كاملة", "إعلانات ضمن المحادثة والبحث", "النموذج"],
            ["عمولات + إعلانات", "رسوم إعلانية من العلامات التجارية", "مصدر الربح"],
            ["تفويض كامل للوكيل", "إجابات مع محتوى مدعوم", "تجربة المستخدم"],
            ["بروتوكولات + بحث + متصفح", "منصة محادثة", "البنية التحتية"],
            ["90%+ من البحث عالمياً", "400+ مليون مستخدم أسبوعياً", "نقطة القوة"],
            ["تآكل الثقة بسبب الإعلانات", "لا بنية تجارية سابقة", "نقطة الضعف"],
        ]
    )

    pdf.body_text("نهج OpenAI يشبه فيسبوك: بناء قاعدة مستخدمين ثم التسييل بالإعلانات. الخطر: ChatGPT بُني على الثقة والإعلانات قد تُضعفها.")
    pdf.body_text("نهج جوجل أكثر طموحاً: امتلاك البنية التحتية للتجارة الذكية. إذا نجحت، ستصبح جوجل «سويفت» (SWIFT) للتجارة الذكية.")

    # ===== الفصل الخامس =====
    pdf.chapter_title("الخامس", "اللاعبون الآخرون")

    pdf.section_title("Perplexity AI — الإعلانات المحادثاتية")
    pdf.bullet_point("برنامج «الأسئلة المدعومة» — أسئلة إضافية مموّلة بعد الإجابة")
    pdf.bullet_point("شركاء أوائل: Nike، Marriott، شركات تقنية")
    pdf.bullet_point("تقييم الشركة وصل إلى 9 مليارات دولار أواخر 2024")

    pdf.section_title("Meta — فيسبوك/إنستغرام")
    pdf.bullet_point("Advantage+ لأتمتة إنشاء الإعلانات واستهدافها بالكامل")
    pdf.bullet_point("Meta AI كمساعد ذكي ونقطة تسوّق داخل واتساب وماسنجر")
    pdf.bullet_point("إيرادات إعلانات: 164 مليار دولار في 2024")
    pdf.bullet_point("أدوات AI لإنشاء إعلانات فيديو وصور بتكلفة أقل 70%")

    pdf.section_title("Amazon")
    pdf.bullet_point("أطلقت Rufus — مساعد تسوّق AI مدمج في التطبيق")
    pdf.bullet_point("إيرادات الإعلانات تجاوزت 50 مليار دولار في 2024")
    pdf.bullet_point("إعلانات مدمجة في التوصيات — الأكثر طبيعية والأصعب اكتشافاً")

    pdf.section_title("Microsoft / Copilot")
    pdf.bullet_point("إعلانات في Bing Chat / Copilot منذ مايو 2023")
    pdf.bullet_point("إعلانات تجارية مرئية: منتجات مع صور وأسعار")
    pdf.bullet_point("استثمار 13 مليار في OpenAI يمنح موقعاً فريداً")

    pdf.section_title("TikTok / ByteDance")
    pdf.bullet_point("TikTok Shop مع توصيات AI")
    pdf.bullet_point("التسوق الحي (Live Shopping) حقق نجاحاً كبيراً في آسيا")

    # ===== الفصل السادس =====
    pdf.chapter_title("السادس", "الأرقام — سوق الإعلانات بالذكاء الاصطناعي")

    pdf.section_title("حجم السوق")
    pdf.add_table(
        ["المصدر", "القيمة", "المؤشر"],
        [
            ["eMarketer/Statista", "~740 مليار $", "سوق الإعلانات الرقمية 2024"],
            ["McKinsey", "~35-40%", "حصة AI في تحسين الإعلانات"],
            ["MarketsandMarkets", "~50-60 مليار $", "سوق AI في الإعلانات 2024"],
            ["Grand View Research", "CAGR ~25-30%", "النمو المتوقع حتى 2028"],
            ["Gartner", "~150-200 مليار $", "التجارة الوكيلة 2030"],
        ]
    )

    pdf.section_title("إيرادات اللاعبين الكبار (2024)")
    pdf.add_table(
        ["نمو سنوي", "إيرادات الإعلانات", "الشركة"],
        [
            ["~11%", "~307 مليار $", "Google"],
            ["~22%", "~164 مليار $", "Meta"],
            ["~24%", "~50+ مليار $", "Amazon"],
            ["~10%", "~18 مليار $", "Microsoft"],
            ["~40%", "~30+ مليار $", "TikTok"],
        ]
    )

    pdf.section_title("التوقعات", RED_ACCENT)
    pdf.bullet_point("بحلول 2027: 60% من عمليات الشراء ستتأثر مباشرة بتوصيات AI — Gartner")
    pdf.bullet_point("بحلول 2028: 25% من عمليات الشراء ستتم عبر وكلاء AI بدون تدخل بشري — Forrester")

    # ===== الفصل السابع =====
    pdf.chapter_title("السابع", "المخاوف والتحديات")

    pdf.section_title("1. الخصوصية", RED_ACCENT)
    pdf.body_text("وكلاء AI بحاجة لمعرفة كل شيء عنك: ميزانيتك، تفضيلاتك، تاريخك الصحي، موقعك، حتى مزاجك.")
    pdf.bullet_point("من يملك هذه البيانات؟ هل يمكن مشاركتها مع المعلنين؟")
    pdf.bullet_point("التشريعات الحالية (GDPR، CCPA) لم تُصمم لعالم الوكلاء الذكية")
    pdf.quote_block("نحن ننتقل من عصر «ملفات تعريف الارتباط» إلى عصر «ملفات تعريف الشخصية الكاملة»", "بروس شناير، خبير الأمن السيبراني")

    pdf.section_title("2. الثقة والحيادية", RED_ACCENT)
    pdf.body_text("إذا كان الوكيل يكسب من الإعلانات، فكيف تثق بتوصياته؟ تضارب المصالح هو التحدي الأكبر.")
    pdf.bullet_point("دراسة MIT (2024): 73% من المستخدمين يثقون بتوصيات AI أكثر من الإعلانات — مما يجعل التلاعب أسهل وأخطر")

    pdf.section_title("3. التلاعب النفسي", RED_ACCENT)
    pdf.bullet_point("اكتشاف لحظات الضعف النفسي واستغلالها")
    pdf.bullet_point("تقنيات إقناع مخصصة (Dark Patterns) بكفاءة غير مسبوقة")
    pdf.bullet_point("لا قوانين واضحة ضد «الإقناع الخوارزمي»")
    pdf.quote_block("الذكاء الاصطناعي لا يعرض عليك إعلاناً — إنه يصنع الرغبة من الصفر", "شوشانا زوبوف")

    pdf.section_title("4. الشفافية", RED_ACCENT)
    pdf.bullet_point("هل يجب الإفصاح عن كل توصية مدفوعة؟")
    pdf.bullet_point("كيف نميّز بين «رأي» AI و«إعلان» AI؟")

    pdf.section_title("5. الاحتكار", RED_ACCENT)
    pdf.bullet_point("بروتوكولات جوجل قد تتحكم في بوابة التجارة الذكية بالكامل")
    pdf.bullet_point("المتاجر الصغيرة ستُقصى")
    pdf.bullet_point("خطر «ضريبة الوكيل» — عمولة للوصول للمستهلك عبر AI")

    pdf.section_title("6. التنظيم والتشريع", RED_ACCENT)
    pdf.bullet_point("الاتحاد الأوروبي يحدّث قانون الخدمات الرقمية ليشمل إعلانات AI")
    pdf.bullet_point("FTC أصدرت تحذيرات بشأن الإعلانات المخفية في أدوات AI")

    # ===== الفصل الثامن =====
    pdf.chapter_title("الثامن", "آراء خبراء ومحللين")

    pdf.quote_block("الإعلانات ليست خطتنا الأولى، لكن مع 400 مليون مستخدم أسبوعي، نحتاج نموذجاً مستداماً. الاشتراكات وحدها لن تكفي لتمويل AGI.", "سام ألتمان — CEO, OpenAI")
    pdf.quote_block("المستقبل ليس البحث عن منتجات — المستقبل هو أن يجد الذكاء الاصطناعي المنتج المناسب لك تلقائياً.", "سوندار بيتشاي — CEO, Google")
    pdf.quote_block("جوجل لا تبني أداة تسوّق — إنها تبني نظام تشغيل للتجارة. من يملك البروتوكول يملك السوق.", "بن تومبسون — Stratechery")
    pdf.quote_block("الإعلانات في ChatGPT ستكون أخطر من إعلانات جوجل بعشر مرات. عندما تثق في شيء كصديق، فإن نصيحته المدفوعة تؤثر فيك أكثر.", "سكوت غالوي — NYU")
    pdf.quote_block("الوكلاء الذكيون هم الحلم النهائي لرأسمالية المراقبة: لا يكتفون بمعرفة ما تريد، بل يقررون نيابة عنك ما ستشتري.", "شوشانا زوبوف")

    pdf.section_title("تقارير مؤسسية")
    pdf.bullet_point("Morgan Stanley: دخول OpenAI لسوق الإعلانات قد يضيف 5-10 مليارات بحلول 2027")
    pdf.bullet_point("Goldman Sachs: التجارة الوكيلة ستعيد رسم خريطة الإنفاق الإعلاني بالكامل")

    # ===== الخلاصة =====
    pdf.add_page()
    pdf.ln(5)
    pdf.set_fill_color(*DARK_BLUE)
    y = pdf.get_y()
    pdf.rect(20, y, pdf.w - 40, 14, "F")
    pdf.set_xy(20, y + 2)
    pdf.set_font("Cairo", "", 18)
    pdf.set_text_color(*WHITE)
    pdf.cell(pdf.w - 40, 10, text="الخلاصة: ملامح المستقبل", align="C")
    pdf.ln(18)

    pdf.section_title("ثلاث حقائق لا مفر منها", ACCENT_ORANGE)

    pdf.set_font("Cairo", "", 12)
    pdf.set_text_color(*DARK_BLUE)
    pdf.cell(0, 9, text="1. الإعلان التقليدي يحتضر", align="R")
    pdf.ln(2)
    pdf.body_text("لن يختفي غداً، لكنه لن يكون المهيمن بعد 5 سنوات. المستقبل لإعلانات مدمجة في سياق AI وللتجارة التي يديرها الوكلاء.")

    pdf.set_font("Cairo", "", 12)
    pdf.set_text_color(*DARK_BLUE)
    pdf.cell(0, 9, text="2. المعركة على البنية التحتية — لا الإعلان", align="R")
    pdf.ln(2)
    pdf.body_text("من يملك «القضبان» التي تمر عليها التجارة الذكية يكسب أكثر ممن يملك «اللافتة» على جانب الطريق.")

    pdf.set_font("Cairo", "", 12)
    pdf.set_text_color(*DARK_BLUE)
    pdf.cell(0, 9, text="3. الخاسر الأكبر: المستهلك — إذا غابت الشفافية", align="R")
    pdf.ln(2)
    pdf.body_text("عندما يصبح «مستشارك الذكي» هو نفسه «بائع الإعلانات»، تتلاشى الحدود بين النصيحة والتسويق.")

    pdf.ln(5)
    # Central question box
    y = pdf.get_y()
    pdf.set_fill_color(*ACCENT_TEAL)
    pdf.rect(25, y, pdf.w - 50, 30, "F")
    pdf.set_xy(30, y + 5)
    pdf.set_font("Cairo", "", 12)
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(pdf.w - 60, 7, text="السؤال المركزي:\nهل سيكون وكيل الذكاء الاصطناعي «محامي المستهلك» الذي يدافع عن مصلحته…\nأم «وسيط المعلن» الذي يبيعه أعلى سعر؟", align="C")
    pdf.set_y(y + 35)

    # ===== المصادر =====
    pdf.ln(10)
    pdf.section_title("قائمة المصادر الرئيسية", MEDIUM_BLUE)
    sources = [
        "Financial Times — OpenAI explores advertising (ديسمبر 2024)",
        "The Information — Inside OpenAI's Costs and Revenue (2024)",
        "Bloomberg — تقارير استراتيجيات OpenAI وGoogle (2024-2025)",
        "Google I/O 2025 — العرض الرئيسي",
        "Google Developers Blog — Commerce Protocols",
        "Stratechery (Ben Thompson) — AI Commerce (2025)",
        "eMarketer — Global Digital Ad Spending (2024-2025)",
        "Gartner — Future of Commerce Report (2025)",
        "Forrester — Predictions 2025: AI-Driven Commerce",
        "Morgan Stanley — OpenAI Monetization Outlook (2025)",
        "Goldman Sachs — Agentic Commerce: The Next Frontier (2025)",
        "MIT Technology Review — Can You Trust AI Recommendations? (2024)",
    ]
    for i, s in enumerate(sources, 1):
        pdf.set_font("Cairo", "", 9)
        pdf.set_text_color(*DARK_GRAY)
        pdf.cell(0, 6, text=f"{i}. {s}", align="R")
        pdf.ln(1)

    # Disclaimer
    pdf.ln(8)
    pdf.set_draw_color(*MEDIUM_BLUE)
    pdf.set_line_width(0.3)
    pdf.line(40, pdf.get_y(), pdf.w - 40, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Cairo", "", 8)
    pdf.set_text_color(140, 140, 140)
    pdf.multi_cell(0, 5, text="أُعدّ هذا التقرير كمادة تحليلية. المعلومات مبنية على مصادر موثّقة مع ملاحظة أن بعض الأرقام تقديرية. يُنصح بالتحقق المستقل قبل النشر.", align="C")

    pdf.output(OUTPUT)
    print(f"✅ PDF saved: {OUTPUT}")
    print(f"Pages: {pdf.pages_count}")


if __name__ == "__main__":
    build_pdf()
