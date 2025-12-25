#!/usr/bin/env python3
"""
Быстрый тест основных функций бота
"""

from database import UserDatabase
from gemini_client import GeminiClient
from bot_handlers import split_long_message, clean_text_for_telegram

def quick_test():
    """Быстрое тестирование"""
    print("⚡ Быстрый тест компонентов...")
    
    # Тест базы данных
    try:
        db = UserDatabase()
        print("✅ База данных: OK")
    except Exception as e:
        print(f"❌ База данных: {e}")
        return False
    
    # Тест Gemini клиента (только инициализация)
    try:
        gemini = GeminiClient()
        print("✅ Gemini клиент: OK")
    except Exception as e:
        print(f"❌ Gemini клиент: {e}")
        return False
    
    # Тест разбивки сообщений
    try:
        long_text = "Тест " * 1000  # Длинный текст
        parts = split_long_message(long_text)
        if all(len(part) <= 4000 for part in parts):
            print("✅ Разбивка сообщений: OK")
        else:
            print("❌ Разбивка сообщений: части превышают лимит")
            return False
    except Exception as e:
        print(f"❌ Разбивка сообщений: {e}")
        return False
    
    print("\n🎉 Все основные компоненты работают!")
    return True

if __name__ == '__main__':
    print("🏆 БЫСТРЫЙ ТЕСТ БОТА")
    print("=" * 30)
    
    success = quick_test()
    
    if success:
        print("\n✅ Бот готов к использованию!")
        print("   Запустите: python main.py")
    else:
        print("\n❌ Обнаружены проблемы")