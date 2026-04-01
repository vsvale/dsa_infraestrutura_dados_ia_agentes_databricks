import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="NASDAQ Stocks Dashboard",
    page_icon="📈",
    layout="wide"
)

# Título principal
st.title("📈 NASDAQ Stocks Dashboard")
st.markdown("---")

# Sidebar para controles
st.sidebar.header("Configurações")

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
                # Exibir informações básicas
                st.header(f"📊 {selected_company} ({stock_symbol})")
                
                # Métricas principais
                col1, col2, col3, col4 = st.columns(4)
                
                current_price = stock_data['Close'][-1]
                price_change = stock_data['Close'][-1] - stock_data['Close'][-2]
                price_change_pct = (price_change / stock_data['Close'][-2]) * 100
                
                with col1:
                    st.metric("Preço Atual", f"${current_price:.2f}")
                
                with col2:
                    st.metric("Variação", f"${price_change:.2f}", f"{price_change_pct:.2f}%")
                
                with col3:
                    max_price = stock_data['High'].max()
                    st.metric("Máxima", f"${max_price:.2f}")
                
                with col4:
                    min_price = stock_data['Low'].min()
                    st.metric("Mínima", f"${min_price:.2f}")
                
                # Gráfico de preços
                st.subheader("📈 Gráfico de Preços")
                fig = px.line(
                    stock_data, 
                    x=stock_data.index, 
                    y='Close',
                    title=f"{selected_company} - Preço das Ações",
                    labels={'x': 'Data', 'Close': 'Preço (USD)'},
                    color_discrete_sequence=['#1f77b4']
                )
                fig.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Preço (USD)",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Gráfico de volume
                st.subheader("📊 Volume de Negociação")
                fig_volume = px.bar(
                    stock_data,
                    x=stock_data.index,
                    y='Volume',
                    title=f"{selected_company} - Volume de Negociação",
                    labels={'x': 'Data', 'Volume': 'Volume'},
                    color_discrete_sequence=['#ff7f0e']
                )
                fig_volume.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Volume"
                )
                st.plotly_chart(fig_volume, use_container_width=True)
                
                # Estatísticas descritivas
                st.subheader("📋 Estatísticas Descritivas")
                st.dataframe(stock_data.describe())
                
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")

# Informações adicionais
st.markdown("---")
st.markdown("### ℹ️ Sobre este Dashboard")
st.markdown("""
Este dashboard interativo permite visualizar dados históricos de ações do NASDAQ em tempo real.

**Funcionalidades:**
- 📈 Visualização de preços históricos
- 📊 Análise de volume de negociação  
- 📋 Estatísticas descritivas
- 🔄 Atualização em tempo real

**Como usar:**
1. Selecione uma empresa na sidebar
2. Escolha o período desejado
3. Clique em "Carregar Dados"
""")

# Footer
st.markdown("---")
st.markdown("🚀 Desenvolvido com Streamlit + Databricks Apps")
