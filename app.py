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
# TICKERS
# -------------------------

tickers = portfolio["Ticker"].unique().tolist()

# Agregamos USD/MXN
download_tickers = tickers + ["MXN=X"]


# -------------------------
# DESCARGAR PRECIOS
# -------------------------

@st.cache_data(ttl=300)
def get_prices(tickers):

    data = yf.download(
        tickers,
        period="5d",
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    return data


data = get_prices(download_tickers)


# -------------------------
# EXTRAER ÚLTIMOS PRECIOS
# -------------------------

prices = {}

for ticker in tickers:

    try:
        series = data["Close"][ticker].dropna()

        if not series.empty:
            prices[ticker] = float(series.iloc[-1])
        else:
            prices[ticker] = None

    except:
        prices[ticker] = None


# USD/MXN
try:

    fx_series = data["Close"]["MXN=X"].dropna()

    usd_mxn = float(fx_series.iloc[-1])

except:

    usd_mxn = None


# -------------------------
# CONVERTIR A MXN
# -------------------------

def price_in_mxn(ticker):

    price = prices.get(ticker)

    if price is None:
        return None

    # Yahoo ya entrega .MX en pesos mexicanos
    if ticker.endswith(".MX"):
        return price

    # Los demás activos están en USD
    if usd_mxn is None:
        return None

    return price * usd_mxn


portfolio["Current_Price"] = portfolio["Ticker"].apply(
    price_in_mxn
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
# VALIDAR PRECIOS
# -------------------------

missing = portfolio[
    portfolio["Current_Price"].isna()
]["Ticker"].unique()

if len(missing) > 0:

    st.warning(
        "No se pudo obtener precio para: "
        + ", ".join(missing)
    )


# -------------------------
# TOTALES
# -------------------------

valid = portfolio.dropna(
    subset=["Current_Value"]
)

total_invested = valid["Invested"].sum()
total_value = valid["Current_Value"].sum()

total_pl = (
    total_value -
    total_invested
)

if total_invested > 0:

    total_return = (
        total_pl /
        total_invested
    ) * 100

else:

    total_return = 0


# -------------------------
# MÉTRICAS
# -------------------------

col1, col2, col3, col4 = st.columns(4)

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

if usd_mxn is not None:

    col4.metric(
        "USD/MXN",
        f"${usd_mxn:.2f}"
    )

else:

    col4.metric(
        "USD/MXN",
        "N/D"
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

    if pd.isna(value):
        return ""

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
    }, na_rep="N/D")
    .map(
        color_result,
        subset=[
            "P/L",
            "Rendimiento"
        ]
    )
)


st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True
)