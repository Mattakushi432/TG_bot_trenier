#!/usr/bin/env python3
"""
Тест подключения к Gemini API
"""

import google.generativeai as genai
from config import GEMINI_API_KEY

def test_gemini_models():
    """Тестирование доступных моделей Gemini"""
    print("🧪 Тестирование Gemini API...")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ API ключ настроен")
        
        # Получаем список доступных моделей
        print("\n📋 Доступные модели:")
        models = genai.list_models()
        
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
                print(f"  ✅ {model.name}")
        
        if not available_models:
            print("❌ Нет доступных моделей для генерации контента")
            return False
        
        # Тестируем первую доступную модель
        test_model_name = available_models[0]
        print(f"\n🔬 Тестируем модель: {test_model_name}")
        
        model = genai.GenerativeModel(test_model_name)
        response = model.generate_content("Привет! Ответь кратко на русском языке.")
        
        print(f"✅ Ответ модели: {response.text[:100]}...")
        print(f"✅ Модель {test_model_name} работает корректно!")
        
        return test_model_name
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def test_fitness_prompt():
    """Тестирование фитнес-промпта"""
    print("\n🏋️ Тестирование фитнес-промпта...")
    
    try:
        # Используем рабочую модель
        working_model = test_gemini_models()
        if not working_model:
            return False
        
        model = genai.GenerativeModel(working_model)
        
        fitness_prompt = """
        Ты - Ронни Коулман, 8-кратный Мистер Олимпия. 
        Создай краткий план тренировок на неделю для новичка мужчины 25 лет.
        Ответь в стиле Ронни Коулмана с фразами "Yeah buddy!" и "Light weight!".
        """
        
        response = model.generate_content(fitness_prompt)
        print(f"✅ Фитнес-ответ: {response.text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка фитнес-промпта: {e}")
        return False

if __name__ == '__main__':
    print("🏆 ТЕСТ GEMINI API")
    print("=" * 50)
    
    # Тест моделей
    working_model = test_gemini_models()
    
    if working_model:
        # Тест фитнес-промпта
        test_fitness_prompt()
        
        print(f"\n🎉 Рекомендуемая модель для использования: {working_model}")
        print("\n💡 Обновите gemini_client.py, используя эту модель:")
        print(f"   self.model = genai.GenerativeModel('{working_model}')")
    else:
        print("\n❌ Gemini API недоступен. Проверьте:")
        print("   1. Правильность API ключа в .env")
        print("   2. Интернет-соединение")
        print("   3. Квоты в Google AI Studio")