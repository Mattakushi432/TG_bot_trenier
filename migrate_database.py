#!/usr/bin/env python3
"""
Миграция базы данных для добавления поля workouts_per_week
"""

import sqlite3
import os
from config import DATABASE_PATH

def migrate_database():
    """Добавление нового поля в существующую базу данных"""
    print("🔄 Миграция базы данных...")
    
    # Создаем директорию если её нет
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        try:
            # Проверяем, существует ли уже колонка
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'workouts_per_week' not in columns:
                print("➕ Добавляем колонку workouts_per_week...")
                cursor.execute('''
                    ALTER TABLE users 
                    ADD COLUMN workouts_per_week INTEGER DEFAULT 3
                ''')
                conn.commit()
                print("✅ Колонка workouts_per_week добавлена")
            else:
                print("✅ Колонка workouts_per_week уже существует")
            
            # Проверяем структуру таблицы
            cursor.execute("PRAGMA table_info(users)")
            columns_info = cursor.fetchall()
            
            print("\n📋 Текущая структура таблицы users:")
            for column in columns_info:
                print(f"   {column[1]} ({column[2]})")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка миграции: {e}")
            return False

def test_migration():
    """Тест миграции"""
    print("\n🧪 Тестирование миграции...")
    
    try:
        from database import UserDatabase
        
        db = UserDatabase()
        
        # Тестовый пользователь с новым полем
        test_user = {
            'user_id': 777777,
            'username': 'migration_test',
            'gender': 'male',
            'age': 25,
            'height': 180.0,
            'weight': 80.0,
            'measurements': {'chest': 100, 'waist': 85, 'hips': 95, 'bicep': 35},
            'fitness_level': 'intermediate',
            'goal': 'fitness',
            'location': 'gym',
            'workouts_per_week': 4,
            'injuries': None
        }
        
        # Сохраняем пользователя
        db.save_user(test_user)
        
        # Получаем пользователя
        retrieved_user = db.get_user(777777)
        
        if retrieved_user and retrieved_user['workouts_per_week'] == 4:
            print("✅ Миграция успешна - новое поле работает")
            return True
        else:
            print("❌ Миграция неуспешна - проблемы с новым полем")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == '__main__':
    print("🗄️ МИГРАЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 40)
    
    # Выполняем миграцию
    migration_success = migrate_database()
    
    if migration_success:
        # Тестируем миграцию
        test_success = test_migration()
        
        if test_success:
            print("\n🎉 Миграция завершена успешно!")
            print("   Теперь можно использовать поле 'workouts_per_week'")
        else:
            print("\n⚠️ Миграция выполнена, но есть проблемы с тестированием")
    else:
        print("\n❌ Миграция не удалась")