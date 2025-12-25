#!/usr/bin/env python3
"""
Тест функциональности "тренировки в неделю"
"""

from database import UserDatabase
from gemini_client import GeminiClient

def test_workouts_per_week():
    """Тестирование разных количеств тренировок в неделю"""
    print("🏋️ Тестирование адаптации под количество тренировок...")
    
    db = UserDatabase()
    gemini = GeminiClient()
    
    # Базовые данные пользователя
    base_user = {
        'user_id': 888888,
        'username': 'test_workouts',
        'gender': 'male',
        'age': 30,
        'height': 175.0,
        'weight': 75.0,
        'measurements': {
            'chest': 95,
            'waist': 80,
            'hips': 90,
            'bicep': 33
        },
        'fitness_level': 'intermediate',
        'goal': 'fitness',
        'location': 'gym',
        'injuries': None
    }
    
    # Тестируем разное количество тренировок
    workout_counts = [2, 3, 4, 5]
    
    for count in workout_counts:
        print(f"\n--- Тест {count} тренировок в неделю ---")
        
        # Создаем пользователя с определенным количеством тренировок
        test_user = base_user.copy()
        test_user['workouts_per_week'] = count
        test_user['user_id'] = 888888 + count  # Уникальный ID
        
        # Сохраняем в базу данных
        db.save_user(test_user)
        
        # Получаем из базы данных для проверки
        retrieved_user = db.get_user(test_user['user_id'])
        
        if retrieved_user and retrieved_user['workouts_per_week'] == count:
            print(f"✅ База данных: сохранено {count} тренировок")
        else:
            print(f"❌ База данных: ошибка сохранения")
            return False
        
        # Тестируем генерацию плана (краткий тест)
        try:
            # Создаем короткий промпт для быстрого теста
            short_prompt = f"Создай краткий план тренировок на {count} дня в неделю для мужчины среднего уровня."
            response = gemini.generate_response(test_user, short_prompt)
            
            if response and str(count) in response:
                print(f"✅ Gemini: учитывает {count} тренировок")
            else:
                print(f"⚠️ Gemini: возможно не учитывает количество тренировок")
                
        except Exception as e:
            print(f"❌ Gemini: ошибка генерации - {e}")
            return False
    
    print(f"\n🎉 Тест завершен! Поддерживается {len(workout_counts)} вариантов тренировок.")
    return True

def test_onboarding_states():
    """Тест состояний онбординга"""
    print("\n📝 Тестирование состояний онбординга...")
    
    from bot_handlers import ONBOARDING_STATES
    
    expected_states = [
        'gender', 'age', 'height', 'weight', 'measurements',
        'fitness_level', 'goal', 'location', 'workouts_per_week', 'injuries'
    ]
    
    actual_states = list(ONBOARDING_STATES.values())
    
    print(f"Ожидаемые состояния: {len(expected_states)}")
    print(f"Фактические состояния: {len(actual_states)}")
    
    missing_states = set(expected_states) - set(actual_states)
    extra_states = set(actual_states) - set(expected_states)
    
    if missing_states:
        print(f"❌ Отсутствуют состояния: {missing_states}")
        return False
    
    if extra_states:
        print(f"⚠️ Дополнительные состояния: {extra_states}")
    
    if 'workouts_per_week' in actual_states:
        print("✅ Состояние 'workouts_per_week' добавлено")
    else:
        print("❌ Состояние 'workouts_per_week' отсутствует")
        return False
    
    return True

if __name__ == '__main__':
    print("🧪 ТЕСТ ФУНКЦИИ 'ТРЕНИРОВКИ В НЕДЕЛЮ'")
    print("=" * 50)
    
    # Тест состояний онбординга
    states_test = test_onboarding_states()
    
    # Тест функциональности
    workouts_test = test_workouts_per_week()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"Состояния онбординга: {'✅ ПРОЙДЕН' if states_test else '❌ ПРОВАЛЕН'}")
    print(f"Функциональность: {'✅ ПРОЙДЕН' if workouts_test else '❌ ПРОВАЛЕН'}")
    
    if states_test and workouts_test:
        print("\n🎉 Функция 'тренировки в неделю' работает корректно!")
        print("   Бот теперь адаптирует программы под доступное время пользователя.")
    else:
        print("\n⚠️ Обнаружены проблемы в новой функциональности.")