import yfinance as yf
import mplfinance as mpf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')

# Fetch S&P 500 Futures (ES=F)
sp = yf.download("ES=F", period="5d", interval="15m", progress=False)
if sp.empty:
    sp = yf.download("ES=F", period="5d", interval="5m", progress=False)

# Flatten multi-level columns
if isinstance(sp.columns, pd.MultiIndex):
    sp.columns = sp.columns.get_level_values(0)

data = sp.tail(80).copy()
last_close = float(data['Close'].iloc[-1])

# --- RSI ---
delta = data['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
data['RSI'] = 100 - (100 / (1 + rs))

# --- MACD ---
ema12 = data['Close'].ewm(span=12).mean()
ema26 = data['Close'].ewm(span=26).mean()
data['MACD'] = ema12 - ema26
data['Signal'] = data['MACD'].ewm(span=9).mean()
data['Hist'] = data['MACD'] - data['Signal']

# Key levels
high_52w = 7002.28
resistance1 = 6945.0
support1 = 6900.0
support2 = 6817.0

hlines = dict(
    hlines=[high_52w, resistance1, support1, support2],
    colors=['#ff4444', '#ff8800', '#00cc66', '#00cc66'],
    linewidths=[2, 1.2, 1.2, 1],
    linestyle=['--', '--', '--', '--']
)

# Additional plots: MA20, MA50, RSI, MACD
ma20 = data['Close'].rolling(20).mean()
ma50 = data['Close'].rolling(50).mean()

# RSI panel
rsi_plot = mpf.make_addplot(data['RSI'], panel=2, color='#ab47bc', width=1.2, ylabel='RSI')
rsi_70 = mpf.make_addplot(pd.Series(70, index=data.index), panel=2, color='#ff4444', width=0.5, linestyle='--')
rsi_30 = mpf.make_addplot(pd.Series(30, index=data.index), panel=2, color='#00cc66', width=0.5, linestyle='--')

# MACD panel
macd_line = mpf.make_addplot(data['MACD'], panel=3, color='#2196F3', width=1.2, ylabel='MACD')
signal_line = mpf.make_addplot(data['Signal'], panel=3, color='#FF9800', width=1)
hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in data['Hist'].fillna(0)]
hist_plot = mpf.make_addplot(data['Hist'], panel=3, type='bar', color=hist_colors, width=0.7)

# MA on main chart
ma20_plot = mpf.make_addplot(ma20, color='#FFD700', width=1.2, linestyle='--')
ma50_plot = mpf.make_addplot(ma50, color='#FF69B4', width=1.2, linestyle='--')

ap = [ma20_plot, ma50_plot, rsi_plot, rsi_70, rsi_30, macd_line, signal_line, hist_plot]

# Style
mc = mpf.make_marketcolors(up='#26a69a', down='#ef5350', inherit=True)
s = mpf.make_mpf_style(
    marketcolors=mc, gridstyle=':', y_on_right=True,
    facecolor='#131722', figcolor='#131722', edgecolor='#2a2e39',
    rc={
        'axes.labelcolor': '#d1d4dc',
        'xtick.color': '#d1d4dc',
        'ytick.color': '#d1d4dc',
        'text.color': '#d1d4dc',
    }
)

# Plot
fig, axes = mpf.plot(
    data,
    type='candle',
    volume=True,
    style=s,
    hlines=hlines,
    addplot=ap,
    figsize=(14, 10),
    returnfig=True,
    tight_layout=True,
    panel_ratios=(4, 1.2, 1.2, 1.2),
)

# Title
axes[0].set_title(f'\n  S&P 500 Futures (ES) — {last_close:,.2f}', color='white', fontsize=15, fontweight='bold', loc='left')

# S/R Labels
labels = [
    (high_52w, f'ATH {high_52w:,.2f}', '#ff4444'),
    (resistance1, f'R1 {resistance1:,.0f}', '#ff8800'),
    (support1, f'S1 {support1:,.0f}', '#00cc66'),
    (support2, f'S2 {support2:,.0f}', '#00cc66'),
]
for level, text, color in labels:
    axes[0].text(0.98, level, f'{text} ', transform=axes[0].get_yaxis_transform(),
                 color=color, fontsize=8.5, va='center', ha='right',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='#131722', edgecolor=color, alpha=0.8))

# Legend
axes[0].text(0.02, 0.97, '— MA20  — MA50', transform=axes[0].transAxes,
             color='#d1d4dc', fontsize=9, va='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#131722', edgecolor='#2a2e39'))

output = '/home/openclaw/.openclaw/workspace/spx_chart.png'
fig.savefig(output, dpi=150, bbox_inches='tight', facecolor='#131722')
print(f"Chart saved: {output}")
print(f"Last price: {last_close:.2f}")
print(f"RSI: {data['RSI'].iloc[-1]:.1f}")
print(f"MACD: {data['MACD'].iloc[-1]:.2f} | Signal: {data['Signal'].iloc[-1]:.2f}")
