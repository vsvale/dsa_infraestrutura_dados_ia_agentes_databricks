"""
NASDAQ Day Trade Analytics — Databricks App
Powered by Databricks Model Serving (Meta-Llama 3.3 70B) + Yahoo Finance
"""

import re
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
from typing import Optional

# ─── Databricks SDK (correct import path for current SDK versions) ───────────
from databricks.sdk import WorkspaceClient

MODEL_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"

@st.cache_resource
def get_databricks_client() -> Optional[WorkspaceClient]:
    try:
        return WorkspaceClient()
    except Exception as e:
        return None

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NASDAQ Day Trade Analytics | DSA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS — Premium Dark-Finance Design ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
  --pink:       #E80070;
  --pink-dark:  #C4005C;
  --pink-light: #FF1A8C;
  --navy:       #0f172a;
  --surface:    #1e293b;
  --surface2:   #263347;
  --border:     rgba(255,255,255,0.08);
  --text:       #f1f5f9;
  --text-muted: #94a3b8;
  --green:      #10b981;
  --red:        #ef4444;
  --gold:       #f59e0b;
  --radius:     12px;
  --radius-lg:  20px;
  --shadow:     0 4px 24px rgba(0,0,0,0.4);
}

* { font-family: 'Inter', -apple-system, sans-serif !important; box-sizing: border-box; }

/* Dark app background */
.stApp { background: var(--navy) !important; color: var(--text) !important; }
section[data-testid="stSidebar"] { background: var(--surface) !important; }
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Headings */
h1, h2, h3, h4 { color: var(--text) !important; letter-spacing: -0.02em; }
p, label, span, div { color: var(--text); }

/* Input fields */
input[type="text"], .stTextInput input {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: var(--radius) !important;
}
.stTextInput input:focus { border-color: var(--pink) !important; box-shadow: 0 0 0 3px rgba(232,0,112,0.15) !important; }

/* Primary button */
.stButton > button {
  background: linear-gradient(135deg, var(--pink) 0%, var(--pink-dark) 100%) !important;
  color: white !important; border: none !important;
  padding: 0.75rem 2rem !important; border-radius: var(--radius) !important;
  font-weight: 700 !important; font-size: 1rem !important;
  box-shadow: 0 4px 20px rgba(232,0,112,0.35) !important;
  transition: all 0.25s ease !important; width: 100% !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 30px rgba(232,0,112,0.5) !important; }

/* Selectbox */
.stSelectbox select, div[data-baseweb="select"] > div {
  background: var(--surface2) !important; border-color: var(--border) !important; color: var(--text) !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 1.25rem !important;
}
div[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
div[data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 700 !important; font-size: 1.6rem !important; }

/* ═══════════════════════════════════════════════════════════════
   STUNNING TABLE DESIGN
═══════════════════════════════════════════════════════════════ */
.stDataFrame {
  border-radius: var(--radius-lg) !important;
  overflow: hidden !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow) !important;
}
.stDataFrame thead { background: linear-gradient(90deg, var(--pink-dark), #7c1d4e) !important; }
.stDataFrame thead th {
  color: white !important; font-weight: 700 !important;
  font-size: 0.75rem !important; text-transform: uppercase !important;
  letter-spacing: 0.1em !important; padding: 14px 16px !important;
  border: none !important; white-space: nowrap;
}
.stDataFrame tbody tr { transition: background 0.15s ease !important; }
.stDataFrame tbody tr:nth-child(even) { background: rgba(255,255,255,0.025) !important; }
.stDataFrame tbody tr:hover { background: rgba(232,0,112,0.06) !important; }
.stDataFrame tbody td {
  color: var(--text) !important; padding: 12px 16px !important;
  border-bottom: 1px solid rgba(255,255,255,0.04) !important;
  font-size: 0.875rem !important; font-variant-numeric: tabular-nums;
}
.stDataFrame th:first-child, .stDataFrame td:first-child { padding-left: 20px !important; }

/* Expander */
details { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }
summary { color: var(--text) !important; }

/* Spinner / info / error */
div[data-testid="stStatusWidget"], .stAlert { border-radius: var(--radius) !important; }
.stSpinner { color: var(--pink) !important; }

/* Sidebar separator */
.css-1d391kg { background: var(--surface); }
hr { border-color: var(--border) !important; }

/* Plotly charts dark bg */
.js-plotly-plot .plotly { border-radius: var(--radius) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--pink-dark); border-radius: 99px; }
</style>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def fmt_num(n: float) -> str:
    if n >= 1e12: return f"${n/1e12:.2f}T"
    if n >= 1e9:  return f"${n/1e9:.2f}B"
    if n >= 1e6:  return f"${n/1e6:.2f}M"
    if n >= 1e3:  return f"${n/1e3:.2f}K"
    return f"${n:.2f}"

def badge(label: str, color: str = "#E80070") -> str:
    return f'<span style="background:{color}22;color:{color};font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:99px;border:1px solid {color}44;letter-spacing:0.06em">{label}</span>'

# ─── Data loading (real Yahoo Finance — no demo fallback) ─────────────────────
@st.cache_data(ttl=300)
def load_stock_data(symbol: str, period: str) -> Optional[pd.DataFrame]:
    """Carrega dados reais via Yahoo Finance."""
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period)
    if data is None or data.empty:
        return None
    required = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(c in data.columns for c in required):
        return None
    data = data.dropna(subset=required)
    if len(data) < 5:
        return None
    return data

@st.cache_data(ttl=300)
def load_ticker_info(symbol: str) -> dict:
    try:
        t = yf.Ticker(symbol)
        return t.info or {}
    except Exception:
        return {}

# ─── Databricks LLM Analysis ──────────────────────────────────────────────────
def databricks_ai_analysis(ticker: str, hist: pd.DataFrame) -> str:
    """Chama Databricks Model Serving para análise de day trade."""
    client = get_databricks_client()
    if client is None:
        return "⚠️ Cliente Databricks não disponível."

    latest   = float(hist['Close'].iloc[-1])
    change   = float((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100)
    hi       = float(hist['High'].max())
    lo       = float(hist['Low'].min())
    avg_vol  = float(hist['Volume'].mean())
    rsi_val  = _calc_rsi(hist['Close'])
    sma20    = float(hist['Close'].rolling(20).mean().iloc[-1])
    ema20    = float(hist['Close'].ewm(span=20, adjust=False).mean().iloc[-1])
    vol_pct  = float(hist['Close'].pct_change().std() * np.sqrt(252) * 100)

    prompt = f"""Você é um analista financeiro especialista em day trade na NASDAQ.
Analise a ação {ticker} com dados dos últimos meses:

Preço atual: ${latest:.2f} | Variação período: {change:+.2f}%
Máxima: ${hi:.2f} | Mínima: ${lo:.2f} | Volume médio: {avg_vol:,.0f}
RSI(14): {rsi_val:.1f} | SMA20: ${sma20:.2f} | EMA20: ${ema20:.2f}
Volatilidade anualizada: {vol_pct:.1f}%

Forneça análise em PT-BR com:
1. **Tendência atual** (Alta/Baixa/Neutra) com justificativa técnica
2. **Suporte e Resistência** — níveis relevantes em USD
3. **Recomendação para Day Trade** — estratégia concisa
4. **Nível de Risco** (Baixo/Médio/Alto) com alerta se necessário
5. **Resumo de notícias relevantes** da empresa (baseado no seu conhecimento até data de corte)

Use markdown com bullets. Seja direto e preciso."""

    try:
        # Use openai-compatible endpoint via SDK
        response = client.serving_endpoints.query(
            name=MODEL_ENDPOINT,
            messages=[
                {"role": "system", "content": "Você é um analista financeiro especialista em day trade e análise técnica."},
                {"role": "user",   "content": prompt}
            ],
            max_tokens=700,
            temperature=0.4
        )
        if response and response.choices:
            raw = response.choices[0].message.content
            return re.sub(r"(Running:[\s\S]*?\n\n)|(^transfer_task_to.*\n?)", "", raw,
                          flags=re.MULTILINE).strip()
        return "Não foi possível obter resposta do modelo."
    except Exception as e:
        return f"⚠️ Erro ao consultar modelo Databricks: {str(e)}"


def _calc_rsi(close: pd.Series, period: int = 14) -> float:
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    v = rsi.iloc[-1]
    return float(v) if not pd.isna(v) else 50.0

# ─── Chart helpers ────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    plot_bgcolor="#0f172a",
    paper_bgcolor="#1e293b",
    font=dict(family="Inter", color="#94a3b8"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showgrid=True, zeroline=False),
    margin=dict(l=60, r=30, t=55, b=50),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(size=11)),
)

def plot_price_chart(hist: pd.DataFrame, ticker: str, ma_periods: list):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist['Close'], mode='lines', name='Fechamento',
        line=dict(color='#E80070', width=2.5),
        fill='tozeroy', fillcolor='rgba(232,0,112,0.05)'
    ))
    colors_ma = ['#FF1A8C', '#f59e0b', '#3b82f6']
    for i, p in enumerate(ma_periods):
        col = f'MA_{p}'
        if col in hist.columns:
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist[col], mode='lines', name=f'MA {p}d',
                line=dict(color=colors_ma[i % 3], width=1.5, dash='dash')
            ))
    fig.update_layout(title=dict(text=f"{ticker} — Evolução do Preço de Fechamento",
                                  font=dict(size=16, color="#f1f5f9"), x=0.01),
                      height=420, **CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

def plot_candlestick(hist: pd.DataFrame, ticker: str):
    fig = go.Figure(data=[go.Candlestick(
        x=hist.index, open=hist['Open'], high=hist['High'],
        low=hist['Low'], close=hist['Close'], name=ticker,
        increasing_line_color='#10b981', decreasing_line_color='#ef4444',
        increasing_fillcolor='rgba(16,185,129,0.7)',
        decreasing_fillcolor='rgba(239,68,68,0.7)'
    )])
    fig.update_layout(
        title=dict(text=f"{ticker} — Candlestick", font=dict(size=15, color="#f1f5f9"), x=0.01),
        xaxis_rangeslider_visible=False, height=400, **CHART_LAYOUT
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_moving_averages(hist: pd.DataFrame, ticker: str):
    h = hist.copy()
    h['SMA_20'] = h['Close'].rolling(20).mean()
    h['EMA_20'] = h['Close'].ewm(span=20, adjust=False).mean()
    fig = go.Figure()
    traces = [
        ('Close',  '#E80070', 'solid',  'Fechamento', 2.5),
        ('SMA_20', '#94a3b8', 'dash',   'SMA 20',     1.5),
        ('EMA_20', '#10b981', 'dot',    'EMA 20',     1.5),
    ]
    for col, color, dash, name, width in traces:
        fig.add_trace(go.Scatter(
            x=h.index, y=h[col], mode='lines', name=name,
            line=dict(color=color, width=width, dash=dash)
        ))
    fig.update_layout(
        title=dict(text=f"{ticker} — Médias Móveis", font=dict(size=15, color="#f1f5f9"), x=0.01),
        height=400, **CHART_LAYOUT
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_volume(hist: pd.DataFrame, ticker: str):
    colors = ['#10b981' if c >= o else '#ef4444'
              for c, o in zip(hist['Close'], hist['Open'])]
    fig = go.Figure(data=[go.Bar(
        x=hist.index, y=hist['Volume'],
        marker_color=colors, opacity=0.85, name='Volume'
    )])
    fig.update_layout(
        title=dict(text=f"{ticker} — Volume de Negociação", font=dict(size=15, color="#f1f5f9"), x=0.01),
        height=320, **CHART_LAYOUT
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_rsi(hist: pd.DataFrame, ticker: str):
    close = hist['Close']
    delta = close.diff()
    gain  = delta.where(delta > 0, 0).rolling(14).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi   = 100 - (100 / (1 + gain / loss))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=rsi, mode='lines', name='RSI',
                             line=dict(color='#f59e0b', width=2)))
    fig.add_hline(y=70, line=dict(color='#ef4444', dash='dash', width=1),
                  annotation_text='Sobrecomprado (70)', annotation_font_color='#ef4444')
    fig.add_hline(y=30, line=dict(color='#10b981', dash='dash', width=1),
                  annotation_text='Sobrevendido (30)', annotation_font_color='#10b981')
    fig.add_hrect(y0=30, y1=70, fillcolor='rgba(255,255,255,0.02)', line_width=0)
    fig.update_layout(
        title=dict(text=f"{ticker} — RSI (14)", font=dict(size=15, color="#f1f5f9"), x=0.01),
        yaxis=dict(range=[0, 100], **CHART_LAYOUT['yaxis']),
        height=280, **{k: v for k, v in CHART_LAYOUT.items() if k != 'yaxis'}
    )
    st.plotly_chart(fig, use_container_width=True)

# ─── Session state ────────────────────────────────────────────────────────────
for key, val in [('analysis_done', False), ('ticker_input', '')]:
    if key not in st.session_state:
        st.session_state[key] = val

# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.markdown(f"""
<div style="padding:1rem 0 0.5rem 0">
  <div style="font-size:1.5rem;font-weight:900;color:#E80070;letter-spacing:-0.03em">📊 DSA Analytics</div>
  <div style="font-size:0.8rem;color:#64748b;margin-top:4px">Day Trade · NASDAQ · Powered by Databricks</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Quick-select popular tickers
SECTORS = {
    "🖥️ Tecnologia": {"Apple": "AAPL", "Microsoft": "MSFT", "NVIDIA": "NVDA",
                       "Google": "GOOGL", "Meta": "META", "Tesla": "TSLA",
                       "AMD": "AMD", "Intel": "INTC", "Salesforce": "CRM"},
    "🏦 Finanças":   {"JPMorgan": "JPM", "Bank of America": "BAC", "Goldman Sachs": "GS",
                       "Visa": "V", "Mastercard": "MA"},
    "🛒 Consumo":    {"Amazon": "AMZN", "Walmart": "WMT", "Home Depot": "HD",
                       "Nike": "NKE", "Starbucks": "SBUX"},
    "💊 Saúde":      {"Johnson & Johnson": "JNJ", "Pfizer": "PFE", "UnitedHealth": "UNH",
                       "Eli Lilly": "LLY"},
}

st.sidebar.markdown("**Selecione rapidamente:**")
sector = st.sidebar.selectbox("Setor:", list(SECTORS.keys()))
company = st.sidebar.selectbox("Empresa:", list(SECTORS[sector].keys()))
quick_ticker = SECTORS[sector][company]

st.sidebar.markdown("**Ou digite o ticker:**")
manual_ticker = st.sidebar.text_input("Ticker (ex: TSLA, AAPL):", value="").upper().strip()

final_ticker = manual_ticker if manual_ticker else quick_ticker

PERIODS = {"5 Dias": "5d", "1 Mês": "1mo", "3 Meses": "3mo",
           "6 Meses": "6mo", "1 Ano": "1y", "2 Anos": "2y", "5 Anos": "5y"}
selected_period_label = st.sidebar.selectbox("Período:", list(PERIODS.keys()), index=4)
period = PERIODS[selected_period_label]

st.sidebar.markdown("---")
st.sidebar.markdown("**Opções de visualização:**")
show_ma         = st.sidebar.checkbox("Médias Móveis", value=True)
ma_choices      = st.sidebar.multiselect("Períodos MA:", ["20", "50", "200"], default=["20", "50"])
show_candlestick = st.sidebar.checkbox("Candlestick", value=True)
show_volume     = st.sidebar.checkbox("Volume", value=True)
show_rsi        = st.sidebar.checkbox("RSI", value=True)
show_ai         = st.sidebar.checkbox("Análise por IA (Databricks)", value=True)

st.sidebar.markdown("---")
analyze_btn = st.sidebar.button("🔍 Analisar", use_container_width=True, type="primary")
if analyze_btn:
    st.session_state.analysis_done = True

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="font-size:0.75rem;color:#475569;line-height:1.6">
  <div style="font-weight:700;color:#64748b;margin-bottom:4px">POWERED BY</div>
  🤖 <b>Databricks Model Serving</b><br>
  📈 <b>Yahoo Finance API</b> (dados reais)<br>
  🔒 LGPD Compliant<br>
  <div style="margin-top:8px;font-size:0.7rem">Dados atualizados a cada 5 min</div>
</div>
""", unsafe_allow_html=True)

# ─── Hero (landing) ───────────────────────────────────────────────────────────
if not st.session_state.analysis_done:
    st.markdown("""
<div style="background:linear-gradient(135deg,#E80070 0%,#7c1d4e 60%,#0f172a 100%);
     border-radius:20px;padding:4rem 3rem;margin-bottom:2.5rem;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;right:0;width:50%;height:100%;
       background:url('https://www.serasaexperian.com.br/wp-content/themes/serasa-experian/assets/images/bg-hero.webp')
       no-repeat center/cover;opacity:0.07"></div>
  <div style="position:relative;z-index:2;max-width:640px">
    <div style="display:inline-block;background:rgba(255,255,255,0.12);backdrop-filter:blur(8px);
         padding:6px 16px;border-radius:99px;font-size:0.8rem;color:white;font-weight:600;
         border:1px solid rgba(255,255,255,0.2);margin-bottom:1.5rem">
      ✦ NASDAQ Day Trade Analytics — Powered by Databricks
    </div>
    <h1 style="font-size:3.25rem;font-weight:900;color:white;margin:0 0 1rem;
         line-height:1.05;letter-spacing:-0.035em">
      Inteligência de Mercado<br>em Tempo Real
    </h1>
    <p style="font-size:1.1rem;color:rgba(255,255,255,0.85);margin:0;line-height:1.7;max-width:480px">
      Análise técnica avançada com Agentes de IA na Databricks. RSI, Candlestick,
      Médias Móveis e insights gerados por LLM — tudo em um único dashboard.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

    # Feature cards
    cols = st.columns(3)
    feats = [
        ("📡", "Dados Reais",        "Yahoo Finance API — preços ao vivo, sem simulação."),
        ("🤖", "IA Databricks",      "LLM Meta-Llama 3.3 70B via Model Serving para análise técnica."),
        ("📊", "Análise Completa",   "RSI, Candlestick, Médias Móveis, Volume e indicadores chave."),
    ]
    for col, (icon, title, desc) in zip(cols, feats):
        with col:
            st.markdown(f"""
<div style="background:linear-gradient(160deg,#1e293b,#263347);border:1px solid rgba(255,255,255,0.07);
     border-radius:16px;padding:2rem;height:100%;transition:all 0.3s">
  <div style="font-size:2.5rem;margin-bottom:1rem">{icon}</div>
  <div style="font-weight:700;font-size:1rem;color:#f1f5f9;margin-bottom:0.5rem">{title}</div>
  <div style="font-size:0.875rem;color:#64748b;line-height:1.6">{desc}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<div style="text-align:center;background:#1e293b;border:1px dashed rgba(232,0,112,0.3);
     border-radius:16px;padding:2.5rem;color:#E80070;font-size:1.1rem;font-weight:600">
  👈 Selecione uma empresa no painel lateral e clique em <b>🔍 Analisar</b>
</div>""", unsafe_allow_html=True)
    st.stop()

# ─── Analysis section ─────────────────────────────────────────────────────────
if not final_ticker:
    st.error("❌ Insira um ticker válido no painel lateral.")
    st.stop()

with st.spinner(f"Carregando dados reais para **{final_ticker}** via Yahoo Finance..."):
    stock_data = load_stock_data(final_ticker, period)

if stock_data is None:
    st.error(f"""
**❌ Não foi possível carregar dados para `{final_ticker}`.**

Possíveis causas:
- Ticker inválido (verifique em [stockanalysis.com](https://stockanalysis.com/list/nasdaq-stocks/))
- Restrição de rede no ambiente Databricks Apps (Yahoo Finance pode estar bloqueado)
- Período inválido para este ativo

**Solução:** Verifique o ticker e tente novamente, ou contate o administrador da app.
""")
    st.stop()

ticker_info = load_ticker_info(final_ticker)

# ─── Compute key metrics ──────────────────────────────────────────────────────
close       = stock_data['Close']
current     = float(close.iloc[-1])
prev        = float(close.iloc[-2]) if len(close) > 1 else current
day_chg     = current - prev
day_chg_pct = (day_chg / prev) * 100 if prev != 0 else 0
period_chg  = float((close.iloc[-1] / close.iloc[0] - 1) * 100)
hi52        = float(stock_data['High'].max())
lo52        = float(stock_data['Low'].min())
avg_vol     = float(stock_data['Volume'].mean())
volatility  = float(close.pct_change().std() * np.sqrt(252) * 100)
rsi_now     = _calc_rsi(close)

company_name = ticker_info.get('longName') or ticker_info.get('shortName') or final_ticker
currency     = ticker_info.get('currency', 'USD')
mktcap       = ticker_info.get('marketCap', 0)
sector_info  = ticker_info.get('sector', '')
exchange     = ticker_info.get('exchange', 'NASDAQ')

# ─── Stock header ─────────────────────────────────────────────────────────────
chg_color  = "#10b981" if day_chg >= 0 else "#ef4444"
chg_icon   = "▲" if day_chg >= 0 else "▼"
rsi_color  = "#ef4444" if rsi_now > 70 else "#10b981" if rsi_now < 30 else "#f59e0b"
rsi_label  = "Sobrecomprado" if rsi_now > 70 else "Sobrevendido" if rsi_now < 30 else "Neutro"

st.markdown(f"""
<div style="background:linear-gradient(135deg,#1e293b,#263347);border:1px solid rgba(255,255,255,0.08);
     border-radius:20px;padding:2rem 2.5rem;margin-bottom:1.5rem;display:flex;
     justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem">
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px">
      <span style="font-size:1.9rem;font-weight:900;color:#f1f5f9">{final_ticker}</span>
      <span style="background:#E8007022;color:#E80070;font-size:0.7rem;font-weight:800;
           padding:4px 12px;border-radius:99px;border:1px solid #E8007044;letter-spacing:0.08em">{exchange}</span>
      {"<span style='background:#26478d22;color:#60a5fa;font-size:0.7rem;font-weight:700;padding:4px 12px;border-radius:99px;border:1px solid #3b82f644'>" + sector_info + "</span>" if sector_info else ""}
    </div>
    <div style="font-size:1rem;color:#64748b;font-weight:500">{company_name}</div>
    {"<div style='font-size:0.8rem;color:#475569;margin-top:4px'>Market Cap: " + fmt_num(mktcap) + "</div>" if mktcap else ""}
  </div>
  <div style="text-align:right">
    <div style="font-size:2.75rem;font-weight:900;color:#f1f5f9;letter-spacing:-0.03em;font-variant-numeric:tabular-nums">
      {currency} {current:,.2f}
    </div>
    <div style="font-size:1.1rem;font-weight:700;color:{chg_color};margin-top:4px">
      {chg_icon} {abs(day_chg):.2f} ({day_chg_pct:+.2f}%) hoje &nbsp;|&nbsp;
      <span style="font-size:0.95rem">{period_chg:+.2f}% no período</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI metrics row ───────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
kpis = [
    (c1, "Preço Atual",     f"${current:,.2f}",         f"{day_chg_pct:+.2f}%"),
    (c2, "Máxima Período",  f"${hi52:,.2f}",            None),
    (c3, "Mínima Período",  f"${lo52:,.2f}",            None),
    (c4, "Volume Médio",    f"{avg_vol/1e6:.1f}M",      None),
    (c5, "Volatilidade",    f"{volatility:.1f}%",       "anualizada"),
    (c6, f"RSI(14) — {rsi_label}", f"{rsi_now:.1f}",   None),
]
for col, label, val, delta in kpis:
    with col:
        if delta:
            st.metric(label, val, delta)
        else:
            st.metric(label, val)

st.markdown("---")

# ─── Prepare chart data (add MAs) ─────────────────────────────────────────────
chart_data = stock_data.copy()
if show_ma:
    for p in ma_choices:
        chart_data[f'MA_{p}'] = chart_data['Close'].rolling(int(p)).mean()

# ─── Price chart ──────────────────────────────────────────────────────────────
st.markdown("### 📈 Preço de Fechamento")
plot_price_chart(chart_data, final_ticker, ma_choices if show_ma else [])

# ─── Candlestick + moving averages side by side ───────────────────────────────
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

# ─── Volume + RSI side by side ────────────────────────────────────────────────
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

# ─── Technical analysis summary table ────────────────────────────────────────
st.markdown("### 🔬 Análise Técnica — Indicadores")
col_left, col_right = st.columns(2)

with col_left:
    sma20_val = float(chart_data['Close'].rolling(20).mean().iloc[-1])
    sma50_val = float(chart_data['Close'].rolling(50).mean().iloc[-1]) if len(chart_data) >= 50 else None
    ema20_val = float(chart_data['Close'].ewm(span=20, adjust=False).mean().iloc[-1])
    macd_line = float(chart_data['Close'].ewm(span=12).mean().iloc[-1] -
                      chart_data['Close'].ewm(span=26).mean().iloc[-1])
    support   = float(stock_data['Low'].rolling(20).min().iloc[-1])
    resist    = float(stock_data['High'].rolling(20).max().iloc[-1])

    indicators = {
        "Indicador": ["SMA 20", "SMA 50", "EMA 20", "MACD (12,26)", "Suporte (20d)", "Resistência (20d)", "RSI (14)"],
        "Valor": [
            f"${sma20_val:.2f}", f"${sma50_val:.2f}" if sma50_val else "—",
            f"${ema20_val:.2f}", f"{macd_line:+.4f}",
            f"${support:.2f}", f"${resist:.2f}", f"{rsi_now:.1f}"
        ],
        "Sinal": [
            "🟢 Alta" if current > sma20_val else "🔴 Baixa",
            ("🟢 Alta" if current > sma50_val else "🔴 Baixa") if sma50_val else "—",
            "🟢 Alta" if current > ema20_val else "🔴 Baixa",
            "🟢 Positivo" if macd_line > 0 else "🔴 Negativo",
            f"{'🟢' if current > support * 1.02 else '🟡'} ${support:.2f}",
            f"{'🔴' if current > resist * 0.98 else '🟡'} ${resist:.2f}",
            rsi_label
        ]
    }
    df_ind = pd.DataFrame(indicators)
    st.dataframe(df_ind, use_container_width=True, hide_index=True)

with col_right:
    stats = {
        "Estatística": ["Preço Médio", "Mediana", "Desvio Padrão", "Mínimo", "Máximo",
                        "Skewness", "Volume Total", "Variação % Total"],
        "Valor": [
            f"${close.mean():.2f}", f"${close.median():.2f}",
            f"${close.std():.2f}", f"${close.min():.2f}", f"${close.max():.2f}",
            f"{float(close.skew()):.3f}", fmt_num(float(stock_data['Volume'].sum())),
            f"{period_chg:+.2f}%"
        ]
    }
    df_stats = pd.DataFrame(stats)
    st.dataframe(df_stats, use_container_width=True, hide_index=True)

st.markdown("---")

# ─── Historical data table ────────────────────────────────────────────────────
st.markdown("### 📋 Dados Históricos — Últimos 30 Pregões")

disp = stock_data.tail(30).copy()
# Format index as date string
disp.index = pd.to_datetime(disp.index).strftime('%d/%m/%Y')
disp = disp[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
disp.index.name = 'Data'
disp = disp.reset_index()

# Compute daily change for color coding
disp['Var. Dia %'] = ((disp['Close'] - disp['Open']) / disp['Open'] * 100).round(2)

# Sort most recent first
disp = disp.iloc[::-1].reset_index(drop=True)

st.dataframe(
    disp,
    use_container_width=True,
    height=480,
    hide_index=True,
    column_config={
        "Data":     st.column_config.TextColumn("📅 Data", width="small"),
        "Open":     st.column_config.NumberColumn("Abertura ($)", format="$%.2f"),
        "High":     st.column_config.NumberColumn("Máxima ($)",  format="$%.2f"),
        "Low":      st.column_config.NumberColumn("Mínima ($)",  format="$%.2f"),
        "Close":    st.column_config.NumberColumn("Fechamento ($)", format="$%.2f"),
        "Volume":   st.column_config.NumberColumn("Volume", format="%,d"),
        "Var. Dia %": st.column_config.NumberColumn("Var. Dia %", format="%.2f%%"),
    }
)

st.markdown("---")

# ─── Databricks AI Analysis ───────────────────────────────────────────────────
if show_ai:
    st.markdown("### 🤖 Análise por IA — Databricks Model Serving")
    st.markdown(f"""
<div style="background:#1e293b;border-left:4px solid #E80070;border-radius:8px;
     padding:0.75rem 1rem;margin-bottom:1rem;font-size:0.8rem;color:#64748b">
  Modelo: <b style="color:#E80070">{MODEL_ENDPOINT}</b> &nbsp;|&nbsp;
  Ativo: <b>{final_ticker}</b> &nbsp;|&nbsp;
  Período: <b>{selected_period_label}</b>
</div>""", unsafe_allow_html=True)

    with st.spinner("Consultando Agente de IA na Databricks..."):
        ai_text = databricks_ai_analysis(final_ticker, stock_data)

    st.markdown(f"""
<div style="background:#1e293b;border:1px solid rgba(232,0,112,0.2);border-radius:16px;padding:2rem">
{ai_text}
</div>""", unsafe_allow_html=True)

# ─── Auto-generated insights ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 💡 Insights Automáticos")

sma20_ins = float(close.rolling(20).mean().iloc[-1])
sma50_ins = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else sma20_ins
insights  = []

if sma20_ins > sma50_ins:
    insights.append(("🟢", "Tendência de Alta", "MA20 acima da MA50 — momentum positivo.", "#10b981"))
else:
    insights.append(("🔴", "Tendência de Baixa", "MA20 abaixo da MA50 — pressão vendedora.", "#ef4444"))

if rsi_now > 70:
    insights.append(("⚠️", "RSI Sobrecomprado", f"RSI={rsi_now:.1f} acima de 70 — possível correção.", "#f59e0b"))
elif rsi_now < 30:
    insights.append(("✅", "RSI Sobrevendido", f"RSI={rsi_now:.1f} abaixo de 30 — possível rebote.", "#3b82f6"))

if volatility > 40:
    insights.append(("⚡", "Alta Volatilidade", f"{volatility:.1f}% a.a. — risco elevado, position sizing essencial.", "#ef4444"))
elif volatility < 15:
    insights.append(("😴", "Baixa Volatilidade", f"{volatility:.1f}% a.a. — ativo estável, spreads menores.", "#64748b"))

near_hi = current >= hi52 * 0.97
near_lo = current <= lo52 * 1.03
if near_hi:
    insights.append(("🔺", "Próximo da Máxima", f"Preço a {(hi52-current)/hi52*100:.1f}% da máxima do período.", "#E80070"))
if near_lo:
    insights.append(("🔻", "Próximo da Mínima", f"Preço a {(current-lo52)/lo52*100:.1f}% acima da mínima.", "#ef4444"))

cols_ins = st.columns(min(len(insights), 3))
for i, (icon, title, desc, color) in enumerate(insights):
    with cols_ins[i % 3]:
        st.markdown(f"""
<div style="background:#1e293b;border:1px solid {color}33;border-left:4px solid {color};
     border-radius:12px;padding:1.25rem;margin-bottom:1rem">
  <div style="font-size:1.5rem;margin-bottom:0.5rem">{icon}</div>
  <div style="font-weight:700;color:{color};font-size:0.9rem;margin-bottom:0.35rem">{title}</div>
  <div style="font-size:0.8rem;color:#94a3b8;line-height:1.5">{desc}</div>
</div>""", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center;padding:1.5rem;color:#334155;font-size:0.78rem">
  <strong style="color:#475569">NASDAQ Day Trade Analytics</strong> — Data Science Academy &nbsp;|&nbsp;
  Dados: Yahoo Finance &nbsp;|&nbsp; IA: Databricks Model Serving &nbsp;|&nbsp;
  <span>⚠️ Não constitui recomendação de investimento</span>
</div>
""", unsafe_allow_html=True)
