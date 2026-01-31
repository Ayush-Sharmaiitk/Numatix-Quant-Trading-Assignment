import pandas as pd
import ta

def add_indicators_15m(df):
    df = df.copy()
    df["SMA_20"] = ta.trend.sma_indicator(df["Close"], window=20)
    df["RSI_14"] = ta.momentum.rsi(df["Close"], window=14)
    return df

def add_indicators_1h(df):
    df = df.copy()
    df["SMA_50"] = ta.trend.sma_indicator(df["Close"], window=50)
    return df
