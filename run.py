#!/usr/bin/env python3
"""
Скрипт для быстрого запуска бота
"""

import os
import sys

def check_requirements():
    """Проверка наличия необходимых файлов и переменных"""
    
    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("📝 Создайте файл .env на основе .env.example")
        print("🔑 Добавьте ваши API ключи:")
        print("   - TELEGRAM_BOT_TOKEN")
        print("   - GEMINI_API_KEY")
        return False
    
    # Проверяем установку зависимостей
    try:
        import telegram
        import google.generativeai
        import dotenv
    except ImportError as e:
        print(f"❌ Не установлены зависимости: {e}")
        print("📦 Установите зависимости: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Основная функция"""
    print("🏆 IFBB Pro Dual-Coach AI")
    print("=" * 50)
    
    if not check_requirements():
        sys.exit(1)
    
    print("✅ Все проверки пройдены!")
    print("🚀 Запускаем бота...")
    print("=" * 50)
    
    # Импортируем и запускаем основной модуль
    try:
        from main import main as run_bot
        run_bot()
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()