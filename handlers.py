from aiogram import types
from data_fetcher import fetch_ohlcv
from indicators import calculate_indicators, generate_recommendation

async def start_handler(message: types.Message):
    await message.reply("Welcome! Send me a message like: BTC/USDT 1h\nTo get indicators and recommendation.")

async def indicators_handler(message: types.Message):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            raise ValueError("Invalid input. Use: COIN TIMEFRAME (e.g., BTC/USDT 1h)")

        symbol = parts[0].upper() + '/USDT'
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