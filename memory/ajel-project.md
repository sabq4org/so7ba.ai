# 📰 مشروع عاجل (Ajel) — سبق الذكية
> تاريخ المراجعة: 2026-02-11

## الريبو
https://github.com/sabq4org/ajel

## التقنيات
- TypeScript (server + client)
- React + Vite + Tailwind
- Express.js
- Drizzle ORM + Neon DB (PostgreSQL)
- Capacitor (iOS/Android)
- AI: OpenAI + Google GenAI + Anthropic

## الأرقام
- 9,563 ملف
- 253 صفحة React + 306 component
- 245 جدول في DB
- ~300 API endpoint
- 168 dependency

## التقييم: 5.5/10

---

## المشاكل الرئيسية

### 1. routes.ts — 39,725 سطر (God File)
- ~300 endpoint في ملف واحد
- أكبر domain: admin (209 endpoint)
- 290 console.log
- 906 try/catch block

### 2. schema.ts — 12,167 سطر
- 245 جدول في ملف واحد

### 3. الجذر مبعثر
- 52 صورة PNG (screenshots تطوير)
- 12 ملف SQL تشخيصي
- ملفات .bak (routes.ts.bak, routes.ts.bak2, schema.ts.backup)
- مجلد attached_assets ضخم
- .replit, sultan.md

### 4. Dependencies مكررة/زائدة (168)
- @google/genai + @google/generative-ai (مكرر)
- node-fetch (غير ضروري مع Node 22)
- 15+ @types/* في dependencies بدل devDependencies

### 5. لا CI/CD ولا Docker
### 6. لا اختبارات تقريباً (e2e/accessibility فقط)

---

## الإيجابيات
- TypeScript شامل
- Helmet + CSP + CSRF + Rate Limiting
- bcrypt + secure sessions
- Memory cache middleware
- Pool monitoring + timedQuery
- README شامل (34K حرف)
- توثيق جيد (SYSTEM_DOCUMENTATION, SECURITY_AUDIT)
- فصل server/client/shared

---

## خطة إعادة الهيكلة (5 أسابيع)

### الأسبوع 1: تنظيف + CI/CD
- تنظيف الجذر (نقل PNG/SQL/bak)
- نقل @types لـ devDependencies
- حذف المكرر
- إضافة GitHub Actions (lint + build + audit)
- إضافة Dockerfile + docker-compose

### الأسبوع 1-2: تقسيم schema.ts → 14 ملف
- schema/auth.ts, schema/articles.ts, schema/categories.ts
- schema/comments.ts, schema/media.ts, schema/users.ts
- schema/loyalty.ts, schema/notifications.ts, schema/themes.ts
- schema/staff.ts, schema/ads.ts, schema/analytics.ts
- schema/zod.ts, schema/misc.ts
- schema/index.ts (barrel export)

### الأسبوع 2-3: تقسيم routes.ts (المرحلة 1)
- routes/auth.ts (~3K سطر)
- routes/media.ts (~2.5K)
- routes/user.ts (~700)
- routes/calendar.ts (~1.5K)

### الأسبوع 3-4: تقسيم routes.ts (المرحلة 2)
- routes/admin.ts (~12K — الأكبر)
- routes/articles.ts (~6K)
- routes/dashboard.ts (~3.5K)

### الأسبوع 4-5: تقسيم routes.ts (المرحلة 3) + مراجعة
- routes/mirqab.ts, themes.ts, ab-tests.ts, categories.ts
- routes/ai.ts, notifications.ts, misc.ts
- مراجعة شاملة + testing

---

## ملاحظات
- المشروع بُني على Replit وتطور بسرعة
- يحتاج "يوم تنظيف" كبير قبل أي توسع
- Cloudflare: 292K زائر/يوم، 26M طلب، 86.95% cache
