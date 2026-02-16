const DISPLAY = {
  'SPX': { name: 'S&P 500', icon: '🇺🇸', label: 'المؤشر الأمريكي' },
  'GOLD': { name: 'الذهب', icon: '🥇', label: 'أونصة / دولار' },
  'OIL': { name: 'النفط', icon: '🛢️', label: 'خام WTI / برميل' },
  'TASI': { name: 'أرامكو', icon: '🇸🇦', label: 'السوق السعودي' }
};

function formatPrice(key, price) {
  if (key === 'SPX') return price.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
  if (key === 'GOLD') return price.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
  return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

async function render() {
  const { marketData } = await chrome.storage.local.get('marketData');
  const container = document.getElementById('markets');
  
  if (!marketData || Object.keys(marketData).length === 0) {
    container.innerHTML = '<div class="loading">جاري جلب البيانات... 📡</div>';
    setTimeout(render, 2000);
    return;
  }
  
  let html = '';
  for (const [key, display] of Object.entries(DISPLAY)) {
    const data = marketData[key];
    if (!data) continue;
    
    const direction = data.up ? 'up' : 'down';
    const arrow = data.up ? '▲' : '▼';
    const sign = data.up ? '+' : '';
    
    html += `
      <div class="market-card ${direction}">
        <div class="market-info">
          <div class="market-name">${display.icon} ${display.name}</div>
          <div class="market-label">${display.label}</div>
        </div>
        <div class="market-data">
          <div class="market-price">${formatPrice(key, data.price)}</div>
          <div class="market-change">${arrow} ${sign}${data.changePct}%</div>
        </div>
      </div>
    `;
  }
  
  container.innerHTML = html;
}

render();

// Auto-refresh popup every 10 seconds
setInterval(render, 10000);
