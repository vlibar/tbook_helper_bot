import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import ccxt
import pandas as pd
import talib
import os

# Replace with your Telegram Bot Token
# BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Or hardcode it: 'YOUR_BOT_TOKEN_HERE'

# Initialize CCXT exchange (Binance as example)
exchange = ccxt.binance({
    'rateLimit': 1200,
})

async def fetch_ohlcv(symbol: str, timeframe: str, limit: int = 100):
    ohlcv = await asyncio.get_event_loop().run_in_executor(
        None, exchange.fetch_ohlcv, symbol, timeframe, None, limit
    )
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df.astype(float)
    return df

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

# Bot setup
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.reply("Welcome! Send me a message like: BTC/USDT 1h\nTo get indicators and recommendation.")

@dp.message()
async def indicators_handler(message: types.Message):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            raise ValueError("Invalid input. Use: COIN TIMEFRAME (e.g., BTC/USDT 1h)")

        symbol = parts[0].upper()
        timeframe = parts[1]

        # Fetch data
        df = await fetch_ohlcv(symbol, timeframe, limit=100)
        if df.empty:
            raise ValueError("No data fetched. Check symbol and timeframe.")

        # Calculate indicators
        df = calculate_indicators(df)
        latest = df.iloc[-1]

        # Generate recommendation
        recommendation, confidence = generate_recommendation(latest)

        # Format response
        response = f"**{symbol} - {timeframe}**\n\n"
        response += f"Latest Close: {latest['close']:.2f}\n"
        response += f"SMA (20): {latest['sma_20']:.2f}\n"
        response += f"EMA (20): {latest['ema_20']:.2f}\n"
        response += f"RSI (14): {latest['rsi_14']:.2f}\n"
        response += f"MACD: {latest['macd']:.4f}\n"
        response += f"MACD Signal: {latest['macd_signal']:.4f}\n"
        response += f"MACD Hist: {latest['macd_hist']:.4f}\n"
        response += f"ATR (14): {latest['atr_14']:.2f}\n"
        response += f"ATR (14) / Close: {latest['atr_14']/latest['close']:.1%}\n\n"
        response += f"**Recommendation: {recommendation}**\n"
        response += f"Confidence: {confidence:.0f}%"

        await message.reply(response, parse_mode='Markdown')

    except Exception as e:
        await message.reply(f"Error: {str(e)}\nPlease try again with valid inputs.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())