# مرصاد — برومبت التنفيذ الكامل

## Instructions

Build a full-stack Arabic news monitoring platform called **"مرصاد" (Mersad)**. This is a SaaS product for Arabic newsrooms that monitors sources in real-time, detects breaking news using AI, and alerts editorial teams instantly.

The entire UI must be **Arabic RTL**, responsive (desktop + mobile), and production-ready.

---

## Tech Stack (strict)

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS + shadcn/ui
- **Database:** PostgreSQL via Prisma ORM
- **Auth:** NextAuth.js (credentials provider — password only, single-user)
- **Real-time:** Server-Sent Events (SSE) for live feed
- **Background Jobs:** Cron routes via Next.js Route Handlers + Vercel Cron (or node-cron for self-hosted)
- **AI:** OpenAI API (GPT-4o-mini for classification, GPT-4o for summarization)
- **Charts:** Recharts
- **Icons:** Lucide React
- **Notifications:** Telegram Bot API + Email (Resend)
- **Deployment:** Vercel (frontend) + Neon (database)

---

## Database Schema (Prisma)

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id           String   @id @default(cuid())
  passwordHash String
  createdAt    DateTime @default(now())
}

model Source {
  id          String       @id @default(cuid())
  name        String
  nameAr      String
  type        SourceType
  identifier  String       // Twitter handle, RSS URL, etc.
  category    String?      // politics, sports, economy, etc.
  priority    Int          @default(5) // 1=highest, 10=lowest
  isActive    Boolean      @default(true)
  lastChecked DateTime?
  items       SourceItem[]
  createdAt   DateTime     @default(now())
  updatedAt   DateTime     @updatedAt
}

enum SourceType {
  TWITTER
  RSS
  GOOGLE_TRENDS
  WEBSITE
  TELEGRAM_CHANNEL
}

model SourceItem {
  id            String        @id @default(cuid())
  sourceId      String
  source        Source         @relation(fields: [sourceId], references: [id])
  externalId    String?       @unique // tweet ID, article URL hash
  title         String?
  content       String
  url           String?
  author        String?
  imageUrl      String?
  publishedAt   DateTime
  discoveredAt  DateTime      @default(now())
  
  // AI Analysis
  urgency       Urgency       @default(NORMAL)
  category      String?
  summary       String?
  aiScore       Float?        // 0-100 importance score
  isBreaking    Boolean       @default(false)
  isDuplicate   Boolean       @default(false)
  duplicateOfId String?
  
  // Editorial
  status        ItemStatus    @default(DISCOVERED)
  assignedTo    String?
  notes         String?
  
  // Cluster (related items grouped)
  clusterId     String?
  cluster       Cluster?      @relation(fields: [clusterId], references: [id])
  
  alerts        Alert[]
  createdAt     DateTime      @default(now())
}

enum Urgency {
  BREAKING    // 🔴 عاجل
  IMPORTANT   // 🟡 مهم
  NORMAL      // 🟢 عادي
  LOW         // ⚪ منخفض
}

enum ItemStatus {
  DISCOVERED   // مكتشف
  REVIEWING    // قيد المراجعة
  WRITING      // قيد التحرير
  PUBLISHED    // منشور
  IGNORED      // مُتجاهل
}

model Cluster {
  id        String       @id @default(cuid())
  title     String
  titleAr   String?
  summary   String?
  itemCount Int          @default(1)
  items     SourceItem[]
  createdAt DateTime     @default(now())
  updatedAt DateTime     @updatedAt
}

model Alert {
  id           String     @id @default(cuid())
  sourceItemId String
  sourceItem   SourceItem @relation(fields: [sourceItemId], references: [id])
  channel      AlertChannel
  sentAt       DateTime   @default(now())
  delivered    Boolean    @default(false)
}

enum AlertChannel {
  TELEGRAM
  EMAIL
  WEB_PUSH
  IN_APP
}

model Competitor {
  id        String   @id @default(cuid())
  name      String
  nameAr    String
  url       String
  rssUrl    String?
  isActive  Boolean  @default(true)
  createdAt DateTime @default(now())
}

model Settings {
  key   String @id
  value String
}
```

---

## Application Structure

```
src/
├── app/
│   ├── layout.tsx                    # RTL Arabic layout
│   ├── page.tsx                      # Redirect to /dashboard
│   ├── login/
│   │   └── page.tsx                  # Password-only login
│   ├── dashboard/
│   │   └── page.tsx                  # Main dashboard
│   ├── feed/
│   │   └── page.tsx                  # Live news feed (real-time)
│   ├── sources/
│   │   ├── page.tsx                  # Manage sources
│   │   └── [id]/page.tsx            # Source details
│   ├── alerts/
│   │   └── page.tsx                  # Alert history & settings
│   ├── competitors/
│   │   └── page.tsx                  # Competitor monitoring
│   ├── archive/
│   │   └── page.tsx                  # Search & browse history
│   ├── settings/
│   │   └── page.tsx                  # App settings
│   └── api/
│       ├── auth/[...nextauth]/       # Auth
│       ├── sources/                  # CRUD sources
│       ├── feed/                     # SSE endpoint for live feed
│       ├── items/                    # CRUD source items
│       ├── alerts/                   # Send alerts
│       ├── ai/
│       │   ├── classify/             # Classify incoming item
│       │   ├── summarize/            # Generate summary
│       │   └── draft/                # Generate article draft
│       └── cron/
│           ├── check-twitter/        # Poll Twitter sources
│           ├── check-rss/            # Poll RSS feeds
│           ├── check-trends/         # Poll Google Trends
│           └── detect-clusters/      # Group related items
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx               # Navigation sidebar (desktop)
│   │   ├── BottomNav.tsx             # Bottom nav (mobile)
│   │   ├── Header.tsx                # Top bar with alerts bell
│   │   └── ThemeToggle.tsx           # Dark mode
│   ├── dashboard/
│   │   ├── StatsCards.tsx            # Key metrics
│   │   ├── LiveTicker.tsx            # Breaking news ticker
│   │   ├── TimelineChart.tsx         # Items discovered over time
│   │   ├── SourceDistribution.tsx    # Pie chart by source type
│   │   └── TopClusters.tsx           # Trending stories
│   ├── feed/
│   │   ├── FeedItem.tsx              # Single feed item card
│   │   ├── FeedFilters.tsx           # Filter controls
│   │   ├── FeedTimeline.tsx          # Scrollable feed
│   │   └── BreakingBanner.tsx        # Red banner for breaking news
│   ├── sources/
│   │   ├── SourceCard.tsx
│   │   ├── AddSourceDialog.tsx
│   │   └── SourceStats.tsx
│   ├── alerts/
│   │   ├── AlertSettings.tsx
│   │   └── AlertHistory.tsx
│   └── shared/
│       ├── UrgencyBadge.tsx          # 🔴🟡🟢 badges
│       ├── StatusBadge.tsx
│       ├── SearchBar.tsx
│       ├── EmptyState.tsx
│       └── LoadingSpinner.tsx
├── lib/
│   ├── prisma.ts                     # Prisma client
│   ├── auth.ts                       # NextAuth config
│   ├── ai.ts                         # AI classification & summarization
│   ├── twitter.ts                    # Twitter API integration
│   ├── rss.ts                        # RSS parser
│   ├── trends.ts                     # Google Trends
│   ├── alerts.ts                     # Send Telegram/Email alerts
│   ├── clustering.ts                 # Group related items
│   └── utils.ts                      # Helpers
└── styles/
    └── globals.css                   # Tailwind + Arabic fonts
```

---

## Page Specifications

### 1. Login Page (`/login`)
- Centered card with app logo "مرصاد 🔭"
- Password input only (no username)
- "دخول" button
- Error shake animation on wrong password
- Redirect to /dashboard on success

### 2. Dashboard (`/dashboard`)

**Top Row — Stats Cards (4 cards):**
- أخبار اليوم (today's discovered items count)
- عاجل الآن (current breaking items count, red pulse animation)
- المصادر النشطة (active sources count)
- متوسط سرعة الاكتشاف (avg minutes before mainstream)

**Middle — Live Breaking Ticker:**
- Red horizontal scrolling banner showing breaking news
- Only shows when there are active breaking items
- Click to jump to item

**Charts Row:**
- Left: Bar chart — items discovered per hour (last 24h)
- Right: Donut chart — distribution by source type

**Bottom — Latest Discoveries Table:**
- Last 20 items
- Columns: الوقت | المصدر | العنوان | الأهمية | الحالة
- Click row to expand details
- Quick actions: تعيين | تجاهل | فتح المصدر

### 3. Live Feed (`/feed`)

**This is the core screen — newsroom teams will stare at this all day.**

- Real-time feed using SSE (Server-Sent Events)
- New items slide in from top with subtle animation
- Sound notification option for breaking news 🔊

**Each Feed Item Card shows:**
- Urgency badge (🔴🟡🟢)
- Source name + icon
- Time (relative: "قبل 3 دقائق")
- Title/Content (first 200 chars)
- Image thumbnail (if available)
- Link to original
- AI summary (expandable)
- Status dropdown (discovered → reviewing → writing → published → ignored)
- Assign button
- Related items count (cluster)

**Filters Sidebar:**
- Urgency: عاجل / مهم / عادي
- Source type: تويتر / RSS / ترندات
- Category: سياسة / اقتصاد / رياضة / تقنية / عام
- Status: مكتشف / قيد التحرير / منشور / متجاهل
- Date range
- Search text

**View modes:**
- Timeline (default)
- Grid (cards)
- Compact (table)

### 4. Sources Management (`/sources`)

- Grid of source cards
- Each card: name, type icon, last checked, items count, status toggle
- Add Source dialog:
  - Name (Arabic)
  - Type dropdown (Twitter/RSS/Telegram/Website)
  - Identifier (handle/@username, URL, etc.)
  - Category
  - Priority (1-10 slider)
- Bulk import via CSV
- Pre-loaded template: top 50 Saudi news sources

### 5. Alerts (`/alerts`)

**Settings:**
- Telegram Bot Token + Chat ID
- Email address
- Alert rules:
  - Breaking (🔴) → Telegram + Email immediately
  - Important (🟡) → Telegram only
  - Cluster threshold (X items in Y minutes → alert)

**History:**
- Table of all sent alerts with delivery status

### 6. Competitors (`/competitors`)

- Add competitor publications (name + RSS URL)
- Dashboard showing: what they published that we didn't cover
- "فجوة التغطية" — coverage gap alerts

### 7. Archive (`/archive`)

- Full-text search across all discovered items
- Advanced filters (date, source, urgency, category)
- Export to CSV/PDF

### 8. Settings (`/settings`)

- Change password
- App name customization
- AI model selection
- Check intervals (how often to poll sources)
- Telegram bot configuration
- Data export (full JSON backup)
- Data import

---

## AI Classification Logic (`lib/ai.ts`)

When a new item arrives from any source:

```typescript
// Step 1: Classify urgency
const classifyPrompt = `
You are a senior Arabic news editor. Analyze this content and classify it.

Content: "${item.content}"
Source: "${source.name}" (${source.type})
Time: "${item.publishedAt}"

Respond in JSON:
{
  "urgency": "BREAKING" | "IMPORTANT" | "NORMAL" | "LOW",
  "category": "politics" | "economy" | "sports" | "tech" | "society" | "entertainment" | "weather" | "security" | "health" | "other",
  "score": 0-100,
  "isBreaking": true/false,
  "reason": "brief Arabic explanation",
  "suggestedTitle": "Arabic headline"
}

Rules:
- BREAKING: Deaths, major appointments, royal decrees, wars, major accidents, critical government decisions
- IMPORTANT: Policy changes, notable events, significant economic news
- NORMAL: Regular news, updates, features
- LOW: Opinions, promotional content, routine announcements
`;

// Step 2: Check for duplicates (compare with last 6 hours of items)
// Step 3: Cluster with related items
// Step 4: If BREAKING or score > 80 → trigger alert
// Step 5: If BREAKING → auto-generate summary
```

---

## Cron Jobs Schedule

| Job | Interval | Description |
|-----|----------|-------------|
| check-twitter | Every 2 min | Poll Twitter/X sources |
| check-rss | Every 5 min | Poll RSS feeds |
| check-trends | Every 10 min | Check Google Trends |
| detect-clusters | Every 5 min | Group related items |
| cleanup | Daily 3 AM | Archive items older than 30 days |

---

## Design System

### Colors
```css
/* Light Mode */
--primary: #0F172A;        /* Navy — headers, sidebar */
--accent: #10B981;         /* Emerald — buttons, badges */
--breaking: #EF4444;       /* Red — breaking news */
--important: #F59E0B;      /* Amber — important */
--normal: #10B981;         /* Green — normal */
--background: #F8FAFC;     /* Light gray bg */
--card: #FFFFFF;

/* Dark Mode */
--primary: #1E293B;
--background: #0F172A;
--card: #1E293B;
```

### Typography
- Font: IBM Plex Sans Arabic (Google Fonts)
- Direction: RTL
- Headlines: Bold 700
- Body: Regular 400

### Responsive Breakpoints
- Mobile: < 768px (bottom nav, stacked cards)
- Tablet: 768-1024px (collapsible sidebar)
- Desktop: > 1024px (full sidebar + multi-column)

### Mobile-Specific
- Bottom navigation: الرئيسية | المباشر | المصادر | التنبيهات | الإعدادات
- Pull-to-refresh on feed
- Swipe right on item → mark as reviewed
- Swipe left → ignore
- Touch targets minimum 44px

---

## Environment Variables

```env
DATABASE_URL=
NEXTAUTH_SECRET=
NEXTAUTH_URL=
ADMIN_PASSWORD_HASH=
OPENAI_API_KEY=
TWITTER_BEARER_TOKEN=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
RESEND_API_KEY=
```

---

## Seed Data

On first run, seed the database with:
1. Default admin user (password: "mersad2026")
2. Top 30 Saudi Twitter sources (SPA, ministries, major journalists)
3. Top 10 Arabic RSS feeds (Reuters Arabic, BBC Arabic, Al Arabiya)
4. Default alert settings
5. Sample categories

---

## Critical Requirements

1. ✅ ALL text in Arabic (RTL)
2. ✅ Mobile-first responsive design
3. ✅ Real-time feed with SSE
4. ✅ AI classification on every incoming item
5. ✅ Instant Telegram alerts for breaking news
6. ✅ Dark mode
7. ✅ Fast — pages must load in < 2 seconds
8. ✅ Accessible — proper ARIA labels
9. ✅ SEO not needed (private app)
10. ✅ PWA support (installable on mobile)
