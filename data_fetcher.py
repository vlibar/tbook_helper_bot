import asyncio
import ccxt
import pandas as pd

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