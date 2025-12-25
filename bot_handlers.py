from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database import UserDatabase
from gemini_client import GeminiClient
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация компонентов
db = UserDatabase()
gemini = GeminiClient()

# Состояния для онбординга
ONBOARDING_STATES = {
    'GENDER': 'gender',
    'AGE': 'age', 
    'HEIGHT': 'height',
    'WEIGHT': 'weight',
    'MEASUREMENTS': 'measurements',
    'FITNESS_LEVEL': 'fitness_level',
    'GOAL': 'goal',
    'LOCATION': 'location',
    'INJURIES': 'injuries'
}

def get_main_keyboard():
    """Основная клавиатура бота"""
    keyboard = [
        [KeyboardButton("🏋️ Новый план тренировок"), KeyboardButton("🍎 Расчет питания")],
        [KeyboardButton("💊 Спортивное питание"), KeyboardButton("📊 Мой прогресс")],
        [KeyboardButton("📏 Обновить замеры"), KeyboardButton("⚙️ Настройки")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if user_data is None:
        # Новый пользователь - начинаем онбординг
        await update.message.reply_text(
            "🏆 Добро пожаловать в IFBB Pro Dual-Coach AI!\n\n"
            "Я твой персональный ИИ-тренер, который поможет достичь целей в фитнесе.\n"
            "Для начала мне нужно узнать о тебе больше.\n\n"
            "Укажи свой пол:",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("👨 Мужской"), KeyboardButton("👩 Женский")]
            ], resize_keyboard=True)
        )
        context.user_data['onboarding_state'] = ONBOARDING_STATES['GENDER']
        context.user_data['user_info'] = {'user_id': user_id, 'username': update.effective_user.username}
    else:
        # Существующий пользователь
        coach_name = "Ронни Коулман" if user_data['gender'] == 'male' else "Дженет Лайог"
        await update.message.reply_text(
            f"Привет! Я {coach_name}, твой персональный тренер! 💪\n\n"
            "Готов продолжить работу над твоими целями?",
            reply_markup=get_main_keyboard()
        )

async def handle_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка процесса онбординга"""
    if 'onboarding_state' not in context.user_data:
        return
    
    state = context.user_data['onboarding_state']
    user_info = context.user_data['user_info']
    text = update.message.text
    
    if state == ONBOARDING_STATES['GENDER']:
        if "Мужской" in text:
            user_info['gender'] = 'male'
            coach_intro = "Привет! Я Ронни Коулман! 💪 Light weight, baby! Готов качаться по-настоящему?"
        elif "Женский" in text:
            user_info['gender'] = 'female'  
            coach_intro = "Привет! Я Дженет Лайог! ✨ Создадим красивое и сильное тело вместе!"
        else:
            await update.message.reply_text("Пожалуйста, выбери пол из предложенных вариантов.")
            return
        
        await update.message.reply_text(
            f"{coach_intro}\n\nТеперь укажи свой возраст (в годах):",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Отмена")]], resize_keyboard=True)
        )
        context.user_data['onboarding_state'] = ONBOARDING_STATES['AGE']
    
    elif state == ONBOARDING_STATES['AGE']:
        try:
            age = int(text)
            if 16 <= age <= 80:
                user_info['age'] = age
                await update.message.reply_text("Отлично! Теперь укажи свой рост в сантиметрах:")
                context.user_data['onboarding_state'] = ONBOARDING_STATES['HEIGHT']
            else:
                await update.message.reply_text("Возраст должен быть от 16 до 80 лет. Попробуй еще раз:")
        except ValueError:
            await update.message.reply_text("Пожалуйста, введи возраст числом:")
    
    elif state == ONBOARDING_STATES['HEIGHT']:
        try:
            height = float(text)
            if 140 <= height <= 220:
                user_info['height'] = height
                await update.message.reply_text("Супер! Теперь укажи свой текущий вес в килограммах:")
                context.user_data['onboarding_state'] = ONBOARDING_STATES['WEIGHT']
            else:
                await update.message.reply_text("Рост должен быть от 140 до 220 см. Попробуй еще раз:")
        except ValueError:
            await update.message.reply_text("Пожалуйста, введи рост числом:")
    
    elif state == ONBOARDING_STATES['WEIGHT']:
        try:
            weight = float(text)
            if 40 <= weight <= 200:
                user_info['weight'] = weight
                await update.message.reply_text(
                    "Отлично! Теперь нужны основные замеры.\n"
                    "Введи через запятую: обхват груди, талии, бедер, бицепса (в см)\n"
                    "Например: 100, 80, 95, 35"
                )
                context.user_data['onboarding_state'] = ONBOARDING_STATES['MEASUREMENTS']
            else:
                await update.message.reply_text("Вес должен быть от 40 до 200 кг. Попробуй еще раз:")
        except ValueError:
            await update.message.reply_text("Пожалуйста, введи вес числом:")
    
    elif state == ONBOARDING_STATES['MEASUREMENTS']:
        try:
            measurements = [float(x.strip()) for x in text.split(',')]
            if len(measurements) == 4:
                user_info['measurements'] = {
                    'chest': measurements[0],
                    'waist': measurements[1], 
                    'hips': measurements[2],
                    'bicep': measurements[3]
                }
                await update.message.reply_text(
                    "Отлично! Теперь выбери свой уровень подготовки:",
                    reply_markup=ReplyKeyboardMarkup([
                        [KeyboardButton("🟢 Новичок"), KeyboardButton("🟡 Средний")],
                        [KeyboardButton("🔴 Продвинутый")]
                    ], resize_keyboard=True)
                )
                context.user_data['onboarding_state'] = ONBOARDING_STATES['FITNESS_LEVEL']
            else:
                await update.message.reply_text("Нужно ввести ровно 4 замера через запятую. Попробуй еще раз:")
        except ValueError:
            await update.message.reply_text("Пожалуйста, введи замеры числами через запятую:")
    
    elif state == ONBOARDING_STATES['FITNESS_LEVEL']:
        if "Новичок" in text:
            user_info['fitness_level'] = 'beginner'
        elif "Средний" in text:
            user_info['fitness_level'] = 'intermediate'
        elif "Продвинутый" in text:
            user_info['fitness_level'] = 'advanced'
        else:
            await update.message.reply_text("Пожалуйста, выбери уровень из предложенных вариантов.")
            return
        
        await update.message.reply_text(
            "Какая у тебя цель?",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("💪 Подтянутое тело"), KeyboardButton("🏆 Выход на сцену (Olympia/IFBB)")]
            ], resize_keyboard=True)
        )
        context.user_data['onboarding_state'] = ONBOARDING_STATES['GOAL']
    
    elif state == ONBOARDING_STATES['GOAL']:
        if "Подтянутое тело" in text:
            user_info['goal'] = 'fitness'
        elif "Выход на сцену" in text:
            user_info['goal'] = 'competition'
        else:
            await update.message.reply_text("Пожалуйста, выбери цель из предложенных вариантов.")
            return
        
        await update.message.reply_text(
            "Где планируешь тренироваться?",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("🏋️ В зале"), KeyboardButton("🏠 Дома")]
            ], resize_keyboard=True)
        )
        context.user_data['onboarding_state'] = ONBOARDING_STATES['LOCATION']
    
    elif state == ONBOARDING_STATES['LOCATION']:
        if "В зале" in text:
            user_info['location'] = 'gym'
        elif "Дома" in text:
            user_info['location'] = 'home'
        else:
            await update.message.reply_text("Пожалуйста, выбери локацию из предложенных вариантов.")
            return
        
        await update.message.reply_text(
            "Есть ли у тебя травмы или ограничения? (напиши 'нет' если их нет)"
        )
        context.user_data['onboarding_state'] = ONBOARDING_STATES['INJURIES']
    
    elif state == ONBOARDING_STATES['INJURIES']:
        user_info['injuries'] = text if text.lower() != 'нет' else None
        
        # Сохраняем пользователя в базу данных
        db.save_user(user_info)
        
        # Завершаем онбординг
        del context.user_data['onboarding_state']
        del context.user_data['user_info']
        
        coach_name = "Ронни Коулман" if user_info['gender'] == 'male' else "Дженет Лайог"
        success_message = (
            f"🎉 Отлично! Регистрация завершена!\n\n"
            f"Теперь я, {coach_name}, буду твоим персональным тренером.\n"
            f"Готов создать для тебя индивидуальную программу! 💪"
        )
        
        await update.message.reply_text(
            success_message,
            reply_markup=get_main_keyboard()
        )

async def handle_workout_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация плана тренировок"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("Сначала пройди регистрацию с помощью команды /start")
        return
    
    await update.message.reply_text("⏳ Создаю персональный план тренировок...")
    
    try:
        workout_plan = await gemini.generate_workout_plan(user_data)
        
        # Сохраняем план в базу данных
        db.save_workout_plan(user_id, {'plan': workout_plan, 'type': 'workout'})
        
        await update.message.reply_text(workout_plan, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка генерации плана тренировок: {e}")
        await update.message.reply_text("Произошла ошибка при создании плана. Попробуй позже.")

async def handle_nutrition_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расчет плана питания"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("Сначала пройди регистрацию с помощью команды /start")
        return
    
    await update.message.reply_text("⏳ Рассчитываю индивидуальный план питания...")
    
    try:
        nutrition_plan = await gemini.calculate_nutrition(user_data)
        await update.message.reply_text(nutrition_plan, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка расчета питания: {e}")
        await update.message.reply_text("Произошла ошибка при расчете питания. Попробуй позже.")

async def handle_supplements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Рекомендации по спортивному питанию"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("Сначала пройди регистрацию с помощью команды /start")
        return
    
    await update.message.reply_text("⏳ Подбираю спортивное питание...")
    
    try:
        supplements = await gemini.recommend_supplements(user_data)
        await update.message.reply_text(supplements, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка подбора добавок: {e}")
        await update.message.reply_text("Произошла ошибка при подборе добавок. Попробуй позже.")

async def handle_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ прогресса пользователя"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("Сначала пройди регистрацию с помощью команды /start")
        return
    
    progress_history = db.get_progress_history(user_id)
    
    if not progress_history:
        await update.message.reply_text(
            "📊 История прогресса пуста.\n\n"
            "Текущие данные:\n"
            f"Вес: {user_data['weight']} кг\n"
            f"Замеры: {user_data.get('measurements', {})}"
        )
    else:
        progress_text = "📊 Твой прогресс:\n\n"
        for i, record in enumerate(progress_history[:5]):  # Показываем последние 5 записей
            progress_text += f"📅 {record['date'][:10]}\n"
            progress_text += f"Вес: {record['weight']} кг\n"
            if record['measurements']:
                progress_text += f"Замеры: {record['measurements']}\n"
            progress_text += "\n"
        
        await update.message.reply_text(progress_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    text = update.message.text
    
    # Проверяем, находимся ли в процессе онбординга
    if 'onboarding_state' in context.user_data:
        await handle_onboarding(update, context)
        return
    
    # Обработка кнопок главного меню
    if "🏋️ Новый план тренировок" in text:
        await handle_workout_plan(update, context)
    elif "🍎 Расчет питания" in text:
        await handle_nutrition_plan(update, context)
    elif "💊 Спортивное питание" in text:
        await handle_supplements(update, context)
    elif "📊 Мой прогресс" in text:
        await handle_progress(update, context)
    elif "📏 Обновить замеры" in text:
        await update.message.reply_text(
            "Введи новые замеры через запятую: обхват груди, талии, бедер, бицепса (в см)\n"
            "Например: 102, 78, 97, 36"
        )
        context.user_data['updating_measurements'] = True
    elif "⚙️ Настройки" in text:
        await update.message.reply_text(
            "⚙️ Настройки:\n\n"
            "Для изменения данных используй команду /start\n"
            "Для сброса всех данных используй команду /reset"
        )
    else:
        # Проверяем, обновляет ли пользователь замеры
        if context.user_data.get('updating_measurements'):
            try:
                measurements = [float(x.strip()) for x in text.split(',')]
                if len(measurements) == 4:
                    user_id = update.effective_user.id
                    user_data = db.get_user(user_id)
                    
                    new_measurements = {
                        'chest': measurements[0],
                        'waist': measurements[1],
                        'hips': measurements[2], 
                        'bicep': measurements[3]
                    }
                    
                    # Обновляем данные пользователя
                    user_data['measurements'] = new_measurements
                    db.save_user(user_data)
                    
                    # Сохраняем в историю прогресса
                    db.save_progress(user_id, user_data['weight'], new_measurements)
                    
                    await update.message.reply_text("✅ Замеры обновлены!")
                    context.user_data['updating_measurements'] = False
                else:
                    await update.message.reply_text("Нужно ввести ровно 4 замера через запятую.")
            except ValueError:
                await update.message.reply_text("Пожалуйста, введи замеры числами через запятую.")
        else:
            # Обычное сообщение - отправляем в Gemini
            user_id = update.effective_user.id
            user_data = db.get_user(user_id)
            
            if user_data:
                await update.message.reply_text("⏳ Думаю над ответом...")
                try:
                    response = await gemini.generate_response(user_data, text)
                    await update.message.reply_text(response, parse_mode='Markdown')
                except Exception as e:
                    logger.error(f"Ошибка генерации ответа: {e}")
                    await update.message.reply_text("Произошла ошибка. Попробуй переформулировать вопрос.")
            else:
                await update.message.reply_text("Сначала пройди регистрацию с помощью команды /start")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс данных пользователя"""
    await update.message.reply_text(
        "⚠️ Это удалит все твои данные. Уверен?\n\n"
        "Напиши 'ДА' для подтверждения или любое другое сообщение для отмены."
    )
    context.user_data['confirming_reset'] = True

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь по боту"""
    help_text = """
🏆 IFBB Pro Dual-Coach AI - Твой персональный ИИ-тренер

🔥 Возможности:
• Персональные планы тренировок на 4 недели
• Точный расчет КБЖУ и план питания  
• Рекомендации по спортивному питанию
• Отслеживание прогресса и замеров
• Адаптация под твой уровень и цели

👨‍🏫 Тренеры:
• Ронни Коулман (для мужчин) - 8x Mr. Olympia
• Дженет Лайог (для женщин) - Bikini Olympia Champion

📱 Команды:
/start - Начать работу с ботом
/help - Показать эту справку
/reset - Сбросить все данные

💪 Готов стать лучшей версией себя? Жми /start!
    """
    
    await update.message.reply_text(help_text)