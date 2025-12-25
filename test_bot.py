#!/usr/bin/env python3
"""
Тест основных компонентов бота
"""

import asyncio
from database import UserDatabase
from gemini_client import GeminiClient

async def test_bot_components():
    """Тестирование компонентов бота"""
    print("🤖 Тестирование компонентов бота...")
    
    # Тест базы данных
    print("\n1️⃣ Тестирование базы данных...")
    try:
        db = UserDatabase()
        
        # Тестовый пользователь
        test_user = {
            'user_id': 999999,
            'username': 'test_user',
            'gender': 'male',
            'age': 25,
            'height': 180.0,
            'weight': 80.0,
            'measurements': {
                'chest': 100,
                'waist': 85,
                'hips': 95,
                'bicep': 35
            },
            'fitness_level': 'intermediate',
            'goal': 'fitness',
            'location': 'gym',
            'injuries': None
        }
        
        db.save_user(test_user)
        retrieved_user = db.get_user(999999)
        
        if retrieved_user:
            print("✅ База данных работает корректно")
        else:
            print("❌ Ошибка работы с базой данных")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False
    
    # Тест Gemini клиента
    print("\n2️⃣ Тестирование Gemini клиента...")
    try:
        gemini = GeminiClient()
        
        # Тестовый запрос
        test_response = gemini.generate_response(
            test_user, 
            "Привет! Создай краткий план тренировок на день."
        )
        
        if test_response and len(test_response) > 10:
            print("✅ Gemini клиент работает корректно")
            print(f"   Пример ответа: {test_response[:100]}...")
        else:
            print("❌ Gemini клиент не отвечает")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка Gemini клиента: {e}")
        return False
    
    # Тест генерации плана тренировок
    print("\n3️⃣ Тестирование генерации плана тренировок...")
    try:
        print("   Генерирую план... (это может занять время)")
        workout_plan = gemini.generate_workout_plan(test_user)
        
        if workout_plan and len(workout_plan) > 50:
            print("✅ Генерация плана тренировок работает")
            print(f"   Длина плана: {len(workout_plan)} символов")
            print(f"   Начало плана: {workout_plan[:150]}...")
        else:
            print("❌ Ошибка генерации плана тренировок")
            print(f"   Получен ответ: {workout_plan}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка генерации плана: {e}")
        return False
    
    print("\n🎉 Все компоненты бота работают корректно!")
    return True

if __name__ == '__main__':
    print("🏆 ТЕСТ КОМПОНЕНТОВ БОТА")
    print("=" * 50)
    
    try:
        success = asyncio.run(test_bot_components())
        
        if success:
            print("\n✅ Бот готов к запуску!")
            print("   Запустите: python main.py")
        else:
            print("\n❌ Обнаружены проблемы в компонентах бота")
            
    except Exception as e:
        print(f"\n❌ Критическая ошибка тестирования: {e}")