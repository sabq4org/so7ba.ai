# أثر Backend + Admin Panel

## المطلوب
بناء backend + لوحة تحكم لتطبيق أخبار "أثر" على سيرفر DigitalOcean.

## التقنيات
- **Framework:** Next.js 14 (App Router)
- **Database:** PostgreSQL (Neon) - الاتصال جاهز
- **ORM:** Prisma
- **UI:** Tailwind CSS + shadcn/ui
- **Auth:** بسيط (username/password) لأنها لوحة تحكم داخلية
- **Port:** 3500 (لا يتعارض مع الخدمات الحالية)

## قاعدة البيانات (Prisma Schema)

### جداول مطلوبة:
1. **sources** - مصادر الأخبار
   - id, name, type (rss/twitter), url, icon, isActive, lastFetchedAt, createdAt
   
2. **articles** - الأخبار
   - id, title, summary, content, imageUrl, link, sourceId, category, publishedAt, isVisible, createdAt
   
3. **twitter_accounts** - حسابات تويتر
   - id, username, displayName, isActive, createdAt
   
4. **settings** - إعدادات عامة
   - id, key, value

## لوحة التحكم (صفحات)

### 1. الرئيسية (Dashboard)
- إحصائيات: عدد الأخبار، المصادر، آخر سحب
- آخر 10 أخبار
- حالة المصادر

### 2. إدارة الأخبار
- جدول بكل الأخبار (مع بحث + فلتر بالمصدر)
- حذف خبر
- إخفاء/إظهار خبر
- معاينة الخبر

### 3. إدارة المصادر (RSS)
- قائمة المصادر مع الحالة (نشط/معطل)
- إضافة مصدر جديد (اسم + رابط RSS)
- حذف مصدر
- تعطيل/تفعيل مصدر
- زر "سحب الآن" لكل مصدر
- آخر وقت سحب

### 4. إدارة تويتر
- قائمة الحسابات المتابَعة
- إضافة حساب تويتر
- حذف حساب
- تعطيل/تفعيل

### 5. الإعدادات
- فترة السحب التلقائي (كل كم دقيقة)
- عدد الأخبار الأقصى لكل مصدر

## API Endpoints

### للتطبيق (iOS)
- `GET /api/articles` - جلب الأخبار (مع pagination + فلتر)
- `GET /api/articles/:id` - تفاصيل خبر
- `GET /api/sources` - قائمة المصادر
- `GET /api/categories` - التصنيفات

### للوحة التحكم
- `POST /api/admin/sources` - إضافة مصدر
- `DELETE /api/admin/sources/:id` - حذف مصدر
- `PATCH /api/admin/sources/:id` - تعديل مصدر
- `DELETE /api/admin/articles/:id` - حذف خبر
- `PATCH /api/admin/articles/:id` - تعديل حالة خبر
- `POST /api/admin/fetch` - سحب فوري
- `POST /api/admin/twitter` - إضافة حساب تويتر

### Cron / Background
- سحب RSS كل 5 دقائق
- فحص الأخبار المحذوفة من المصدر
- سحب تغريدات (لاحقاً)

## التصميم
- RTL كامل
- ألوان أثر: ذهبي #C8A96E + أسود #0A0A0A
- Dark mode
- عربي بالكامل
- متجاوب (responsive)

## المصادر الافتراضية (تُضاف تلقائياً)
1. سبق - https://sabq.org/rss
2. العربية - https://www.alarabiya.net/feed/rss2/ar.xml
3. الشرق الأوسط - https://aawsat.com/feed
4. اليوم - https://www.alyaum.com/rss
5. الرياض - https://www.alriyadh.com/rss

## ملاحظات
- المشروع في: /opt/athr-admin/
- يشتغل على port 3500
- systemd service اسمه athr-admin
- Nginx reverse proxy على domain فرعي (لاحقاً)
