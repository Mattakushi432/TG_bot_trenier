import sqlite3
import json
import os
from datetime import datetime
from config import DATABASE_PATH

class UserDatabase:
    def __init__(self):
        # Создаем директорию для базы данных если её нет
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    gender TEXT,
                    age INTEGER,
                    height REAL,
                    weight REAL,
                    measurements TEXT,
                    fitness_level TEXT,
                    goal TEXT,
                    location TEXT,
                    injuries TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица прогресса
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    weight REAL,
                    measurements TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица планов тренировок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workout_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    plan_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
    
    def save_user(self, user_data):
        """Сохранение данных пользователя"""
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, gender, age, height, weight, measurements, 
                 fitness_level, goal, location, injuries, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['user_id'],
                user_data.get('username'),
                user_data.get('gender'),
                user_data.get('age'),
                user_data.get('height'),
                user_data.get('weight'),
                json.dumps(user_data.get('measurements', {})),
                user_data.get('fitness_level'),
                user_data.get('goal'),
                user_data.get('location'),
                user_data.get('injuries'),
                datetime.now()
            ))
            
            conn.commit()
    
    def get_user(self, user_id):
        """Получение данных пользователя"""
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                user_data = dict(zip(columns, row))
                
                # Парсим JSON данные
                if user_data['measurements']:
                    user_data['measurements'] = json.loads(user_data['measurements'])
                
                return user_data
            
            return None
    
    def save_progress(self, user_id, weight, measurements):
        """Сохранение прогресса пользователя"""
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO progress (user_id, weight, measurements)
                VALUES (?, ?, ?)
            ''', (user_id, weight, json.dumps(measurements)))
            
            conn.commit()
    
    def get_progress_history(self, user_id, limit=10):
        """Получение истории прогресса"""
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM progress 
                WHERE user_id = ? 
                ORDER BY date DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            progress_list = []
            for row in rows:
                progress_data = dict(zip(columns, row))
                if progress_data['measurements']:
                    progress_data['measurements'] = json.loads(progress_data['measurements'])
                progress_list.append(progress_data)
            
            return progress_list
    
    def save_workout_plan(self, user_id, plan_data):
        """Сохранение плана тренировок"""
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO workout_plans (user_id, plan_data)
                VALUES (?, ?)
            ''', (user_id, json.dumps(plan_data)))
            
            conn.commit()
    
    def get_latest_workout_plan(self, user_id):
        """Получение последнего плана тренировок"""
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT plan_data FROM workout_plans 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            
            return None