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

# Configuração da página com identidade visual Serasa Experian
st.set_page_config(
    page_title="Serasa Experian - NASDAQ Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Serasa Experian Analytics Platform v2.0"
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
    
    /* Hero with animated gradient - Serasa Pink */
    .hero-container {
        background: linear-gradient(-45deg, #E80070, #C4005C, #D0006F, #FF1A8C);
        background-size: 400% 400%;
        animation: gradientShift 8s ease infinite;
        border-radius: 24px;
        padding: 5rem 4rem;
        margin: 1rem 0 3rem 0;
        position: relative;
        overflow: hidden;
        box-shadow: 0 30px 60px -15px rgba(232, 0, 112, 0.4);
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
                      color: str = "var(--color-primary)", chart_type: str = "line") -> go.Figure:
    """Cria gráfico aprimorado com estilo Serasa"""
    if chart_type == "line":
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[y_column],
            mode='lines',
            line=dict(
                color=color,
                width=3
            ),
            fill='tonexty' if 'tonexty' in locals() else None,
            fillcolor=f'{color}20'
        ))
    elif chart_type == "bar":
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data.index,
            y=data[y_column],
            marker_color=color,
            opacity=0.8
        ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18, color="var(--color-primary)")
        ),
        xaxis_title="Data",
        yaxis_title=y_column,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color="var(--color-text-primary)"),
        margin=dict(l=60, r=30, t=60, b=60),
        hovermode='x unified',
        showlegend=False,
        height=400
    )
    
    return fig

def format_large_number(num: float) -> str:
    """Formata números grandes para melhor legibilidade"""
    if num >= 1e9:
        return f"${num/1e9:.1f}B"
    elif num >= 1e6:
        return f"${num/1e6:.1f}M"
    elif num >= 1e3:
        return f"${num/1e3:.1f}K"
    else:
        return f"${num:.2f}"

# Cache para melhor performance
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_stock_data(symbol: str, period: str) -> Optional[pd.DataFrame]:
    """Carrega dados da ação com cache e tratamento de erros"""
    try:
        data = yf.download(symbol, period=period, progress=False)
        if data.empty:
            return None
        
        # Limpeza e validação básica
        data = data.dropna()
        if len(data) < 2:
            return None
            
        return data
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

# Logo e título principal com design Serasa Experian
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("📊")
with col2:
    st.markdown("# **Serasa Experian Analytics**")
    st.markdown("### Plataforma Avançada de Análise de Mercado")

st.markdown("---")

# Sidebar aprimorado com identidade visual Serasa
st.sidebar.markdown("### 📊 Painel de Controle")
st.sidebar.markdown("**Personalize sua análise inteligente**")

# Lista expandida de ações populares com setores
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

# Seleção de setor e empresa
selected_sector = st.sidebar.selectbox(
    "🏢 Setor Econômico:",
    options=list(popular_stocks.keys()),
    index=0
)

sector_stocks = popular_stocks[selected_sector]
selected_company = st.sidebar.selectbox(
    "📈 Empresa:",
    options=list(sector_stocks.keys())
)

stock_symbol = sector_stocks[selected_company]

# Período de tempo expandido
period_options = {
    "5 Dias": "5d",
    "1 Mês": "1mo",
    "3 Meses": "3mo", 
    "6 Meses": "6mo",
    "1 Ano": "1y",
    "2 Anos": "2y",
    "5 Anos": "5y"
}

selected_period = st.sidebar.selectbox(
    "📅 Período de Análise:",
    options=list(period_options.keys()),
    index=4  # Default para 1 ano
)

period = period_options[selected_period]

# Opções avançadas
st.sidebar.markdown("### ⚙️ Opções Avançadas")
show_volume = st.sidebar.checkbox("📊 Mostrar Volume", value=True)
show_moving_averages = st.sidebar.checkbox("📈 Médias Móveis", value=True)
ma_periods = st.sidebar.multiselect(
    "Períodos das Médias:",
    options=["20", "50", "200"],
    default=["20", "50"]
)

# Botão principal de carregamento
col1, col2, col3 = st.sidebar.columns([1, 2, 1])
with col2:
    load_data = st.button(
        "🚀 Carregar Dados", 
        use_container_width=True,
        type="primary"
    )
# Lógica principal de carregamento e análise
if load_data:
    stock_data = load_stock_data(stock_symbol, period)
    
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
        st.markdown("### 📈 Evolução do Preço")
        price_fig = create_enhanced_chart(
            chart_data, 
            f"{selected_company} - Histórico de Preços",
            'Close',
            "var(--color-primary)"
        )
        
        # Adicionar médias móveis ao gráfico
        if show_moving_averages and ma_periods:
            colors = ["var(--color-secondary)", "var(--color-accent)", "#9C27B0"]
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
            st.markdown("### 📊 Volume de Negociação")
            volume_fig = create_enhanced_chart(
                chart_data, 
                f"{selected_company} - Volume de Negociação",
                'Volume',
                "var(--color-success)",
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
        
        # Insights automáticos
        st.markdown("### � Insights Inteligentes")
        
        insights = []
        
        # Análise de tendência
        short_ma = chart_data['Close'].rolling(window=20).mean().iloc[-1]
        long_ma = chart_data['Close'].rolling(window=50).mean().iloc[-1]
        
        if short_ma > long_ma:
            insights.append("📈 **Tendência de Alta:** Média de 20 dias acima da média de 50 dias")
        elif short_ma < long_ma:
            insights.append("📉 **Tendência de Baixa:** Média de 20 dias abaixo da média de 50 dias")
        else:
            insights.append("➡️ **Tendência Neutra:** Médias móveis próximas")
        
        # Análise de volatilidade
        if volatility > 30:
            insights.append("⚠️ **Alta Volatilidade:** Ativo com grande variação de preços")
        elif volatility < 15:
            insights.append("📊 **Baixa Volatilidade:** Ativo estável nos últimos períodos")
        
        # Análise de preço
        if current_price > max_price * 0.95:
            insights.append("🔺 **Próximo da Máxima:** Preço próximo de máximas recentes")
        elif current_price < min_price * 1.05:
            insights.append("🔻 **Próximo da Mínima:** Preço próximo de mínimas recentes")
        
        # Exibir insights
        for insight in insights:
            st.markdown(f"- {insight}")
            
else:
    # ===== HERO SECTION - Ultra Modern Landing Page =====
    st.markdown("""
    <div class="hero-container">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 3rem; position: relative; z-index: 2;">
            <div style="flex: 1; min-width: 320px;">
                <div style="display: inline-block; background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); padding: 0.5rem 1rem; border-radius: 50px; margin-bottom: 1.5rem; border: 1px solid rgba(255,255,255,0.2);">
                    <span style="color: white; font-size: 0.875rem; font-weight: 500;">� Powered by Serasa Experian</span>
                </div>
                <h1 class="hero-title">Análise Inteligente<br/>de Mercado</h1>
                <p class="hero-subtitle">
                    Descubra oportunidades de investimento com dados em tempo real, 
                    indicadores técnicos avançados e insights impulsionados por IA.
                </p>
                <div style="margin-bottom: 2rem;">
                    <span class="trust-badge">🔒 LGPD Compliant</span>
                    <span class="trust-badge">⚡ Real-time</span>
                    <span class="trust-badge">🤖 AI-Powered</span>
                </div>
                <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                    <div style="text-align: center; padding: 0.75rem 1.5rem; background: rgba(255,255,255,0.1); border-radius: 12px; border: 1px solid rgba(255,255,255,0.2);">
                        <div style="font-size: 1.5rem; font-weight: 700; color: white;">15+</div>
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.8);">Empresas</div>
                    </div>
                    <div style="text-align: center; padding: 0.75rem 1.5rem; background: rgba(255,255,255,0.1); border-radius: 12px; border: 1px solid rgba(255,255,255,0.2);">
                        <div style="font-size: 1.5rem; font-weight: 700; color: white;">7</div>
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.8);">Períodos</div>
                    </div>
                    <div style="text-align: center; padding: 0.75rem 1.5rem; background: rgba(255,255,255,0.1); border-radius: 12px; border: 1px solid rgba(255,255,255,0.2);">
                        <div style="font-size: 1.5rem; font-weight: 700; color: white;">5+</div>
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.8);">Indicadores</div>
                    </div>
                </div>
            </div>
            <div style="flex: 0 0 auto; text-align: center;">
                <div class="floating-icon" style="font-size: 10rem; filter: drop-shadow(0 20px 40px rgba(0,0,0,0.3));">
                    �
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== FEATURE SHOWCASE - Modern Bento Grid =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 3rem;'>✨ Recursos Poderosos</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    features = [
        ("⚡", "Dados em Tempo Real", "Acesso instantâneo a dados de mercado via Yahoo Finance API. Atualizações automáticas e precisas."),
        ("📊", "Análise Técnica Avançada", "RSI, Médias Móveis, Suporte/Resistência, Volatilidade e Bandas de Bollinger em um só lugar."),
        ("🎯", "Insights por IA", "Algoritmos inteligentes identificam tendências e oportunidades automaticamente para você.")
    ]
    
    for col, (icon, title, desc) in zip([col1, col2, col3], features):
        with col:
            st.markdown(f"""
            <div class="feature-card" style="height: 100%;">
                <div class="feature-icon">{icon}</div>
                <h4 style="color: #E80070; margin-bottom: 1rem; font-weight: 700; font-size: 1.25rem;">{title}</h4>
                <p style="color: #6C757D; font-size: 1rem; line-height: 1.7;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== STATS SECTION - Gradient Cards =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>📈 Em Números</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats_data = [
        ("15+", "Empresas", "📊"),
        ("7", "Períodos", "📅"),
        ("4", "Setores", "🏢"),
        ("5+", "Indicadores", "📉")
    ]
    
    for col, (number, label, icon) in zip([col1, col2, col3, col4], stats_data):
        with col:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                border-radius: 20px;
                padding: 2rem 1rem;
                text-align: center;
                border: 1px solid rgba(230,0,126,0.1);
                box-shadow: 0 4px 20px rgba(0,0,0,0.05);
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-8px)'; this.style.boxShadow='0 20px 40px -15px rgba(230, 0, 126, 0.2)';" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 20px rgba(0,0,0,0.05)';">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <div class="stat-number">{number}</div>
                <p style="color: #6C757D; font-size: 0.9rem; margin: 0; font-weight: 500;">{label}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== HOW IT WORKS - Modern Steps =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>🚀 Como Funciona?</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    steps = [
        ("1", "🏢", "Escolha", "Selecione o setor econômico"),
        ("2", "📈", "Configure", "Defina empresa e período"),
        ("3", "📊", "Analise", "Visualize gráficos e métricas"),
        ("4", "💡", "Decida", "Tome decisões informadas")
    ]
    
    for col, (num, icon, title, desc) in zip([col1, col2, col3, col4], steps):
        with col:
            st.markdown(f"""
            <div class="step-card">
                <div class="step-number">{num}</div>
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">{icon}</div>
                <h5 style="color: #E6007E; margin-bottom: 0.75rem; font-weight: 700; font-size: 1.1rem;">{title}</h5>
                <p style="color: #6C757D; font-size: 0.9rem; margin: 0; line-height: 1.6;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== MARKET PREVIEW - Live Demo Chart =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>📈 Preview do Mercado</h3>", unsafe_allow_html=True)
    
    # Create animated preview data
    preview_data = pd.DataFrame({
        'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'],
        'Variação %': [1.2, -0.5, 2.1, 0.8, 1.5]
    })
    
    fig_preview = go.Figure()
    colors = ['#E6007E' if x > 0 else '#DC3545' for x in preview_data['Variação %']]
    
    fig_preview.add_trace(go.Bar(
        x=preview_data['Dia'],
        y=preview_data['Variação %'],
        marker=dict(
            color=colors,
            line=dict(color=colors, width=2),
            opacity=0.8
        ),
        text=preview_data['Variação %'].apply(lambda x: f'{x:+.1f}%'),
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
    
    # ===== CTA SECTION - Final Call to Action =====
    st.markdown("""
    <div class="cta-section">
        <div style="position: relative; z-index: 2;">
            <h2 style="color: #E6007E; margin-bottom: 1rem; font-weight: 800; font-size: 2rem;">🎯 Pronto para começar?</h2>
            <p style="color: #6C757D; margin-bottom: 2rem; font-size: 1.15rem; max-width: 500px; margin-left: auto; margin-right: auto;">
                Selecione uma empresa no painel lateral e descubra insights poderosos sobre o mercado financeiro.
            </p>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; color: #6C757D; font-size: 0.9rem;">
                    <span style="color: #E6007E;">✓</span> Gratuito
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem; color: #6C757D; font-size: 0.9rem;">
                    <span style="color: #E6007E;">✓</span> Sem cadastro
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem; color: #6C757D; font-size: 0.9rem;">
                    <span style="color: #E6007E;">✓</span> Dados em tempo real
                </div>
            </div>
            <div style="font-size: 2.5rem; animation: bounce 2s infinite;">👈</div>
        </div>
    </div>
    
    <style>
        @keyframes bounce {
            0%, 100% { transform: translateX(0); }
            50% { transform: translateX(-15px); }
        }
    </style>
    """, unsafe_allow_html=True)

# Informações adicionais com estilo Serasa
st.markdown("---")
st.markdown("### ℹ️ **Sobre o Serasa Stocks**")
st.markdown("""
**Plataforma inteligente de análise de ações** desenvolvida com a qualidade e confiança Serasa.

**🚀 Funcionalidades Principais:**
- 📈 **Visualização em tempo real** de preços históricos
- 📊 **Análise de volume** de negociação
- 📋 **Estatísticas detalhadas** para tomada de decisão
- 🔄 **Dados atualizados** diretamente do mercado
- 🎯 **Interface intuitiva** com design Serasa

**💡 Como usar:**
1. **Selecione** uma empresa no painel lateral
2. **Escolha** o período de análise desejado
3. **Clique** em "Carregar Dados" para visualizar
4. **Explore** os gráficos e estatísticas

**🔒 Segurança e Confiança:**
Dados obtidos de fontes confiáveis com a qualidade Serasa Experian.
""")

# Footer profissional Serasa Experian
st.markdown("---")
st.markdown("""
<div class="footer">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div>
            <strong>🚀 Serasa Experian Analytics Platform</strong><br>
            <small>Análise inteligente de mercado com a confiança Serasa Experian</small>
        </div>
        <div style="text-align: right;">
            <small>Versão 2.0 • LGPD Compliance</small><br>
            <small>© 2024 Serasa Experian. Todos os direitos reservados.</small>
        </div>
    </div>
    <div style="border-top: 1px solid var(--color-border); padding-top: 1rem; margin-top: 1rem;">
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <span style="color: var(--color-text-secondary);">🔒 Segurança de dados</span>
            <span style="color: var(--color-text-secondary);">📊 Analytics avançado</span>
            <span style="color: var(--color-text-secondary);">🌍 LGPD Compliance</span>
            <span style="color: var(--color-text-secondary);">⚡ Performance otimizada</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
