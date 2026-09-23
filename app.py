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


# -------------------------
# CARGAR PORTAFOLIO
# -------------------------

portfolio = pd.read_csv("portfolio.csv")
portfolio.columns = portfolio.columns.str.strip()


# -------------------------
# PRECIO ACTUAL
# -------------------------

@st.cache_data(ttl=300)
def get_price(ticker):

    data = yf.Ticker(ticker).history(period="5d")

    if data.empty:
        return None

    return data["Close"].iloc[-1]


# -------------------------
# TIPO DE CAMBIO USD/MXN
# -------------------------

usd_mxn = get_price("MXN=X")


# -------------------------
# CONVERTIR TODO A MXN
# -------------------------

def current_price_mxn(ticker):

    price = get_price(ticker)

    if price is None:
        return None

    # Acciones mexicanas
    if ticker.endswith(".MX"):
        return price

    # Activos estadounidenses
    return price * usd_mxn


portfolio["Current_Price"] = portfolio["Ticker"].apply(
    current_price_mxn
)


# -------------------------
# CÁLCULOS
# -------------------------

portfolio["Invested"] = (
    portfolio["Shares"] *
    portfolio["Purchase_Price"]
)

portfolio["Current_Value"] = (
    portfolio["Shares"] *
    portfolio["Current_Price"]
)

portfolio["P_L"] = (
    portfolio["Current_Value"] -
    portfolio["Invested"]
)

portfolio["Return_%"] = (
    portfolio["P_L"] /
    portfolio["Invested"]
) * 100


# -------------------------
# TOTALES
# -------------------------

total_invested = portfolio["Invested"].sum()
total_value = portfolio["Current_Value"].sum()

total_pl = total_value - total_invested

total_return = (
    total_pl / total_invested
) * 100


# -------------------------
# MÉTRICAS
# -------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Invertido",
    f"${total_invested:,.2f} MXN"
)

col2.metric(
    "Valor actual",
    f"${total_value:,.2f} MXN"
)

col3.metric(
    "Plusvalía / Minusvalía",
    f"${total_pl:,.2f}",
    f"{total_return:.2f}%"
)


# -------------------------
# TABLA
# -------------------------

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
    "Compra",
    "Actual",
    "P/L",
    "Rendimiento"
]


# -------------------------
# COLORES
# -------------------------

def color_result(value):

    if value > 0:
        return "color: green"

    if value < 0:
        return "color: red"

    return ""


styled = (
    display.style
    .format({
        "Compra": "${:,.2f}",
        "Actual": "${:,.2f}",
        "P/L": "${:,.2f}",
        "Rendimiento": "{:.2f}%"
    })
    .map(
        color_result,
        subset=["P/L", "Rendimiento"]
    )
)


st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True
)


# -------------------------
# FX
# -------------------------

st.caption(
    f"USD/MXN: {usd_mxn:.2f}"
)