"""
NASDAQ Day Trade Analytics — Databricks App
Powered by Databricks Model Serving + Yahoo Finance
"""

import re
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from typing import Optional

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

MODEL_ENDPOINT = "databricks-gemini-3-1-flash-lite"

@st.cache_resource
def get_databricks_client() -> Optional[WorkspaceClient]:
    try:
        return WorkspaceClient()
    except Exception:
        return None

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NASDAQ Day Trade Analytics | DSA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS  (ready.so-inspired: sand texture hero, clean white cards, warm palette)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Tokens ── */
:root {
  --pink:        #E80070;
  --pink-dark:   #C4005C;
  --pink-light:  #FF1A8C;
  --navy:        #0f172a;
  --surface:     #ffffff;
  --surface-dim: #f8f8f6;   /* ready.so warm off-white */
  --surface2:    #f0efec;   /* sand-tinted card */
  --border:      #e8e6e0;
  --text:        #1a1a1a;
  --text-muted:  #6b7280;
  --green:       #059669;
  --red:         #dc2626;
  --gold:        #d97706;
  --radius:      14px;
  --radius-lg:   22px;
  --shadow-sm:   0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
  --shadow-md:   0 4px 24px rgba(0,0,0,0.10);
  --shadow-glow: 0 8px 40px rgba(232,0,112,0.18);
}

/* ── Base ── */
* { font-family: 'Inter', -apple-system, sans-serif !important; box-sizing: border-box; }
.stApp { background: var(--surface-dim) !important; color: var(--text) !important; }
p, label, div, span { color: var(--text); }
h1,h2,h3,h4 { color: var(--text) !important; letter-spacing: -0.025em; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid var(--border) !important; }
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] .stMarkdown p { color: var(--text-muted) !important; }

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--pink) 0%, var(--pink-dark) 100%) !important;
  color: white !important; border: none !important;
  padding: 0.75rem 1.75rem !important; border-radius: var(--radius) !important;
  font-weight: 700 !important; font-size: 0.95rem !important;
  box-shadow: var(--shadow-glow) !important;
  transition: all 0.2s ease !important; width: 100% !important; letter-spacing: 0.01em;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 12px 40px rgba(232,0,112,0.3) !important; }

/* ── Inputs ── */
.stTextInput input {
  background: var(--surface2) !important; border: 1.5px solid var(--border) !important;
  color: var(--text) !important; border-radius: var(--radius) !important;
}
.stTextInput input:focus { border-color: var(--pink) !important; box-shadow: 0 0 0 3px rgba(232,0,112,0.1) !important; }

/* ── Selectbox ── */
div[data-baseweb="select"] > div { background: var(--surface2) !important; border: 1.5px solid var(--border) !important; border-radius: var(--radius) !important; }

/* ── Metric cards ── */
div[data-testid="stMetric"] {
  background: var(--surface) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; padding: 1.25rem 1.5rem !important;
  box-shadow: var(--shadow-sm) !important;
}
div[data-testid="stMetricLabel"] p { color: var(--text-muted) !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600 !important; }
div[data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 800 !important; font-size: 1.55rem !important; }
div[data-testid="stMetricDelta"] { font-size: 0.85rem !important; font-weight: 600 !important; }

/* ── Native dataframe table — PREMIUM STYLING ── */
.stDataFrame { border-radius: var(--radius-lg) !important; overflow: hidden !important; box-shadow: var(--shadow-md) !important; border: 1px solid var(--border) !important; }
/* Streamlit wraps the table in an iframe; we style what we can from the outside */
.stDataFrame > div { border-radius: var(--radius-lg) !important; }

/* ── Expander ── */
details { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }
summary { color: var(--text) !important; font-weight: 600; }

/* ── HR ── */
hr { border-color: var(--border) !important; margin: 2rem 0 !important; }

/* ── Spinner ── */
.stSpinner p { color: var(--pink) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--surface2); }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--pink); }

/* ── AI analysis block ── */
.ai-block { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 2rem 2.25rem; box-shadow: var(--shadow-sm); margin-top: 0.5rem; }
.ai-block p, .ai-block li, .ai-block strong { color: var(--text) !important; }

/* ── Custom HTML table (historical data) ── */
.data-table-wrap { border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-md); border: 1px solid var(--border); background: white; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.data-table thead { background: linear-gradient(90deg, #1a1a2e 0%, #E80070 180%); }
.data-table thead th {
  color: white; font-weight: 700; font-size: 0.72rem; text-transform: uppercase;
  letter-spacing: 0.1em; padding: 16px 18px; text-align: right; white-space: nowrap; border: none;
}
.data-table thead th:first-child { text-align: left; padding-left: 22px; }
.data-table tbody tr { transition: background 0.12s ease; border-bottom: 1px solid #f3f4f6; }
.data-table tbody tr:last-child { border-bottom: none; }
.data-table tbody tr:nth-child(even) { background: #fafaf9; }
.data-table tbody tr:hover { background: #fff0f6; }
.data-table tbody td {
  color: #1a1a1a; padding: 13px 18px; text-align: right;
  font-size: 0.875rem; font-weight: 500;
}
.data-table tbody td:first-child { text-align: left; padding-left: 22px; color: #6b7280; font-size: 0.82rem; font-weight: 400; }
.data-table .close-col { font-weight: 700; color: #1a1a1a; }
.badge-up   { display: inline-block; background: #ecfdf5; color: #059669; border-radius: 99px; padding: 2px 9px; font-size: 0.75rem; font-weight: 700; }
.badge-down { display: inline-block; background: #fef2f2; color: #dc2626; border-radius: 99px; padding: 2px 9px; font-size: 0.75rem; font-weight: 700; }
.badge-flat { display: inline-block; background: #f3f4f6; color: #6b7280; border-radius: 99px; padding: 2px 9px; font-size: 0.75rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def fmt_large(n: float) -> str:
    if n >= 1e12: return f"${n/1e12:.2f}T"
    if n >= 1e9:  return f"${n/1e9:.2f}B"
    if n >= 1e6:  return f"${n/1e6:.2f}M"
    if n >= 1e3:  return f"${n/1e3:.1f}K"
    return f"${n:.2f}"

def fmt_vol(n: float) -> str:
    if n >= 1e9: return f"{n/1e9:.2f}B"
    if n >= 1e6: return f"{n/1e6:.1f}M"
    if n >= 1e3: return f"{n/1e3:.0f}K"
    return str(int(n))

def _calc_rsi(close: pd.Series, period: int = 14) -> float:
    delta = close.diff()
    gain  = delta.where(delta > 0, 0).rolling(period).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs    = gain / loss
    rsi   = 100 - (100 / (1 + rs))
    v     = rsi.iloc[-1]
    return float(v) if not pd.isna(v) else 50.0

# ─── Data ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_stock_data(symbol: str, period: str) -> Optional[pd.DataFrame]:
    ticker = yf.Ticker(symbol)
    data   = ticker.history(period=period)
    if data is None or data.empty:
        return None
    required = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(c in data.columns for c in required):
        return None
    data = data.dropna(subset=required)
    return data if len(data) >= 5 else None

@st.cache_data(ttl=300)
def load_ticker_info(symbol: str) -> dict:
    try:
        return yf.Ticker(symbol).info or {}
    except Exception:
        return {}

# ─── Databricks LLM ───────────────────────────────────────────────────────────
def databricks_ai_analysis(ticker: str, hist: pd.DataFrame) -> str:
    client = get_databricks_client()
    if client is None:
        return "⚠️ Cliente Databricks não disponível."

    close    = hist['Close']
    latest   = float(close.iloc[-1])
    change   = float((close.iloc[-1] / close.iloc[0] - 1) * 100)
    hi       = float(hist['High'].max())
    lo       = float(hist['Low'].min())
    avg_vol  = float(hist['Volume'].mean())
    rsi_val  = _calc_rsi(close)
    sma20    = float(close.rolling(20).mean().iloc[-1])
    ema20    = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
    vol_pct  = float(close.pct_change().std() * np.sqrt(252) * 100)

    prompt = f"""Você é um analista financeiro especialista em day trade na NASDAQ.
Analise a ação {ticker} com dados dos últimos meses:

- Preço atual: ${latest:.2f} | Variação no período: {change:+.2f}%
- Máxima: ${hi:.2f} | Mínima: ${lo:.2f} | Volume médio: {avg_vol:,.0f}
- RSI(14): {rsi_val:.1f} | SMA20: ${sma20:.2f} | EMA20: ${ema20:.2f}
- Volatilidade anualizada: {vol_pct:.1f}%

Forneça análise em PT-BR com:
1. **Tendência atual** (Alta/Baixa/Neutra) com justificativa técnica
2. **Suporte e Resistência** — níveis relevantes em USD
3. **Recomendação para Day Trade** — estratégia concisa
4. **Nível de Risco** (Baixo/Médio/Alto) com alerta se necessário
5. **Contexto de mercado** da empresa baseado no seu conhecimento

Use markdown com bullets. Seja direto e objetivo."""

    try:
        response = client.serving_endpoints.query(
            name=MODEL_ENDPOINT,
            messages=[
                ChatMessage(role=ChatMessageRole.SYSTEM, content="Você é um analista financeiro especialista em day trade."),
                ChatMessage(role=ChatMessageRole.USER,   content=prompt)
            ],
            max_tokens=700,
            temperature=0.4
        )
        if response and response.choices:
            raw = response.choices[0].message.content
            return re.sub(r"(Running:[\s\S]*?\n\n)|(^transfer_task_to.*\n?)", "",
                          raw, flags=re.MULTILINE).strip()
        return "Não foi possível obter resposta do modelo."
    except Exception as e:
        return f"⚠️ Erro ao consultar modelo Databricks: {str(e)}"

# ─── Chart theme ──────────────────────────────────────────────────────────────
CHART = dict(
    plot_bgcolor='#ffffff',
    paper_bgcolor='#f8f8f6',
    font=dict(family='Inter', color='#6b7280', size=11),
    xaxis=dict(gridcolor='#f0efec', showgrid=True, zeroline=False, linecolor='#e8e6e0'),
    yaxis=dict(gridcolor='#f0efec', showgrid=True, zeroline=False, linecolor='#e8e6e0'),
    margin=dict(l=60, r=30, t=55, b=50),
    hovermode='x unified',
    hoverlabel=dict(bgcolor='white', bordercolor='#e8e6e0', font_size=12, font_family='Inter'),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(size=11, color='#374151')),
)

def _apply(fig, title, h=400):
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color='#1a1a1a', weight=700), x=0.01),
        height=h, **CHART
    )
    return fig

def plot_price(hist, ticker, ma_periods):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist['Close'], mode='lines', name='Fechamento',
        line=dict(color='#E80070', width=2.5),
        fill='tozeroy', fillcolor='rgba(232,0,112,0.04)'
    ))
    for i, p in enumerate(ma_periods):
        col = f'MA_{p}'
        if col in hist.columns:
            color = ['#C4005C','#d97706','#3b82f6'][i % 3]
            fig.add_trace(go.Scatter(x=hist.index, y=hist[col], mode='lines',
                                     name=f'MA {p}d', line=dict(color=color, width=1.5, dash='dash')))
    st.plotly_chart(_apply(fig, f"{ticker} — Preço de Fechamento", 420), use_container_width=True)

def plot_candlestick(hist, ticker):
    fig = go.Figure(data=[go.Candlestick(
        x=hist.index, open=hist['Open'], high=hist['High'],
        low=hist['Low'], close=hist['Close'], name=ticker,
        increasing_line_color='#059669', decreasing_line_color='#dc2626',
        increasing_fillcolor='rgba(5,150,105,0.65)',
        decreasing_fillcolor='rgba(220,38,38,0.65)'
    )])
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(_apply(fig, f"{ticker} — Candlestick", 400), use_container_width=True)

def plot_moving_averages(hist, ticker):
    h = hist.copy()
    h['SMA_20'] = h['Close'].rolling(20).mean()
    h['EMA_20'] = h['Close'].ewm(span=20, adjust=False).mean()
    fig = go.Figure()
    for col, color, dash, name, w in [
        ('Close',  '#E80070', 'solid', 'Fechamento', 2.5),
        ('SMA_20', '#9ca3af', 'dash',  'SMA 20',     1.5),
        ('EMA_20', '#059669', 'dot',   'EMA 20',     1.5),
    ]:
        fig.add_trace(go.Scatter(x=h.index, y=h[col], mode='lines', name=name,
                                 line=dict(color=color, width=w, dash=dash)))
    st.plotly_chart(_apply(fig, f"{ticker} — Médias Móveis", 400), use_container_width=True)

def plot_volume(hist, ticker):
    colors = ['#059669' if c >= o else '#dc2626'
              for c, o in zip(hist['Close'], hist['Open'])]
    fig = go.Figure(data=[go.Bar(x=hist.index, y=hist['Volume'],
                                  marker_color=colors, opacity=0.8, name='Volume')])
    st.plotly_chart(_apply(fig, f"{ticker} — Volume de Negociação", 300), use_container_width=True)

def plot_rsi(hist, ticker):
    close = hist['Close']
    delta = close.diff()
    gain  = delta.where(delta > 0, 0).rolling(14).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi   = 100 - (100 / (1 + gain / loss))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=rsi, mode='lines', name='RSI',
                             line=dict(color='#d97706', width=2)))
    fig.add_hline(y=70, line=dict(color='#dc2626', dash='dash', width=1),
                  annotation_text='70', annotation_font_color='#dc2626', annotation_position='right')
    fig.add_hline(y=30, line=dict(color='#059669', dash='dash', width=1),
                  annotation_text='30', annotation_font_color='#059669', annotation_position='right')
    fig.add_hrect(y0=30, y1=70, fillcolor='rgba(217,119,6,0.04)', line_width=0)
    ch = {**CHART}; ch['yaxis'] = {**CHART['yaxis'], 'range': [0, 100]}
    fig.update_layout(title=dict(text=f"{ticker} — RSI (14)", font=dict(size=15, color='#1a1a1a'), x=0.01),
                      height=280, **ch)
    st.plotly_chart(fig, use_container_width=True)

# ─── Premium HTML table ────────────────────────────────────────────────────────
def render_historical_table(hist: pd.DataFrame):
    disp = hist.tail(30).copy().iloc[::-1]
    rows = ""
    for idx, row in disp.iterrows():
        date_str = pd.Timestamp(idx).strftime('%d/%m/%Y')
        chg      = ((row['Close'] - row['Open']) / row['Open']) * 100
        if chg > 0.05:
            badge = f'<span class="badge-up">▲ {chg:+.2f}%</span>'
        elif chg < -0.05:
            badge = f'<span class="badge-down">▼ {chg:.2f}%</span>'
        else:
            badge = f'<span class="badge-flat">≈ {chg:.2f}%</span>'
        rows += f"""
        <tr>
          <td>{date_str}</td>
          <td class="close-col">${row['Close']:.2f}</td>
          <td>${row['Open']:.2f}</td>
          <td>${row['High']:.2f}</td>
          <td>${row['Low']:.2f}</td>
          <td>{fmt_vol(row['Volume'])}</td>
          <td>{badge}</td>
        </tr>"""

    html = f"""
    <div class="data-table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th style="text-align:left">Data</th>
            <th>Fechamento</th>
            <th>Abertura</th>
            <th>Máxima</th>
            <th>Mínima</th>
            <th>Volume</th>
            <th>Var. Dia</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)

# ─── Session state ─────────────────────────────────────────────────────────────
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding:1.25rem 0 0.75rem 0;border-bottom:1px solid #f0efec;margin-bottom:1rem">
  <div style="font-size:1.4rem;font-weight:900;color:#E80070;letter-spacing:-0.03em">📊 DSA Analytics</div>
  <div style="font-size:0.76rem;color:#9ca3af;margin-top:4px;font-weight:500">Day Trade · NASDAQ · Databricks AI</div>
</div>
""", unsafe_allow_html=True)

SECTORS = {
    "🖥️ Tecnologia": {"Apple":"AAPL","Microsoft":"MSFT","NVIDIA":"NVDA","Google":"GOOGL",
                       "Meta":"META","Tesla":"TSLA","AMD":"AMD","Salesforce":"CRM","Intel":"INTC"},
    "🏦 Finanças":   {"JPMorgan":"JPM","Goldman Sachs":"GS","Visa":"V","Mastercard":"MA","Bank of America":"BAC"},
    "🛒 Consumo":    {"Amazon":"AMZN","Walmart":"WMT","Home Depot":"HD","Nike":"NKE","Starbucks":"SBUX"},
    "💊 Saúde":      {"Johnson & Johnson":"JNJ","Pfizer":"PFE","UnitedHealth":"UNH","Eli Lilly":"LLY"},
}

st.sidebar.markdown("**Empresa:**")
sector  = st.sidebar.selectbox("Setor:", list(SECTORS.keys()), label_visibility="collapsed")
company = st.sidebar.selectbox("Empresa:", list(SECTORS[sector].keys()), label_visibility="collapsed")
quick_ticker = SECTORS[sector][company]

st.sidebar.markdown("**Ou insira o ticker:**")
manual_ticker = st.sidebar.text_input("Ticker:", value="", placeholder="ex: TSLA, NVDA").upper().strip()
final_ticker  = manual_ticker if manual_ticker else quick_ticker

PERIODS = {"5 Dias":"5d","1 Mês":"1mo","3 Meses":"3mo","6 Meses":"6mo","1 Ano":"1y","2 Anos":"2y","5 Anos":"5y"}
st.sidebar.markdown("**Período:**")
period_label = st.sidebar.selectbox("Período:", list(PERIODS.keys()), index=4, label_visibility="collapsed")
period       = PERIODS[period_label]

st.sidebar.markdown("---")
st.sidebar.markdown("**Visualizações:**")
show_ma          = st.sidebar.checkbox("Médias Móveis", value=True)
ma_choices       = st.sidebar.multiselect("Períodos MA (dias):", ["20","50","200"], default=["20","50"]) if show_ma else []
show_candlestick = st.sidebar.checkbox("Candlestick", value=True)
show_volume      = st.sidebar.checkbox("Volume", value=True)
show_rsi         = st.sidebar.checkbox("RSI (14)", value=True)
show_ai          = st.sidebar.checkbox("Análise IA (Databricks)", value=True)

st.sidebar.markdown("---")
if st.sidebar.button("🔍 Analisar", type="primary"):
    st.session_state.analysis_done = True

st.sidebar.markdown("""
<div style="margin-top:1rem;font-size:0.72rem;color:#9ca3af;line-height:1.7">
  🤖 <b>Databricks Model Serving</b><br>
  📈 <b>Yahoo Finance</b> — dados reais<br>
  🔒 Nenhum dado simulado
</div>
""", unsafe_allow_html=True)

# ─── Hero (landing — ready.so inspired) ───────────────────────────────────────
if not st.session_state.analysis_done:
    # Sand-texture hero (ready.so pattern)
    st.markdown("""
<div style="
  background: linear-gradient(135deg,rgba(232,0,112,0.96) 0%,rgba(196,0,92,0.97) 100%),
              url('https://ready.so/images/Sand-Texture.webp') center/cover;
  background-blend-mode: multiply;
  border-radius: 22px; padding: 4.5rem 3.5rem; margin-bottom: 2.5rem; position:relative; overflow:hidden">
  <div style="position:absolute;top:0;right:0;width:45%;height:100%;
    background:radial-gradient(circle at 70% 40%,rgba(255,255,255,0.12) 0%,transparent 65%);pointer-events:none"></div>
  <div style="max-width:600px;position:relative;z-index:2">
    <div style="display:inline-block;background:rgba(255,255,255,0.15);backdrop-filter:blur(10px);
         padding:6px 18px;border-radius:99px;font-size:0.78rem;color:white;font-weight:700;
         border:1px solid rgba(255,255,255,0.25);margin-bottom:1.75rem;letter-spacing:0.06em">
      ✦ NASDAQ DAY TRADE ANALYTICS — DATABRICKS AI
    </div>
    <h1 style="font-size:3.5rem;font-weight:900;color:white;margin:0 0 1rem;line-height:1.05;letter-spacing:-0.04em">
      Inteligência de<br>mercado em<br>tempo real
    </h1>
    <p style="font-size:1.05rem;color:rgba(255,255,255,0.88);margin:0;line-height:1.75;max-width:460px">
      Análise técnica avançada com Agentes de IA na Databricks.
      RSI, Candlestick, Médias Móveis e insights por LLM — dados 100% reais.
    </p>
    <div style="margin-top:2rem;display:flex;gap:0.75rem;flex-wrap:wrap">
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);
           color:white;padding:6px 16px;border-radius:99px;font-size:0.8rem;font-weight:600">📡 Yahoo Finance API</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);
           color:white;padding:6px 16px;border-radius:99px;font-size:0.8rem;font-weight:600">🤖 Meta-Llama 3.3 70B</span>
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);
           color:white;padding:6px 16px;border-radius:99px;font-size:0.8rem;font-weight:600">🔒 Sem dados demo</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Feature cards — ready.so clean white card style
    cols = st.columns(3)
    feats = [
        ("📡","Dados Reais",       "#E80070","Histórico via Yahoo Finance API. Preços, volume e indicadores sem simulação."),
        ("🤖","IA Databricks",    "#C4005C","Meta-Llama 3.3 70B via Model Serving analisa tendências e dá recomendações."),
        ("📊","Análise Completa", "#FF1A8C","RSI, Candlestick, SMA/EMA, Volume e tabela histórica com variação diária."),
    ]
    for col,(icon,title,accent,desc) in zip(cols,feats):
        with col:
            st.markdown(f"""
<div style="background:white;border:1px solid #e8e6e0;border-radius:18px;padding:2.25rem 2rem;
     box-shadow:0 2px 12px rgba(0,0,0,0.06);height:100%;
     border-top:3px solid {accent}">
  <div style="font-size:2.25rem;margin-bottom:1.1rem">{icon}</div>
  <div style="font-weight:800;font-size:1.05rem;color:#1a1a1a;margin-bottom:0.6rem">{title}</div>
  <div style="font-size:0.875rem;color:#6b7280;line-height:1.65">{desc}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Steps row
    st.markdown("<h3 style='text-align:center;font-size:1.5rem;font-weight:800;color:#1a1a1a;margin-bottom:1.5rem'>Como funciona</h3>",
                unsafe_allow_html=True)
    steps = st.columns(4)
    for col,(n,label,desc) in zip(steps,[
        ("1","Selecione","Escolha setor e empresa no painel lateral"),
        ("2","Configure","Defina período e indicadores desejados"),
        ("3","Analise","Veja gráficos interativos e métricas"),
        ("4","Decida","Leia insights gerados por IA Databricks"),
    ]):
        with col:
            st.markdown(f"""
<div style="background:white;border:1px solid #e8e6e0;border-radius:16px;padding:1.5rem;text-align:center;
     box-shadow:0 1px 6px rgba(0,0,0,0.05)">
  <div style="width:44px;height:44px;background:linear-gradient(135deg,#E80070,#C4005C);color:white;
       border-radius:50%;display:flex;align-items:center;justify-content:center;
       font-weight:800;font-size:1.15rem;margin:0 auto 1rem;box-shadow:0 4px 14px rgba(232,0,112,0.3)">{n}</div>
  <div style="font-weight:700;color:#1a1a1a;margin-bottom:0.4rem;font-size:0.95rem">{label}</div>
  <div style="font-size:0.8rem;color:#9ca3af;line-height:1.55">{desc}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<br>
<div style="background:white;border:1.5px dashed #f0d0e0;border-radius:18px;padding:2.5rem;
     text-align:center;box-shadow:0 1px 6px rgba(0,0,0,0.04)">
  <div style="font-size:1.5rem;font-weight:800;color:#E80070;margin-bottom:0.6rem">Pronto para começar?</div>
  <div style="color:#9ca3af;font-size:0.95rem;max-width:420px;margin:0 auto 0.5rem">
    Selecione uma empresa no painel lateral e clique em <strong>🔍 Analisar</strong>.
  </div>
  <div style="font-size:1.25rem;color:#E80070;margin-top:0.75rem">←</div>
</div>""", unsafe_allow_html=True)
    st.stop()

# ─── Load real data ────────────────────────────────────────────────────────────
if not final_ticker:
    st.error("❌ Insira um ticker válido no painel lateral.")
    st.stop()

with st.spinner(f"Carregando dados reais para **{final_ticker}**..."):
    stock_data  = load_stock_data(final_ticker, period)
    ticker_info = load_ticker_info(final_ticker)

if stock_data is None:
    st.error(f"""**❌ Não foi possível carregar dados para `{final_ticker}`.**

Possíveis causas:
- Ticker inválido — verifique em [stockanalysis.com](https://stockanalysis.com/list/nasdaq-stocks/)
- Yahoo Finance pode estar bloqueado no ambiente Databricks Apps
- Período inválido para este ativo

Tente outro ticker ou verifique sua conexão.""")
    st.stop()

# ─── Metrics ──────────────────────────────────────────────────────────────────
close        = stock_data['Close']
current      = float(close.iloc[-1])
prev         = float(close.iloc[-2]) if len(close) > 1 else current
day_chg      = current - prev
day_chg_pct  = (day_chg / prev * 100) if prev else 0
period_chg   = float((close.iloc[-1] / close.iloc[0] - 1) * 100)
hi_period    = float(stock_data['High'].max())
lo_period    = float(stock_data['Low'].min())
avg_vol      = float(stock_data['Volume'].mean())
volatility   = float(close.pct_change().std() * np.sqrt(252) * 100)
rsi_now      = _calc_rsi(close)
rsi_label    = "Sobrecomprado" if rsi_now > 70 else "Sobrevendido" if rsi_now < 30 else "Neutro"
rsi_color    = "#dc2626" if rsi_now > 70 else "#059669" if rsi_now < 30 else "#d97706"

company_name = ticker_info.get('longName') or ticker_info.get('shortName') or final_ticker
mktcap       = ticker_info.get('marketCap', 0)
sector_info  = ticker_info.get('sector', '')
exchange     = ticker_info.get('exchange', 'NASDAQ')
currency     = ticker_info.get('currency', 'USD')

# ─── Stock header ─────────────────────────────────────────────────────────────
chg_color  = "#059669" if day_chg >= 0 else "#dc2626"
chg_arrow  = "▲" if day_chg >= 0 else "▼"

st.markdown(f"""
<div style="background:white;border:1px solid #e8e6e0;border-radius:20px;padding:2rem 2.5rem;
     margin-bottom:1.5rem;box-shadow:0 2px 16px rgba(0,0,0,0.06);display:flex;
     justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;
     border-left:4px solid #E80070">
  <div>
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap">
      <span style="font-size:1.9rem;font-weight:900;color:#1a1a1a">{final_ticker}</span>
      <span style="background:#E8007015;color:#E80070;font-size:0.68rem;font-weight:800;
           padding:3px 11px;border-radius:99px;border:1px solid #E8007030;letter-spacing:0.08em">{exchange}</span>
      {"<span style='background:#f0f9ff;color:#0369a1;font-size:0.68rem;font-weight:700;padding:3px 11px;border-radius:99px;border:1px solid #bae6fd'>" + sector_info + "</span>" if sector_info else ""}
    </div>
    <div style="font-size:1rem;color:#6b7280;font-weight:500">{company_name}</div>
    {"<div style='font-size:0.8rem;color:#9ca3af;margin-top:3px'>Market Cap: <b>" + fmt_large(mktcap) + "</b></div>" if mktcap else ""}
  </div>
  <div style="text-align:right">
    <div style="font-size:2.8rem;font-weight:900;color:#1a1a1a;line-height:1">{currency} {current:,.2f}</div>
    <div style="font-size:1rem;font-weight:700;color:{chg_color};margin-top:6px">
      {chg_arrow} {abs(day_chg):.2f} ({day_chg_pct:+.2f}%) hoje
      <span style="color:#9ca3af;font-weight:400;font-size:0.85rem"> &nbsp;|&nbsp; {period_chg:+.2f}% no período</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI row ──────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: st.metric("Preço Atual",    f"{current:,.2f}",  f"{day_chg_pct:+.2f}%")
with c2: st.metric("Máxima Período", f"{hi_period:,.2f}")
with c3: st.metric("Mínima Período", f"{lo_period:,.2f}")
with c4: st.metric("Volume Médio",   fmt_vol(avg_vol))
with c5: st.metric("Volatilidade",   f"{volatility:.1f}%", "anualizada")
with c6: st.metric(f"RSI(14) — {rsi_label}", f"{rsi_now:.1f}")

st.markdown("---")

# ─── Price chart ──────────────────────────────────────────────────────────────
chart_data = stock_data.copy()
if show_ma:
    for p in ma_choices:
        chart_data[f'MA_{p}'] = chart_data['Close'].rolling(int(p)).mean()

st.markdown("### 📈 Evolução do Preço")
plot_price(chart_data, final_ticker, ma_choices if show_ma else [])

# ─── Candlestick + MAs ────────────────────────────────────────────────────────
if show_candlestick or show_ma:
    col_a, col_b = st.columns(2)
    with col_a:
        if show_candlestick:
            st.markdown("### 🕯️ Candlestick")
            plot_candlestick(stock_data, final_ticker)
    with col_b:
        if show_ma:
            st.markdown("### 〰️ Médias Móveis")
            plot_moving_averages(stock_data, final_ticker)

# ─── Volume + RSI ─────────────────────────────────────────────────────────────
if show_volume or show_rsi:
    col_c, col_d = st.columns([3, 2])
    with col_c:
        if show_volume:
            st.markdown("### 📊 Volume de Negociação")
            plot_volume(stock_data, final_ticker)
    with col_d:
        if show_rsi:
            st.markdown("### ⚡ RSI (14)")
            plot_rsi(stock_data, final_ticker)

st.markdown("---")

# ─── Technical indicators table ───────────────────────────────────────────────
st.markdown("### 🔬 Indicadores Técnicos")
col_left, col_right = st.columns(2)

with col_left:
    sma20_v = float(close.rolling(20).mean().iloc[-1])
    sma50_v = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
    ema20_v = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
    macd_v  = float(close.ewm(span=12).mean().iloc[-1] - close.ewm(span=26).mean().iloc[-1])
    sup_v   = float(stock_data['Low'].rolling(20).min().iloc[-1])
    res_v   = float(stock_data['High'].rolling(20).max().iloc[-1])

    df_ind = pd.DataFrame({
        "Indicador": ["SMA 20","SMA 50","EMA 20","MACD (12,26)","Suporte 20d","Resistência 20d","RSI (14)"],
        "Valor":     [f"${sma20_v:.2f}", f"${sma50_v:.2f}" if sma50_v else "—",
                      f"${ema20_v:.2f}", f"{macd_v:+.4f}",
                      f"${sup_v:.2f}", f"${res_v:.2f}", f"{rsi_now:.1f}"],
        "Sinal":     ["Alta ↑" if current>sma20_v else "Baixa ↓",
                      ("Alta ↑" if current>sma50_v else "Baixa ↓") if sma50_v else "—",
                      "Alta ↑" if current>ema20_v else "Baixa ↓",
                      "Positivo" if macd_v>0 else "Negativo",
                      "Acima" if current>sup_v*1.02 else "Próximo",
                      "Abaixo" if current<res_v*0.98 else "Próximo",
                      rsi_label],
    })
    st.dataframe(df_ind, use_container_width=True, hide_index=True)

with col_right:
    df_stats = pd.DataFrame({
        "Estatística": ["Preço Médio","Mediana","Desvio Padrão","Mínimo","Máximo","Volume Total","Var. % Total"],
        "Valor":       [f"${close.mean():.2f}", f"${close.median():.2f}",
                        f"${close.std():.2f}",  f"${close.min():.2f}",
                        f"${close.max():.2f}",  fmt_vol(float(stock_data['Volume'].sum())),
                        f"{period_chg:+.2f}%"],
    })
    st.dataframe(df_stats, use_container_width=True, hide_index=True)

st.markdown("---")

# ─── Historical data — premium HTML table ─────────────────────────────────────
st.markdown("### 📋 Histórico — Últimos 30 Pregões")
render_historical_table(stock_data)

st.markdown("---")

# ─── AI Analysis — rendered as plain markdown (NOT inside HTML div) ────────────
if show_ai:
    st.markdown("### 🤖 Análise por IA — Databricks Model Serving")
    st.markdown(f"""
<div style="background:#fff5f9;border:1px solid #f0d0e0;border-radius:12px;
     padding:0.75rem 1.25rem;margin-bottom:1rem;font-size:0.8rem">
  Modelo: <strong style="color:#E80070">{MODEL_ENDPOINT}</strong> &nbsp;·&nbsp;
  Ativo: <strong>{final_ticker}</strong> &nbsp;·&nbsp; Período: <strong>{period_label}</strong>
</div>""", unsafe_allow_html=True)

    with st.spinner("Consultando Agente de IA na Databricks..."):
        ai_text = databricks_ai_analysis(final_ticker, stock_data)

    # Render as proper markdown — NOT inside an HTML div (fixes garbled text)
    with st.container():
        st.markdown(ai_text)

st.markdown("---")

# ─── Auto insights ────────────────────────────────────────────────────────────
st.markdown("### 💡 Insights Automáticos")
sma20_i = float(close.rolling(20).mean().iloc[-1])
sma50_i = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else sma20_i
insights = []
if sma20_i > sma50_i:
    insights.append(("🟢","Tendência de Alta","MA20 acima da MA50 — momentum positivo.","#059669"))
else:
    insights.append(("🔴","Tendência de Baixa","MA20 abaixo da MA50 — pressão vendedora.","#dc2626"))
if rsi_now > 70:
    insights.append(("⚠️","RSI Sobrecomprado",f"RSI={rsi_now:.1f} — possível correção no curto prazo.","#d97706"))
elif rsi_now < 30:
    insights.append(("✅","RSI Sobrevendido",f"RSI={rsi_now:.1f} — possível rebote técnico.","#3b82f6"))
if volatility > 40:
    insights.append(("⚡","Alta Volatilidade",f"{volatility:.1f}% a.a. — position sizing essencial.","#dc2626"))
elif volatility < 15:
    insights.append(("😴","Baixa Volatilidade",f"{volatility:.1f}% a.a. — ativo estável.","#6b7280"))
if current >= hi_period * 0.97:
    insights.append(("🔺","Próximo da Máxima",f"A {(hi_period-current)/hi_period*100:.1f}% da máxima do período.","#E80070"))

cols_i = st.columns(min(len(insights), 3))
for i,(icon,title,desc,color) in enumerate(insights):
    with cols_i[i % 3]:
        st.markdown(f"""
<div style="background:white;border:1px solid {color}25;border-left:4px solid {color};
     border-radius:14px;padding:1.25rem;margin-bottom:1rem;box-shadow:0 1px 6px rgba(0,0,0,0.04)">
  <div style="font-size:1.4rem;margin-bottom:0.5rem">{icon}</div>
  <div style="font-weight:700;color:{color};font-size:0.875rem;margin-bottom:0.35rem">{title}</div>
  <div style="font-size:0.8rem;color:#6b7280;line-height:1.55">{desc}</div>
</div>""", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem;color:#9ca3af;font-size:0.78rem;border-top:1px solid #e8e6e0;margin-top:1rem">
  <strong style="color:#6b7280">NASDAQ Day Trade Analytics</strong> — Data Science Academy &nbsp;·&nbsp;
  Yahoo Finance &nbsp;·&nbsp; Databricks Model Serving &nbsp;·&nbsp;
  <em>Não constitui recomendação de investimento</em>
</div>
""", unsafe_allow_html=True)
