import pandas as pd
import talib
import numpy as np

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
    max_signals = 4

    # RSI
    if latest['rsi_14'] < 40:
        bullish += 1
    elif latest['rsi_14'] > 60:
        bearish += 1

    # MACD
    if latest['macd'] > latest['macd_signal']:
        bullish += 1
    elif latest['macd'] < latest['macd_signal']:
        bearish += 1

    # SMA
    if latest['close'] > latest['sma_20']:
        bullish += 1
    elif latest['close'] < latest['sma_20']:
        bearish += 1

    # EMA
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
        confidence = 0

    return recommendation, confidence


def calculate_support_resistance(df: pd.DataFrame, window: int = 20):
    """
    Calculate nearest support and resistance levels using pivot points
    and recent highs/lows
    """
    recent_data = df.tail(window)
    
    # Find local minima (support) and maxima (resistance)
    lows = recent_data['low'].values
    highs = recent_data['high'].values
    current_price = df.iloc[-1]['close']
    
    # Support: highest low below current price
    potential_supports = lows[lows < current_price]
    if len(potential_supports) > 0:
        support = np.max(potential_supports)
    else:
        # If no support found, use 20-period low
        support = recent_data['low'].min()
    
    # Resistance: lowest high above current price
    potential_resistances = highs[highs > current_price]
    if len(potential_resistances) > 0:
        resistance = np.min(potential_resistances)
    else:
        # If no resistance found, use 20-period high
        resistance = recent_data['high'].max()
    
    return support, resistance


def calculate_entry_targets(latest: pd.Series, current_price: float, 
                            support: float, resistance: float, 
                            recommendation: str):
    """
    Calculate entry, stop loss, and target levels based on:
    - ATR for volatility
    - Support/Resistance levels
    - Recommendation signal
    """
    atr = latest['atr_14']
    
    if recommendation == 'Buy':
        # Entry: current price or slightly below
        entry = current_price
        
        # Stop loss: below support or 2x ATR below entry
        stop_atr = entry - (2 * atr)
        stop_support = support - (0.5 * atr)  # Slightly below support
        stop = max(stop_atr, stop_support)
        
        # Target: resistance or 3x ATR above entry (whichever is closer)
        target_atr = entry + (3 * atr)
        target_resistance = resistance
        target = min(target_atr, target_resistance)
        
    elif recommendation == 'Sell':
        # Entry: current price or slightly above
        entry = current_price
        
        # Stop loss: above resistance or 2x ATR above entry
        stop_atr = entry + (2 * atr)
        stop_resistance = resistance + (0.5 * atr)  # Slightly above resistance
        stop = min(stop_atr, stop_resistance)
        
        # Target: support or 3x ATR below entry
        target_atr = entry - (3 * atr)
        target_support = support
        target = max(target_atr, target_support)
        
    else:  # Hold
        # For hold, show potential levels anyway
        entry = current_price
        stop = support - (0.5 * atr)
        target = resistance
    
    # Calculate percentages and risk/reward
    stop_pct = abs((entry - stop) / entry) * 100
    target_pct = abs((target - entry) / entry) * 100
    
    # Risk/Reward ratio
    risk = abs(entry - stop)
    reward = abs(target - entry)
    rr_ratio = reward / risk if risk > 0 else 0
    
    return {
        'entry': entry,
        'stop': stop,
        'target': target,
        'stop_pct': stop_pct,
        'target_pct': target_pct,
        'rr_ratio': rr_ratio
    }
