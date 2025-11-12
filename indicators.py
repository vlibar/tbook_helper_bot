import pandas as pd
import talib

def calculate_indicators(df: pd.DataFrame):
    df['sma_20'] = talib.SMA(df['close'], timeperiod=20)
    df['ema_20'] = talib.EMA(df['close'], timeperiod=20)
    df['rsi_14'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(
        df['close'], fastperiod=12, slowperiod=26, signalperiod=9
    )
    df['atr_14'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    return df

def generate_recommendation(latest: pd.Series):
    bullish = 0
    bearish = 0
    max_signals = 4  # RSI, MACD, Close > SMA, Close > EMA

    # RSI: <30 buy (oversold), >70 sell (overbought). Here <40 bullish, >60 bearish for milder
    if latest['rsi_14'] < 40:
        bullish += 1
    elif latest['rsi_14'] > 60:
        bearish += 1

    # MACD: MACD > Signal bullish
    if latest['macd'] > latest['macd_signal']:
        bullish += 1
    elif latest['macd'] < latest['macd_signal']:
        bearish += 1

    # Close > SMA bullish
    if latest['close'] > latest['sma_20']:
        bullish += 1
    elif latest['close'] < latest['sma_20']:
        bearish += 1

    # Close > EMA bullish
    if latest['close'] > latest['ema_20']:
        bullish += 1
    elif latest['close'] < latest['ema_20']:
        bearish += 1

    net_score = bullish - bearish
    confidence = abs(net_score) / max_signals * 100

    if net_score > 0:
        recommendation = 'Buy'
    elif net_score < 0:
        recommendation = 'Sell'
    else:
        recommendation = 'Hold'
        confidence = 0  # No clear signal

    return recommendation, confidence