import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px


# -----------------------------
# CONFIGURACIÓN
# -----------------------------

st.set_page_config(
    page_title="Investment Dashboard de Héctor Salomón",
    page_icon="📈",
    layout="wide"
)

st.title("Investment Dashboard")
st.caption("Seguimiento simple de mi portafolio")


# -----------------------------
# CARGAR PORTAFOLIO
# -----------------------------

portfolio = pd.read_csv("portfolio.csv")

tickers = portfolio["Ticker"].tolist()


# -----------------------------
# DESCARGAR PRECIOS
# -----------------------------

@st.cache_data(ttl=300)
def get_prices(tickers):

    prices = {}

    for ticker in tickers:

        data = yf.Ticker(ticker)

        history = data.history(period="5d")

        if not history.empty:
            prices[ticker] = history["Close"].iloc[-1]
        else:
            prices[ticker] = None

    return prices


prices = get_prices(tickers)


portfolio["Current_Price"] = portfolio["Ticker"].map(prices)


# -----------------------------
# CÁLCULOS
# -----------------------------

portfolio["Cost_Basis"] = (
    portfolio["Shares"] *
    portfolio["Purchase_Price"]
)

portfolio["Current_Value"] = (
    portfolio["Shares"] *
    portfolio["Current_Price"]
)

portfolio["Profit_Loss"] = (
    portfolio["Current_Value"] -
    portfolio["Cost_Basis"]
)

portfolio["Return_%"] = (
    portfolio["Profit_Loss"] /
    portfolio["Cost_Basis"]
) * 100


# -----------------------------
# MÉTRICAS GENERALES
# -----------------------------

total_cost = portfolio["Cost_Basis"].sum()

total_value = portfolio["Current_Value"].sum()

total_profit = total_value - total_cost

total_return = (total_profit / total_cost) * 100


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Capital invertido",
    f"${total_cost:,.2f}"
)

col2.metric(
    "Valor actual",
    f"${total_value:,.2f}"
)

col3.metric(
    "Ganancia / pérdida",
    f"${total_profit:,.2f}"
)

col4.metric(
    "Rendimiento",
    f"{total_return:.2f}%"
)


# -----------------------------
# TABLA
# -----------------------------

st.subheader("Portafolio")

st.dataframe(
    portfolio,
    use_container_width=True
)


# -----------------------------
# DISTRIBUCIÓN
# -----------------------------

st.subheader("Distribución del portafolio")

fig = px.pie(
    portfolio,
    values="Current_Value",
    names="Ticker",
    hole=0.4
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# RENDIMIENTO
# -----------------------------

st.subheader("Rendimiento por inversión")

fig2 = px.bar(
    portfolio,
    x="Ticker",
    y="Return_%",
    text_auto=".2f"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)