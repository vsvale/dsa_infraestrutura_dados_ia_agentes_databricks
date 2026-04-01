import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta

# Configuração da página com identidade visual Serasa
st.set_page_config(
    page_title="Serasa Stocks - NASDAQ Dashboard",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para identidade visual Serasa
st.markdown("""
<style>
    /* Cores Serasa */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Títulos e cabeçalhos */
    .stTitle {
        color: #0066CC;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
    }
    
    .stHeader {
        color: #0066CC;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Métricas */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 1rem;
        border-radius: 8px;
    }
    
    /* Botões */
    .stButton > button {
        background-color: #0066CC;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #0052a3;
    }
    
    /* Positivo (verde Serasa) */
    .positive {
        color: #00A650;
    }
    
    /* Negativo */
    .negative {
        color: #dc3545;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #6c757d;
        font-size: 0.9rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Logo e título principal
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("📊")
with col2:
    st.markdown("# **Serasa Stocks**")
    st.markdown("### Análise Inteligente de Ações NASDAQ")

st.markdown("---")

# Sidebar com identidade visual Serasa
st.sidebar.markdown("### 📊 Painel de Controle")
st.sidebar.markdown("**Personalize sua análise**")

# Lista de ações populares
popular_stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT", 
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "Meta": "META"
}

# Seleção de ações
selected_company = st.sidebar.selectbox(
    "Selecione uma empresa:",
    options=list(popular_stocks.keys())
)

stock_symbol = popular_stocks[selected_company]

# Período de tempo
period_options = {
    "1 Mês": "1mo",
    "3 Meses": "3mo", 
    "6 Meses": "6mo",
    "1 Ano": "1y",
    "2 Anos": "2y"
}

selected_period = st.sidebar.selectbox(
    "Selecione o período:",
    options=list(period_options.keys())
)

period = period_options[selected_period]

# Botão para carregar dados
if st.sidebar.button("Carregar Dados"):
    with st.spinner(f"Carregando dados de {selected_company}..."):
        try:
            # Baixar dados do Yahoo Finance
            stock_data = yf.download(stock_symbol, period=period)
            
            if stock_data.empty:
                st.error("Não foi possível carregar os dados. Tente novamente.")
            else:
                # Exibir informações básicas com estilo Serasa
                st.markdown(f"## � {selected_company} ({stock_symbol})")
                st.markdown(f"**Análise em tempo real**")
                
                # Métricas principais
                col1, col2, col3, col4 = st.columns(4)
                
                current_price = stock_data['Close'][-1]
                price_change = stock_data['Close'][-1] - stock_data['Close'][-2]
                price_change_pct = (price_change / stock_data['Close'][-2]) * 100
                
                with col1:
                    st.metric("💰 Preço Atual", f"${current_price:.2f}")
                
                with col2:
                    change_color = "normal" if price_change >= 0 else "inverse"
                    st.metric("📈 Variação", f"${price_change:.2f}", f"{price_change_pct:.2f}%", delta_color=change_color)
                
                with col3:
                    st.metric("🔺 Máxima", f"${max_price:.2f}")
                
                with col4:
                    st.metric("🔻 Mínima", f"${min_price:.2f}")
                
                # Gráfico de preços com cores Serasa
                st.subheader("📈 Evolução do Preço")
                fig = px.line(
                    stock_data, 
                    x=stock_data.index, 
                    y='Close',
                    title=f"{selected_company} - Histórico de Preços",
                    labels={'x': 'Data', 'Close': 'Preço (USD)'},
                    color_discrete_sequence=['#0066CC']
                )
                fig.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Preço (USD)",
                    hovermode='x unified',
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color="#333333"),
                    title_font=dict(color="#0066CC", size=16)
                )
                fig.update_traces(line_width=2)
                st.plotly_chart(fig, use_container_width=True)
                
                # Gráfico de volume com cores Serasa
                st.subheader("📊 Volume de Negociação")
                fig_volume = px.bar(
                    stock_data,
                    x=stock_data.index,
                    y='Volume',
                    title=f"{selected_company} - Volume de Negociação",
                    labels={'x': 'Data', 'Volume': 'Volume'},
                    color_discrete_sequence=['#00A650']
                )
                fig_volume.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Volume",
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color="#333333"),
                    title_font=dict(color="#00A650", size=16)
                )
                st.plotly_chart(fig_volume, use_container_width=True)
                
                # Estatísticas descritivas com estilo Serasa
                st.subheader("📋 Estatísticas Detalhadas")
                
                # Formatando dados para melhor visualização
                stats_df = stock_data.describe()
                stats_df = stats_df.round(2)
                st.dataframe(stats_df, use_container_width=True)
                
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")

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

# Footer com identidade Serasa
st.markdown("---")
st.markdown("""
<div class="footer">
    <strong>🚀 Desenvolvido por Serasa Experian</strong><br>
    <small>Confiabilidade e inovação em análise de dados financeiros</small>
</div>
""", unsafe_allow_html=True)
