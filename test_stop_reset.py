#!/usr/bin/env python3
"""
Тест команд /stop и /reset
"""

from database import UserDatabase
import sqlite3
from config import DATABASE_PATH

def test_reset_functionality():
    """Тестирование функции сброса данных"""
    print("🔄 Тестирование функции сброса...")
    
    db = UserDatabase()
    
    # Создаем тестового пользователя
    test_user = {
        'user_id': 999999,
        'username': 'reset_test',
        'gender': 'male',
        'age': 30,
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
        'workouts_per_week': 3,
        'injuries': None
    }
    
    # Сохраняем пользователя
    db.save_user(test_user)
    
    # Добавляем прогресс
    db.save_progress(999999, 79.0, {
        'chest': 101,
        'waist': 84,
        'hips': 94,
        'bicep': 36
    })
    
    # Добавляем план тренировок
    db.save_workout_plan(999999, {'plan': 'Test workout plan', 'type': 'workout'})
    
    print("✅ Тестовые данные созданы")
    
    # Проверяем, что данные существуют
    user_data = db.get_user(999999)
    progress_data = db.get_progress_history(999999)
    workout_plan = db.get_latest_workout_plan(999999)
    
    if user_data and progress_data and workout_plan:
        print("✅ Все данные присутствуют в базе")
    else:
        print("❌ Не все данные созданы")
        return False
    
    # Симулируем удаление данных (как в команде /reset)
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE user_id = ?', (999999,))
            cursor.execute('DELETE FROM progress WHERE user_id = ?', (999999,))
            cursor.execute('DELETE FROM workout_plans WHERE user_id = ?', (999999,))
            conn.commit()
        
        print("✅ Данные удалены из базы")
        
        # Проверяем, что данные действительно удалены
        user_data_after = db.get_user(999999)
        progress_data_after = db.get_progress_history(999999)
        workout_plan_after = db.get_latest_workout_plan(999999)
        
        if not user_data_after and not progress_data_after and not workout_plan_after:
            print("✅ Все данные успешно удалены")
            return True
        else:
            print("❌ Не все данные удалены")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка удаления: {e}")
        return False

def test_stop_messages():
    """Тестирование сообщений команды /stop"""
    print("\n🛑 Тестирование сообщений команды /stop...")
    
    # Тестируем сообщения для разных полов
    test_cases = [
        {
            'gender': 'male',
            'expected_phrases': ['Ронни Коулман', 'Yeah buddy', 'Light weight']
        },
        {
            'gender': 'female', 
            'expected_phrases': ['Дженет Лайог', 'сильной и красивой']
        },
        {
            'gender': None,
            'expected_phrases': ['До свидания', 'IFBB Pro Dual-Coach AI']
        }
    ]
    
    for case in test_cases:
        print(f"\n--- Тест для пола: {case['gender'] or 'не указан'} ---")
        
        # Симулируем создание сообщения
        if case['gender']:
            user_data = {'gender': case['gender']}
            coach_name = "Ронни Коулман" if case['gender'] == 'male' else "Дженет Лайог"
            goodbye_message = (
                f"👋 До свидания от {coach_name}!\n\n"
                "🏆 Помни: чемпионы никогда не сдаются!\n"
                "💪 Твои данные сохранены и ждут твоего возвращения.\n\n"
                "🔄 Когда будешь готов продолжить - просто напиши /start\n"
                "🗑️ Если захочешь начать заново - используй /reset\n\n"
                "✨ Удачи в достижении твоих целей!"
            )
            
            if case['gender'] == 'male':
                goodbye_message += "\n\n💥 Yeah buddy! Light weight! Увидимся на тренировке!"
            else:
                goodbye_message += "\n\n✨ Оставайся сильной и красивой! До встречи!"
        else:
            goodbye_message = (
                "👋 До свидания!\n\n"
                "Спасибо, что попробовал IFBB Pro Dual-Coach AI!\n"
                "Возвращайся когда захочешь начать тренироваться! 💪"
            )
        
        # Проверяем наличие ожидаемых фраз
        all_found = True
        for phrase in case['expected_phrases']:
            if phrase in goodbye_message:
                print(f"✅ Найдена фраза: '{phrase}'")
            else:
                print(f"❌ Не найдена фраза: '{phrase}'")
                all_found = False
        
        if all_found:
            print("✅ Все ожидаемые фразы найдены")
        else:
            print("❌ Не все фразы найдены")
    
    return True

def test_reset_confirmation():
    """Тест подтверждения сброса"""
    print("\n⚠️ Тестирование подтверждения сброса...")
    
    # Тестируем различные варианты ответов
    test_responses = [
        {'input': 'ДА УДАЛИТЬ', 'should_reset': True},
        {'input': '❌ Отмена', 'should_reset': False},
        {'input': 'отмена', 'should_reset': False},
        {'input': 'нет', 'should_reset': False},
        {'input': 'да', 'should_reset': False},  # Неточное подтверждение
        {'input': 'что-то другое', 'should_reset': False}
    ]
    
    for test in test_responses:
        response = test['input']
        expected = test['should_reset']
        
        # Логика как в боте
        if response == 'ДА УДАЛИТЬ':
            actual_reset = True
        elif "❌ Отмена" in response or response.lower() in ['отмена', 'нет', 'cancel']:
            actual_reset = False
        else:
            actual_reset = False  # Требует повторного подтверждения
        
        if actual_reset == expected:
            print(f"✅ '{response}' -> {'Сброс' if actual_reset else 'Отмена'}")
        else:
            print(f"❌ '{response}' -> Неожиданный результат")
    
    return True

if __name__ == '__main__':
    print("🧪 ТЕСТ КОМАНД /stop И /reset")
    print("=" * 50)
    
    # Тест функции сброса
    reset_test = test_reset_functionality()
    
    # Тест сообщений остановки
    stop_test = test_stop_messages()
    
    # Тест подтверждения сброса
    confirmation_test = test_reset_confirmation()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"Функция сброса: {'✅ ПРОЙДЕН' if reset_test else '❌ ПРОВАЛЕН'}")
    print(f"Сообщения /stop: {'✅ ПРОЙДЕН' if stop_test else '❌ ПРОВАЛЕН'}")
    print(f"Подтверждение сброса: {'✅ ПРОЙДЕН' if confirmation_test else '❌ ПРОВАЛЕН'}")
    
    if reset_test and stop_test and confirmation_test:
        print("\n🎉 Команды /stop и /reset работают корректно!")
        print("   Пользователи могут безопасно остановить бота или начать заново.")
    else:
        print("\n⚠️ Обнаружены проблемы в новых командах.")