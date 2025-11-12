import os

# Replace with your Telegram Bot Token
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Or hardcode it: 'YOUR_BOT_TOKEN_HERE'

# CCXT Exchange configuration
EXCHANGE_CONFIG = {
    'rateLimit': 1200,
}