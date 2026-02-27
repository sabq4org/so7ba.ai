# Cursor Prompt — جرعة Backend + Admin Dashboard

## 🎯 المشروع
بناء **Backend API كامل + لوحة تحكم ويب** لتطبيق جرعة (تطبيق أخبار عربي على iOS).

التطبيق الحالي يتصل بـ `http://165.227.57.44:3500` وهو Node.js/Express. المطلوب توسيعه وبناء لوحة تحكم متكاملة.

---

## 📦 Stack التقني

### Backend
- **Runtime:** Node.js 20+
- **Framework:** Express.js + TypeScript
- **Database:** PostgreSQL + Prisma ORM
- **Auth:** JWT (access + refresh tokens) — admin only
- **Cache:** Redis (للأخبار والتغريدات)
- **Job Queue:** node-cron (جلب RSS كل 15 دقيقة، X كل 30 دقيقة)
- **Storage:** Cloudinary (لصور الأخبار)
- **Deployment:** Docker Compose

### Admin Dashboard (Frontend)
- **Framework:** React 18 + Vite + TypeScript
- **UI:** Tailwind CSS + shadcn/ui
- **Charts:** Recharts
- **State:** Zustand
- **RTL:** `dir="rtl"` على الـ root، Tailwind RTL plugin
- **اللغة:** عربية كاملة

---

## 🗄️ Database Schema (Prisma)

```prisma
model Admin {
  id           String   @id @default(uuid())
  email        String   @unique
  passwordHash String
  name         String
  role         AdminRole @default(EDITOR)
  createdAt    DateTime @default(now())
  lastLoginAt  DateTime?
  sessions     AdminSession[]
}

enum AdminRole {
  SUPER_ADMIN
  EDITOR
  VIEWER
}

model AdminSession {
  id        String   @id @default(uuid())
  adminId   String
  token     String   @unique
  expiresAt DateTime
  admin     Admin    @relation(fields: [adminId], references: [id])
}

model Article {
  id          Int      @id @default(autoincrement())
  title       String
  description String?
  link        String   @unique
  imageUrl    String?
  source      String
  category    String?
  pubDate     DateTime?
  status      ArticleStatus @default(ACTIVE)
  isFeatured  Boolean  @default(false)
  isPinned    Boolean  @default(false)
  viewCount   Int      @default(0)
  createdAt   DateTime @default(now())
  deletedAt   DateTime?
  moderatedBy String?
  moderatedAt DateTime?
}

enum ArticleStatus {
  ACTIVE
  HIDDEN
  DELETED
}

model NewsSource {
  id        String   @id @default(uuid())
  name      String
  nameAr    String
  rssUrl    String?
  icon      String?
  isActive  Boolean  @default(true)
  lastFetch DateTime?
  fetchCount Int     @default(0)
  errorCount Int     @default(0)
  createdAt DateTime @default(now())
}

model XSource {
  id         String   @id @default(uuid())
  handle     String   @unique
  name       String
  avatarUrl  String?
  type       XSourceType @default(MEDIA)
  isActive   Boolean  @default(true)
  lastFetch  DateTime?
  tweets     XTweet[]
  createdAt  DateTime @default(now())
}

enum XSourceType {
  MEDIA
  INFLUENCER
}

model XTweet {
  id           String   @id @default(uuid())
  tweetId      String   @unique
  authorHandle String
  authorName   String
  authorAvatar String?
  text         String
  likes        Int      @default(0)
  retweets     Int      @default(0)
  replies      Int      @default(0)
  mediaUrls    String[] @default([])
  isRetweet    Boolean  @default(false)
  isReply      Boolean  @default(false)
  status       TweetStatus @default(ACTIVE)
  sourceId     String?
  influencerId String?
  source       XSource? @relation(fields: [sourceId], references: [id])
  createdAt    DateTime
  fetchedAt    DateTime @default(now())
}

enum TweetStatus {
  ACTIVE
  HIDDEN
  DELETED
}

model AppUser {
  id          String   @id @default(uuid())
  deviceId    String   @unique
  platform    String   @default("ios")
  appVersion  String?
  locale      String   @default("ar")
  createdAt   DateTime @default(now())
  lastSeenAt  DateTime @default(now())
  sessions    AppSession[]
  events      AppEvent[]
}

model AppSession {
  id        String   @id @default(uuid())
  userId    String
  startedAt DateTime @default(now())
  endedAt   DateTime?
  duration  Int?     // بالثواني
  user      AppUser  @relation(fields: [userId], references: [id])
}

model AppEvent {
  id        String   @id @default(uuid())
  userId    String
  event     String   // article_view, tweet_view, search, etc.
  metadata  Json?
  createdAt DateTime @default(now())
  user      AppUser  @relation(fields: [userId], references: [id])
}

model DailyStats {
  id           String   @id @default(uuid())
  date         DateTime @unique
  activeUsers  Int      @default(0)
  newUsers     Int      @default(0)
  totalViews   Int      @default(0)
  articleViews Int      @default(0)
  tweetViews   Int      @default(0)
  searches     Int      @default(0)
  topArticles  Json?    // [{id, title, views}]
  topSources   Json?    // [{source, count}]
}
```

---

## 🔌 Backend API Endpoints

### Auth
```
POST /api/admin/login          { email, password } → { accessToken, refreshToken, admin }
POST /api/admin/refresh        { refreshToken } → { accessToken }
POST /api/admin/logout
GET  /api/admin/me
```

### Articles (iOS App)
```
GET  /api/articles             ?page&limit&category&search&source
GET  /api/articles/:id
POST /api/articles/:id/view    (إحصائية — من التطبيق)
```

### Articles Admin
```
GET    /api/admin/articles              ?page&limit&category&status&source&search
PUT    /api/admin/articles/:id/status   { status: "HIDDEN"|"ACTIVE" }
PUT    /api/admin/articles/:id/feature  { isFeatured: bool }
PUT    /api/admin/articles/:id/pin      { isPinned: bool }
DELETE /api/admin/articles/:id          (soft delete)
POST   /api/admin/articles/fetch        (يشغّل جلب RSS الآن)
```

### X / Tweets Admin
```
GET  /api/admin/tweets                 ?page&limit&status
PUT  /api/admin/tweets/:id/status      { status: "HIDDEN"|"ACTIVE" }
GET  /api/admin/x-sources              قائمة المصادر والمؤثرين
POST /api/admin/x-sources              إضافة مصدر جديد { handle, type }
PUT  /api/admin/x-sources/:id          تعديل
PUT  /api/admin/x-sources/:id/toggle   تفعيل/إيقاف
DELETE /api/admin/x-sources/:id
POST /api/admin/x-sources/fetch        (يشغّل جلب X الآن)
```

### News Sources Admin
```
GET  /api/admin/news-sources
POST /api/admin/news-sources           { name, nameAr, rssUrl, icon }
PUT  /api/admin/news-sources/:id
PUT  /api/admin/news-sources/:id/toggle
DELETE /api/admin/news-sources/:id
```

### Analytics (Admin)
```
GET /api/admin/stats/overview          اليوم: مستخدمين، مشاهدات، تغريدات، أخبار
GET /api/admin/stats/daily             ?from&to — إحصائيات يومية للرسوم البيانية
GET /api/admin/stats/top-articles      ?limit=10 — أكثر الأخبار مشاهدة
GET /api/admin/stats/top-sources       توزيع المصادر
GET /api/admin/stats/users             إجمالي مسجلين، جدد اليوم، نشطين 30 يوم
GET /api/admin/stats/categories        توزيع الأخبار على التصنيفات
```

### App Users (iOS SDK)
```
POST /api/app/register                 { deviceId, platform, appVersion, locale }
POST /api/app/event                    { deviceId, event, metadata }
POST /api/app/session/start            { deviceId }
POST /api/app/session/end              { deviceId, sessionId, duration }
```

---

## 🖥️ لوحة التحكم — الصفحات

### 1. الداشبورد الرئيسي `/`
- **4 بطاقات KPI في الأعلى:**
  - إجمالي المستخدمين المسجلين
  - المستخدمين النشطين (آخر 24 ساعة)
  - الأخبار المنشورة اليوم
  - إجمالي المشاهدات اليوم
- **رسم بياني خطي:** مستخدمين نشطين آخر 30 يوم
- **رسم بياني أعمدة:** مشاهدات الأخبار آخر 7 أيام
- **جدول:** أكثر 5 أخبار مشاهدة اليوم
- **قائمة:** آخر 5 أخبار تم إخفاؤها

### 2. إدارة الأخبار `/articles`
- **جدول** يعرض: الصورة، العنوان (قابل للنقر)، المصدر، التصنيف، التاريخ، المشاهدات، الحالة
- **فلاتر:** المصدر، التصنيف، الحالة (نشط/مخفي/محذوف)
- **بحث** في العنوان
- **Actions لكل خبر:**
  - 👁️ إخفاء / إظهار (toggle)
  - ⭐ تمييز كخبر بارز (Featured)
  - 📌 تثبيت (Pinned)
  - 🗑️ حذف (مع تأكيد)
- **زر "جلب الأخبار الآن"** يشغّل RSS fetch يدوياً
- **Pagination** — 20 خبر لكل صفحة

### 3. إدارة التغريدات `/tweets`
- **جدول:** الصورة الرمزية، اسم الحساب، نص التغريدة (مقتطع)، الوقت، الإعجابات، الحالة
- **فلاتر:** النوع (مصدر/مؤثر)، الحالة
- **Actions:** إخفاء / إظهار، حذف
- **زر "جلب التغريدات الآن"**

### 4. مصادر الأخبار `/news-sources`
- جدول المصادر: الاسم، RSS URL، آخر جلب، عدد الأخبار، الحالة
- إضافة / تعديل / حذف / تفعيل-إيقاف

### 5. مصادر X والمؤثرون `/x-sources`
- **تبين:** مصادر إعلامية / مؤثرون
- جدول: الصورة، الاسم، @handle، النوع، عدد التغريدات، آخر جلب، الحالة
- إضافة حساب جديد بـ handle فقط (يجلب البيانات من X API تلقائياً)
- تفعيل / إيقاف / حذف

### 6. المستخدمون `/users`
- إجمالي المسجلين
- جدول: Device ID (مقتصر)، المنصة، الإصدار، تاريخ التسجيل، آخر نشاط
- رسم بياني: نمو المستخدمين الجدد شهرياً

### 7. الإحصائيات `/analytics`
- **Date range picker** (اختيار الفترة)
- رسم بياني خطي: مستخدمين نشطين يومياً
- رسم بياني أعمدة: مشاهدات أخبار vs تغريدات
- Pie chart: توزيع التصنيفات
- جدول: أكثر الأخبار مشاهدة في الفترة
- جدول: أكثر المصادر تفاعلاً

### 8. إعدادات `/settings`
- إدارة حسابات الأدمن (إضافة، تعديل الصلاحيات، حذف)
- إعدادات الـ Cron (تكرار جلب RSS، جلب X)
- إعدادات التطبيق (اسم التطبيق، شعار، روابط)

---

## 📁 هيكل المشروع

```
jur3a-backend/
├── prisma/
│   └── schema.prisma
├── src/
│   ├── index.ts              # Express entry point
│   ├── config/
│   │   ├── env.ts
│   │   └── redis.ts
│   ├── middleware/
│   │   ├── auth.ts           # JWT verification
│   │   ├── adminOnly.ts
│   │   └── rateLimit.ts
│   ├── routes/
│   │   ├── articles.ts       # iOS app
│   │   ├── app.ts            # iOS SDK (register/events)
│   │   ├── admin/
│   │   │   ├── auth.ts
│   │   │   ├── articles.ts
│   │   │   ├── tweets.ts
│   │   │   ├── sources.ts
│   │   │   ├── users.ts
│   │   │   └── stats.ts
│   ├── services/
│   │   ├── rss.service.ts    # XML parsing + fetch
│   │   ├── x.service.ts      # X API v2 integration
│   │   ├── stats.service.ts  # Daily stats calculation
│   │   └── cache.service.ts  # Redis helpers
│   ├── jobs/
│   │   ├── rss.job.ts        # Cron: كل 15 دقيقة
│   │   └── x.job.ts          # Cron: كل 30 دقيقة
│   └── utils/
│       ├── htmlCleaner.ts
│       └── dateParser.ts
├── admin-dashboard/          # React App
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Articles.tsx
│   │   │   ├── Tweets.tsx
│   │   │   ├── NewsSources.tsx
│   │   │   ├── XSources.tsx
│   │   │   ├── Users.tsx
│   │   │   ├── Analytics.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── Sidebar.tsx   # RTL sidebar عربي
│   │   │   │   ├── Header.tsx
│   │   │   │   └── Layout.tsx
│   │   │   ├── KPICard.tsx
│   │   │   ├── DataTable.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   └── ConfirmDialog.tsx
│   │   ├── hooks/
│   │   │   ├── useArticles.ts
│   │   │   ├── useStats.ts
│   │   │   └── useAuth.ts
│   │   ├── store/
│   │   │   └── authStore.ts
│   │   └── lib/
│   │       └── api.ts        # Axios instance
│   └── index.html            # dir="rtl"
├── docker-compose.yml
└── .env.example
```

---

## ⚙️ متغيرات البيئة (.env)

```env
# Database
DATABASE_URL=postgresql://jur3a:password@localhost:5432/jur3a_db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-super-secret-key
JWT_REFRESH_SECRET=your-refresh-secret
JWT_EXPIRES_IN=15m
JWT_REFRESH_EXPIRES_IN=7d

# X (Twitter) API
X_BEARER_TOKEN=your-x-bearer-token
X_API_BASE_URL=https://api.twitter.com/2

# Cloudinary (اختياري)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Admin Dashboard
ADMIN_EMAIL=admin@jur3a.app
ADMIN_PASSWORD=ChangeMe123!

# App
PORT=3500
NODE_ENV=production
CORS_ORIGIN=https://admin.jur3a.app
```

---

## 🐳 docker-compose.yml

```yaml
version: '3.8'
services:
  api:
    build: .
    ports: ["3500:3500"]
    environment:
      DATABASE_URL: postgresql://jur3a:password@db:5432/jur3a_db
      REDIS_URL: redis://redis:6379
    depends_on: [db, redis]

  admin:
    build: ./admin-dashboard
    ports: ["3501:80"]

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: jur3a_db
      POSTGRES_USER: jur3a
      POSTGRES_PASSWORD: password
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
```

---

## 🎨 تصميم لوحة التحكم

### Sidebar (يمين — RTL)
```
┌─────────────────┐
│  🗞️ جرعة       │
│  لوحة التحكم    │
├─────────────────┤
│ 📊 الداشبورد    │
│ 📰 الأخبار      │
│ 🐦 التغريدات    │
│ 📡 المصادر      │
│ ✨ المؤثرون     │
│ 👥 المستخدمون   │
│ 📈 الإحصائيات   │
│ ⚙️ الإعدادات    │
└─────────────────┘
```

### ألوان لوحة التحكم
- Primary: `#1A56DB` (نفس لون التطبيق)
- Success: `#059669`
- Danger: `#DC2626`
- Warning: `#D97706`
- Background: `#F8F9FB`

---

## 🔐 نظام الصلاحيات

| الدور | الداشبورد | عرض الأخبار | إخفاء/حذف | إدارة المصادر | إدارة الأدمن |
|-------|-----------|-------------|------------|---------------|--------------|
| VIEWER | ✅ | ✅ | ❌ | ❌ | ❌ |
| EDITOR | ✅ | ✅ | ✅ | ✅ | ❌ |
| SUPER_ADMIN | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🚀 متطلبات التنفيذ

1. ابدأ بـ `prisma init` وأنشئ الـ schema الكامل
2. بناء الـ Express API مع كل الـ routes
3. نظام Auth JWT كامل مع middleware
4. Cron jobs للـ RSS والـ X
5. بناء لوحة التحكم React مع RTL كامل
6. جميع الجداول مع Pagination + Search + Filter
7. الرسوم البيانية بـ Recharts
8. نظام الصلاحيات على الـ Backend والـ Frontend
9. Docker Compose يشغّل كل شيء بأمر واحد: `docker-compose up`

---

## 📋 ملاحظات مهمة

- **الـ iOS App موجود** ومتصل بـ `http://165.227.57.44:3500` — لا تغيّر الـ endpoints الحالية (`/api/articles`, `/api/x/fetch`, `/api/influencers`)
- **الأخبار المحذوفة:** soft delete فقط (الحقل `deletedAt`) — لا تُرسل للتطبيق
- **الـ Cache:** الأخبار تُخزَّن في Redis بـ TTL 10 دقائق
- **X API:** استخدم Bearer Token فقط (v2 Free tier)
- **لوحة التحكم:** تعمل على `/admin` أو port مستقل `3501`
- **اللغة:** لوحة التحكم عربية كاملة مع RTL
