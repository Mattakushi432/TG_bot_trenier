#!/usr/bin/env python3
"""
Примеры использования компонентов бота для тестирования
"""

import asyncio
from database import UserDatabase
from gemini_client import GeminiClient
from utils import FitnessCalculator, ProgressTracker, WorkoutGenerator

def test_database():
    """Тестирование базы данных"""
    print("🗄️ Тестирование базы данных...")
    
    db = UserDatabase()
    
    # Тестовые данные пользователя
    test_user = {
        'user_id': 12345,
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
        'workouts_per_week': 3,
        'injuries': None
    }
    
    # Сохраняем пользователя
    db.save_user(test_user)
    print("✅ Пользователь сохранен")
    
    # Получаем пользователя
    retrieved_user = db.get_user(12345)
    print(f"✅ Пользователь получен: {retrieved_user['username']}")
    
    # Сохраняем прогресс
    db.save_progress(12345, 79.5, {
        'chest': 101,
        'waist': 84,
        'hips': 95,
        'bicep': 36
    })
    print("✅ Прогресс сохранен")
    
    # Получаем историю прогресса
    progress = db.get_progress_history(12345)
    print(f"✅ История прогресса: {len(progress)} записей")
    
    return True

def test_fitness_calculator():
    """Тестирование фитнес-калькулятора"""
    print("\n🧮 Тестирование фитнес-калькулятора...")
    
    calc = FitnessCalculator()
    
    # Тестовые данные
    weight = 80.0
    height = 180.0
    age = 25
    gender = 'male'
    
    # Расчет BMR
    bmr = calc.calculate_bmr(weight, height, age, gender)
    print(f"✅ BMR: {bmr:.0f} ккал")
    
    # Расчет TDEE
    tdee = calc.calculate_tdee(bmr, 'moderate', 'intermediate')
    print(f"✅ TDEE: {tdee:.0f} ккал")
    
    # Расчет макронутриентов
    macros = calc.calculate_macros(tdee, 'fitness', gender)
    print(f"✅ Макросы: Б{macros['protein']}г Ж{macros['fats']}г У{macros['carbs']}г")
    
    # Расчет BMI
    bmi = calc.calculate_bmi(weight, height)
    category = calc.get_bmi_category(bmi)
    print(f"✅ BMI: {bmi} ({category})")
    
    return True

def test_workout_generator():
    """Тестирование генератора тренировок"""
    print("\n🏋️ Тестирование генератора тренировок...")
    
    generator = WorkoutGenerator()
    
    # Получаем упражнения для зала
    gym_exercises = generator.EXERCISES['gym']['chest']
    print(f"✅ Упражнения для груди (зал): {len(gym_exercises)} шт.")
    print(f"   Примеры: {', '.join(gym_exercises[:3])}")
    
    # Получаем упражнения для дома
    home_exercises = generator.EXERCISES['home']['chest']
    print(f"✅ Упражнения для груди (дом): {len(home_exercises)} шт.")
    print(f"   Примеры: {', '.join(home_exercises[:3])}")
    
    # Диапазоны повторений
    rep_ranges = generator.get_rep_range('intermediate', 'fitness')
    print(f"✅ Диапазоны повторений: {rep_ranges}")
    
    return True

async def test_gemini_client():
    """Тестирование Gemini клиента"""
    print("\n🤖 Тестирование Gemini клиента...")
    
    try:
        client = GeminiClient()
        
        # Тестовые данные пользователя
        test_user_data = {
            'gender': 'male',
            'age': 25,
            'height': 180,
            'weight': 80,
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
        
        # Генерируем системный промпт
        system_prompt = client.get_system_prompt(test_user_data)
        print("✅ Системный промпт сгенерирован")
        print(f"   Длина: {len(system_prompt)} символов")
        
        # Проверяем, что промпт содержит правильного персонажа
        if 'Ронни Коулман' in system_prompt:
            print("✅ Персонаж определен правильно (Ронни Коулман)")
        
        print("⚠️  Для полного тестирования Gemini API нужен действующий ключ")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Gemini: {e}")
        return False

def test_progress_tracker():
    """Тестирование трекера прогресса"""
    print("\n📊 Тестирование трекера прогресса...")
    
    tracker = ProgressTracker()
    
    # Тестируем расчет прогресса
    initial_weight = 85.0
    current_weight = 80.0
    target_weight = 75.0
    
    progress = tracker.calculate_progress_percentage(
        current_weight, target_weight, initial_weight
    )
    print(f"✅ Прогресс по весу: {progress:.1f}%")
    
    # Тестируем форматирование изменений
    old_bicep = 35.0
    new_bicep = 36.5
    
    change = tracker.format_measurement_change(old_bicep, new_bicep)
    print(f"✅ Изменение бицепса: {change} см")
    
    return True

def run_all_tests():
    """Запуск всех тестов"""
    print("🧪 ЗАПУСК ТЕСТОВ КОМПОНЕНТОВ")
    print("=" * 50)
    
    tests = [
        ("База данных", test_database),
        ("Фитнес-калькулятор", test_fitness_calculator),
        ("Генератор тренировок", test_workout_generator),
        ("Трекер прогресса", test_progress_tracker),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Асинхронный тест Gemini
    try:
        gemini_result = asyncio.run(test_gemini_client())
        results.append(("Gemini клиент", gemini_result))
    except Exception as e:
        print(f"❌ Ошибка в тесте Gemini: {e}")
        results.append(("Gemini клиент", False))
    
    # Результаты
    print("\n" + "=" * 50)
    print("📋 РЕЗУЛЬТАТЫ ТЕСТОВ")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Итого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все компоненты работают корректно!")
    else:
        print("⚠️  Некоторые компоненты требуют внимания")
    
    return passed == total

def demo_user_flow():
    """Демонстрация пользовательского сценария"""
    print("\n" + "=" * 50)
    print("🎭 ДЕМОНСТРАЦИЯ ПОЛЬЗОВАТЕЛЬСКОГО СЦЕНАРИЯ")
    print("=" * 50)
    
    # Создаем пользователя
    print("\n1️⃣ Регистрация нового пользователя...")
    
    user_data = {
        'user_id': 99999,
        'username': 'demo_user',
        'gender': 'female',
        'age': 28,
        'height': 165.0,
        'weight': 60.0,
        'measurements': {
            'chest': 90,
            'waist': 70,
            'hips': 95,
            'bicep': 28
        },
        'fitness_level': 'beginner',
        'goal': 'fitness',
        'location': 'home',
        'workouts_per_week': 2,
        'injuries': None
    }
    
    db = UserDatabase()
    db.save_user(user_data)
    print("✅ Пользователь зарегистрирован")
    
    # Расчеты для пользователя
    print("\n2️⃣ Расчет параметров...")
    
    calc = FitnessCalculator()
    bmr = calc.calculate_bmr(
        user_data['weight'], 
        user_data['height'], 
        user_data['age'], 
        user_data['gender']
    )
    tdee = calc.calculate_tdee(bmr, 'light', user_data['fitness_level'])
    macros = calc.calculate_macros(tdee, user_data['goal'], user_data['gender'])
    
    print(f"✅ BMR: {bmr:.0f} ккал")
    print(f"✅ TDEE: {tdee:.0f} ккал")
    print(f"✅ Макросы: Б{macros['protein']}г Ж{macros['fats']}г У{macros['carbs']}г")
    
    # Прогресс через месяц
    print("\n3️⃣ Обновление прогресса через месяц...")
    
    new_measurements = {
        'chest': 91,
        'waist': 68,
        'hips': 94,
        'bicep': 29
    }
    
    db.save_progress(99999, 58.5, new_measurements)
    
    tracker = ProgressTracker()
    waist_change = tracker.format_measurement_change(70, 68)
    bicep_change = tracker.format_measurement_change(28, 29)
    
    print(f"✅ Изменение талии: {waist_change} см")
    print(f"✅ Изменение бицепса: {bicep_change} см")
    print("✅ Прогресс сохранен")
    
    # Получение истории
    print("\n4️⃣ Просмотр истории прогресса...")
    
    progress_history = db.get_progress_history(99999)
    print(f"✅ Найдено {len(progress_history)} записей прогресса")
    
    print("\n🎉 Демонстрация завершена успешно!")

if __name__ == '__main__':
    try:
        # Запускаем тесты
        success = run_all_tests()
        
        # Демонстрация
        demo_user_flow()
        
        if success:
            print("\n🚀 Все системы готовы к запуску!")
        else:
            print("\n⚠️  Обнаружены проблемы, проверьте конфигурацию")
            
    except KeyboardInterrupt:
        print("\n❌ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        raise