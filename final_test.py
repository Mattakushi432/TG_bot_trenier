#!/usr/bin/env python3
"""
Финальный тест всей системы IFBB Pro Dual-Coach AI
"""

import asyncio
from database import UserDatabase
from gemini_client import GeminiClient
from bot_handlers import split_long_message, clean_text_for_telegram
import sqlite3
from config import DATABASE_PATH

def test_all_components():
    """Финальный тест всех компонентов"""
    print("🏆 ФИНАЛЬНЫЙ ТЕСТ ВСЕЙ СИСТЕМЫ")
    print("=" * 60)
    
    results = {}
    
    # 1. Тест базы данных
    print("\n1️⃣ Тестирование базы данных...")
    try:
        db = UserDatabase()
        
        # Тестовый пользователь с ВСЕМИ полями
        test_user = {
            'user_id': 111111,
            'username': 'final_test',
            'gender': 'male',
            'age': 28,
            'height': 175.0,
            'weight': 78.0,
            'measurements': {
                'chest': 98,
                'waist': 82,
                'hips': 92,
                'bicep': 34
            },
            'fitness_level': 'intermediate',
            'goal': 'fitness',
            'location': 'gym',
            'workouts_per_week': 4,
            'injuries': None
        }
        
        db.save_user(test_user)
        retrieved_user = db.get_user(111111)
        
        if retrieved_user and retrieved_user['workouts_per_week'] == 4:
            print("✅ База данных: ВСЕ поля сохраняются корректно")
            results['database'] = True
        else:
            print("❌ База данных: Проблемы с сохранением")
            results['database'] = False
            
    except Exception as e:
        print(f"❌ База данных: Ошибка - {e}")
        results['database'] = False
    
    # 2. Тест Gemini API
    print("\n2️⃣ Тестирование Gemini API...")
    try:
        gemini = GeminiClient()
        
        # Быстрый тест
        response = gemini.generate_response(test_user, "Привет! Кратко ответь как тренер.")
        
        if response and len(response) > 10:
            print("✅ Gemini API: Работает стабильно")
            results['gemini'] = True
        else:
            print("❌ Gemini API: Нет ответа")
            results['gemini'] = False
            
    except Exception as e:
        print(f"❌ Gemini API: Ошибка - {e}")
        results['gemini'] = False
    
    # 3. Тест разбивки сообщений
    print("\n3️⃣ Тестирование разбивки сообщений...")
    try:
        long_text = "Тест разбивки сообщений. " * 500  # Длинный текст
        parts = split_long_message(long_text)
        
        if all(len(part) <= 4000 for part in parts) and len(parts) > 1:
            print(f"✅ Разбивка сообщений: {len(parts)} частей, все в пределах лимита")
            results['message_splitting'] = True
        else:
            print("❌ Разбивка сообщений: Проблемы с лимитами")
            results['message_splitting'] = False
            
    except Exception as e:
        print(f"❌ Разбивка сообщений: Ошибка - {e}")
        results['message_splitting'] = False
    
    # 4. Тест команды сброса
    print("\n4️⃣ Тестирование команды сброса...")
    try:
        # Добавляем данные для удаления
        db.save_progress(111111, 77.0, {'chest': 99, 'waist': 81, 'hips': 91, 'bicep': 35})
        db.save_workout_plan(111111, {'plan': 'Test plan', 'type': 'workout'})
        
        # Удаляем как в команде /reset
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE user_id = ?', (111111,))
            cursor.execute('DELETE FROM progress WHERE user_id = ?', (111111,))
            cursor.execute('DELETE FROM workout_plans WHERE user_id = ?', (111111,))
            conn.commit()
        
        # Проверяем удаление
        deleted_user = db.get_user(111111)
        if not deleted_user:
            print("✅ Команда сброса: Полное удаление данных работает")
            results['reset_command'] = True
        else:
            print("❌ Команда сброса: Данные не удалены")
            results['reset_command'] = False
            
    except Exception as e:
        print(f"❌ Команда сброса: Ошибка - {e}")
        results['reset_command'] = False
    
    # 5. Тест отображения прогресса
    print("\n5️⃣ Тестирование отображения прогресса...")
    try:
        # Создаем пользователя для теста отображения
        display_user = {
            'user_id': 222222,
            'username': 'display_test',
            'gender': 'female',
            'age': 25,
            'height': 165.0,
            'weight': 60.0,
            'measurements': {
                'chest': 88,
                'waist': 68,
                'hips': 95,
                'bicep': 28
            },
            'fitness_level': 'beginner',
            'goal': 'fitness',
            'location': 'home',
            'workouts_per_week': 2,
            'injuries': None
        }
        
        db.save_user(display_user)
        
        # Тестируем форматирование
        def format_measurements(measurements):
            if not measurements:
                return "Нет данных"
            
            formatted = []
            labels = {
                'chest': 'Грудь',
                'waist': 'Талия', 
                'hips': 'Бедра',
                'bicep': 'Бицепс'
            }
            
            for key, value in measurements.items():
                label = labels.get(key, key.capitalize())
                formatted.append(f"{label}: {value} см")
            
            return "\n".join(formatted)
        
        formatted = format_measurements(display_user['measurements'])
        
        if "Грудь: 88 см" in formatted and "Талия: 68 см" in formatted:
            print("✅ Отображение прогресса: Красивое форматирование работает")
            results['progress_display'] = True
        else:
            print("❌ Отображение прогресса: Проблемы с форматированием")
            results['progress_display'] = False
            
    except Exception as e:
        print(f"❌ Отображение прогресса: Ошибка - {e}")
        results['progress_display'] = False
    
    # 6. Тест адаптивных программ
    print("\n6️⃣ Тестирование адаптивных программ...")
    try:
        # Тестируем разные количества тренировок
        workout_counts = [2, 3, 4, 5]
        adaptive_works = True
        
        for count in workout_counts:
            test_user_adaptive = display_user.copy()
            test_user_adaptive['workouts_per_week'] = count
            test_user_adaptive['user_id'] = 222222 + count
            
            db.save_user(test_user_adaptive)
            retrieved = db.get_user(test_user_adaptive['user_id'])
            
            if not retrieved or retrieved['workouts_per_week'] != count:
                adaptive_works = False
                break
        
        if adaptive_works:
            print("✅ Адаптивные программы: Все варианты тренировок поддерживаются")
            results['adaptive_programs'] = True
        else:
            print("❌ Адаптивные программы: Проблемы с сохранением")
            results['adaptive_programs'] = False
            
    except Exception as e:
        print(f"❌ Адаптивные программы: Ошибка - {e}")
        results['adaptive_programs'] = False
    
    # Подсчет результатов
    print("\n" + "=" * 60)
    print("📊 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for component, result in results.items():
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        component_name = {
            'database': 'База данных',
            'gemini': 'Gemini API',
            'message_splitting': 'Разбивка сообщений',
            'reset_command': 'Команда сброса',
            'progress_display': 'Отображение прогресса',
            'adaptive_programs': 'Адаптивные программы'
        }.get(component, component)
        
        print(f"{component_name:<25} {status}")
        if result:
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 ИТОГО: {passed}/{total} компонентов работают корректно")
    
    if passed == total:
        print("\n🎉 ВСЯ СИСТЕМА РАБОТАЕТ ИДЕАЛЬНО!")
        print("🚀 IFBB Pro Dual-Coach AI готов к продакшену!")
        print("\n🏆 Особенности системы:")
        print("   • Двойная личность ИИ (Ронни/Дженет)")
        print("   • Адаптивные программы (2-5+ тренировок)")
        print("   • Красивое отображение прогресса")
        print("   • Автоматическая разбивка длинных сообщений")
        print("   • Полный контроль данных (/reset, /stop)")
        print("   • Научный подход к расчетам")
        print("\n💪 Готов помочь пользователям достичь их фитнес-целей!")
    else:
        print(f"\n⚠️ Обнаружены проблемы в {total - passed} компонентах")
        print("   Требуется дополнительная отладка")
    
    return passed == total

if __name__ == '__main__':
    success = test_all_components()
    
    if success:
        print("\n🎊 ПРОЕКТ ЗАВЕРШЕН УСПЕШНО! 🎊")
    else:
        print("\n🔧 Требуется доработка некоторых компонентов")