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

st.title("Investment Dashboard de Héctor Salomón")
st.caption("Seguimiento simple del portafolio de mi hijo")


# Cargar archivo
portfolio = pd.read_csv("portfolio.csv")
portfolio.columns = portfolio.columns.str.strip()

# Obtener precios actuales
@st.cache_data(ttl=300)
def get_price(ticker):
    data = yf.Ticker(ticker).history(period="5d")
    return data["Close"].iloc[-1]

portfolio["Current_Price"] = portfolio["Ticker"].apply(get_price)

# Cálculos
portfolio["Invested"] = (
    portfolio["Shares"] * portfolio["Purchase_Price"]
)

portfolio["Current_Value"] = (
    portfolio["Shares"] * portfolio["Current_Price"]
)

portfolio["P_L"] = (
    portfolio["Current_Value"] - portfolio["Invested"]
)

portfolio["Return_%"] = (
    portfolio["P_L"] / portfolio["Invested"]
) * 100

# Totales
total_invested = portfolio["Invested"].sum()
total_value = portfolio["Current_Value"].sum()
total_pl = portfolio["P_L"].sum()
total_return = (total_pl / total_invested) * 100

# Color total
pl_color = "green" if total_pl >= 0 else "red"

col1, col2, col3 = st.columns(3)

col1.metric(
    "Invested",
    f"${total_invested:,.2f}"
)

col2.metric(
    "Current value",
    f"${total_value:,.2f}"
)

with col3:
    st.metric(
        "P/L",
        f"${total_pl:,.2f}",
        f"{total_return:.2f}%"
    )

# Tabla
display = portfolio[
    [
        "Ticker",
        "Shares",
        "Purchase_Price",
        "Current_Price",
        "P_L",
        "Return_%"
    ]
].copy()

display.columns = [
    "Ticker",
    "Shares",
    "Avg Price",
    "Current Price",
    "P/L",
    "Return %"
]

def color_pl(value):
    if isinstance(value, (int, float)):
        if value > 0:
            return "color: green"
        elif value < 0:
            return "color: red"
    return ""

styled = (
    display.style
    .format({
        "Avg Price": "${:,.2f}",
        "Current Price": "${:,.2f}",
        "P/L": "${:,.2f}",
        "Return %": "{:.2f}%"
    })
    .map(color_pl, subset=["P/L", "Return %"])
)

st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True
)