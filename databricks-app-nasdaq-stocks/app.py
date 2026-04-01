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

# CSS customizado para identidade visual Serasa Experian
st.markdown("""
<style>
    /* CSS Variables Serasa Experian */
    :root {
        --color-primary: #0066CC;
        --color-primary-dark: #0052A3;
        --color-secondary: #00A650;
        --color-accent: #FF6B35;
        --color-surface: #F8F9FA;
        --color-border: #E9ECEF;
        --color-text-primary: #212529;
        --color-text-secondary: #6C757D;
        --color-success: #00A650;
        --color-warning: #FFC107;
        --color-error: #DC3545;
        --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --font-family-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
        --border-radius-sm: 4px;
        --border-radius-md: 8px;
        --border-radius-lg: 12px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.12);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.16);
        --shadow-lg: 0 10px 25px rgba(0,0,0,0.20);
        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Base styles */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        color: var(--color-text-primary);
        font-family: var(--font-family-primary);
    }
    
    /* Typography */
    .stTitle, h1, h2, h3, h4, h5, h6 {
        color: var(--color-primary);
        font-family: var(--font-family-primary);
        font-weight: 600;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }
    
    h1 { font-size: 2.5rem; font-weight: 700; }
    h2 { font-size: 2rem; }
    h3 { font-size: 1.5rem; }
    
    /* Sidebar enhancements */
    .css-1d391kg, .css-1lcbmhc {
        background: var(--color-surface);
        border-right: 1px solid var(--color-border);
    }
    
    /* Cards and containers */
    div[data-testid="metric-container"], 
    div[data-testid="stHorizontalBlock"],
    div[data-testid="column"] {
        background: white;
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-md);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        transition: all var(--transition-base);
    }
    
    div[data-testid="metric-container"]:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    /* Buttons Serasa */
    .stButton > button {
        background: var(--color-primary);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: var(--border-radius-md);
        font-weight: 600;
        font-family: var(--font-family-primary);
        transition: all var(--transition-base);
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        background: var(--color-primary-dark);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }
    
    /* Select boxes and inputs */
    .stSelectbox > div > div {
        background: white;
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-md);
    }
    
    /* Data visualization */
    .js-plotly-plot {
        border-radius: var(--border-radius-lg);
        overflow: hidden;
    }
    
    /* Status indicators */
    .positive {
        color: var(--color-success);
        font-weight: 600;
    }
    
    .negative {
        color: var(--color-error);
        font-weight: 600;
    }
    
    .neutral {
        color: var(--color-text-secondary);
        font-weight: 600;
    }
    
    /* Loading states */
    .stSpinner > div {
        border-top-color: var(--color-primary) !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: var(--color-text-secondary);
        font-size: 0.875rem;
        margin-top: 3rem;
        padding: 2rem;
        border-top: 1px solid var(--color-border);
        background: var(--color-surface);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem;
        }
        
        div[data-testid="metric-container"] {
            padding: 1rem;
        }
    }
    
    /* Accessibility */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Custom animations */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-slide-in {
        animation: slideInUp 0.6s ease-out;
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
    # Mensagem inicial
    st.markdown("""
    <div style="
        text-align: center;
        padding: 3rem;
        background: var(--color-surface);
        border-radius: var(--border-radius-lg);
        margin: 2rem 0;
    ">
        <h2 style="color: var(--color-primary); margin-bottom: 1rem;">🚀 Bem-vindo à Serasa Experian Analytics</h2>
        <p style="color: var(--color-text-secondary); font-size: 1.1rem; line-height: 1.6;">
            Selecione uma empresa e período no painel lateral para iniciar sua análise inteligente de mercado.
            <br><br>
            <strong>Recursos avançados:</strong> Médias móveis, análise técnica, volatilidade e insights automáticos.
        </p>
    </div>
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
