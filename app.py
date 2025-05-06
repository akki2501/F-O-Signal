import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 F&O Buy/Sell Signal Generator (No pandas_ta)")

st.sidebar.header("📊 Input Parameters")
ticker = st.sidebar.text_input("Enter Ticker (NSE)", "RELIANCE.NS")
interval = st.sidebar.selectbox("Timeframe", ["15m", "30m", "1h"])
period = st.sidebar.selectbox("Lookback Period", ["5d", "7d", "1mo"])

@st.cache_data
def load_data(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval)
    return data.dropna()

data = load_data(ticker, period, interval)

# Calculate RSI
delta = data["Close"].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
data["RSI"] = 100 - (100 / (1 + rs))

# Calculate MACD
exp1 = data["Close"].ewm(span=12, adjust=False).mean()
exp2 = data["Close"].ewm(span=26, adjust=False).mean()
data["MACD"] = exp1 - exp2
data["Signal_Line"] = data["MACD"].ewm(span=9, adjust=False).mean()

# Buy/Sell Signal Logic
def signal(row):
    if row["RSI"] < 30 and row["MACD"] > row["Signal_Line"]:
        return "BUY"
    elif row["RSI"] > 70 and row["MACD"] < row["Signal_Line"]:
        return "SELL"
    else:
        return "HOLD"

data["Signal"] = data.apply(signal, axis=1)

# Show Signal
st.metric("💡 Latest Signal", data["Signal"].iloc[-1])
st.write("Latest Technicals:")
st.dataframe(data[["Close", "RSI", "MACD", "Signal_Line", "Signal"]].tail(5))

# Candlestick + MACD Plot
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

