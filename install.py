#!/usr/bin/env python3
"""
Скрипт автоматической установки и настройки бота
"""

import os
import sys
import subprocess
import shutil

def print_header():
    """Вывод заголовка"""
    print("🏆" + "=" * 48 + "🏆")
    print("    IFBB Pro Dual-Coach AI - Установка")
    print("🏆" + "=" * 48 + "🏆")
    print()

def check_python_version():
    """Проверка версии Python"""
    print("🔍 Проверка версии Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше!")
        print(f"   Текущая версия: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_dependencies():
    """Установка зависимостей"""
    print("\n📦 Установка зависимостей...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Зависимости установлены успешно!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка установки зависимостей!")
        return False

def create_env_file():
    """Создание файла .env"""
    print("\n⚙️ Настройка переменных окружения...")
    
    if os.path.exists('.env'):
        print("📄 Файл .env уже существует")
        overwrite = input("   Перезаписать? (y/N): ").lower().strip()
        if overwrite != 'y':
            return True
    
    # Копируем пример
    if os.path.exists('.env.example'):
        shutil.copy('.env.example', '.env')
        print("✅ Создан файл .env на основе .env.example")
    else:
        # Создаем базовый .env
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("# Telegram Bot Configuration\n")
            f.write("TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here\n\n")
            f.write("# Google Gemini API Configuration\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n\n")
            f.write("# Database Configuration\n")
            f.write("DATABASE_PATH=./data/users.db\n")
        print("✅ Создан базовый файл .env")
    
    return True

def setup_api_keys():
    """Настройка API ключей"""
    print("\n🔑 Настройка API ключей...")
    print("   Вам понадобятся:")
    print("   1. Telegram Bot Token (от @BotFather)")
    print("   2. Google Gemini API Key (от Google AI Studio)")
    print()
    
    setup_now = input("   Настроить ключи сейчас? (y/N): ").lower().strip()
    
    if setup_now == 'y':
        # Telegram Bot Token
        telegram_token = input("   Введите Telegram Bot Token: ").strip()
        
        # Gemini API Key
        gemini_key = input("   Введите Gemini API Key: ").strip()
        
        # Обновляем .env файл
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace('your_telegram_bot_token_here', telegram_token)
        content = content.replace('your_gemini_api_key_here', gemini_key)
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ API ключи сохранены!")
    else:
        print("⚠️  Не забудьте настроить API ключи в файле .env")
    
    return True

def create_directories():
    """Создание необходимых директорий"""
    print("\n📁 Создание директорий...")
    
    directories = ['data', 'logs']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Создана директория: {directory}")
        else:
            print(f"📁 Директория уже существует: {directory}")
    
    return True

def final_check():
    """Финальная проверка"""
    print("\n🔍 Финальная проверка...")
    
    # Проверяем наличие .env
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        return False
    
    # Проверяем содержимое .env
    with open('.env', 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    if 'your_telegram_bot_token_here' in env_content:
        print("⚠️  Telegram Bot Token не настроен в .env")
    
    if 'your_gemini_api_key_here' in env_content:
        print("⚠️  Gemini API Key не настроен в .env")
    
    print("✅ Установка завершена!")
    return True

def print_instructions():
    """Вывод инструкций по запуску"""
    print("\n" + "=" * 50)
    print("🚀 ИНСТРУКЦИИ ПО ЗАПУСКУ")
    print("=" * 50)
    print()
    print("1. Настройте API ключи в файле .env:")
    print("   - TELEGRAM_BOT_TOKEN (получить от @BotFather)")
    print("   - GEMINI_API_KEY (получить от Google AI Studio)")
    print()
    print("2. Запустите бота:")
    print("   python run.py")
    print("   или")
    print("   python main.py")
    print()
    print("3. Найдите вашего бота в Telegram и отправьте /start")
    print()
    print("📚 Дополнительная информация в README.md")
    print("🐛 Проблемы? Проверьте логи в директории logs/")
    print()

def main():
    """Основная функция установки"""
    print_header()
    
    # Проверка Python
    if not check_python_version():
        sys.exit(1)
    
    # Установка зависимостей
    if not install_dependencies():
        sys.exit(1)
    
    # Создание .env файла
    if not create_env_file():
        sys.exit(1)
    
    # Настройка API ключей
    if not setup_api_keys():
        sys.exit(1)
    
    # Создание директорий
    if not create_directories():
        sys.exit(1)
    
    # Финальная проверка
    if not final_check():
        sys.exit(1)
    
    # Инструкции
    print_instructions()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Установка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка установки: {e}")
        sys.exit(1)