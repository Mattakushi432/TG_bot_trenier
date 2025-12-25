"""
Утилиты для расчетов и вспомогательных функций
"""

import math
from datetime import datetime, timedelta

class FitnessCalculator:
    """Класс для фитнес-расчетов"""
    
    @staticmethod
    def calculate_bmr(weight, height, age, gender):
        """
        Расчет базального метаболизма по формуле Миффлина-Сан Жеора
        
        Args:
            weight (float): Вес в кг
            height (float): Рост в см
            age (int): Возраст в годах
            gender (str): 'male' или 'female'
        
        Returns:
            float: BMR в калориях
        """
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        return bmr
    
    @staticmethod
    def calculate_tdee(bmr, activity_level, fitness_level):
        """
        Расчет общего расхода энергии (TDEE)
        
        Args:
            bmr (float): Базальный метаболизм
            activity_level (str): Уровень активности
            fitness_level (str): Уровень подготовки
        
        Returns:
            float: TDEE в калориях
        """
        # Базовые коэффициенты активности
        activity_multipliers = {
            'sedentary': 1.2,      # Сидячий образ жизни
            'light': 1.375,        # Легкая активность
            'moderate': 1.55,      # Умеренная активность
            'active': 1.725,       # Высокая активность
            'very_active': 1.9     # Очень высокая активность
        }
        
        # Определяем коэффициент на основе уровня подготовки
        if fitness_level == 'beginner':
            multiplier = activity_multipliers['light']
        elif fitness_level == 'intermediate':
            multiplier = activity_multipliers['moderate']
        else:  # advanced
            multiplier = activity_multipliers['active']
        
        return bmr * multiplier
    
    @staticmethod
    def calculate_macros(calories, goal, gender):
        """
        Расчет макронутриентов (БЖУ)
        
        Args:
            calories (float): Общее количество калорий
            goal (str): Цель ('fitness' или 'competition')
            gender (str): Пол
        
        Returns:
            dict: Словарь с БЖУ
        """
        if goal == 'competition':
            # Для соревновательной подготовки
            protein_ratio = 0.35 if gender == 'male' else 0.40
            fat_ratio = 0.20 if gender == 'male' else 0.25
            carb_ratio = 1 - protein_ratio - fat_ratio
        else:
            # Для общего фитнеса
            protein_ratio = 0.25 if gender == 'male' else 0.30
            fat_ratio = 0.25 if gender == 'male' else 0.30
            carb_ratio = 1 - protein_ratio - fat_ratio
        
        protein_calories = calories * protein_ratio
        fat_calories = calories * fat_ratio
        carb_calories = calories * carb_ratio
        
        return {
            'calories': round(calories),
            'protein': round(protein_calories / 4),  # 4 ккал/г
            'fats': round(fat_calories / 9),         # 9 ккал/г
            'carbs': round(carb_calories / 4),       # 4 ккал/г
            'protein_calories': round(protein_calories),
            'fat_calories': round(fat_calories),
            'carb_calories': round(carb_calories)
        }
    
    @staticmethod
    def calculate_bmi(weight, height):
        """
        Расчет индекса массы тела (BMI)
        
        Args:
            weight (float): Вес в кг
            height (float): Рост в см
        
        Returns:
            float: BMI
        """
        height_m = height / 100  # Переводим в метры
        return round(weight / (height_m ** 2), 1)
    
    @staticmethod
    def get_bmi_category(bmi):
        """
        Определение категории BMI
        
        Args:
            bmi (float): Индекс массы тела
        
        Returns:
            str: Категория BMI
        """
        if bmi < 18.5:
            return "Недостаточный вес"
        elif 18.5 <= bmi < 25:
            return "Нормальный вес"
        elif 25 <= bmi < 30:
            return "Избыточный вес"
        else:
            return "Ожирение"

class ProgressTracker:
    """Класс для отслеживания прогресса"""
    
    @staticmethod
    def calculate_progress_percentage(current, target, initial):
        """
        Расчет процента достижения цели
        
        Args:
            current (float): Текущее значение
            target (float): Целевое значение
            initial (float): Начальное значение
        
        Returns:
            float: Процент прогресса
        """
        if target == initial:
            return 100.0
        
        progress = (current - initial) / (target - initial) * 100
        return max(0, min(100, progress))
    
    @staticmethod
    def format_measurement_change(old_value, new_value):
        """
        Форматирование изменения замеров
        
        Args:
            old_value (float): Старое значение
            new_value (float): Новое значение
        
        Returns:
            str: Отформатированное изменение
        """
        change = new_value - old_value
        if change > 0:
            return f"+{change:.1f}"
        elif change < 0:
            return f"{change:.1f}"
        else:
            return "0"

class WorkoutGenerator:
    """Генератор тренировочных программ"""
    
    # Базы упражнений
    EXERCISES = {
        'gym': {
            'chest': [
                'Жим штанги лежа', 'Жим гантелей лежа', 'Жим гантелей на наклонной',
                'Разводка гантелей', 'Отжимания на брусьях', 'Кроссовер'
            ],
            'back': [
                'Подтягивания', 'Тяга штанги в наклоне', 'Тяга гантели в наклоне',
                'Тяга верхнего блока', 'Тяга горизонтального блока', 'Становая тяга'
            ],
            'shoulders': [
                'Жим штанги стоя', 'Жим гантелей сидя', 'Разводка гантелей в стороны',
                'Разводка в наклоне', 'Подъемы перед собой', 'Шраги'
            ],
            'arms': [
                'Подъем штанги на бицепс', 'Молотки с гантелями', 'Жим узким хватом',
                'Французский жим', 'Подъемы на блоке', 'Отжимания на брусьях'
            ],
            'legs': [
                'Приседания со штангой', 'Жим ногами', 'Выпады с гантелями',
                'Румынская тяга', 'Подъемы на носки', 'Разгибания ног'
            ]
        },
        'home': {
            'chest': [
                'Отжимания классические', 'Отжимания с наклоном', 'Отжимания узким хватом',
                'Отжимания с хлопком', 'Планка', 'Пуловер с гантелью'
            ],
            'back': [
                'Подтягивания (турник)', 'Тяга гантелей в наклоне', 'Супермен',
                'Обратная планка', 'Тяга резинки', 'Гиперэкстензия'
            ],
            'shoulders': [
                'Жим гантелей стоя', 'Разводка гантелей', 'Подъемы перед собой',
                'Отжимания в стойке', 'Планка вверх-вниз', 'Круги руками'
            ],
            'arms': [
                'Подъемы гантелей на бицепс', 'Молотки', 'Отжимания узким хватом',
                'Обратные отжимания', 'Планка на руках', 'Сгибания с резинкой'
            ],
            'legs': [
                'Приседания', 'Выпады', 'Болгарские приседания',
                'Подъемы на носки', 'Ягодичный мостик', 'Прыжки'
            ]
        }
    }
    
    @staticmethod
    def get_rep_range(fitness_level, goal):
        """
        Определение диапазона повторений
        
        Args:
            fitness_level (str): Уровень подготовки
            goal (str): Цель тренировок
        
        Returns:
            dict: Диапазоны повторений для разных типов упражнений
        """
        if goal == 'competition':
            if fitness_level == 'advanced':
                return {'strength': '3-5', 'hypertrophy': '8-12', 'endurance': '15-20'}
            else:
                return {'strength': '5-8', 'hypertrophy': '10-15', 'endurance': '15-25'}
        else:  # fitness
            if fitness_level == 'beginner':
                return {'strength': '8-12', 'hypertrophy': '12-15', 'endurance': '15-20'}
            else:
                return {'strength': '6-10', 'hypertrophy': '10-15', 'endurance': '15-20'}

def format_datetime(dt):
    """Форматирование даты и времени"""
    return dt.strftime("%d.%m.%Y %H:%M")

def validate_measurements(measurements):
    """
    Валидация замеров тела
    
    Args:
        measurements (dict): Словарь с замерами
    
    Returns:
        bool: True если замеры валидны
    """
    required_keys = ['chest', 'waist', 'hips', 'bicep']
    
    if not all(key in measurements for key in required_keys):
        return False
    
    # Проверяем разумные диапазоны (в см)
    ranges = {
        'chest': (60, 150),
        'waist': (50, 120),
        'hips': (60, 150),
        'bicep': (20, 60)
    }
    
    for key, (min_val, max_val) in ranges.items():
        value = measurements.get(key, 0)
        if not (min_val <= value <= max_val):
            return False
    
    return True