import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 F&O Buy/Sell Signal Generator")

st.sidebar.header("📊 Input Parameters")
ticker = st.sidebar.text_input("Enter Ticker (NSE)", "RELIANCE.NS")
interval = st.sidebar.selectbox("Timeframe", ["15m", "30m", "1h"])
period = st.sidebar.selectbox("Lookback Period", ["5d", "7d", "1mo"])

@st.cache_data
def load_data(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval)
    return data.dropna()

data = load_data(ticker, period, interval)

data["RSI"] = ta.rsi(data["Close"], length=14)
macd = ta.macd(data["Close"])
data["MACD"] = macd["MACD_12_26_9"]
data["Signal_Line"] = macd["MACDs_12_26_9"]

def signal(row):
    if row["RSI"] < 30 and row["MACD"] > row["Signal_Line"]:
        return "BUY"
    elif row["RSI"] > 70 and row["MACD"] < row["Signal_Line"]:
        return "SELL"
    else:
        return "HOLD"

data["Signal"] = data.apply(signal, axis=1)

st.metric("💡 Latest Signal", data["Signal"].iloc[-1])
st.write("Latest Technicals:")
st.dataframe(data[["Close", "RSI", "MACD", "Signal_Line", "Signal"]].tail(5))

fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data.index, open=data['Open'], high=data['High'],
    low=data['Low'], close=data['Close'], name='Price'
))
fig.add_trace(go.Scatter(
    x=data.index, y=data["MACD"], name='MACD', line=dict(color='blue')
))
fig.add_trace(go.Scatter(
    x=data.index, y=data["Signal_Line"], name='Signal Line', line=dict(color='orange')
))
fig.update_layout(title=f'{ticker} Price & MACD Signals', height=600)
st.plotly_chart(fig, use_container_width=True)
