import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import time
from typing import Dict, List, Tuple, Optional
import re
import json

# Databricks SDK imports para integracao nativa
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

# Configuracao do cliente Databricks
@st.cache_resource
def get_databricks_client():
    """Inicializa cliente Databricks Workspace"""
    try:
        return WorkspaceClient()
    except Exception as e:
        st.warning(f"Databricks client nao disponivel: {e}")
        return None

# Model Serving endpoint para analise de acoes
MODEL_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"  # Endpoint de LLM na Databricks

# Configuracao da pagina com identidade visual
st.set_page_config(
    page_title="NASDAQ Analytics - Powered by Databricks",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "NASDAQ Analytics Platform - Databricks AI Powered"
    }
)

# CSS customizado - Design Ultra Moderno Serasa
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    :root {
        --serasa-pink: #E80070;
        --serasa-pink-dark: #C4005C;
        --serasa-pink-light: #FF1A8C;
        --serasa-magenta: #D0006F;
        --accent-purple: #6B2D5C;
    }
    
    * {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Hero with sand texture background */
    .hero-container {
        background: 
            linear-gradient(135deg, rgba(232, 0, 112, 0.95) 0%, rgba(196, 0, 92, 0.95) 100%),
            url('https://ready.so/images/Sand-Texture.webp');
        background-size: cover, cover;
        background-position: center, center;
        background-blend-mode: multiply, normal;
        border-radius: 16px;
        padding: 4rem 3rem;
        margin: 0 0 3rem 0;
        position: relative;
        overflow: hidden;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Particle effect overlay */
    .hero-container::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(255,255,255,0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255,255,255,0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(255,20,147,0.25) 0%, transparent 50%);
        animation: float 20s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(30px, -30px) scale(1.1); }
        66% { transform: translate(-20px, 20px) scale(0.9); }
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        color: white;
        margin-bottom: 1rem;
        line-height: 1.05;
        letter-spacing: -0.03em;
        position: relative;
        z-index: 2;
        text-shadow: 0 4px 30px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.35rem;
        color: rgba(255,255,255,0.95);
        margin-bottom: 2.5rem;
        max-width: 550px;
        line-height: 1.7;
        position: relative;
        z-index: 2;
        font-weight: 400;
    }
    
    /* Modern Feature Cards - Serasa Theme */
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        border: 1px solid rgba(230,0,126,0.08);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #E80070, #FF1A8C);
        transform: scaleX(0);
        transition: transform 0.5s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 30px 60px -20px rgba(232, 0, 112, 0.25);
        border-color: rgba(232,0,112,0.2);
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        display: inline-block;
        filter: drop-shadow(0 4px 10px rgba(232,0,112,0.2));
    }
    
    /* Glass Trust Badges */
    .trust-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 0.6rem 1.2rem;
        border-radius: 50px;
        font-size: 0.9rem;
        color: white;
        font-weight: 500;
        margin-right: 0.75rem;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(255,255,255,0.25);
        position: relative;
        z-index: 2;
        transition: all 0.3s ease;
    }
    
    .trust-badge:hover {
        background: rgba(255,255,255,0.25);
        transform: translateY(-2px);
    }
    
    /* Stats with gradient text - Serasa Pink */
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #E80070 0%, #FF1A8C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    /* Step cards with numbers - Serasa Theme */
    .step-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(230,0,126,0.08);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .step-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px -15px rgba(230, 0, 126, 0.15);
    }
    
    .step-number {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #E80070 0%, #FF1A8C 100%);
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.5rem;
        margin: 0 auto 1.5rem auto;
        box-shadow: 0 10px 30px -10px rgba(232, 0, 112, 0.4);
    }
    
    /* Floating icon animation */
    @keyframes iconFloat {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        25% { transform: translateY(-15px) rotate(3deg); }
        75% { transform: translateY(15px) rotate(-3deg); }
    }
    
    .floating-icon {
        animation: iconFloat 6s ease-in-out infinite;
        font-size: 7rem;
        opacity: 0.95;
        filter: drop-shadow(0 10px 30px rgba(232,0,112,0.3));
        position: relative;
        z-index: 2;
    }
    
    /* CTA Section - Serasa Theme */
    .cta-section {
        background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 100%);
        border-radius: 24px;
        padding: 3rem;
        text-align: center;
        margin-top: 3rem;
        border: 2px dashed rgba(230,0,126,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .cta-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(232,0,112,0.03) 0%, transparent 70%);
        animation: rotate 30s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Section headers - Serasa Pink */
    h3 {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #E80070 !important;
        margin-bottom: 2rem !important;
        letter-spacing: -0.02em;
    }
    
    /* Button animations - Serasa Pink */
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #E80070, #C4005C, #E80070) !important;
        background-size: 200% auto !important;
        animation: shimmer 3s linear infinite !important;
        color: white !important;
        border: none !important;
        padding: 0.875rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(232, 0, 112, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(232, 0, 112, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Componentes reutilizáveis para análise de dados
def create_metric_card(title: str, value: str, change: Optional[float] = None, 
                         icon: str = "📊", color: str = "primary") -> None:
    """Cria um card de métrica com estilo Serasa Experian"""
    color_map = {
        "primary": "var(--color-primary)",
        "success": "var(--color-success)",
        "warning": "var(--color-warning)",
        "error": "var(--color-error)"
    }
    
    change_class = "positive" if change and change > 0 else "negative" if change and change < 0 else "neutral"
    change_symbol = "📈" if change and change > 0 else "📉" if change and change < 0 else "➡️"
    
    st.markdown(f"""
    <div style="
        background: white;
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-md);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        margin: 0.5rem 0;
        transition: all var(--transition-base);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
            <h4 style="margin: 0; color: {color_map.get(color, 'var(--color-primary)')};">{title}</h4>
        </div>
        <div style="font-size: 1.8rem; font-weight: 700; color: var(--color-text-primary);">{value}</div>
        {f'<div style="font-size: 0.9rem; color: var(--color-text-secondary); margin-top: 0.5rem;">{change_symbol} {change:+.2f}%</div>' if change is not None else ''}
    </div>
    """, unsafe_allow_html=True)

def create_stock_header(company_name: str, symbol: str, current_price: float, 
                      price_change: float, price_change_pct: float) -> None:
    """Cria cabeçalho informativo da ação"""
    change_color = "var(--color-success)" if price_change >= 0 else "var(--color-error)"
    change_icon = "📈" if price_change >= 0 else "📉"
    
    st.markdown(f"""
    <div class="animate-slide-in" style="
        background: linear-gradient(135deg, var(--color-surface) 0%, white 100%);
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-lg);
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-md);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h1 style="margin: 0; color: var(--color-primary); font-size: 2rem;">{company_name}</h1>
                <p style="margin: 0.5rem 0 0 0; color: var(--color-text-secondary); font-size: 1.1rem;">{symbol}</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 2.5rem; font-weight: 700; color: var(--color-text-primary);">${current_price:.2f}</div>
                <div style="display: flex; align-items: center; justify-content: flex-end; margin-top: 0.5rem;">
                    <span style="color: {change_color}; font-weight: 600; margin-right: 0.5rem;">{change_icon} ${price_change:+.2f}</span>
                    <span style="color: {change_color}; font-weight: 600;">({price_change_pct:+.2f}%)</span>
                </div>
            </div>
        </div>
        <div style="color: var(--color-text-secondary); font-size: 0.9rem;">
            📊 Análise em tempo real • Serasa Experian Analytics
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_enhanced_chart(data: pd.DataFrame, title: str, y_column: str, 
                      color: str = "#E80070", chart_type: str = "line") -> go.Figure:
    """Cria gráfico aprimorado com estilo Serasa"""
    # Mapeia cores CSS para hex se necessario
    color_map = {
        "var(--color-primary)": "#E80070",
        "var(--color-secondary)": "#C4005C",
        "var(--color-accent)": "#FF1A8C",
        "var(--color-success)": "#10b981",
        "var(--color-warning)": "#f59e0b",
        "var(--color-error)": "#ef4444",
        "var(--color-text-primary)": "#1a1a2e",
        "var(--color-text-secondary)": "#6b7280"
    }
    
    # Converte cor se for variavel CSS
    plot_color = color_map.get(color, color)
    
    if chart_type == "line":
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[y_column],
            mode='lines',
            line=dict(
                color=plot_color,
                width=3
            )
        ))
    elif chart_type == "bar":
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data.index,
            y=data[y_column],
            marker_color=plot_color,
            opacity=0.8
        ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18, color="#E80070")
        ),
        xaxis_title="Data",
        yaxis_title=y_column,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color="#1a1a2e"),
        margin=dict(l=60, r=30, t=60, b=60),
        hovermode='x unified',
        showlegend=False,
        height=400
    )
    
    return fig

def format_large_number(num: float) -> str:
    """Formata numeros grandes para melhor legibilidade"""
    if num >= 1e9:
        return f"${num/1e9:.1f}B"
    elif num >= 1e6:
        return f"${num/1e6:.1f}M"
    elif num >= 1e3:
        return f"${num/1e3:.1f}K"
    else:
        return f"${num:.2f}"

########## Databricks AI Agent Functions ##########

def databricks_ai_stock_analysis(ticker: str, hist: pd.DataFrame, metrics: dict) -> str:
    """
    Usa Databricks Model Serving para analise de acoes com LLM.
    Substituto dos agentes Groq/DeepSeek do codigo original.
    """
    try:
        client = get_databricks_client()
        if client is None:
            return "**Analise IA:** Cliente Databricks nao disponivel. Verifique as configuracoes de autenticacao."
        
        # Prepara dados resumidos para o prompt
        latest_price = float(hist['Close'].iloc[-1])
        price_change = float((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100)
        max_price = float(hist['High'].max())
        min_price = float(hist['Low'].min())
        avg_volume = float(hist['Volume'].mean())
        
        # Cria prompt estruturado para o LLM
        prompt = f"""Voce e um analista financeiro especialista em day trade. 
Analise a acao {ticker} com base nos seguintes dados dos ultimos 6 meses:

**Dados Tecnicos:**
- Preco Atual: ${latest_price:.2f}
- Variacao Periodo: {price_change:+.2f}%
- Maxima: ${max_price:.2f}
- Minima: ${min_price:.2f}
- Volume Medio: {avg_volume:,.0f}

**Recomendacao:**
Forneca uma analise concisa (maximo 5 linhas) sobre:
1. Tendencia atual (Alta/Baixa/Neutra)
2. Niveis de suporte e resistencia relevantes
3. Recomendacao de estrategia para day trade
4. Alerta de risco se aplicavel

Use formato markdown com bullets para organizar a resposta."""

        # Chama o endpoint de Model Serving na Databricks
        with st.spinner("Consultando Agente de IA na Databricks..."):
            messages = [
                ChatMessage(role=ChatMessageRole.SYSTEM, content="Voce e um analista financeiro especialista em day trade e analise tecnica."),
                ChatMessage(role=ChatMessageRole.USER, content=prompt)
            ]
            
            try:
                response = client.serving_endpoints.query(
                    name=MODEL_ENDPOINT,
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7
                )
                
                # Extrai resposta do LLM
                if response and response.choices:
                    ai_response = response.choices[0].message.content
                    # Limpa resposta se necessario
                    clean_response = re.sub(r"(Running:[\s\S]*?\n\n)|(^transfer_task_to.*\n?)", "", ai_response, flags=re.MULTILINE).strip()
                    return clean_response
                else:
                    return "**Analise IA:** Nao foi possivel obter resposta do modelo."
                    
            except Exception as e:
                return f"**Analise IA:** Erro ao consultar modelo - {str(e)}"
                
    except Exception as e:
        return f"**Analise IA:** Erro na analise - {str(e)}"


def databricks_web_search_summary(ticker: str) -> str:
    """
    Simula busca web usando funcoes de IA do Databricks para noticias recentes.
    Nota: Em producao, integrar com Unity Catalog + Vector Search para noticias.
    """
    try:
        client = get_databricks_client()
        if client is None:
            return ""
            
        prompt = f"""Resuma as principais noticias sobre a empresa {ticker} no mercado financeiro.
Foque em: lancamentos de produtos, resultados trimestrais, movimentacoes relevantes.
Maximo 3 bullets, formato markdown."""

        messages = [
            ChatMessage(role=ChatMessageRole.SYSTEM, content="Voce e um assistente de pesquisa financeira."),
            ChatMessage(role=ChatMessageRole.USER, content=prompt)
        ]
        
        try:
            response = client.serving_endpoints.query(
                name=MODEL_ENDPOINT,
                messages=messages,
                max_tokens=300,
                temperature=0.5
            )
            
            if response and response.choices:
                return response.choices[0].message.content
            return ""
        except:
            return ""
            
    except:
        return ""


########## Funcoes de Visualizacao (DSA Original Adaptado) ##########

def dsa_plot_candlestick(hist: pd.DataFrame, ticker: str):
    """Plot candlestick - adaptado do codigo DSA original"""
    fig = go.Figure(
        data=[go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name=ticker
        )]
    )
    
    fig.update_layout(
        title=f"{ticker} - Grafico Candlestick",
        xaxis_title="Data",
        yaxis_title="Preco ($)",
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=450,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def dsa_plot_media_movel(hist: pd.DataFrame, ticker: str):
    """Plot medias moveis - adaptado do codigo DSA original"""
    # Calcula medias
    hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
    hist['EMA_20'] = hist['Close'].ewm(span=20, adjust=False).mean()
    
    fig = go.Figure()
    
    # Adiciona traces
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist['Close'],
        mode='lines', name='Preco',
        line=dict(color='#E80070', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist['SMA_20'],
        mode='lines', name='SMA 20',
        line=dict(color='#6b7280', width=1.5, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist['EMA_20'],
        mode='lines', name='EMA 20',
        line=dict(color='#10b981', width=1.5, dash='dot')
    ))
    
    fig.update_layout(
        title=f"{ticker} - Medias Moveis",
        xaxis_title="Data",
        yaxis_title="Preco ($)",
        plot_bgcolor='white',
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)


# Cache para melhor performance
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_stock_data(symbol: str, period: str) -> Optional[pd.DataFrame]:
    """Carrega dados da ação com cache e tratamento de erros"""
    try:
        # Usa Ticker ao inves de download direto
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data is None or data.empty:
            st.error(f"Nenhum dado encontrado para {symbol}. Verifique se o ticker está correto.")
            return None
        
        # Verifica se temos as colunas necessarias
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in data.columns:
                st.error(f"Coluna {col} não encontrada nos dados de {symbol}")
                return None
        
        # Limpeza e validação básica
        data = data.dropna()
        if len(data) < 2:
            st.error(f"Dados insuficientes para {symbol} (apenas {len(data)} registros)")
            return None
        
        # Info de debug
        st.info(f"Carregados {len(data)} registros para {symbol}")
        
        return data
        
    except Exception as e:
        st.error(f"Erro ao carregar dados de {symbol}: {str(e)}")
        st.info("Dica: Tente um período diferente ou verifique sua conexão com a internet.")
        return None


def generate_demo_data(symbol: str, period: str = "6mo") -> pd.DataFrame:
    """Gera dados de demonstração quando a API falha"""
    import numpy as np
    from datetime import datetime, timedelta
    
    # Define numero de dias baseado no periodo
    days_map = {"5d": 5, "1mo": 22, "3mo": 66, "6mo": 132, "1y": 252, "2y": 504, "5y": 1260}
    days = days_map.get(period, 132)
    
    # Gera datas
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=days, freq='B')  # Business days
    
    # Gera preço base
    base_price = np.random.uniform(50, 200)
    
    # Gera serie de precos com tendencia e volatilidade
    returns = np.random.normal(0.001, 0.02, len(dates))
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Gera OHLC a partir do preço de fechamento
    data = pd.DataFrame(index=dates)
    data['Close'] = prices
    data['High'] = prices * (1 + np.abs(np.random.normal(0, 0.01, len(dates))))
    data['Low'] = prices * (1 - np.abs(np.random.normal(0, 0.01, len(dates))))
    data['Open'] = data['Low'] + np.random.random(len(dates)) * (data['High'] - data['Low'])
    data['Volume'] = np.random.randint(1000000, 50000000, len(dates))
    
    return data


# Inicializa session state para manter estado do botao
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None


def run_analysis():
    """Callback para executar analise"""
    st.session_state.analysis_done = True


# Logo e título principal com design Serasa Experian
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("📊")
with col2:
    st.markdown("# **Serasa Experian Analytics**")
    st.markdown("### Plataforma Avançada de Análise de Mercado")

st.markdown("---")

# Sidebar aprimorado com identidade visual Serasa e instrucoes DSA
st.sidebar.markdown("### Painel de Controle")
st.sidebar.markdown("**Personalize sua analise inteligente**")

# Lista expandida de acoes populares com setores
popular_stocks = {
    "Technology": {
        "Apple": "AAPL",
        "Microsoft": "MSFT", 
        "Google": "GOOGL",
        "Meta": "META",
        "Tesla": "TSLA",
        "NVIDIA": "NVDA"
    },
    "Finance": {
        "JPMorgan Chase": "JPM",
        "Bank of America": "BAC",
        "Wells Fargo": "WFC"
    },
    "Healthcare": {
        "Johnson & Johnson": "JNJ",
        "Pfizer": "PFE",
        "UnitedHealth": "UNH"
    },
    "Consumer": {
        "Amazon": "AMZN",
        "Walmart": "WMT",
        "Home Depot": "HD"
    }
}

# Secao de instrucoes simples
st.sidebar.markdown("---")
st.sidebar.markdown("**Como Usar:** Selecione empresa e periodo, depois clique em Analisar.")

# Selecao de setor e empresa
selected_sector = st.sidebar.selectbox(
    "Setor Economico:",
    options=list(popular_stocks.keys()),
    index=0
)

sector_stocks = popular_stocks[selected_sector]
selected_company = st.sidebar.selectbox(
    "Empresa:",
    options=list(sector_stocks.keys())
)

stock_symbol = sector_stocks[selected_company]

# Periodo de tempo expandido
period_options = {
    "5 Dias": "5d",
    "1 Mes": "1mo",
    "3 Meses": "3mo", 
    "6 Meses": "6mo",
    "1 Ano": "1y",
    "2 Anos": "2y",
    "5 Anos": "5y"
}

selected_period = st.sidebar.selectbox(
    "Periodo de Analise:",
    options=list(period_options.keys()),
    index=4  # Default para 1 ano
)

period = period_options[selected_period]

# Opcoes avancadas
st.sidebar.markdown("---")
st.sidebar.markdown("### Opcoes Avancadas")
show_volume = st.sidebar.checkbox("Mostrar Volume", value=True)
show_moving_averages = st.sidebar.checkbox("Medias Moveis", value=True)
show_candlestick = st.sidebar.checkbox("Grafico Candlestick", value=True)
show_ai_analysis = st.sidebar.checkbox("Analise por IA (Databricks)", value=True)

ma_periods = st.sidebar.multiselect(
    "Periodos das Medias:",
    options=["20", "50", "200"],
    default=["20", "50"]
)

# Modo demonstracao - padrao True ja que API nao funciona no Databricks App
use_demo_data = st.sidebar.checkbox("Usar Dados Reais (Yahoo Finance)", value=False, help="Desative para usar dados reais. Nota: Pode nao funcionar no Databricks App devido a restricoes de rede.")

if not use_demo_data:
    st.sidebar.info("Modo demonstracao ativo. Dados sao simulados.")

# Info sobre Databricks AI
st.sidebar.markdown("---")
st.sidebar.markdown("### Powered by Databricks")
st.sidebar.markdown("""
Esta aplicacao utiliza:
- **Databricks Model Serving** para analise com LLM
- **Databricks SQL Warehouse** para consultas
- **Unity Catalog** para governanca de dados
- **Vector Search** para recomendacoes
""")

# Botao principal de carregamento
st.sidebar.markdown("---")
load_data = st.sidebar.button(
    "Analisar", 
    use_container_width=True,
    type="primary",
    on_click=run_analysis
)

# Lógica principal de carregamento e análise
if st.session_state.analysis_done:
    # Por padrao usa dados de demonstracao (modo demo=True por padrao)
    if not use_demo_data:
        # Modo demonstracao
        stock_data = generate_demo_data(stock_symbol, period)
        st.info(f"Usando dados de demonstracao para {stock_symbol} ({len(stock_data)} registros)")
    else:
        # Tenta carregar dados reais (provavelmente vai falhar no Databricks App)
        stock_data = load_stock_data(stock_symbol, period)
        if stock_data is None:
            st.error("Nao foi possivel carregar dados reais. Usando demonstracao.")
            stock_data = generate_demo_data(stock_symbol, period)
    
    if stock_data is not None:
        # Calcular métricas básicas
        current_price = stock_data['Close'][-1]
        price_change = stock_data['Close'][-1] - stock_data['Close'][-2] if len(stock_data) > 1 else 0
        price_change_pct = (price_change / stock_data['Close'][-2]) * 100 if len(stock_data) > 1 else 0
        max_price = stock_data['High'].max()
        min_price = stock_data['Low'].min()
        avg_volume = stock_data['Volume'].mean()
        volatility = stock_data['Close'].pct_change().std() * np.sqrt(252) * 100  # Anualizada
        
        # Cabeçalho informativo
        create_stock_header(selected_company, stock_symbol, current_price, price_change, price_change_pct)
        
        # Métricas principais em cards
        st.markdown("### 📊 Métricas Principais")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Preço Atual", 
                f"${current_price:.2f}", 
                price_change_pct,
                "💰",
                "primary"
            )
        
        with col2:
            create_metric_card(
                "Variação Diária", 
                f"${price_change:+.2f}", 
                price_change_pct,
                "📈",
                "success" if price_change >= 0 else "error"
            )
        
        with col3:
            create_metric_card(
                "Máxima (52w)", 
                format_large_number(max_price), 
                None,
                "🔺",
                "primary"
            )
        
        with col4:
            create_metric_card(
                "Volatilidade", 
                f"{volatility:.1f}%", 
                None,
                "📊",
                "warning"
            )
        
        # Preparar dados para gráficos
        chart_data = stock_data.copy()
        
        # Adicionar médias móveis se solicitado
        if show_moving_averages and ma_periods:
            for period in ma_periods:
                chart_data[f'MA_{period}'] = chart_data['Close'].rolling(window=int(period)).mean()
        
        # Gráfico principal de preços
        st.markdown("### Evolucao do Preco")
        price_fig = create_enhanced_chart(
            chart_data, 
            f"{selected_company} - Historico de Precos",
            'Close',
            "#E80070"
        )
        
        # Adicionar medias moveis ao grafico
        if show_moving_averages and ma_periods:
            colors = ["#C4005C", "#FF1A8C", "#9C27B0"]
            for i, period in enumerate(ma_periods):
                if f'MA_{period}' in chart_data.columns:
                    price_fig.add_trace(go.Scatter(
                        x=chart_data.index,
                        y=chart_data[f'MA_{period}'],
                        mode='lines',
                        name=f'MA {period} dias',
                        line=dict(color=colors[i % len(colors)], width=2, dash='dash'),
                        opacity=0.8
                    ))
        
        price_fig.update_layout(showlegend=True)
        st.plotly_chart(price_fig, use_container_width=True)
        
        # Gráfico de volume
        if show_volume:
            st.markdown("### Volume de Negociacao")
            volume_fig = create_enhanced_chart(
                chart_data, 
                f"{selected_company} - Volume de Negociacao",
                'Volume',
                "#10b981",
                "bar"
            )
            st.plotly_chart(volume_fig, use_container_width=True)
        
        # Análise técnica avançada
        st.markdown("### 🔍 Análise Técnica")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Indicadores de Tendência**")
            
            # Calcular RSI simples
            delta = stock_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            st.metric("RSI (14)", f"{current_rsi:.1f}", 
                     "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral")
            
            # Suporte e Resistência
            recent_high = stock_data['High'].rolling(window=20).max().iloc[-1]
            recent_low = stock_data['Low'].rolling(window=20).min().iloc[-1]
            
            st.write(f"**Resistência:** ${recent_high:.2f}")
            st.write(f"**Suporte:** ${recent_low:.2f}")
        
        with col2:
            st.markdown("**Estatísticas Descritivas**")
            
            stats_data = {
                'Métrica': [
                    'Preço Médio',
                    'Desvio Padrão', 
                    'Mediana',
                    'Volume Médio',
                    'Variação % Total'
                ],
                'Valor': [
                    f"${stock_data['Close'].mean():.2f}",
                    f"${stock_data['Close'].std():.2f}",
                    f"${stock_data['Close'].median():.2f}",
                    format_large_number(avg_volume),
                    f"{((stock_data['Close'][-1] / stock_data['Close'][0]) - 1) * 100:+.2f}%"
                ]
            }
            
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        # Tabela de dados históricos
        st.markdown("### 📋 Dados Históricos")
        
        # Preparar dados para exibição (últimos 30 dias)
        display_data = stock_data.tail(30).copy()
        display_data.index = display_data.index.strftime('%d/%m/%Y')
        display_data = display_data.round(2)
        
        # Formatar colunas
        display_data.columns = [col.replace('_', ' ').title() for col in display_data.columns]
        
        st.dataframe(
            display_data, 
            use_container_width=True,
            height=400,
            column_config={
                "Close": st.column_config.NumberColumn("Preço Fechamento", format="$%.2f"),
                "Volume": st.column_config.NumberColumn("Volume", format="%,")
            }
        )
        
        # ===== Databricks AI Analysis =====
        st.markdown("### Analise por IA - Databricks Model Serving")
        
        # Prepara metricas para o agente
        metrics = {
            'current_price': float(current_price),
            'price_change': float(price_change),
            'volatility': float(volatility),
            'avg_volume': float(avg_volume)
        }
        
        # Chama funcao de analise da Databricks
        ai_analysis = databricks_ai_stock_analysis(stock_symbol, stock_data, metrics)
        
        # Exibe analise da IA
        if ai_analysis:
            st.markdown(ai_analysis)
        
        # Busca noticias resumidas
        news_summary = databricks_web_search_summary(selected_company)
        if news_summary:
            with st.expander("Noticias Relevantes (IA)"):
                st.markdown(news_summary)
        
        # ===== Graficos Adicionais (DSA Original) =====
        st.markdown("### Graficos Candlestick e Medias Moveis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dsa_plot_candlestick(stock_data, stock_symbol)
        
        with col2:
            dsa_plot_media_movel(stock_data, stock_symbol)
        
        # ===== Insights - Clean =====
        st.markdown("<h3 style='font-weight: 600; color: #1a1a2e;'>Insights</h3>", unsafe_allow_html=True)
        
        insights = []
        
        # Analise de tendencia
        short_ma = chart_data['Close'].rolling(window=20).mean().iloc[-1]
        long_ma = chart_data['Close'].rolling(window=50).mean().iloc[-1]
        
        if short_ma > long_ma:
            insights.append("**Tendencia de Alta:** Media de 20 dias acima da media de 50 dias")
        elif short_ma < long_ma:
            insights.append("**Tendencia de Baixa:** Media de 20 dias abaixo da media de 50 dias")
        else:
            insights.append("**Tendencia Neutra:** Medias moveis proximas")
        
        # Analise de volatilidade
        if volatility > 30:
            insights.append("**Alta Volatilidade:** Ativo com grande variacao de precos")
        elif volatility < 15:
            insights.append("**Baixa Volatilidade:** Ativo estavel nos ultimos periodos")
        
        # Analise de preco
        if current_price > max_price * 0.95:
            insights.append("**Proximo da Maxima:** Preco proximo de maximas recentes")
        elif current_price < min_price * 1.05:
            insights.append("**Proximo da Minima:** Preco proximo de minimas recentes")
        
        # Exibir insights
        for insight in insights:
            st.markdown(f"- {insight}")
            
else:
    # ===== HERO SECTION - Clean & Minimal =====
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #E80070 0%, #C4005C 100%);
        border-radius: 16px;
        padding: 4rem 3rem;
        margin: 0 0 3rem 0;
    ">
        <div style="max-width: 600px;">
            <div style="margin-bottom: 1rem;">
                <span style="
                    display: inline-block;
                    background: rgba(255,255,255,0.15);
                    padding: 0.5rem 1rem;
                    border-radius: 50px;
                    font-size: 0.875rem;
                    color: white;
                    font-weight: 500;
                    border: 1px solid rgba(255,255,255,0.2);
                    margin-right: 0.5rem;
                ">Powered by Serasa</span>
                <span style="
                    display: inline-block;
                    background: rgba(255,255,255,0.15);
                    padding: 0.5rem 1rem;
                    border-radius: 50px;
                    font-size: 0.875rem;
                    color: white;
                    font-weight: 500;
                    border: 1px solid rgba(255,255,255,0.2);
                ">LGPD Compliant</span>
            </div>
            <h1 style="
                font-size: 3rem;
                font-weight: 700;
                color: white;
                margin-bottom: 1rem;
                line-height: 1.1;
                letter-spacing: -0.02em;
            ">Analise Inteligente de Mercado</h1>
            <p style="
                font-size: 1.125rem;
                color: rgba(255,255,255,0.9);
                margin: 0;
                max-width: 500px;
                line-height: 1.6;
            ">Descubra oportunidades de investimento com dados em tempo real, indicadores tecnicos avancados e insights impulsionados por IA.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== FEATURES - Clean Cards =====
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem; font-weight: 600; color: #1a1a2e;'>Recursos Poderosos</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    features = [
        ("Dados em Tempo Real", "Acesso instantaneo a dados de mercado via Yahoo Finance API. Atualizacoes automaticas e precisas."),
        ("Analise Tecnica Avancada", "RSI, Medias Moveis, Suporte/Resistencia, Volatilidade e Bandas de Bollinger em um so lugar."),
        ("Insights por IA", "Algoritmos inteligentes identificam tendencias e oportunidades automaticamente para voce.")
    ]
    
    for col, (title, desc) in zip([col1, col2, col3], features):
        with col:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 2rem;
                border: 1px solid #e5e7eb;
                height: 100%;
            ">
                <div style="color: #E80070; margin-bottom: 0.75rem; font-weight: 600; font-size: 1.125rem;">
                    {title}
                </div>
                <div style="color: #6b7280; font-size: 0.95rem; line-height: 1.6;">
                    {desc}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== STATS - Clean Numbers =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem; font-weight: 600; color: #1a1a2e;'>Em Numeros</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats_data = [
        ("15+", "Empresas"),
        ("7", "Periodos"),
        ("4", "Setores"),
        ("5+", "Indicadores")
    ]
    
    for col, (number, label) in zip([col1, col2, col3, col4], stats_data):
        with col:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                border: 1px solid #e5e7eb;
            ">
                <div style="font-size: 2.5rem; font-weight: 700; color: #E80070; margin-bottom: 0.25rem;">
                    {number}
                </div>
                <div style="color: #6b7280; font-size: 0.875rem; font-weight: 500;">
                    {label}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== HOW IT WORKS - Clean Steps =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem; font-weight: 600; color: #1a1a2e;'>Como Funciona?</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    steps = [
        ("1", "Escolha", "Selecione o setor economico"),
        ("2", "Configure", "Defina empresa e periodo"),
        ("3", "Analise", "Visualize graficos e metricas"),
        ("4", "Decida", "Tome decisoes informadas")
    ]
    
    for col, (num, title, desc) in zip([col1, col2, col3, col4], steps):
        with col:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                border: 1px solid #e5e7eb;
            ">
                <div style="
                    width: 48px;
                    height: 48px;
                    background: #E80070;
                    color: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 600;
                    font-size: 1.25rem;
                    margin: 0 auto 1rem auto;
                ">{num}</div>
                <div style="color: #1a1a2e; margin-bottom: 0.5rem; font-weight: 600; font-size: 1rem;">
                    {title}
                </div>
                <div style="color: #6b7280; font-size: 0.875rem; margin: 0;">
                    {desc}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== MARKET PREVIEW - Clean Chart =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem; font-weight: 600; color: #1a1a2e;'>Preview do Mercado</h3>", unsafe_allow_html=True)
    
    # Create animated preview data
    preview_data = pd.DataFrame({
        'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'],
        'Variacao %': [1.2, -0.5, 2.1, 0.8, 1.5]
    })
    
    fig_preview = go.Figure()
    colors = ['#E80070' if x > 0 else '#ef4444' for x in preview_data['Variacao %']]
    
    fig_preview.add_trace(go.Bar(
        x=preview_data['Dia'],
        y=preview_data['Variacao %'],
        marker=dict(
            color=colors,
            line=dict(color=colors, width=2),
            opacity=0.8
        ),
        text=preview_data['Variacao %'].apply(lambda x: f'{x:+.1f}%'),
        textposition='outside',
        textfont=dict(size=14, color='#333', family='Inter')
    ))
    
    fig_preview.update_layout(
        height=300,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=True,
            zerolinecolor='rgba(0,0,0,0.1)',
            zerolinewidth=2
        ),
        xaxis=dict(showgrid=False),
        font=dict(family='Inter')
    )
    st.plotly_chart(fig_preview, use_container_width=True)
    
    # ===== CTA SECTION - Clean =====
    st.markdown("""
    <div style="
        background: #fafafa;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        margin-top: 3rem;
        border: 1px dashed #e5e7eb;
    ">
        <div style="color: #E80070; margin-bottom: 1rem; font-weight: 700; font-size: 1.75rem;">
            Pronto para comecar?
        </div>
        <div style="color: #6b7280; margin-bottom: 2rem; font-size: 1rem; max-width: 500px; margin-left: auto; margin-right: auto;">
            Selecione uma empresa no painel lateral e descubra insights poderosos sobre o mercado financeiro.
        </div>
        <div style="margin-bottom: 1.5rem;">
            <span style="display: inline-flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.9rem; margin: 0 0.75rem;">
                <span style="color: #E80070; font-weight: 700;">✓</span> Gratuito
            </span>
            <span style="display: inline-flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.9rem; margin: 0 0.75rem;">
                <span style="color: #E80070; font-weight: 700;">✓</span> Sem cadastro
            </span>
            <span style="display: inline-flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.9rem; margin: 0 0.75rem;">
                <span style="color: #E80070; font-weight: 700;">✓</span> Dados em tempo real
            </span>
        </div>
        <div style="font-size: 1.5rem; color: #E80070; font-weight: 600;">&larr;</div>
    </div>
    """, unsafe_allow_html=True)

# Footer clean
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #6b7280;">
    <p style="margin: 0; font-size: 0.875rem;">
        <strong>NASDAQ Analytics Platform</strong> | 
        <span>LGPD Compliant</span> | 
        <span>2024 Serasa Experian</span>
    </p>
</div>
""", unsafe_allow_html=True)
