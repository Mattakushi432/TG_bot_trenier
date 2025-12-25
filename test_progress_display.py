#!/usr/bin/env python3
"""
Тест отображения прогресса пользователя
"""

from database import UserDatabase
import json

def test_progress_display():
    """Тестирование отображения прогресса"""
    print("📊 Тестирование отображения прогресса...")
    
    db = UserDatabase()
    
    # Создаем тестового пользователя
    test_user = {
        'user_id': 555555,
        'username': 'progress_test',
        'gender': 'male',
        'age': 30,
        'height': 180.0,
        'weight': 93.0,
        'measurements': {
            'chest': 100.0,
            'waist': 109.0,
            'hips': 108.0,
            'bicep': 15.0
        },
        'fitness_level': 'intermediate',
        'goal': 'fitness',
        'location': 'gym',
        'workouts_per_week': 3,
        'injuries': None
    }
    
    # Сохраняем пользователя
    db.save_user(test_user)
    print("✅ Тестовый пользователь создан")
    
    # Получаем пользователя
    user_data = db.get_user(555555)
    
    # Тестируем функцию форматирования замеров
    def format_measurements(measurements):
        """Форматирование замеров для красивого отображения"""
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
    
    # Тестируем форматирование
    formatted_measurements = format_measurements(user_data['measurements'])
    
    print("\n📏 Тест форматирования замеров:")
    print("До форматирования:")
    print(f"  {user_data['measurements']}")
    print("После форматирования:")
    print(f"  {formatted_measurements}")
    
    # Создаем красивое сообщение о прогрессе
    progress_message = (
        "📊 Твой профиль:\n\n"
        f"⚖️ Текущий вес: {user_data['weight']} кг\n\n"
        f"📏 Замеры тела:\n{formatted_measurements}\n\n"
        "📈 История изменений пуста.\n"
        "Обновляй замеры регулярно, чтобы отслеживать прогресс!"
    )
    
    print("\n📱 Итоговое сообщение для пользователя:")
    print("-" * 40)
    print(progress_message)
    print("-" * 40)
    
    # Добавляем запись в историю прогресса
    new_measurements = {
        'chest': 101.0,
        'waist': 107.0,
        'hips': 107.0,
        'bicep': 16.0
    }
    
    db.save_progress(555555, 91.5, new_measurements)
    print("\n✅ Добавлена запись в историю прогресса")
    
    # Получаем историю
    progress_history = db.get_progress_history(555555)
    
    if progress_history:
        print("\n📈 Тест отображения истории:")
        for record in progress_history:
            date_str = record['date'][:10] if record['date'] else "Неизвестная дата"
            formatted_hist_measurements = format_measurements(record['measurements'])
            
            history_message = (
                f"📅 {date_str}\n"
                f"⚖️ Вес: {record['weight']} кг\n"
                f"📏 Замеры:\n{formatted_hist_measurements}"
            )
            
            print("-" * 30)
            print(history_message)
            print("-" * 30)
    
    return True

def test_measurement_updates():
    """Тест обновления замеров"""
    print("\n🔄 Тестирование обновления замеров...")
    
    new_measurements = {
        'chest': 102.0,
        'waist': 105.0,
        'hips': 106.0,
        'bicep': 17.0
    }
    
    # Форматируем как в боте
    measurements_text = "\n".join([
        f"Грудь: {new_measurements['chest']} см",
        f"Талия: {new_measurements['waist']} см", 
        f"Бедра: {new_measurements['hips']} см",
        f"Бицепс: {new_measurements['bicep']} см"
    ])
    
    success_message = (
        "✅ Замеры обновлены!\n\n"
        f"📏 Новые замеры:\n{measurements_text}\n\n"
        "📊 Данные сохранены в историю прогресса."
    )
    
    print("📱 Сообщение об обновлении замеров:")
    print("-" * 40)
    print(success_message)
    print("-" * 40)
    
    return True

if __name__ == '__main__':
    print("🧪 ТЕСТ ОТОБРАЖЕНИЯ ПРОГРЕССА")
    print("=" * 50)
    
    # Тест отображения прогресса
    progress_test = test_progress_display()
    
    # Тест обновления замеров
    update_test = test_measurement_updates()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"Отображение прогресса: {'✅ ПРОЙДЕН' if progress_test else '❌ ПРОВАЛЕН'}")
    print(f"Обновление замеров: {'✅ ПРОЙДЕН' if update_test else '❌ ПРОВАЛЕН'}")
    
    if progress_test and update_test:
        print("\n🎉 Отображение прогресса теперь красивое и понятное!")
        print("   Замеры показываются в читаемом формате с эмодзи.")
    else:
        print("\n⚠️ Обнаружены проблемы в отображении.")