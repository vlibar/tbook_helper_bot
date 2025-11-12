from aiogram import types
from data_fetcher import fetch_ohlcv
from indicators import (
    calculate_indicators, 
    generate_recommendation,
    calculate_support_resistance,
    calculate_entry_targets
)

async def start_handler(message: types.Message):
    await message.reply(
        "Welcome! 🚀\n\n"
        "Send me a cryptocurrency symbol to get multi-timeframe analysis.\n\n"
        "Examples:\n"
        "• BTC\n"
        "• ETH\n"
        "• SOL\n"
        "• DOGE"
    )

async def indicators_handler(message: types.Message):
    try:
        symbol = message.text.strip().upper()
        if '/' not in symbol:
            symbol = f"{symbol}/USDT"
        
        # Validate basic format
        if not symbol or len(symbol) < 3:
            raise ValueError("Invalid symbol. Use: BTC, ETH, SOL, etc.")

        # Timeframes to analyze
        timeframes = ['5m', '1h', '4h', '12h', '1d']
        
        # Send "processing" message
        processing_msg = await message.reply(f"🔄 Analyzing {symbol}...")
        
        # Fetch data for all timeframes
        recommendations = {}
        main_df = None  # We'll use 1h for price changes and support/resistance
        
        for tf in timeframes:
            try:
                df = await fetch_ohlcv(symbol, tf, limit=100)
                if df.empty:
                    continue
                    
                df = calculate_indicators(df)
                latest = df.iloc[-1]
                recommendation, confidence = generate_recommendation(latest)
                recommendations[tf] = (recommendation, confidence)
                
                # Store 1h data for detailed analysis
                if tf == '1h':
                    main_df = df
                    
            except Exception as e:
                recommendations[tf] = ("Error", 0)
        
        if not recommendations or main_df is None:
            raise ValueError("Could not fetch data. Check symbol.")
        
        # Get current price from 1h timeframe
        current_price = main_df.iloc[-1]['close']
        
        # Calculate price changes
        price_changes = await calculate_price_changes(symbol, current_price)
        
        # Calculate support and resistance
        support, resistance = calculate_support_resistance(main_df)
        
        # Calculate entry, stop, and target levels
        latest = main_df.iloc[-1]
        entry_levels = calculate_entry_targets(
            latest, 
            current_price, 
            support, 
            resistance,
            recommendations.get('1h', ('Hold', 0))[0]
        )
        
        # Format response
        response = f"📊 **{symbol}**\n"
        response += f"💰 Price: ${current_price:.2f}\n\n"
        
        # Multi-timeframe recommendations
        response += "⏱ **Timeframe Signals:**\n"
        for tf in timeframes:
            rec, conf = recommendations.get(tf, ("N/A", 0))
            emoji = "🟢" if rec == "Buy" else "🔴" if rec == "Sell" else "⚪"
            response += f"• {tf}: {emoji} {rec} ({conf:.0f}%)\n"
        
        response += "\n📈 **Price Changes:**\n"
        for period, change in price_changes.items():
            emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            response += f"• {period}: {emoji} {change:+.2f}%\n"
        
        # Support/Resistance
        response += "\n🎯 **Key Levels:**\n"
        support_dist = ((current_price - support) / current_price) * 100
        resistance_dist = ((resistance - current_price) / current_price) * 100
        response += f"• Support: ${support:.2f} ({support_dist:.1f}% below)\n"
        response += f"• Resistance: ${resistance:.2f} ({resistance_dist:.1f}% above)\n"
        
        # Entry/Stop/Target levels
        if entry_levels:
            response += "\n💡 **Trading Levels:**\n"
            response += f"• Entry: ${entry_levels['entry']:.2f}\n"
            response += f"• Stop Loss: ${entry_levels['stop']:.2f} (-{entry_levels['stop_pct']:.1f}%)\n"
            response += f"• Target: ${entry_levels['target']:.2f} (+{entry_levels['target_pct']:.1f}%)\n"
            response += f"• Risk/Reward: 1:{entry_levels['rr_ratio']:.1f}\n"
        
        # Delete processing message and send result
        await processing_msg.delete()
        await message.reply(response, parse_mode='Markdown')

    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}\nPlease try again with a valid symbol.")


async def calculate_price_changes(symbol: str, current_price: float):
    """Calculate price changes over different periods"""
    changes = {}
    periods = {
        '15m': 15,
        '1h': 60,
        '8h': 480,
        '24h': 1440
    }
    
    for label, minutes in periods.items():
        try:
            # Fetch historical data
            if minutes <= 60:
                df = await fetch_ohlcv(symbol, '1m', limit=minutes + 1)
            elif minutes <= 480:
                df = await fetch_ohlcv(symbol, '5m', limit=(minutes // 5) + 1)
            else:
                df = await fetch_ohlcv(symbol, '1h', limit=(minutes // 60) + 1)
            
            if not df.empty:
                old_price = df.iloc[0]['close']
                change_pct = ((current_price - old_price) / old_price) * 100
                changes[label] = change_pct
            else:
                changes[label] = 0.0
        except:
            changes[label] = 0.0
    
    return changes
