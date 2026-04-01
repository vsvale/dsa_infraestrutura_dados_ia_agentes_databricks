# NASDAQ Stocks Dashboard

Aplicação Databricks para análise de ações do NASDAQ desenvolvida com Streamlit.

## 🚀 Funcionalidades

- **Visualização em Tempo Real**: Dados históricos de ações do Yahoo Finance
- **Gráficos Interativos**: Preços e volume com Plotly
- **Métricas Principais**: Preço atual, variação, máximas e mínimas
- **Interface Responsiva**: Design moderno com Streamlit

## 📁 Estrutura do Projeto

```
databricks-app-nasdaq-stocks/
├── databricks.yml          # Configuração do Databricks Asset Bundle
├── requirements.txt        # Dependências Python
├── README.md              # Documentação
└── src/
    └── app.py             # Aplicação Streamlit principal
```

## 🛠️ Tecnologias

- **Streamlit**: Framework para aplicações web
- **Pandas**: Manipulação de dados
- **Plotly**: Visualizações interativas
- **yfinance**: Dados financeiros do Yahoo Finance
- **Databricks Apps**: Plataforma de hospedagem

## 📋 Pré-requisitos

- Workspace Databricks com Apps habilitado
- Python 3.8+
- Dependências listadas em `requirements.txt`

## 🔧 Configuração

1. Configure o workspace no `databricks.yml`:
   ```yaml
   workspace:
     host: https://your-workspace.databricks.com
     root_path: /Workspace/Users/your-email@databricks.com/nasdaq-stocks-app
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Deploy

1. Build do bundle:
   ```bash
   databricks bundle deploy
   ```

2. Run local:
   ```bash
   databricks bundle run nasdaq-stocks-app
   ```

## 📊 Como Usar

1. Selecione uma empresa na sidebar
2. Escolha o período desejado (1 mês a 2 anos)
3. Clique em "Carregar Dados"
4. Visualize gráficos e estatísticas

## 🎯 Empresas Disponíveis

- Apple (AAPL)
- Microsoft (MSFT)
- Amazon (AMZN)
- Google (GOOGL)
- Tesla (TSLA)
- NVIDIA (NVDA)
- Meta (META)

## 🔄 Personalização

Para adicionar novas empresas, edite o dicionário `popular_stocks` em `src/app.py`:

```python
popular_stocks = {
    "Nova Empresa": "SYMBOL",
    # ... outras empresas
}
```

## 📝 Desenvolvimento

### Testes Locais

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar localmente
streamlit run src/app.py
```

### Deploy no Databricks

```bash
# Deploy para development
databricks bundle deploy -t development

# Deploy para production  
databricks bundle deploy -t production
```

## 🐛 Troubleshooting

### Erros Comuns

1. **Dados não carregam**: Verifique conexão com internet
2. **Erro de dependência**: Confirme versões em requirements.txt
3. **Workspace não encontrado**: Valide host no databricks.yml

### Logs

Verifique logs da aplicação no Databricks Workspace:
- Apps → NASDAQ Stocks Dashboard → Logs

## 📈 Roadmap

- [ ] Adicionar mais indicadores técnicos
- [ ] Comparação entre múltiplas ações
- [ ] Alertas de preço
- [ ] Exportação de dados
- [ ] Integração com Unity Catalog

## 📞 Suporte

Para dúvidas ou suporte, consulte a documentação do Databricks Apps ou abra uma issue.
