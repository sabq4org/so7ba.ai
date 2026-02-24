#!/usr/bin/env node
/**
 * صُحبة Dashboard Server — localhost:9898
 * لوحة تحكم شخصية لأبو محمد
 */

const http = require('http');
const https = require('https');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const PORT = 9898;
const ACCOUNT = 'sabq4u@gmail.com';
const HTML_FILE = path.join(__dirname, 'index.html');
const CONFIG_FILE = '/Users/alialhazmi/.openclaw/openclaw.json';

// --- Helpers ---
function fetchJSON(url, extraHeaders = {}) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https') ? https : http;
    const req = mod.get(url, { timeout: 10000, headers: { 'Accept': 'application/json', ...extraHeaders } }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { reject(new Error('Invalid JSON')); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
  });
}

// --- API: Calendar Events ---
function getEvents() {
  const now = new Date();
  const from = now.toISOString();
  const to = new Date(now.getTime() + 14 * 86400000).toISOString();
  try {
    const result = execSync(
      `GOG_ACCOUNT=${ACCOUNT} gog calendar events primary --from "${from}" --to "${to}" --json`,
      { timeout: 15000, encoding: 'utf8' }
    );
    const data = JSON.parse(result);
    return { ok: true, events: data.events || [] };
  } catch (err) {
    return { ok: false, error: err.message, events: [] };
  }
}

// --- API: Prayer Times ---
async function getPrayer() {
  try {
    const now = new Date();
    const dd = String(now.getDate()).padStart(2, '0');
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const yyyy = now.getFullYear();
    const url = `http://api.aladhan.com/v1/timingsByCity/${dd}-${mm}-${yyyy}?city=Riyadh&country=SaudiArabia&method=4`;
    const data = await fetchJSON(url);
    const t = data.data.timings;
    const hijri = data.data.date.hijri;
    return {
      ok: true,
      timings: {
        Fajr: t.Fajr, Sunrise: t.Sunrise, Dhuhr: t.Dhuhr,
        Asr: t.Asr, Maghrib: t.Maghrib, Isha: t.Isha,
        Imsak: t.Imsak
      },
      hijri: {
        day: hijri.day,
        month: hijri.month.ar,
        year: hijri.year,
        weekday: hijri.weekday.ar
      }
    };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

// --- API: Weather ---
async function getWeather() {
  try {
    const data = await fetchJSON('https://wttr.in/Riyadh?format=j1');
    const c = data.current_condition[0];
    const today = data.weather?.[0];
    return {
      ok: true,
      current: {
        temp: c.temp_C,
        feelsLike: c.FeelsLikeC,
        humidity: c.humidity,
        desc: c.weatherDesc?.[0]?.value || '',
        windSpeed: c.windspeedKmph,
        uvIndex: c.uvIndex
      },
      today: today ? {
        maxTemp: today.maxtempC,
        minTemp: today.mintempC
      } : null
    };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

// --- API: Agents ---
function getAgents() {
  try {
    const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    const list = config.agents?.list || [];
    const AGENT_META = {
      'main':          { emoji: '🧠', ar: 'صُحبة', role: 'المدير العام' },
      'coder':         { emoji: '💻', ar: 'كوّدر', role: 'برمجة وتطوير' },
      'writer':        { emoji: '✍️', ar: 'كاتب', role: 'صناعة محتوى' },
      'researcher':    { emoji: '🔍', ar: 'باحث', role: 'بحث وتحليل' },
      'organizer':     { emoji: '📋', ar: 'منظّم', role: 'بريد وجدولة' },
      'memory':        { emoji: '🧠', ar: 'ذاكرة', role: 'حفظ المعرفة' },
      'marketer':      { emoji: '📈', ar: 'مسوّق', role: 'تسويق وSEO' },
      'designer':      { emoji: '🎨', ar: 'مصمم', role: 'إنفوجرافيك وعروض' },
      'tweet-factory': { emoji: '🐦', ar: 'سجع', role: 'مصنع التغريدات' },
      'translator':    { emoji: '🌐', ar: 'تُرجمان', role: 'ترجمة وتحليل' },
      'ideas-kitchen': { emoji: '💡', ar: 'شرارة', role: 'مطبخ الأفكار' },
      'taskroom':      { emoji: '📋', ar: 'متابع', role: 'غرفة المتابعة' }
    };
    const agents = list.map(ag => {
      const meta = AGENT_META[ag.id] || { emoji: '🤖', ar: ag.name || ag.id, role: '' };
      return {
        id: ag.id,
        emoji: meta.emoji,
        name: meta.ar,
        role: meta.role,
        model: ag.model || 'default'
      };
    });
    return { ok: true, agents };
  } catch (err) {
    return { ok: false, error: err.message, agents: [] };
  }
}

// --- API: OpenAI Usage ---
async function getOpenAIUsage() {
  let apiKey;
  try {
    const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    apiKey = config.env?.OPENAI_API_KEY;
  } catch {}
  if (!apiKey) return { ok: false, error: 'OPENAI_API_KEY غير موجود في الكونفيج' };

  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const startDate = `${year}-${month}-01`;
  const endDate = `${year}-${month}-${day}`;

  try {
    const [usageRes, subRes] = await Promise.allSettled([
      fetchJSON(`https://api.openai.com/v1/dashboard/billing/usage?start_date=${startDate}&end_date=${endDate}`, { Authorization: `Bearer ${apiKey}` }),
      fetchJSON('https://api.openai.com/v1/dashboard/billing/subscription', { Authorization: `Bearer ${apiKey}` })
    ]);
    const usage = usageRes.status === 'fulfilled' ? usageRes.value : null;
    const sub   = subRes.status  === 'fulfilled' ? subRes.value  : null;
    const totalCents = usage?.total_usage ?? 0;
    return {
      ok: true,
      totalUsage: parseFloat((totalCents / 100).toFixed(2)),
      hardLimit:  sub?.hard_limit_usd ?? null,
      softLimit:  sub?.soft_limit_usd ?? null,
      startDate, endDate
    };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

// --- API: ElevenLabs Usage ---
async function getElevenLabsUsage() {
  let apiKey;
  try {
    const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    apiKey = config.env?.ELEVENLABS_API_KEY;
  } catch {}
  if (!apiKey) apiKey = '9a2cda21af0960b5930a4b465058c36e3f43a500da7f16744bfb38cca2f3639c';

  try {
    const data = await fetchJSON('https://api.elevenlabs.io/v1/user', { 'xi-api-key': apiKey });
    const sub = data.subscription || {};
    const count = sub.character_count ?? 0;
    const limit = sub.character_limit ?? 0;
    const remaining = limit - count;
    const usagePercent = limit > 0 ? parseFloat(Math.min(100, (count / limit * 100)).toFixed(1)) : 0;
    return {
      ok: true,
      plan: sub.tier || 'غير محدد',
      characterCount: count,
      characterLimit: limit,
      remaining,
      usagePercent,
      nextReset: sub.next_character_count_reset_unix
        ? new Date(sub.next_character_count_reset_unix * 1000).toLocaleDateString('ar-SA')
        : null
    };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

// --- Server ---
const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');

  if (req.method === 'GET' && req.url === '/api/events') {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify(getEvents()));
    return;
  }

  if (req.method === 'GET' && req.url === '/api/prayer') {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify(await getPrayer()));
    return;
  }

  if (req.method === 'GET' && req.url === '/api/weather') {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify(await getWeather()));
    return;
  }

  if (req.method === 'GET' && req.url === '/api/agents') {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify(getAgents()));
    return;
  }

  if (req.method === 'GET' && (req.url === '/' || req.url === '/index.html')) {
    try {
      const html = fs.readFileSync(HTML_FILE, 'utf8');
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      res.end(html);
    } catch {
      res.writeHead(404);
      res.end('index.html not found');
    }
    return;
  }

  if (req.method === 'GET' && req.url === '/api/openai') {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify(await getOpenAIUsage()));
    return;
  }

  if (req.method === 'GET' && req.url === '/api/elevenlabs') {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify(await getElevenLabsUsage()));
    return;
  }

  if (req.method === 'GET' && req.url === '/api/anthropic') {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify({ status: 'placeholder', consoleUrl: 'https://console.anthropic.com/settings/billing' }));
    return;
  }

  if (req.method === 'GET' && req.url === '/api/gemini') {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify({ status: 'placeholder', consoleUrl: 'https://console.cloud.google.com/billing' }));
    return;
  }

  if (req.method === 'GET' && req.url === '/calendar.html') {
    const calFile = path.join(__dirname, 'calendar.html');
    try {
      const html = fs.readFileSync(calFile, 'utf8');
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      res.end(html);
    } catch {
      res.writeHead(404);
      res.end('calendar.html not found');
    }
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`✅ صُحبة Dashboard → http://localhost:${PORT}`);
});
