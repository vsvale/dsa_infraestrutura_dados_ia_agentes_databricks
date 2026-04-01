# 🚀 Serasa Experian Analytics - NASDAQ Platform

## 📋 Visão Geral

Plataforma avançada de análise de mercado desenvolvida com **Serasa Experian**, combinando design moderno, analytics inteligente e conformidade total com **LGPD**.

### ✨ Principais Diferenciais

- 🎨 **Design System Serasa Experian** - Interface profissional com tokens CSS e identidade visual corporativa
- 📊 **Analytics Avançado** - Indicadores técnicos, volatilidade, médias móveis e insights automáticos
- 🔒 **LGPD Compliance** - Nenhuma coleta de dados pessoais, política de privacidade transparente
- ⚡ **Performance Otimizada** - Cache inteligente, carregamento assíncrono e responsive design
- 🌐 **Acessibilidade Web** - Suporte a leitores de tela, navegação por teclado e motion reduction
- 🏢 **Organização por Setores** - Technology, Finance, Healthcare e Consumer

## �️ Arquitetura e Tecnologias

### Frontend
- **Streamlit 1.29.0** - Framework principal de UI
- **Plotly 5.17.0** - Visualizações interativas avançadas
- **CSS3 Custom** - Design system com variáveis e tokens
- **Responsive Design** - Mobile-first com breakpoints

### Backend & Dados
- **yfinance 0.2.28** - Integração com Yahoo Finance API
- **Pandas 2.1.4** - Processamento de dados
- **NumPy 1.24.3** - Cálculos numéricos
- **Python 3.9+** - Base de desenvolvimento

### Databricks Integration
- **Unity Catalog Ready** - Estrutura preparada para catálogo unificado
- **SQL Warehouse** - Conectividade com warehouses Databricks
- **Secrets Management** - Segurança no armazenamento de credenciais

## �📁 Estrutura do Projeto

```
databricks-app-nasdaq-stocks/
├── app.py                 # Aplicação principal
├── app.yml                # Configuração Databricks
├── databricks.yml          # Bundle configuration
├── requirements.txt        # Dependências Python
├── privacy_policy.md       # Política LGPD
└── README.md             # Este documento
```

## 🚀 Instalação e Deploy

### Ambiente Local
```bash
# Clonar repositório
git clone <repository-url>
cd databricks-app-nasdaq-stocks

# Instalar dependências
pip install -r requirements.txt

# Executar localmente
streamlit run app.py
```

### Deploy Databricks
```bash
# Validar configuração
databricks apps validate --profile <PROFILE>

# Deploy para desenvolvimento
databricks apps deploy nasdaq-stocks-app --source-code-path . --profile <PROFILE>

# Deploy para produção
databricks apps deploy nasdaq-stocks-app --source-code-path . --profile <PROFILE> --target production
```

## 🎯 Funcionalidades

### Análise de Mercado
- **Preços em Tempo Real** - Dados atualizados via Yahoo Finance
- **Métricas Principais** - Preço atual, variação, máximas, mínimas, volatilidade
- **Gráficos Interativos** - Evolução de preços com médias móveis
- **Volume de Negociação** - Análise de volume e padrões

### Indicadores Técnicos
- **RSI (14)** - Relative Strength Index para sobrecompra/sobrevenda
- **Médias Móveis** - 20, 50 e 200 dias configuráveis
- **Suporte e Resistência** - Níveis baseados em máximas/mínimas recentes
- **Volatilidade** - Cálculo anualizado para risco

### Insights Inteligentes
- **Análise de Tendência** - Baseada em cruzamento de médias móveis
- **Classificação de Volatilidade** - Alta, média ou baixa
- **Alertas de Preço** - Proximidade com máximas/mínimas
- **Recomendações Automáticas** - Baseadas em indicadores técnicos

## 🎨 Design System

### Tokens CSS
```css
:root {
    --color-primary: #0066CC;
    --color-secondary: #00A650;
    --color-accent: #FF6B35;
    --color-surface: #F8F9FA;
    --color-border: #E9ECEF;
    --font-family-primary: 'Inter', sans-serif;
    --border-radius-md: 8px;
    --shadow-md: 0 4px 6px rgba(0,0,0,0.16);
    --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Componentes Reutilizáveis
- `create_metric_card()` - Cards de métricas animados
- `create_stock_header()` - Cabeçalho informativo da ação
- `create_enhanced_chart()` - Gráficos Plotly personalizados
- `format_large_number()` - Formatação de valores financeiros

## 🔒 LGPD e Privacidade

### Práticas Implementadas
- ✅ **Privacy by Design** - Arquitetura focada em não coleta
- ✅ **Dados Anonimizados** - Nenhuma informação pessoal processada
- ✅ **Cache Temporário** - 5 minutos apenas
- ✅ **Logs Seguros** - Sem informações sensíveis
- ✅ **Transparência** - Política de privacidade acessível

### Direitos dos Usuários
- **Acesso** - Todos os dados são públicos e acessíveis
- **Correção** - Dados podem ser atualizados em tempo real
- **Eliminação** - Cache limpo automaticamente
- **Portabilidade** - Exportação de dados a qualquer momento

## 🌐 Acessibilidade

### WCAG 2.1 AA
- **Contraste** - Razão de contraste mínima de 4.5:1
- **Navegação** - Totalmente operável por teclado
- **Leitores de Tela** - Semântica HTML5 e ARIA labels
- **Redução de Movimento** - Respeita `prefers-reduced-motion`

### Responsividade
- **Mobile** - 320px a 768px
- **Tablet** - 768px a 1024px  
- **Desktop** - 1024px+

### Deploy no Databricks

```bash
# Deploy para development
databricks bundle deploy -t development

# Deploy para production  
databricks bundle deploy -t production
```

## � Suporte e Contato

### Canal Técnico
- **Email:** tech-support@serasaexperian.com.br
- **Slack:** #nasdaq-analytics-support
- **Documentation:** [Confluence Space]
- **Status Page:** status.serasaexperian.com.br

### Business Hours
- **Segunda a Sexta:** 9:00 - 18:00 (BRT)
- **Sábados:** 9:00 - 12:00
- **Domingos:** Fechado

---

## � Licença e Direitos

© 2024 Serasa Experian. Todos os direitos reservados.

Este projeto está licenciado sob os termos de uso interno da Serasa Experian e deve seguir todas as políticas de governança corporativa.

---

**Desenvolvido com ❤️ pela equipe Serasa Experian Analytics**
