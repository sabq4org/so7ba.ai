# مطلوب: إصلاح SEO — تحويل sabq.org من SPA إلى SSR

## المشكلة الحالية

الموقع يعمل كـ SPA (Single Page Application) بالكامل — كل الصفحات ترجع نفس HTML الثابت (11,659 bytes) بغض النظر عن المحتوى.

عند زيارة أي صفحة مقال (مثل `/article/DwmsXiT`):
- الـ HTML المصدري فاضي — فيه فقط `<div id="root">` مع skeleton loader
- الـ `<title>` ثابت: "سبق الذكية - منصة الأخبار الذكية" لكل الصفحات
- الـ `og:title` و `og:description` و `og:image` ثابتة ولا تتغير حسب المقال
- لا يوجد canonical URL
- لا يوجد Schema Article (ld+json) خاص بالمقال
- المحتوى يتحمّل بالكامل عبر JavaScript بعد فتح الصفحة

هذا يعني:
- محركات البحث تشوف كل الصفحات متطابقة
- مشاركة خبر على تويتر/واتساب ما تعرض عنوانه ولا صورته
- الأرشفة ضعيفة والترافيك العضوي يضيع

## المطلوب

تحويل الموقع إلى SSR (Server-Side Rendering) بحيث كل صفحة ترجع HTML كامل فيه المحتوى من أول طلب (First Request).

## التفاصيل الفنية

### الفريمورك الحالي
- Vite + React (على الأرجح — الملف: `/assets/index-D3QwFP_p.js`)
- Google App Engine (الهيدر: `via: 1.1 google`)
- Cloudflare CDN
- Google Analytics GA4 + GTM + DMS Signal

### الحل المقترح
تحويل إلى Next.js (لأن المشروع React) أو استخدام Vite SSR Plugin.

الخيار الأفضل: **Next.js App Router** — لأنه:
- يدعم React مباشرة (نفس الكومبوننتات الحالية)
- SSR + Static Generation + ISR (Incremental Static Regeneration)
- أداء ممتاز مع Cloudflare
- مجتمع كبير ودعم طويل المدى

### البديل السريع (لو التحويل الكامل يأخذ وقت)
**Pre-rendering لصفحات المقالات فقط** — سيرفر وسيط (middleware) يقرأ الـ route، يجيب بيانات المقال من الـ API، ويحقن الـ meta tags في الـ HTML قبل ما يرسله للمتصفح. هذا يحل مشكلة السوشال ومحركات البحث بدون إعادة بناء كامل.

## المتطلبات لكل صفحة مقال

### 1. عنصر `<title>` ديناميكي
```html
<title>عنوان الخبر — سبق</title>
```

### 2. Meta Description ديناميكي
```html
<meta name="description" content="أول 160 حرف من محتوى الخبر..." />
```

### 3. Open Graph Tags (للمشاركة على السوشال)
```html
<meta property="og:type" content="article" />
<meta property="og:url" content="https://sabq.org/article/XXXX" />
<meta property="og:title" content="عنوان الخبر" />
<meta property="og:description" content="ملخص الخبر" />
<meta property="og:image" content="https://sabq.org/images/article-image.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:site_name" content="صحيفة سبق الإلكترونية" />
<meta property="og:locale" content="ar_SA" />
<meta property="article:published_time" content="2026-02-14T09:00:00Z" />
<meta property="article:modified_time" content="2026-02-14T10:00:00Z" />
<meta property="article:section" content="اسم القسم" />
<meta property="article:tag" content="كلمة مفتاحية" />
```

### 4. Twitter Card Tags
```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@sababorgnews" />
<meta name="twitter:title" content="عنوان الخبر" />
<meta name="twitter:description" content="ملخص الخبر" />
<meta name="twitter:image" content="https://sabq.org/images/article-image.jpg" />
```

### 5. Canonical URL
```html
<link rel="canonical" href="https://sabq.org/article/XXXX" />
```

### 6. Schema Article (JSON-LD)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "عنوان الخبر",
  "description": "ملخص الخبر",
  "image": ["https://sabq.org/images/article-image.jpg"],
  "datePublished": "2026-02-14T09:00:00+03:00",
  "dateModified": "2026-02-14T10:00:00+03:00",
  "author": {
    "@type": "Person",
    "name": "اسم المحرر"
  },
  "publisher": {
    "@type": "NewsMediaOrganization",
    "name": "صحيفة سبق الإلكترونية",
    "logo": {
      "@type": "ImageObject",
      "url": "https://sabq.org/branding/sabq-og-image.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://sabq.org/article/XXXX"
  },
  "articleSection": "اسم القسم",
  "keywords": ["كلمة1", "كلمة2"]
}
</script>
```

### 7. محتوى الخبر في HTML
جسم الخبر (النص + الصور) لازم يكون موجود في الـ HTML المصدري داخل عناصر semantic:
```html
<article>
  <h1>عنوان الخبر</h1>
  <time datetime="2026-02-14T09:00:00+03:00">14 فبراير 2026</time>
  <p>محتوى الخبر...</p>
  <img src="..." alt="وصف الصورة" />
</article>
```

## المتطلبات لصفحات الأقسام

كل صفحة قسم (محلي، رياضي، عالمي...) تحتاج:
- `<title>` خاص: "أخبار محلية — سبق"
- Meta description خاص بالقسم
- OG tags خاصة
- Canonical URL
- قائمة المقالات في HTML (مو بس JavaScript)

## المتطلبات للصفحة الرئيسية

- `<title>` ديناميكي أو ثابت مناسب ✅ (موجود حالياً)
- عناوين آخر الأخبار في HTML المصدري (مو موجودة حالياً)
- Schema WebSite + SearchAction للظهور في بحث قوقل مع مربع بحث

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "صحيفة سبق الإلكترونية",
  "url": "https://sabq.org",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://sabq.org/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
</script>
```

## الأشياء الموجودة والشغّالة (لا تغيرها)

- Sitemap.xml ✅
- Robots.txt ✅
- HTTPS + Cloudflare ✅
- Google Analytics GA4 ✅
- GTM ✅
- DMS Signal Integration ✅
- Security Headers ✅
- Schema Organization (JSON-LD) ✅
- سرعة استجابة السيرفر ممتازة (0.18s) ✅

## الأولويات

1. **عاجل جداً:** صفحات المقالات — SSR أو على الأقل meta tags ديناميكية
2. **عاجل:** OG tags ديناميكية لكل مقال (المشاركة على السوشال)
3. **مهم:** Schema NewsArticle لكل خبر
4. **مهم:** Canonical URLs
5. **تحسين:** صفحات الأقسام SSR
6. **تحسين:** الصفحة الرئيسية SSR

## طريقة الاختبار

بعد التنفيذ، كل صفحة مقال لازم تنجح في هالاختبارات:

```bash
# 1. التأكد من وجود عنوان المقال في HTML
curl -s https://sabq.org/article/XXXX | grep '<title>'
# المتوقع: عنوان الخبر — سبق

# 2. التأكد من OG tags
curl -s https://sabq.org/article/XXXX | grep 'og:title'
# المتوقع: عنوان الخبر (مو عنوان الموقع العام)

# 3. التأكد من وجود المحتوى
curl -s https://sabq.org/article/XXXX | grep -c '<article\|<h1'
# المتوقع: أكثر من 0

# 4. فحص المشاركة
# https://developers.facebook.com/tools/debug/
# https://cards-dev.twitter.com/validator
```

## ملاحظات إضافية

- الموقع حالياً على Google App Engine — لو التحويل لـ Next.js، ممكن يُستضاف على Vercel أو يبقى على GAE مع adapter مخصص
- Cloudflare ممكن يعمل cache للصفحات المُرندرة — هذا يحسن الأداء بشكل كبير
- ISR (Incremental Static Regeneration) مثالي للأخبار — يرندر الصفحة مرة ويحدّثها كل فترة
- لا تنسَ اختبار الأداء بعد التحويل (Core Web Vitals) — SSR ممكن يبطئ TTFB لو ما انضبط صح
