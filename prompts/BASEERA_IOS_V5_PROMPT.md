# بصيرة iOS v5.0 — برومبت تطوير التطبيق

## المشروع
تطبيق **بصيرة** (Baseera) — منصة ذكاء إعلامي سعودية بالعربية. الباكند تم تحديثه لـ v5.0 مع endpoints جديدة. المطلوب تحديث تطبيق iOS ليتوافق مع API الجديد ويعرض كل البيانات.

## التقنيات
- SwiftUI (iOS 16+)
- Dark theme فقط
- RTL كامل (عربي)
- الباكند: `http://165.227.57.44:8000`

## الثيم (لا تغيره)
```swift
struct BTheme {
    static let bg          = Color(hex: "0D1B2A")
    static let bgCard      = Color(hex: "162032")
    static let bgHover     = Color(hex: "1B2A3D")
    static let accent      = Color(hex: "10B981")  // أخضر
    static let red         = Color(hex: "EF4444")
    static let yellow      = Color(hex: "F59E0B")
    static let orange      = Color(hex: "F97316")
    static let blue        = Color(hex: "3B82F6")
    static let purple      = Color(hex: "8B5CF6")
    static let textPrimary = Color(hex: "F1F5F9")
    static let textSecondary = Color(hex: "94A3B8")
    static let textMuted   = Color(hex: "64748B")
    static let border      = Color(hex: "1E3A5F")
}
```

---

## API v5.0 — الـ Endpoint الرئيسي

### `GET /api/dashboard`
يرجع كل شيء بطلب واحد:

```json
{
  "version": "5.0",
  "scene": {
    "safety_score": 72,
    "status": "مستقر",
    "status_en": "stable",
    "color": "green",
    "icon": "✅",
    "recommendation": "المشهد مستقر — يمكنك النشر بشكل طبيعي",
    "warnings": [],
    "forecast": "من المتوقع أن يظل المشهد هادئاً",
    "forecast_direction": "stable",
    "sentiment_breakdown": { "positive_pct": 35, "negative_pct": 15, "neutral_pct": 45, "mixed_pct": 5 },
    "total_analyzed": 120,
    "active_alerts": 0
  },
  "mood": { "label": "إيجابي", "icon": "😊" },
  "ai_scene_reading": "المشهد الإعلامي السعودي يشهد حالة استقرار...",
  "ai_summary": "ملخص مختصر...",
  "recommendation": "المشهد مستقر — يمكنك النشر بشكل طبيعي",
  "recommendation_level": "normal",
  "trajectory": {
    "direction": "stable",
    "direction_ar": "مستقر",
    "confidence": 80,
    "change_pct": -2.5,
    "safety_trend": [{"timestamp": "...", "value": 72}, ...],
    "negative_trend": [{"timestamp": "...", "value": 15}, ...]
  },
  "stats": {
    "total_monitored": 120,
    "sentiment": { "positive": 42, "negative": 18, "neutral": 54, "mixed": 6 },
    "positive_ratio": 35,
    "negative_ratio": 15
  },
  "emotions": { "anger": 5, "fear": 3, "disgust": 1, "sadness": 4, "sarcasm": 2, "anxiety": 3 },
  "dominant_emotion": "anger",
  "trends": [{"name": "هاشتاق", "count": 50, "sentiment": "positive"}, ...],
  "topic_map": [{"topic": "اقتصاد", "size": 45, "sentiment_score": 0.6, "trend": "up"}, ...],
  "crisis_summary": { "total": 2, "critical": 0, "escalation": 1, "watch": 1, "from_news": 1, "from_twitter": 1 },
  "alerts": [{"id": "...", "title": "...", "severity": "watch", "timestamp": "..."}],
  "early_warnings": [{"type": "sentiment_shift", "description": "...", "severity": 6, "topic": "..."}],
  "anomalies": [{"metric": "volume", "current": 50, "expected": 20, "ratio": 2.5}],
  "comparison": {
    "has_history": true,
    "today": { "articles": 120, "positive_ratio": 35, "negative_ratio": 15, "safety_score": 72 },
    "yesterday": { "articles": 95, "positive_ratio": 30, "negative_ratio": 20, "safety_score": 65 },
    "last_week": { "articles": 80, "positive_ratio": 40, "negative_ratio": 10, "safety_score": 78 }
  },
  "baseline": { "has_baseline": true, "avg_articles": 100, "avg_safety_score": 68, "sample_count": 50 },
  "pulse_data": [
    {"timestamp": "...", "safety_score": 72, "positive": 10, "negative": 3, "neutral": 12, "crisis_count": 0, "total": 25, "mood": "إيجابي"}
  ],
  "top_sources": [{"name": "RT Arabic", "count": 15}, ...],
  "latest_articles": [{"title": "...", "source": "...", "sentiment": "positive", "time": "..."}]
}
```

### Endpoints إضافية
```
GET /api/early-warnings          → { warnings: [], total: 0 }
GET /api/baseline                → { baseline: { has_baseline, avg_articles, ... } }
GET /api/trajectory?hours=6      → { trajectory: { direction, direction_ar, confidence, ... } }
GET /api/comparison              → { today: {}, yesterday: {}, last_week: {} }
GET /api/pulse?hours=48          → { data: [{ timestamp, safety_score, positive, negative, ... }] }
GET /api/crisis/{id}/report      → { report: { analysis, scenarios, actions, statement_draft, ... } }
GET /api/sentiment/heatmap       → { data: [{ hour, anger, fear, ... }] }
GET /api/sentiment/by-topic      → { topics: [{ name, positive, negative, neutral }] }
GET /api/news/saudi?size=10      → { articles: [...] }
GET /api/news/world?size=10      → { articles: [...] }
GET /api/crisis/scan             → { crises: [...] }
GET /api/radar                   → { articles: [...], total: N }
GET /api/trends/hashtags         → { hashtags: [...] }
GET /api/sentiment/overview      → { positive, negative, neutral, ... }
```

---

## الملفات الموجودة (19 ملف Swift)

| الملف | الحجم | الوظيفة |
|-------|-------|---------|
| `baseeraApp.swift` | 21 سطر | Entry point + RTL |
| `ContentView.swift` | 74 سطر | TabBar سفلي (6 تابات) |
| `Models.swift` | 337 سطر | النماذج |
| `NewsService.swift` | 1088 سطر | الخدمة الرئيسية |
| `DashboardView.swift` | 378 سطر | لوحة القيادة |
| `RadarView.swift` | ~400 سطر | رادار الأخبار (4 تابات) |
| `CrisisView.swift` | ~200 سطر | قائمة الأزمات |
| `CrisisDetailView.swift` | ~150 سطر | تفاصيل أزمة |
| `SentimentView.swift` | ~200 سطر | تحليل المشاعر |
| `SearchView.swift` | ~100 سطر | البحث |
| `SettingsView.swift` | ~80 سطر | الإعدادات |
| `Theme.swift` | 119 سطر | الألوان |
| `Components.swift` | ~200 سطر | مكونات مشتركة |
| `RTLComponents.swift` | ~50 سطر | مكونات RTL |
| `RTLModifier.swift` | ~30 سطر | ViewModifier للـ RTL |
| `AIService.swift` | ~100 سطر | خدمة AI |
| `CrisisEngine.swift` | ~150 سطر | محرك أزمات محلي |
| `KeywordGroups.swift` | ~100 سطر | مجموعات كلمات |
| `HashtagAnalysisView.swift` | ~150 سطر | تحليل هاشتاق |

---

## المطلوب تحديثه

### 1. Models.swift — إضافة نماذج v5 الجديدة

أضف هذه النماذج (لا تحذف القديمة):

```swift
// ─── Dashboard v5 Response ───
struct DashboardV5Response: Codable {
    let status: String?
    let version: String?
    let scene: SceneData?
    let mood: MoodData?
    let ai_scene_reading: String?
    let ai_summary: String?
    let recommendation: String?
    let recommendation_level: String?
    let trajectory: TrajectoryData?
    let stats: StatsData?
    let emotions: EmotionsData?
    let dominant_emotion: String?
    let trends: [TrendItem]?
    let topic_map: [TopicItem]?
    let crisis_summary: CrisisSummary?
    let alerts: [AlertItem]?
    let early_warnings: [EarlyWarning]?
    let anomalies: [AnomalyItem]?
    let comparison: ComparisonData?
    let baseline: BaselineData?
    let pulse_data: [PulsePoint]?
    let top_sources: [SourceItem]?
    let latest_articles: [LatestArticle]?
    let timestamp: String?
}

struct SceneData: Codable {
    let safety_score: Int?
    let status: String?
    let status_en: String?
    let color: String?
    let icon: String?
    let recommendation: String?
    let warnings: [String]?
    let forecast: String?
    let forecast_direction: String?
    let sentiment_breakdown: SentimentBreakdown?
    let total_analyzed: Int?
    let active_alerts: Int?
}

struct SentimentBreakdown: Codable {
    let positive_pct: Double?
    let negative_pct: Double?
    let neutral_pct: Double?
    let mixed_pct: Double?
}

struct MoodData: Codable {
    let label: String?
    let icon: String?
}

struct TrajectoryData: Codable {
    let direction: String?
    let direction_ar: String?
    let confidence: Int?
    let change_pct: Double?
    let safety_trend: [TrendPoint]?
    let negative_trend: [TrendPoint]?
}

struct TrendPoint: Codable {
    let timestamp: String?
    let value: Double?
}

struct StatsData: Codable {
    let total_monitored: Int?
    let sentiment: SentimentCounts?
    let positive_ratio: Double?
    let negative_ratio: Double?
}

struct SentimentCounts: Codable {
    let positive: Int?
    let negative: Int?
    let neutral: Int?
    let mixed: Int?
}

struct EmotionsData: Codable {
    let anger: Double?
    let fear: Double?
    let disgust: Double?
    let sadness: Double?
    let sarcasm: Double?
    let anxiety: Double?
}

struct TrendItem: Codable, Identifiable {
    var id: String { name ?? UUID().uuidString }
    let name: String?
    let count: Int?
    let sentiment: String?
}

struct TopicItem: Codable, Identifiable {
    var id: String { topic ?? UUID().uuidString }
    let topic: String?
    let size: Double?
    let sentiment_score: Double?
    let trend: String?
}

struct CrisisSummary: Codable {
    let total: Int?
    let critical: Int?
    let escalation: Int?
    let watch: Int?
    let from_news: Int?
    let from_twitter: Int?
}

struct AlertItem: Codable, Identifiable {
    var id: String { title ?? UUID().uuidString }
    let title: String?
    let severity: String?
    let timestamp: String?
    let description: String?
}

struct EarlyWarning: Codable, Identifiable {
    var id: String { "\(type ?? "")-\(topic ?? "")" }
    let type: String?
    let description: String?
    let severity: Int?
    let topic: String?
    let timestamp: String?
}

struct AnomalyItem: Codable, Identifiable {
    var id: String { metric ?? UUID().uuidString }
    let metric: String?
    let current: Double?
    let expected: Double?
    let ratio: Double?
}

struct ComparisonData: Codable {
    let has_history: Bool?
    let today: PeriodStats?
    let yesterday: PeriodStats?
    let last_week: PeriodStats?
}

struct PeriodStats: Codable {
    let articles: Int?
    let positive_ratio: Double?
    let negative_ratio: Double?
    let safety_score: Double?
}

struct BaselineData: Codable {
    let has_baseline: Bool?
    let avg_articles: Double?
    let avg_tweets: Double?
    let avg_positive_ratio: Double?
    let avg_negative_ratio: Double?
    let avg_crisis_count: Double?
    let avg_safety_score: Double?
    let sample_count: Int?
}

struct PulsePoint: Codable, Identifiable {
    var id: String { timestamp ?? UUID().uuidString }
    let timestamp: String?
    let safety_score: Double?
    let positive: Int?
    let negative: Int?
    let neutral: Int?
    let crisis_count: Int?
    let total: Int?
    let mood: String?
}

struct SourceItem: Codable, Identifiable {
    var id: String { name ?? UUID().uuidString }
    let name: String?
    let count: Int?
}

struct LatestArticle: Codable, Identifiable {
    var id: String { title ?? UUID().uuidString }
    let title: String?
    let source: String?
    let sentiment: String?
    let time: String?
}
```

### 2. NewsService.swift — إضافة fetchDashboardV5

أضف هذا الدالة (أبقِ fetchDashboard القديمة):

```swift
@Published var dashboardV5: DashboardV5Response?

func fetchDashboardV5() async {
    isDashboardLoading = true
    defer { isDashboardLoading = false }

    guard let url = URL(string: "\(baseURL)/api/dashboard") else { return }

    do {
        let (data, _) = try await URLSession.shared.data(from: url)
        let decoded = try JSONDecoder().decode(DashboardV5Response.self, from: data)
        await MainActor.run {
            self.dashboardV5 = decoded
        }
    } catch {
        print("Dashboard v5 error: \(error)")
    }
}
```

### 3. DashboardView.swift — إعادة بناء كاملة

هذا أهم ملف. يجب أن يحتوي على 6 أقسام:

#### القسم 1: ملخص المشهد (Hero)
- **شريط علوي**: أيقونة الحالة (✅/⚠️/🔴) + "مستقر"/"متوتر"/"أزمة" + درجة الأمان (0-100) كشريط ملون
- **اللون**: أخضر (≥70) / أصفر (40-69) / برتقالي (20-39) / أحمر (<20)
- **فقرة AI**: `ai_scene_reading` بخط عادي (كأن محلل يتكلم)
- **التوصية**: خلفية ملونة حسب `recommendation_level` (normal=أخضر, caution=أصفر, warning=برتقالي, critical=أحمر)
- **المسار**: سهم + "يتحسن ↗" أو "مستقر →" أو "يتراجع ↘" من `trajectory.direction_ar`
- **تصميم**: بطاقة بزوايا مدورة، gradient خفيف

#### القسم 2: الإحصائيات
- **صف أول**: 4 بطاقات صغيرة (أخبار | تغريدات | مواضيع | تنبيهات)
- **صف ثاني**: أشرطة المشاعر الستة (غضب، خوف، اشمئزاز، حزن، سخرية، قلق) من `emotions`
- كل شريط = نسبة مئوية + لون مميز + اسم الشعور

#### القسم 3: نبض المشهد
- رسم بياني خطي (SwiftUI Charts أو يدوي) يعرض `pulse_data`
- 3 خطوط: إيجابي (أخضر) + سلبي (أحمر) + درجة الأمان (ذهبي)
- المحور X = الوقت، المحور Y = القيمة
- إذا `pulse_data` فارغ → "جاري جمع البيانات..."

#### القسم 4: خريطة المواضيع
- عرض `topic_map` كفقاعات/chips
- كل موضوع: اسم + حجم (حجم الخط أو حجم الدائرة) + لون حسب المشاعر
- أخضر = إيجابي (sentiment_score > 0.3)، أحمر = سلبي (< -0.3)، رمادي = محايد
- سهم صغير ↗↘→ حسب `trend`
- إذا فارغ → "لا توجد مواضيع حالياً"

#### القسم 5: لوحة الإنذار المبكر
- عرض `early_warnings` + `anomalies` معاً
- كل تنبيه: أيقونة (⚡/🔄/📢/📈) حسب `type` + الوصف + درجة الخطورة
- تنبيه نوعه: `weak_signal`=⚡, `sentiment_shift`=🔄, `influencer_activity`=📢, `acceleration`=📈
- إذا فارغ → دائرة خضراء كبيرة + "لا إنذارات — المشهد هادئ"

#### القسم 6: مقارنة الفترات
- 3 أعمدة: اليوم | أمس | الأسبوع الماضي
- لكل فترة: عدد الأخبار + نسبة الإيجابي + نسبة السلبي + درجة الأمان
- أسهم تغيير ↑↓ ملونة (أخضر = تحسن، أحمر = تراجع)
- إذا `comparison.has_history == false` → "ستتوفر المقارنة بعد يوم من التشغيل"

### 4. CrisisView.swift — تحديث
- استخدم `crisis_summary` من dashboard لعرض ملخص علوي
- عند الضغط على أزمة → `GET /api/crisis/{id}/report` → عرض:
  - تحليل AI
  - السيناريوهات المحتملة
  - الإجراءات الفورية
  - مسودة بيان
  - مؤشر المسار (يتصاعد/يهدأ)

### 5. SentimentView.swift — تحديث
- **تاب 1 "نظرة عامة"**: أشرطة المشاعر الستة + pie chart للإيجابي/السلبي/المحايد
- **تاب 2 "حسب الموضوع"**: `GET /api/sentiment/by-topic` → كل موضوع مع أشرطته
- **تاب 3 "خريطة حرارة"**: `GET /api/sentiment/heatmap` → جدول ساعة × مشاعر بألوان

### 6. ContentView.swift — تحديث طفيف
- غيّر اسم التاب الأول من "القيادة" إلى "المشهد"

---

## قواعد التصميم الإلزامية

1. **Dark theme فقط** — خلفية `BTheme.bg`، بطاقات `BTheme.bgCard`
2. **RTL كامل** — كل النصوص عربية، المحاذاة يمين
3. **الألوان**: استخدم ألوان `BTheme` فقط — لا ألوان hardcoded
4. **البطاقات**: زوايا مدورة (16)، حدود `BTheme.border` خفيفة
5. **الخطوط**: عناوين `.title3.bold()`، نصوص `.body`، أرقام `.system(.title2, design: .rounded)`
6. **spacing**: بين الأقسام 20، داخل البطاقة 16، padding أفقي 16
7. **Pull to refresh**: `.refreshable { await refresh() }`
8. **Loading states**: `ProgressView()` مع نص عربي
9. **Empty states**: أيقونة كبيرة + نص وصفي (مو فقط "فارغ")
10. **iOS 16+**: لا تستخدم APIs أحدث من iOS 16
11. **Charts**: إذا استخدمت SwiftUI Charts (`import Charts`), ضعها داخل `if #available(iOS 16, *)`
12. **لا third-party**: لا SPM packages خارجية — SwiftUI فقط

## ملاحظات مهمة

- ⚠️ كل الحقول بالـ API ممكن تكون `nil` — استخدم optional chaining و default values
- ⚠️ `pulse_data` و `comparison` فارغين أول 24 ساعة — اعرض حالات "جاري الجمع"
- ⚠️ `topic_map` فارغ بدون بيانات تويتر — اعرض empty state جميل
- ⚠️ لا تحذف أي كود موجود يشتغل — أضف فوقه أو عدّل
- ⚠️ الأسماء بالعربي في الواجهة — الكود بالإنجليزية

---

## ملخص الملفات المطلوب تعديلها

| الملف | نوع التغيير |
|-------|------------|
| `Models.swift` | **إضافة** نماذج v5 (لا تحذف القديمة) |
| `NewsService.swift` | **إضافة** `fetchDashboardV5()` + `@Published var dashboardV5` |
| `DashboardView.swift` | **إعادة بناء كاملة** — 6 أقسام |
| `CrisisView.swift` | **تحديث** — ملخص أزمات + master-detail |
| `CrisisDetailView.swift` | **تحديث** — تقرير AI كامل |
| `SentimentView.swift` | **تحديث** — 3 تابات |
| `ContentView.swift` | **تحديث طفيف** — اسم التاب |

**لا تعدّل**: Theme.swift, baseeraApp.swift, RadarView.swift, SearchView.swift, SettingsView.swift, Components.swift, RTL*.swift
