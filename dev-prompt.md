أنت مطور Full-Stack متخصص في TypeScript/React/Node.js. مطلوب منك تنفيذ خطة تطوير شاملة لمنصة إخبارية. نفّذ المهام بالترتيب التالي مع الالتزام بأفضل الممارسات.

---

## المرحلة 1: الإصلاحات الحرجة (أولوية قصوى)

### 1.1 Error Boundaries
- أضف Error Boundary على مستوى التطبيق في `App.tsx`
- أضف Error Boundary لكل Route محمّل بـ lazy loading
- كل Error Boundary يعرض رسالة واضحة للمستخدم مع زر "إعادة المحاولة"

### 1.2 تنظيف Console Logs
- احذف جميع `console.log` من كود الإنتاج:
  - `ArticleDetail.tsx` (أسطر 162, 175, 185, 192, 207)
  - `queryClient.ts` (أسطر 32, 71)
- استبدلها بـ logger مركزي يعمل في development فقط

### 1.3 إصلاح التنقل
- استبدل `window.location.href` بـ `navigate()` من React Router في `Login.tsx`

---

## المرحلة 2: إصلاح تسرب الذاكرة (حرج)

### 2.1 Activity Cache (`server/auth.ts`)
```typescript
// أضف تنظيف دوري لـ activityUpdateCache
setInterval(() => {
  const oneHourAgo = Date.now() - 60 * 60 * 1000;
  for (const [userId, timestamp] of activityUpdateCache.entries()) {
    if (timestamp < oneHourAgo) {
      activityUpdateCache.delete(userId);
    }
  }
}, 30 * 60 * 1000);
```

### 2.2 Memory Cache (`server/memoryCache.ts`)
- أصلح Pattern Matching ليكون O(n) بدل O(n*m)
- تكرار واحد على المفاتيح بدل تكرار لكل pattern

---

## المرحلة 3: تحسين استعلامات قاعدة البيانات

### 3.1 إصلاح N+1 Queries
- أصلح `notificationWorker.ts`: حوّل المعالجة من تتابعية إلى متوازية
- استخدم `Promise.allSettled` مع حد تزامن (concurrency limit = 5)

### 3.2 إضافة فهارس (Indexes)
```sql
CREATE INDEX idx_articles_status_published ON articles (status, "publishedAt" DESC);
CREATE INDEX idx_articles_views ON articles (views DESC);
CREATE INDEX idx_reading_history_user ON "readingHistory" ("userId", "createdAt" DESC);
CREATE INDEX idx_comments_article_status ON comments ("articleId", status);
CREATE INDEX idx_notifications_user ON "notificationsInbox" ("userId", "createdAt" DESC);
```

---

## المرحلة 4: تحسين أداء الواجهة

### 4.1 Memoization
- أضف `useMemo` و `useCallback` في:
  - `ArticleDetail.tsx` — mutation callbacks
  - `Home.tsx` — query configurations
- لا تبالغ: فقط المكونات التي تُعاد رسمها بدون سبب

### 4.2 تقليل Refetch
- غيّر `refetchInterval` في لوحة التحكم من 2 دقيقة إلى 5 دقائق

### 4.3 Lazy Loading للمكتبات الثقيلة
```typescript
const Recharts = React.lazy(() => import('recharts'));
const ApexCharts = React.lazy(() => import('react-apexcharts'));
```

### 4.4 Skeleton Loading
- أضف Skeleton components للمقالات والصفحة الرئيسية

### 4.5 دمج مكونات البطاقات
- ادمج المكونات التالية في `BaseArticleCard` موحد:
  - `ArticleCard.tsx`
  - `NewsArticleCard.tsx`
  - `AIArticleCard.tsx`
  - `InfographicArticleCard.tsx`
- استخدم `variant` prop للتفريق بين الأنواع
- حافظ على نفس الواجهة الخارجية (API) لكل نوع

---

## المرحلة 5: تحسين الوظائف المجدولة (Background Jobs)

- أضف retry logic (3 محاولات مع exponential backoff)
- أضف graceful shutdown handlers لإنهاء الوظائف الجارية قبل إيقاف السيرفر
- أضف max-runtime enforcement (timeout لكل وظيفة)
- أضف تنبيهات (logging) عند فشل وظيفة حرجة

---

## المرحلة 6: Docker و Deployment

### 6.1 Dockerfile
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --production
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:5000/health || exit 1
CMD ["node", "dist/index.cjs"]
```

### 6.2 Docker Compose
- أضف `docker-compose.yml` مع: app + postgres + redis (للمرحلة القادمة)

---

## المرحلة 7: Cloudflare R2 للتخزين

- عدّل `objectStorage.ts` لدعم R2 عبر S3-compatible API
- استخدم `@aws-sdk/client-s3` مع endpoint مخصص لـ R2
- أضف migration script لنقل الملفات المحلية إلى R2
- اجعل التخزين قابل للتبديل عبر environment variable:
  ```
  STORAGE_PROVIDER=local|r2
  ```

---

## المرحلة 8: المراقبة والأمان

### 8.1 مراقبة
- اربط Sentry لتتبع الأخطاء (frontend + backend)
- أضف health check endpoint (`/health`)
- أضف middleware لقياس وقت الاستجابة وتسجيله

### 8.2 أمان
- شدّد Content Security Policy (أزل `unsafe-inline` و `unsafe-eval`)
- أصلح أي CSP violations تظهر
- راجع OWASP Top 10 الأساسية

---

## المرحلة 9: تحسينات الذكاء الاصطناعي والتوصيات

### 9.1 محرك التوصيات
- فعّل Content Vectors باستخدام embeddings للتشابه بين المقالات
- حسّن حساب User Affinities
- خصّص التغذية الإخبارية لكل مستخدم بناءً على سلوكه

### 9.2 AI Features
- حسّن توليد المقالات التلقائي
- فعّل تحليل المشاعر للتعليقات
- حسّن توليد SEO metadata تلقائياً
- فعّل الإشراف الآلي على التعليقات (فلترة المحتوى المسيء)

---

## المرحلة 10: PWA والنشرات

### 10.1 PWA
- أضف Service Worker للعمل بدون إنترنت
- فعّل Push Notifications
- أضف manifest.json كامل
- حسّن First Contentful Paint

### 10.2 النشرات
- فعّل النشرات الصوتية (Text-to-Speech)
- أضف قوالب بريدية متجاوبة

---

## قواعد عامة (التزم بها في كل المراحل):

1. **TypeScript strict mode** — لا `any` إلا في حالات مبررة
2. **اختبارات** — أضف unit tests لكل إصلاح حرج
3. **لا تكسر الموجود** — كل تغيير يجب أن يكون backward compatible
4. **commits واضحة** — كل commit يشرح ماذا ولماذا
5. **لا dependencies جديدة** إلا إذا ضرورية فعلاً
6. **التوثيق** — وثّق أي تغيير معماري في README
7. **نفّذ مرحلة مرحلة** — لا تنتقل للتالية قبل اكتمال الحالية
