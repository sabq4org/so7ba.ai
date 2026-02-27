# 📱 Sabq iOS App — Claude Code Prompt

## المهمة
ابنِ تطبيق iOS كامل لصحيفة **سبق الإلكترونية** (sabq.org) باستخدام **SwiftUI** و **Swift 6**، يستهدف **iOS 17+**. التطبيق يتصل بـ REST API موجود (الملف المرفق: `sabq-ios-api.json` — Postman Collection).

---

## 🏗️ التقنيات المطلوبة

- **Language:** Swift 6
- **UI Framework:** SwiftUI (لا UIKit إلا عند الضرورة القصوى)
- **Minimum Target:** iOS 17.0
- **Architecture:** MVVM + Clean Architecture
- **Networking:** Native URLSession + async/await (لا Alamofire)
- **Data Persistence:** SwiftData (للكاش والمفضلة) + UserDefaults (للإعدادات)
- **Image Loading:** AsyncImage أو مكتبة خفيفة (Kingfisher أو Nuke)
- **Push Notifications:** APNs + Firebase Cloud Messaging (FCM)
- **Dependency Injection:** Environment / @Observable pattern
- **Navigation:** NavigationStack (iOS 17 native)
- **Localization:** Arabic (primary) + English
- **Layout Direction:** RTL-first (Right-to-Left)

---

## 🔌 API Reference

**Base URL:** `https://sabq.org`
**Auth:** Bearer Token (JWT)
**Format:** JSON (UTF-8)

### الملف المرفق يحتوي على كل الـ Endpoints:

### 🔐 Authentication (8 endpoints)
| Method | Path | الوظيفة |
|--------|------|---------|
| POST | `/api/v1/auth/register` | تسجيل حساب جديد (email, password, firstName, lastName, phone, gender, city, country) |
| POST | `/api/v1/auth/activate` | تفعيل الحساب بكود (userId, code) |
| POST | `/api/v1/auth/resend-activation` | إعادة إرسال كود التفعيل |
| POST | `/api/v1/auth/login` | تسجيل الدخول (يرجع token + user) — يشمل deviceInfo (platform, model, osVersion, appVersion) |
| POST | `/api/v1/auth/forgot-password` | نسيت كلمة المرور |
| POST | `/api/v1/auth/reset-password` | إعادة تعيين كلمة المرور (userId, code, newPassword) |
| POST | `/api/v1/auth/logout` | تسجيل خروج (يحتاج token) |
| POST | `/api/v1/auth/logout-all` | خروج من كل الأجهزة (يحتاج token) |

### 📰 Articles & News (11 endpoints)
| Method | Path | الوظيفة |
|--------|------|---------|
| GET | `/api/v1/articles` | قائمة الأخبار (params: limit, offset, category, newsType, featured, since) |
| GET | `/api/v1/articles/:articleId` | خبر واحد بالتفاصيل |
| GET | `/api/v1/articles?category=UUID` | أخبار حسب القسم |
| GET | `/api/v1/breaking` | الأخبار العاجلة |
| GET | `/api/v1/articles?featured=true` | الأخبار المميزة |
| GET | `/api/homepage` | الصفحة الرئيسية (مجمّعة) |
| GET | `/api/articles/:slug/related` | أخبار مرتبطة |
| GET | `/api/v1/weekly-photos` | صور الأسبوع (page, limit) |
| GET | `/api/breaking-ticker/active` | شريط الأخبار العاجلة |
| POST | `/api/v1/articles/:articleId/view` | تسجيل مشاهدة (deviceId, platform, appVersion) |
| POST | `/api/v1/articles/batch-view` | تسجيل مشاهدات دفعة واحدة (offline sync) |

### 📂 Categories (3 endpoints)
| Method | Path | الوظيفة |
|--------|------|---------|
| GET | `/api/v1/categories` | كل الأقسام |
| GET | `/api/v1/menu-groups` | قائمة التنقل للتطبيق |
| GET | `/api/categories` | أقسام الويب |

### 👤 Profile (6 endpoints)
| Method | Path | الوظيفة |
|--------|------|---------|
| GET | `/api/v1/members/profile` | جلب الملف الشخصي |
| PUT | `/api/v1/members/profile` | تحديث الملف الشخصي |
| POST | `/api/v1/members/profile/image` | رفع صورة (base64) |
| DELETE | `/api/v1/members/profile/image` | حذف الصورة |
| POST | `/api/v1/members/change-password` | تغيير كلمة المرور |
| DELETE | `/api/v1/members/account` | حذف الحساب |

### ❤️ Interests (5 endpoints)
| Method | Path | الوظيفة |
|--------|------|---------|
| GET | `/api/v1/interests` | الاهتمامات المتاحة |
| GET | `/api/v1/members/interests` | اهتماماتي |
| PUT | `/api/v1/members/interests` | تحديث كل الاهتمامات |
| POST | `/api/v1/members/interests/add` | إضافة اهتمام |
| DELETE | `/api/v1/members/interests/:categoryId` | حذف اهتمام |

### 🔔 Push Notifications (6 endpoints)
| Method | Path | الوظيفة |
|--------|------|---------|
| POST | `/api/v1/devices/register` | تسجيل الجهاز (deviceToken, platform:ios, tokenProvider:apns, deviceName, osVersion, appVersion, language, timezone) |
| DELETE | `/api/v1/devices/unregister` | إلغاء تسجيل الجهاز |
| GET | `/api/v1/devices/status` | حالة الجهاز |
| GET | `/api/v1/topics` | المواضيع المتاحة للإشعارات |
| POST | `/api/v1/notifications/event` | تتبع حدث إشعار (campaignId, eventType, deviceToken) |
| POST | `/api/v1/members/fcm-token` | تسجيل FCM Token (authenticated) |

### 💬 Comments (2 endpoints)
| Method | Path | الوظيفة |
|--------|------|---------|
| GET | `/api/articles/:slug/comments` | تعليقات الخبر (page, limit) |
| POST | `/api/articles/:slug/comments` | إضافة تعليق (content, parentId) — يحتاج token |

### 👍 Reactions & Bookmarks (2 endpoints)
| Method | Path | الوظيفة |
|--------|------|---------|
| POST | `/api/articles/:id/react` | تفاعل (type: like) — يحتاج token |
| POST | `/api/articles/:id/bookmark` | حفظ/إلغاء حفظ (toggle) — يحتاج token |

### 🔍 Search (2 endpoints)
| Method | Path | الوظيفة |
|--------|------|---------|
| GET | `/api/v1/search` | بحث (q, limit, offset, categoryId) |
| GET | `/api/search` | بحث ويب |

### 🎵 Audio (3 endpoints)
| Method | Path | الوظيفة |
|--------|------|---------|
| GET | `/api/audio-newsletters/public` | النشرات الصوتية |
| GET | `/api/audio-newsletters/public/:id` | نشرة صوتية واحدة |
| GET | `/api/articles/:slug/summary-audio` | ملخص صوتي للخبر |

---

## 📱 الشاشات المطلوبة (بالترتيب)

### 1. Splash Screen
- لوقو سبق
- انتقال سلس للصفحة الرئيسية

### 2. Onboarding (أول مرة فقط)
- 3 شاشات تعريفية
- اختيار الاهتمامات (من `/api/v1/interests`)
- تفعيل الإشعارات

### 3. الصفحة الرئيسية (Home)
- **شريط الأخبار العاجلة** (ticker) في الأعلى — من `/api/breaking-ticker/active`
- **أخبار مميزة** (featured) — slider/carousel أفقي
- **أخبار عاجلة** — قسم خاص بلون مميز (أحمر)
- **آخر الأخبار** — قائمة عمودية مع infinite scroll (offset pagination)
- **Pull to refresh**

### 4. شاشة الأقسام (Categories)
- Tabs أفقية في الأعلى من `/api/v1/menu-groups`
- كل تاب يجيب أخبار القسم
- التمرير بين الأقسام بـ swipe

### 5. تفاصيل الخبر (Article Detail)
- عنوان + صورة رئيسية (full bleed)
- اسم الكاتب + التاريخ
- المحتوى (HTML rendering عبر WebView أو AttributedString)
- ملخص صوتي (مشغّل صوت مدمج) من `/api/articles/:slug/summary-audio`
- أزرار: مشاركة / حفظ / تفاعل / تعليق
- أخبار مرتبطة في الأسفل
- تسجيل المشاهدة تلقائياً `/api/v1/articles/:articleId/view`

### 6. البحث (Search)
- حقل بحث مع debounce (300ms)
- نتائج فورية
- فلتر حسب القسم
- تاريخ البحث المحفوظ محلياً

### 7. المفضلة (Bookmarks)
- قائمة الأخبار المحفوظة
- حذف بالسحب (swipe to delete)
- تزامن مع السيرفر عند وجود اتصال

### 8. صور الأسبوع (Weekly Photos)
- عرض شبكي (Grid)
- عرض كامل بالضغط (fullscreen gallery)

### 9. النشرات الصوتية (Audio Newsletters)
- قائمة النشرات
- مشغّل صوتي مع:
  - تشغيل/إيقاف
  - شريط تقدم
  - سرعة التشغيل (1x, 1.5x, 2x)
  - تشغيل في الخلفية (Background Audio)
  - Lock Screen controls

### 10. الملف الشخصي / الإعدادات (Profile & Settings)
- **حالة عدم تسجيل الدخول:** زر تسجيل دخول / إنشاء حساب
- **بعد تسجيل الدخول:**
  - الصورة + الاسم
  - إدارة الاهتمامات
  - تغيير كلمة المرور
  - حذف الحساب
- **إعدادات عامة:**
  - حجم الخط (صغير / متوسط / كبير)
  - الوضع الليلي (Dark Mode / Light / System)
  - اللغة (عربي / إنجليزي)
  - إدارة الإشعارات (عام / حسب القسم) من `/api/v1/topics`
  - مسح الكاش
  - نسخة التطبيق

### 11. تسجيل الدخول / إنشاء حساب (Auth Screens)
- تسجيل دخول (email + password)
- إنشاء حساب (كل الحقول من register endpoint)
- تفعيل بالكود (OTP-style input)
- نسيت كلمة المرور
- Sign in with Apple (إلزامي لـ App Store)

### 12. التعليقات
- عرض شجري (parent/child)
- إضافة تعليق (يحتاج تسجيل دخول)
- Pagination

---

## 🎨 التصميم والهوية البصرية

### الألوان
```swift
// Primary
static let sabqGreen = Color(hex: "#00A650")  // الأخضر الرئيسي لسبق
static let sabqDarkGreen = Color(hex: "#007A3D")

// Breaking News
static let breakingRed = Color(hex: "#E53935")

// Backgrounds
static let backgroundPrimary = Color(.systemBackground)
static let backgroundSecondary = Color(.secondarySystemBackground)

// Text
static let textPrimary = Color(.label)
static let textSecondary = Color(.secondaryLabel)
```

### Typography
- العناوين الرئيسية: **Bold 22pt**
- العناوين الفرعية: **SemiBold 18pt**
- النص الأساسي: **Regular 16pt**
- النص الثانوي: **Regular 14pt**
- الخط: System Arabic (SF Arabic)
- **الاتجاه: RTL بالكامل**

### أيقونات
- SF Symbols (أساسي)

---

## 🏛️ بنية المشروع

```
SabqApp/
├── App/
│   ├── SabqApp.swift              # Entry point
│   ├── AppDelegate.swift          # Push notifications setup
│   └── ContentView.swift          # Root TabView
├── Core/
│   ├── Network/
│   │   ├── APIClient.swift        # URLSession wrapper + async/await
│   │   ├── APIEndpoints.swift     # كل الـ endpoints كـ enum
│   │   ├── APIError.swift         # Custom errors
│   │   ├── TokenManager.swift     # Token storage (Keychain)
│   │   └── RequestInterceptor.swift
│   ├── Models/
│   │   ├── Article.swift          # Codable model
│   │   ├── Category.swift
│   │   ├── User.swift
│   │   ├── Comment.swift
│   │   ├── AudioNewsletter.swift
│   │   └── PushDevice.swift
│   ├── Storage/
│   │   ├── CacheManager.swift     # SwiftData cache
│   │   ├── BookmarkStore.swift
│   │   └── SearchHistory.swift
│   └── Utilities/
│       ├── HTMLRenderer.swift     # HTML → AttributedString
│       ├── DateFormatter+Ext.swift
│       ├── Color+Hex.swift
│       └── Constants.swift
├── Features/
│   ├── Home/
│   │   ├── HomeView.swift
│   │   ├── HomeViewModel.swift
│   │   ├── BreakingTickerView.swift
│   │   ├── FeaturedCarouselView.swift
│   │   └── ArticleRowView.swift
│   ├── Categories/
│   │   ├── CategoriesView.swift
│   │   └── CategoriesViewModel.swift
│   ├── ArticleDetail/
│   │   ├── ArticleDetailView.swift
│   │   ├── ArticleDetailViewModel.swift
│   │   ├── AudioPlayerView.swift
│   │   └── RelatedArticlesView.swift
│   ├── Search/
│   │   ├── SearchView.swift
│   │   └── SearchViewModel.swift
│   ├── Bookmarks/
│   │   ├── BookmarksView.swift
│   │   └── BookmarksViewModel.swift
│   ├── Audio/
│   │   ├── AudioListView.swift
│   │   ├── AudioPlayerViewModel.swift
│   │   └── MiniPlayerView.swift
│   ├── Auth/
│   │   ├── LoginView.swift
│   │   ├── RegisterView.swift
│   │   ├── ActivationView.swift
│   │   ├── ForgotPasswordView.swift
│   │   └── AuthViewModel.swift
│   ├── Profile/
│   │   ├── ProfileView.swift
│   │   ├── ProfileViewModel.swift
│   │   ├── InterestsView.swift
│   │   └── SettingsView.swift
│   ├── Comments/
│   │   ├── CommentsView.swift
│   │   └── CommentsViewModel.swift
│   ├── WeeklyPhotos/
│   │   ├── WeeklyPhotosView.swift
│   │   └── PhotoGalleryView.swift
│   └── Onboarding/
│       ├── OnboardingView.swift
│       └── InterestPickerView.swift
├── Components/
│   ├── ArticleCard.swift          # Reusable card
│   ├── LoadingView.swift
│   ├── ErrorView.swift
│   ├── EmptyStateView.swift
│   ├── ShareButton.swift
│   ├── BookmarkButton.swift
│   └── ReactionButton.swift
├── Resources/
│   ├── Assets.xcassets
│   ├── Localizable.xcstrings      # Arabic + English
│   └── Info.plist
└── Extensions/
    ├── View+Extensions.swift
    ├── String+Extensions.swift
    └── Date+Extensions.swift
```

---

## ⚡ متطلبات أداء وتجربة مستخدم

### الأداء
- **التحميل الأولي < 2 ثانية**
- **Lazy loading** للصور والقوائم
- **Offline support:** كاش آخر 50 خبر عبر SwiftData
- **Batch view tracking** — تجميع المشاهدات وإرسالها دفعة (offline sync)
- **Debounced search** — 300ms
- **Infinite scroll** بدون تقطيع

### التجربة
- **Haptic feedback** عند التفاعل والحفظ
- **Pull to refresh** في كل الشاشات الرئيسية
- **Skeleton loading** (shimmer effect) بدل spinner
- **Smooth transitions** بين الشاشات
- **Share sheet** أصلي (UIActivityViewController)
- **Deep linking** — `sabq://article/{id}` + Universal Links `https://sabq.org/{slug}`

### الأمان
- **Token في Keychain** (لا UserDefaults)
- **Certificate pinning** (اختياري)
- **App Transport Security** مفعّل
- **Sign in with Apple** إلزامي

---

## 📋 Checklist قبل التسليم

- [ ] كل الـ 46 endpoint مستخدمة ومربوطة
- [ ] RTL يشتغل 100% بدون مشاكل
- [ ] Dark Mode يشتغل
- [ ] الإشعارات تشتغل (APNs + FCM registration)
- [ ] الصوت يشتغل في الخلفية
- [ ] Offline mode (كاش + batch sync)
- [ ] كل الشاشات responsive (iPhone SE → iPhone 16 Pro Max)
- [ ] لا warnings ولا errors في Build
- [ ] التعليقات بالعربي في الكود
- [ ] Error handling لكل API call
- [ ] Loading states لكل شاشة
- [ ] Empty states لكل قائمة فارغة

---

## 🚀 ابدأ بالتالي (بالترتيب)

1. **إعداد المشروع** — Xcode project + folder structure + SwiftData setup
2. **Networking layer** — APIClient + كل الـ endpoints + Token management
3. **Models** — كل الـ Codable models
4. **الصفحة الرئيسية** — Home + Breaking ticker + Featured + Article list
5. **تفاصيل الخبر** — Article detail + HTML render + audio + share
6. **الأقسام** — Categories tabs + content
7. **البحث** — Search + history
8. **Auth** — Login + Register + Activate + Forgot password + Apple Sign In
9. **الملف الشخصي** — Profile + Settings + Interests
10. **المفضلة** — Bookmarks + offline
11. **التعليقات** — Comments view + post
12. **الصوت** — Audio newsletters + background playback
13. **الإشعارات** — Push setup + topics management
14. **صور الأسبوع** — Gallery view
15. **Onboarding** — First launch flow
16. **Polish** — Animations + haptics + edge cases

---

## ملف الـ API الكامل

الملف المرفق `sabq-ios-api.json` هو Postman Collection v2.1 يحتوي كل الـ endpoints مع:
- URLs كاملة
- HTTP Methods
- Request bodies (JSON examples)
- Query parameters
- Auth headers
- متغيرات (baseUrl, token, userId, deviceToken)

استخدمه كمرجع أساسي لكل الـ API calls.
