import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Função para calcular o VaR
def calculate_var(returns, confidence_level, holding_period, investment):
    var = np.percentile(returns, 100 * (1 - confidence_level))
    var_adj = var * np.sqrt(holding_period)
    var_value = investment * var_adj
    return var_value

# Função para realizar o backtest do VaR
def backtest_var(returns, confidence_level, holding_period, investment):
    var_series = []
    breaches = 0

    for i in range(holding_period, len(returns)):
        window = returns.iloc[i-holding_period:i]
        var = np.percentile(window, 100 * (1 - confidence_level))
        var_series.append(var)
        if returns.iloc[i] < var:
            breaches += 1

    var_series = pd.Series(var_series, index=returns.index[holding_period:])
    return var_series, breaches

# Configuração da página
st.set_page_config(page_title="Sistema de VaR para Ativos Lineares", layout="wide")
st.title("Sistema de Valor em Risco (VaR) para Ativos Lineares")

# Barra lateral com as configurações
st.sidebar.header("Configurações")

# Input do símbolo das ações do Yahoo Finance
stocks_input = st.sidebar.text_input(
    'Digite os símbolos das ações separados por espaço:',
    'AAPL MSFT'
)

# Convertendo a string de entrada em uma lista de ações
stocks = stocks_input.split()

# Input de exposição (valor aplicado)
investment = st.sidebar.number_input("Exposição (valor aplicado):", min_value=0.0, value=10000.0)

# Input de intervalo de confiança
confidence_level = st.sidebar.slider("Intervalo de Confiança:", min_value=0.90, max_value=0.99, value=0.95, step=0.01)

# Input de período de retenção
holding_period = st.sidebar.number_input("Período de Retenção (dias):", min_value=1, max_value=252, value=10)

# Download dos dados
if len(stocks) > 0:
    try:
        data = yf.download(stocks, start="2020-01-01", end=datetime.today().strftime('%Y-%m-%d'), progress=False)['Adj Close']
        if data.empty:
            st.error("Erro ao baixar os dados: Nenhum dado retornado.")
        else:
            st.subheader("Dados das Ações Selecionadas")
            st.line_chart(data)
            
            # Calcular os retornos diários
            returns = data.pct_change().dropna()
            
            # Divisão em colunas para melhor organização dos resultados
            col1, col2 = st.columns(2)
            
            with col1:
                # Cálculo do VaR
                st.subheader("Valor em Risco (VaR)")
                var_value = calculate_var(returns, confidence_level, holding_period, investment)
                st.metric(label="VaR Estimado", value=f"R$ {var_value:,.2f}")

            with col2:
                # Backtest do VaR
                st.subheader("Backtest do VaR")
                var_series, breaches = backtest_var(returns, confidence_level, holding_period, investment)
                
                fig, ax = plt.subplots()
                returns.plot(ax=ax, label='Retornos Diários', color='blue')
                var_series.plot(ax=ax, label='VaR', color='red')
                ax.set_title("Backtest do VaR")
                ax.legend()
                st.pyplot(fig)
                
                st.metric(label="Número de Violações", value=breaches)
    except Exception as e:
        st.error(f"Erro ao baixar os dados: {e}")
else:
    st.warning("Por favor, digite pelo menos um símbolo de ação.")

# Rodar a aplicação com `streamlit run app.py`

