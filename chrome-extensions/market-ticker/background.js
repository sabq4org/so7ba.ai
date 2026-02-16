// Market Ticker - Background Service Worker
// Fetches live market data and updates badge

const SYMBOLS = {
  'SPX': { name: 'S&P 500', query: 'SPY' },
  'GOLD': { name: 'الذهب', query: 'GC=F' },
  'OIL': { name: 'النفط', query: 'CL=F' },
  'TASI': { name: 'تاسي', query: '2222.SR' }  // Aramco as TASI proxy
};

let currentIndex = 0;
const symbolKeys = Object.keys(SYMBOLS);
let marketData = {};

async function fetchMarketData() {
  try {
    for (const [key, sym] of Object.entries(SYMBOLS)) {
      try {
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${sym.query}?interval=1d&range=1d`;
        const resp = await fetch(url, {
          headers: { 'User-Agent': 'Mozilla/5.0' }
        });
        
        if (resp.ok) {
          const data = await resp.json();
          const meta = data.chart.result[0].meta;
          const price = meta.regularMarketPrice;
          const prevClose = meta.chartPreviousClose || meta.previousClose;
          const change = price - prevClose;
          const changePct = ((change / prevClose) * 100).toFixed(2);
          
          marketData[key] = {
            price: price,
            change: change.toFixed(2),
            changePct: changePct,
            up: change >= 0
          };
        }
      } catch (e) {
        console.log(`Error fetching ${key}:`, e);
      }
    }
    
    await chrome.storage.local.set({ marketData });
    updateBadge();
  } catch (e) {
    console.error('Fetch error:', e);
  }
}

function updateBadge() {
  const key = symbolKeys[currentIndex];
  const data = marketData[key];
  
  if (!data) {
    chrome.action.setBadgeText({ text: '...' });
    return;
  }
  
  // Format price for badge (short)
  let badgeText = '';
  if (key === 'SPX') {
    badgeText = Math.round(data.price).toString();
  } else if (key === 'GOLD') {
    badgeText = Math.round(data.price).toString();
  } else {
    badgeText = data.price.toFixed(1);
  }
  
  // Color: green for up, red for down
  const color = data.up ? '#34A853' : '#EA4335';
  
  chrome.action.setBadgeText({ text: badgeText });
  chrome.action.setBadgeBackgroundColor({ color: color });
  
  // Tooltip
  const arrow = data.up ? '▲' : '▼';
  chrome.action.setTitle({ 
    title: `${SYMBOLS[key].name}: ${data.price} ${arrow} ${data.changePct}%` 
  });
}

// Rotate displayed symbol every 5 seconds
function rotateBadge() {
  currentIndex = (currentIndex + 1) % symbolKeys.length;
  updateBadge();
}

// Initial fetch
fetchMarketData();

// Refresh data every 60 seconds
chrome.alarms.create('fetchData', { periodInMinutes: 1 });

// Rotate badge every 5 seconds
chrome.alarms.create('rotateBadge', { periodInMinutes: 0.083 }); // ~5 sec

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'fetchData') {
    fetchMarketData();
  } else if (alarm.name === 'rotateBadge') {
    rotateBadge();
  }
});
