#!/usr/bin/env python3
"""Generate educational Arabic PDF about Varicose Veins for Yara"""

from fpdf import FPDF

FONT_PATH = "/home/openclaw/.local/share/fonts/Cairo.ttf"
OUTPUT = "/home/openclaw/.openclaw/workspace/reports/الدوالي-شرح-مبسط.pdf"

# Colors
DARK_BLUE = (13, 71, 161)
MEDIUM_BLUE = (30, 136, 229)
LIGHT_BLUE = (227, 242, 253)
TEAL = (0, 150, 136)
TEAL_LIGHT = (224, 242, 241)
RED = (198, 40, 40)
RED_LIGHT = (255, 235, 238)
ORANGE = (230, 126, 34)
GREEN = (46, 125, 50)
GREEN_LIGHT = (232, 245, 233)
PURPLE = (106, 27, 154)
PURPLE_LIGHT = (243, 229, 245)
DARK_GRAY = (55, 55, 55)
LIGHT_GRAY = (245, 245, 245)
WHITE = (255, 255, 255)


class ArabicPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Cairo", "", FONT_PATH)
        self.set_text_shaping(True)
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(18, 18, 18)

    def footer(self):
        self.set_y(-18)
        self.set_font("Cairo", "", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, text=f"— {self.page_no()} —", align="C", new_x="LEFT", new_y="TOP")

    def colored_box(self, x, y, w, h, fill_color, border_color=None, radius=0):
        self.set_fill_color(*fill_color)
        if radius > 0:
            self.rect(x, y, w, h, "F", round_corners=True, corner_radius=radius)
        else:
            self.rect(x, y, w, h, "F")
        if border_color:
            self.set_draw_color(*border_color)
            self.set_line_width(0.5)
            if radius > 0:
                self.rect(x, y, w, h, "D", round_corners=True, corner_radius=radius)
            else:
                self.rect(x, y, w, h, "D")

    def cover_page(self):
        self.add_page()
        # Top accent bar
        self.set_fill_color(*DARK_BLUE)
        self.rect(0, 0, self.w, 6, "F")
        self.set_fill_color(*TEAL)
        self.rect(0, 6, self.w, 2, "F")

        # Main title area
        self.ln(35)
        
        # Heart + veins emoji as decorative element
        self.set_font("Cairo", "", 40)
        self.set_text_color(*RED)
        self.cell(0, 20, text="🩸🦵", align="C", new_x="LEFT", new_y="NEXT")
        self.ln(8)

        # Title
        self.set_font("Cairo", "", 32)
        self.set_text_color(*DARK_BLUE)
        self.cell(0, 18, text="الدوالي", align="C", new_x="LEFT", new_y="NEXT")
        self.ln(4)

        # Subtitle
        self.set_font("Cairo", "", 18)
        self.set_text_color(*TEAL)
        self.cell(0, 12, text="شرح مبسّط وسهل", align="C", new_x="LEFT", new_y="NEXT")
        self.ln(3)

        # Decorative line
        cx = self.w / 2
        self.set_draw_color(*TEAL)
        self.set_line_width(1.5)
        self.line(cx - 35, self.get_y(), cx + 35, self.get_y())
        self.ln(12)

        # Info box
        y = self.get_y()
        self.colored_box(35, y, self.w - 70, 30, LIGHT_BLUE, MEDIUM_BLUE)
        self.set_xy(35, y + 6)
        self.set_font("Cairo", "", 12)
        self.set_text_color(*DARK_BLUE)
        self.cell(self.w - 70, 8, text="📚 ملف تعليمي مبسّط", align="C", new_x="LEFT", new_y="NEXT")
        self.set_x(35)
        self.set_font("Cairo", "", 10)
        self.set_text_color(*DARK_GRAY)
        self.cell(self.w - 70, 8, text="يشرح الدوالي بطريقة سهلة ومفهومة", align="C", new_x="LEFT", new_y="NEXT")
        self.set_y(y + 35)

        # Bottom bars
        self.set_fill_color(*DARK_BLUE)
        self.rect(0, self.h - 8, self.w, 6, "F")
        self.set_fill_color(*TEAL)
        self.rect(0, self.h - 10, self.w, 2, "F")

    def section_header(self, title, emoji, color):
        self.ln(8)
        y = self.get_y()
        # Background bar
        light = tuple(min(255, c + 180) for c in color)
        self.set_fill_color(*color)
        self.rect(18, y, self.w - 36, 13, "F")
        self.set_xy(18, y + 1)
        self.set_font("Cairo", "", 16)
        self.set_text_color(*WHITE)
        self.cell(self.w - 36, 11, text=f"{emoji}  {title}", align="C", new_x="LEFT", new_y="NEXT")
        self.ln(6)

    def body(self, text):
        self.set_font("Cairo", "", 12)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(0, 9, text=text, align="R", new_x="LEFT", new_y="NEXT")
        self.ln(3)

    def bullet(self, text, icon="●", color=None):
        if color is None:
            color = DARK_GRAY
        self.set_font("Cairo", "", 12)
        self.set_text_color(*color)
        self.multi_cell(0, 9, text=f"  {icon}  {text}", align="R", new_x="LEFT", new_y="NEXT")
        self.ln(2)

    def info_box(self, text, bg_color, border_color, icon="💡"):
        self.ln(3)
        y = self.get_y()
        # Estimate height
        self.set_font("Cairo", "", 11)
        # Use a rough estimate: ~60 chars per line, 9pt line height
        lines = max(2, len(text) // 55 + 2)
        h = lines * 9 + 12
        self.colored_box(22, y, self.w - 44, h, bg_color, border_color)
        # Accent bar on right
        self.set_fill_color(*border_color)
        self.rect(self.w - 25, y, 3, h, "F")
        self.set_xy(25, y + 5)
        self.set_font("Cairo", "", 11)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(self.w - 54, 8, text=f"{icon}  {text}", align="R", new_x="LEFT", new_y="NEXT")
        self.set_y(max(self.get_y() + 2, y + h + 4))

    def numbered(self, num, title, desc="", color=None):
        if color is None:
            color = DARK_BLUE
        self.set_font("Cairo", "", 13)
        self.set_text_color(*color)
        self.cell(0, 10, text=f"  {num}  {title}", align="R", new_x="LEFT", new_y="NEXT")
        if desc:
            self.set_font("Cairo", "", 11)
            self.set_text_color(*DARK_GRAY)
            self.multi_cell(0, 8, text=f"       {desc}", align="R", new_x="LEFT", new_y="NEXT")
        self.ln(2)


def build():
    pdf = ArabicPDF()

    # ===== COVER =====
    pdf.cover_page()

    # ===== وش هي الدوالي؟ =====
    pdf.add_page()
    pdf.section_header("وش هي الدوالي؟", "🔍", DARK_BLUE)
    pdf.body("الدوالي (بالإنجليزي: Varicose Veins) هي أوردة منتفخة ومتضخمة تظهر عادةً في الساقين والقدمين. تكون ظاهرة تحت الجلد بلون أزرق أو بنفسجي غامق، وأحياناً تكون ملتوية أو بارزة.")

    pdf.info_box("الأوردة هي الأنابيب اللي ترجّع الدم من أعضاء الجسم إلى القلب. عكس الشرايين اللي توصل الدم من القلب للجسم.", LIGHT_BLUE, MEDIUM_BLUE, "🩸")

    pdf.ln(4)
    pdf.section_header("كيف تصير الدوالي؟", "⚙️", TEAL)
    pdf.body("داخل الأوردة في صمامات صغيرة (مثل الأبواب) شغلتها تخلي الدم يمشي باتجاه واحد فقط — من تحت لفوق، يعني من الرِّجل إلى القلب.")
    pdf.body("لما هالصمامات تضعف أو تتلف:")
    pdf.numbered("①", "الصمامات ما تقفل صح", "بدل ما الدم يطلع للقلب، يرجع وينزل لتحت")
    pdf.numbered("②", "الدم يتجمّع في الوريد", "الوريد يبدأ ينتفخ ويتمدد من كثر الدم المتراكم")
    pdf.numbered("③", "الوريد يكبر ويبان", "يصير ظاهر تحت الجلد، متورم ومتعرّج")

    pdf.info_box("تخيّلي خرطوم ماء فيه بلّوف (صمامات)… لو البلّوف خربت، الماء بيرجع ويتجمع ويورّم الخرطوم. نفس الفكرة بالضبط!", GREEN_LIGHT, GREEN, "🪴")

    # ===== الأسباب =====
    pdf.add_page()
    pdf.section_header("ليش تصير الدوالي؟ (الأسباب)", "❓", ORANGE)

    pdf.numbered("①", "الوقوف أو الجلوس لفترات طويلة", "يخلي الدم يتجمع في الأرجل لأن الجاذبية تسحبه لتحت", ORANGE)
    pdf.numbered("②", "الوراثة", "لو أحد من العائلة عنده دوالي، احتمال تجيك أكبر", ORANGE)
    pdf.numbered("③", "العمر", "كل ما كبرنا، الصمامات تضعف مع الوقت", ORANGE)
    pdf.numbered("④", "الحمل", "وزن البطن يضغط على أوردة الحوض والأرجل", ORANGE)
    pdf.numbered("⑤", "الوزن الزائد", "ضغط أكثر على الأوردة", ORANGE)
    pdf.numbered("⑥", "قلة الحركة", "العضلات تساعد الأوردة تضخ الدم، لو ما تتحركين يصير ضغط", ORANGE)

    # ===== الأعراض =====
    pdf.ln(4)
    pdf.section_header("وش أعراضها؟", "🩺", RED)

    pdf.bullet("أوردة بارزة وملتوية باللون الأزرق أو البنفسجي", "🔵", RED)
    pdf.bullet("ثقل أو ألم في الساقين خصوصاً آخر اليوم", "😣", RED)
    pdf.bullet("تورّم في الكاحل أو القدم", "🦶", RED)
    pdf.bullet("حكة حول الوريد المتأثر", "🤏", RED)
    pdf.bullet("تشنجات عضلية في الليل", "🌙", RED)
    pdf.bullet("الأعراض تزيد مع الوقوف الطويل وتخف مع الراحة ورفع الرِّجل", "📌", RED)

    pdf.info_box("مو كل الدوالي تسبب ألم — أحياناً تكون مجرد شكل تحت الجلد بدون أعراض.", RED_LIGHT, RED, "⚠️")

    # ===== الأنواع =====
    pdf.add_page()
    pdf.section_header("أنواع الدوالي", "📋", PURPLE)

    pdf.numbered("①", "الأوردة العنكبوتية (Spider Veins)", "خطوط رفيعة حمراء أو زرقاء تحت الجلد — أصغر نوع وعادةً ما تسبب ألم", PURPLE)
    pdf.numbered("②", "دوالي سطحية", "الأوردة الزرقاء البارزة المعروفة — الأكثر شيوعاً", PURPLE)
    pdf.numbered("③", "دوالي عميقة", "في الأوردة العميقة داخل العضلات — أخطر نوع وممكن تسبب جلطات", PURPLE)

    # ===== العلاج =====
    pdf.ln(4)
    pdf.section_header("كيف تُعالَج الدوالي؟", "💊", GREEN)

    pdf.body("العلاج يعتمد على شدة الحالة:")

    pdf.info_box("الحالات البسيطة — تغيير نمط الحياة:", GREEN_LIGHT, GREEN, "🌿")
    pdf.bullet("الحركة والمشي المنتظم", "✅")
    pdf.bullet("رفع الرِّجلين عند الراحة", "✅")
    pdf.bullet("لبس جوارب ضاغطة طبية", "✅")
    pdf.bullet("تجنب الوقوف أو الجلوس الطويل", "✅")
    pdf.bullet("الحفاظ على وزن صحي", "✅")

    pdf.ln(2)
    pdf.info_box("الحالات المتوسطة والشديدة — علاج طبي:", LIGHT_BLUE, MEDIUM_BLUE, "🏥")
    pdf.numbered("①", "العلاج بالليزر", "أشعة ليزر تقفل الوريد المتضرر بدون جراحة", MEDIUM_BLUE)
    pdf.numbered("②", "الحقن (التصليب / Sclerotherapy)", "حقن مادة داخل الوريد تخليه يقفل ويختفي", MEDIUM_BLUE)
    pdf.numbered("③", "التردد الحراري (Radiofrequency)", "حرارة تقفل الوريد من الداخل", MEDIUM_BLUE)
    pdf.numbered("④", "الجراحة (نزع الوريد)", "في الحالات الشديدة — يُزال الوريد كاملاً", MEDIUM_BLUE)

    pdf.info_box("الجسم عنده أوردة كثيرة بديلة — لو وريد واحد انقفل أو انشال، الدم يلاقي طرق ثانية يرجع للقلب عادي.", TEAL_LIGHT, TEAL, "💡")

    # ===== الوقاية =====
    pdf.add_page()
    pdf.section_header("كيف نتجنّب الدوالي؟ (الوقاية)", "🛡️", TEAL)

    pdf.bullet("المشي والرياضة بانتظام — خصوصاً المشي والسباحة", "🏃‍♀️", TEAL)
    pdf.bullet("لا تجلسين أو توقفين فترة طويلة — غيّري وضعك كل 30 دقيقة", "⏰", TEAL)
    pdf.bullet("ارفعي رجلك على مخدة وقت الراحة", "🛋️", TEAL)
    pdf.bullet("حافظي على وزن صحي", "⚖️", TEAL)
    pdf.bullet("اشربي ماء كثير", "💧", TEAL)
    pdf.bullet("تجنبي الكعب العالي لفترات طويلة", "👠", TEAL)
    pdf.bullet("الأكل الصحي — خضار وفواكه ووألياف", "🥗", TEAL)

    # ===== متى تروحين للدكتور =====
    pdf.ln(4)
    pdf.section_header("متى لازم تروحين للدكتور؟", "🚨", RED)

    pdf.bullet("ألم شديد أو تورم مفاجئ في الرِّجل", "🔴", RED)
    pdf.bullet("تغيّر لون الجلد حول الوريد", "🔴", RED)
    pdf.bullet("نزيف من الدوالي", "🔴", RED)
    pdf.bullet("قرحة أو جرح ما يلتئم قرب الكاحل", "🔴", RED)
    pdf.bullet("احمرار أو حرارة في منطقة الوريد (احتمال التهاب أو جلطة)", "🔴", RED)

    # ===== ملخص =====
    pdf.ln(6)
    y = pdf.get_y()
    pdf.colored_box(22, y, pdf.w - 44, 55, LIGHT_BLUE, DARK_BLUE)
    pdf.set_fill_color(*DARK_BLUE)
    pdf.rect(22, y, pdf.w - 44, 14, "F")
    pdf.set_xy(22, y + 2)
    pdf.set_font("Cairo", "", 14)
    pdf.set_text_color(*WHITE)
    pdf.cell(pdf.w - 44, 10, text="📝  خلاصة سريعة", align="C", new_x="LEFT", new_y="NEXT")

    pdf.set_xy(28, y + 17)
    pdf.set_font("Cairo", "", 11)
    pdf.set_text_color(*DARK_GRAY)
    summary = [
        "✅  الدوالي = أوردة منتفخة بسبب ضعف الصمامات",
        "✅  تصير غالباً في الأرجل بسبب الجاذبية",
        "✅  الحركة + الوزن الصحي = أفضل وقاية",
        "✅  أغلب الحالات تُعالَج بدون جراحة",
        "✅  لو الأعراض شديدة → لازم دكتور"
    ]
    for line in summary:
        pdf.set_x(28)
        pdf.cell(pdf.w - 56, 7, text=line, align="R", new_x="LEFT", new_y="NEXT")

    pdf.output(OUTPUT)
    print(f"✅ PDF saved: {OUTPUT}")
    print(f"Pages: {pdf.pages_count}")


if __name__ == "__main__":
    build()
