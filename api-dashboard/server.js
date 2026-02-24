require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3500;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────

function getCurrentMonthRange() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const startDate = `${year}-${month}-01`;
  const endDate = `${year}-${month}-${day}`;
  return { startDate, endDate };
}

// ─────────────────────────────────────────────
// OpenAI
// ─────────────────────────────────────────────

app.get('/api/openai', async (req, res) => {
  const apiKey = process.env.OPENAI_API_KEY;

  if (!apiKey) {
    return res.json({
      status: 'error',
      error: 'OPENAI_API_KEY غير موجود في ملف .env',
    });
  }

  try {
    const { startDate, endDate } = getCurrentMonthRange();

    const headers = {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    };

    const [usageRes, subRes] = await Promise.allSettled([
      axios.get(
        `https://api.openai.com/v1/dashboard/billing/usage?start_date=${startDate}&end_date=${endDate}`,
        { headers }
      ),
      axios.get('https://api.openai.com/v1/dashboard/billing/subscription', {
        headers,
      }),
    ]);

    const usageData =
      usageRes.status === 'fulfilled' ? usageRes.value.data : null;
    const subData =
      subRes.status === 'fulfilled' ? subRes.value.data : null;

    const totalUsageCents = usageData?.total_usage ?? 0;
    const totalUsageDollars = (totalUsageCents / 100).toFixed(2);
    const hardLimit = subData?.hard_limit_usd ?? null;
    const softLimit = subData?.soft_limit_usd ?? null;

    res.json({
      status: 'ok',
      totalUsage: parseFloat(totalUsageDollars),
      hardLimit,
      softLimit,
      startDate,
      endDate,
    });
  } catch (err) {
    res.json({
      status: 'error',
      error: err?.response?.data?.error?.message || err.message,
    });
  }
});

// ─────────────────────────────────────────────
// ElevenLabs
// ─────────────────────────────────────────────

app.get('/api/elevenlabs', async (req, res) => {
  const apiKey =
    process.env.ELEVENLABS_API_KEY ||
    '9a2cda21af0960b5930a4b465058c36e3f43a500da7f16744bfb38cca2f3639c';

  try {
    const response = await axios.get('https://api.elevenlabs.io/v1/user', {
      headers: {
        'xi-api-key': apiKey,
      },
    });

    const data = response.data;
    const subscription = data.subscription || {};

    const characterCount = subscription.character_count ?? 0;
    const characterLimit = subscription.character_limit ?? 0;
    const remaining = characterLimit - characterCount;
    const usagePercent =
      characterLimit > 0
        ? Math.min(100, ((characterCount / characterLimit) * 100).toFixed(1))
        : 0;

    res.json({
      status: 'ok',
      plan: subscription.tier || 'غير محدد',
      characterCount,
      characterLimit,
      remaining,
      usagePercent: parseFloat(usagePercent),
      nextReset: subscription.next_character_count_reset_unix
        ? new Date(
            subscription.next_character_count_reset_unix * 1000
          ).toLocaleDateString('ar-SA')
        : null,
    });
  } catch (err) {
    res.json({
      status: 'error',
      error: err?.response?.data?.detail?.message || err.message,
    });
  }
});

// ─────────────────────────────────────────────
// Anthropic (placeholder)
// ─────────────────────────────────────────────

app.get('/api/anthropic', async (req, res) => {
  res.json({
    status: 'placeholder',
    message: 'Anthropic لا توفر Usage API عام. تحقق من Console.',
    consoleUrl: 'https://console.anthropic.com/settings/billing',
  });
});

// ─────────────────────────────────────────────
// Google Gemini (placeholder)
// ─────────────────────────────────────────────

app.get('/api/gemini', async (req, res) => {
  res.json({
    status: 'placeholder',
    message: 'Google Gemini لا توفر Usage API عام. تحقق من Console.',
    consoleUrl: 'https://console.cloud.google.com/billing',
  });
});

// ─────────────────────────────────────────────
// Health check
// ─────────────────────────────────────────────

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

// ─────────────────────────────────────────────
// Start
// ─────────────────────────────────────────────

app.listen(PORT, () => {
  console.log(`✅ API Dashboard يعمل على: http://localhost:${PORT}`);
});
