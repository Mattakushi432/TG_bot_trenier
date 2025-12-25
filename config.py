import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Google Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', './data/users.db')

# Bot Configuration
BOT_NAME = "IFBB Pro Dual-Coach AI"
BOT_VERSION = "1.0.0"

# Validation
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не найден в переменных окружения")