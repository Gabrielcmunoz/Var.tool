import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Função para calcular o VaR
def calculate_var(data, confidence_level, holding_period, investment):
    returns = data.pct_change().dropna()
    var = np.percentile(returns, 100 * (1 - confidence_level))
    var_adj = var * np.sqrt(holding_period)
    var_value = investment * var_adj
    return var_value

# Função para realizar o backtest do VaR
def backtest_var(data, confidence_level, holding_period, investment):
    returns = data.pct_change().dropna()
    var_series = []
    breaches = 0
    
    for i in range(len(returns)):
        if i < holding_period:
            continue
        var = np.percentile(returns[i-holding_period:i], 100 * (1 - confidence_level))
        var_series.append(var)
        if returns.iloc[i] < var:
            breaches += 1
    
    var_series = pd.Series(var_series, index=returns.index[holding_period:])
    return var_series, breaches

# Configuração da página
st.title("Sistema de VaR para Ativos Lineares")
st.sidebar.header("Configurações")

# Seleção das ações do Yahoo Finance
stocks = st.sidebar.multiselect(
    'Selecione as ações:',
    ('AAPL', 'GOOGL', 'MSFT', 'AMZN', 'FB', 'TSLA', 'BRK-A', 'V', 'JNJ', 'WMT'),
    ('AAPL', 'MSFT')
)

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
            st.header("Dados das Ações Selecionadas")
            st.line_chart(data)
            
            # Cálculo do VaR
            var_value = calculate_var(data, confidence_level, holding_period, investment)
            st.write(f"O Valor em Risco (VaR) é de: R$ {var_value:,.2f}")

            # Backtest do VaR
            st.header("Backtest do VaR")
            var_series, breaches = backtest_var(data, confidence_level, holding_period, investment)
            
            fig, ax = plt.subplots()
            data.pct_change().plot(ax=ax, label='Retornos Diários')
            pd.Series(var_series, index=data.index[-len(var_series):]).plot(ax=ax, label='VaR')
            ax.legend()
            st.pyplot(fig)
            
            st.write(f"Número de violações: {breaches}")
    except Exception as e:
        st.error(f"Erro ao baixar os dados: {e}")
else:
    st.warning("Por favor, selecione pelo menos uma ação.")

# Rodar a aplicação com `streamlit run app.py`


