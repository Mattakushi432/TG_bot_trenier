import google.generativeai as genai
from config import GEMINI_API_KEY
import json

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def get_system_prompt(self, user_data):
        """Генерация системного промпта на основе данных пользователя"""
        
        # Определяем персонажа на основе пола
        if user_data.get('gender') == 'male':
            coach_persona = """
            Ты — Ронни Коулман (Ronnie Coleman), 8-кратный "Мистер Олимпия". 
            Стиль: мощный, харизматичный, мотивирующий ("Light weight, baby!", "Yeah buddy!"), 
            упор на силовые показатели и экстремальную массу.
            """
        else:
            coach_persona = """
            Ты — Дженет Лайог (Janet Layug), чемпионка "Bikini Olympia". 
            Стиль: профессиональный, эстетичный, фокус на пропорциях, 
            качестве кожи и мышечном тонусе.
            """
        
        system_prompt = f"""
        IFBB Pro Dual-Coach AI
        
        Role: Ты — гибридный ИИ-ассистент, объединяющий двух легенд мирового бодибилдинга.
        
        {coach_persona}
        
        Goal: Создавать индивидуальные программы тренировок и питания, вести пользователя 
        от новичка до уровня подготовки к турнирам "Olympia" или "IFBB World Championships".
        
        Данные пользователя:
        - Пол: {user_data.get('gender', 'не указан')}
        - Возраст: {user_data.get('age', 'не указан')}
        - Рост: {user_data.get('height', 'не указан')} см
        - Вес: {user_data.get('weight', 'не указан')} кг
        - Замеры: {user_data.get('measurements', {})}
        - Уровень: {user_data.get('fitness_level', 'не указан')}
        - Цель: {user_data.get('goal', 'не указана')}
        - Локация: {user_data.get('location', 'не указана')}
        - Травмы: {user_data.get('injuries', 'нет')}
        
        Core Capabilities:
        1. Training Management: Генерируй тренировочный план на 4 недели (Microcycle). 
           Используй принципы прогрессии нагрузок, периодизации и метаболического отклика.
        
        2. Nutrition & Calories: Рассчитывай КБЖУ на основе формулы Миффлина-Сан Жеора 
           с поправкой на коэффициент активности и цель.
        
        3. Sports Supplements: Рекомендуй только доказанные добавки исходя из дефицитов и целей.
        
        Constraints:
        - Никаких общих советов. Только конкретные упражнения, количество подходов и повторений.
        - Соблюдай тон выбранного персонажа, но сохраняй научную точность.
        - Используй Markdown для таблиц тренировок.
        - В конце каждого ответа — мотивирующая цитата в стиле персонажа.
        
        Отвечай на русском языке.
        """
        
        return system_prompt
    
    async def generate_response(self, user_data, user_message):
        """Генерация ответа от Gemini"""
        try:
            system_prompt = self.get_system_prompt(user_data)
            
            # Формируем полный промпт
            full_prompt = f"{system_prompt}\n\nВопрос пользователя: {user_message}"
            
            # Генерируем ответ
            response = self.model.generate_content(full_prompt)
            
            return response.text
            
        except Exception as e:
            return f"Произошла ошибка при генерации ответа: {str(e)}"
    
    async def generate_workout_plan(self, user_data):
        """Генерация плана тренировок"""
        prompt = """
        Создай детальный план тренировок на 4 недели в формате таблицы Markdown.
        
        Требования:
        - Укажи конкретные упражнения, подходы, повторения
        - Учти уровень подготовки и цель пользователя
        - Добавь прогрессию нагрузок по неделям
        - Включи разминку и заминку
        - Если локация "Дом" - используй упражнения с минимальным инвентарем
        
        Формат ответа должен содержать:
        1. Общие принципы программы
        2. Недельный сплит
        3. Детальные тренировки по дням
        4. Рекомендации по прогрессии
        """
        
        return await self.generate_response(user_data, prompt)
    
    async def calculate_nutrition(self, user_data):
        """Расчет питания и КБЖУ"""
        prompt = """
        Рассчитай индивидуальный план питания с точными значениями КБЖУ.
        
        Используй:
        - Формулу Миффлина-Сан Жеора для базового метаболизма
        - Коэффициент активности на основе тренировочного режима
        - Поправку на цель (набор массы/сушка/поддержание)
        
        Предоставь:
        1. Точные цифры КБЖУ в день
        2. Распределение по приемам пищи
        3. Примерное меню на день
        4. Рекомендации по времени приема пищи относительно тренировок
        """
        
        return await self.generate_response(user_data, prompt)
    
    async def recommend_supplements(self, user_data):
        """Рекомендации по спортивному питанию"""
        prompt = """
        Порекомендуй спортивные добавки на основе цели и уровня подготовки.
        
        Включи только научно обоснованные добавки:
        - Креатин моногидрат
        - Протеин (сывороточный/казеиновый)
        - Аминокислоты (BCAA/EAA)
        - Витаминно-минеральные комплексы
        - Омега-3
        
        Для каждой добавки укажи:
        1. Дозировку
        2. Время приема
        3. Ожидаемый эффект
        4. Приоритет (обязательно/желательно/опционально)
        """
        
        return await self.generate_response(user_data, prompt)