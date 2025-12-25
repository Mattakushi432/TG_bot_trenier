from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database import UserDatabase
from gemini_client import GeminiClient
from config import DATABASE_PATH
import logging
import re
import sqlite3

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация компонентов
db = UserDatabase()
gemini = GeminiClient()

def clean_text_for_telegram(text):
    """Очистка текста от проблемных символов для Telegram"""
    if not text:
        return text
    
    # Убираем проблемные символы Markdown
    text = text.replace('*', '')
    text = text.replace('_', '')
    text = text.replace('`', '')
    text = text.replace('[', '')
    text = text.replace(']', '')
    
    # Убираем HTML теги если есть
    text = re.sub(r'<[^>]+>', '', text)
    
    return text

def split_long_message(text, max_length=4000):
    """Разбивка длинного сообщения на части"""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    # Разбиваем по абзацам
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        # Если добавление абзаца превысит лимит
        if len(current_part) + len(paragraph) + 2 > max_length:
            if current_part:
                parts.append(current_part.strip())
                current_part = paragraph
            else:
                # Если один абзац слишком длинный, разбиваем по предложениям
                sentences = paragraph.split('. ')
                for sentence in sentences:
                    if len(current_part) + len(sentence) + 2 > max_length:
                        if current_part:
                            parts.append(current_part.strip())
                            current_part = sentence
                        else:
                            # Если предложение слишком длинное, обрезаем
                            parts.append(sentence[:max_length-50] + "...")
                    else:
                        current_part += sentence + ". "
        else:
            current_part += paragraph + "\n\n"
    
    if current_part.strip():
        parts.append(current_part.strip())
    
    return parts

async def send_long_message(update, text):
    """Отправка длинного сообщения частями"""
    clean_text = clean_text_for_telegram(text)
    parts = split_long_message(clean_text)
    
    for i, part in enumerate(parts):
        if i == 0:
            await update.message.reply_text(part)
        else:
            # Добавляем номер части для длинных сообщений
            part_header = f"📄 Часть {i+1}/{len(parts)}:\n\n"
            await update.message.reply_text(part_header + part)

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
    'WORKOUTS_PER_WEEK': 'workouts_per_week',
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
            "Сколько раз в неделю ты можешь тренироваться?",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("2 раза"), KeyboardButton("3 раза")],
                [KeyboardButton("4 раза"), KeyboardButton("5+ раз")]
            ], resize_keyboard=True)
        )
        context.user_data['onboarding_state'] = ONBOARDING_STATES['WORKOUTS_PER_WEEK']
    
    elif state == ONBOARDING_STATES['WORKOUTS_PER_WEEK']:
        if "2 раза" in text:
            user_info['workouts_per_week'] = 2
        elif "3 раза" in text:
            user_info['workouts_per_week'] = 3
        elif "4 раза" in text:
            user_info['workouts_per_week'] = 4
        elif "5+ раз" in text:
            user_info['workouts_per_week'] = 5
        else:
            await update.message.reply_text("Пожалуйста, выбери количество тренировок из предложенных вариантов.")
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
        workouts_text = f"{user_info['workouts_per_week']} раз в неделю"
        
        success_message = (
            f"🎉 Отлично! Регистрация завершена!\n\n"
            f"Теперь я, {coach_name}, буду твоим персональным тренером.\n"
            f"Учту, что ты можешь тренироваться {workouts_text}.\n"
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
        workout_plan = gemini.generate_workout_plan(user_data)
        
        # Сохраняем план в базу данных
        db.save_workout_plan(user_id, {'plan': workout_plan, 'type': 'workout'})
        
        # Отправляем план частями если он длинный
        await send_long_message(update, workout_plan)
        
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
        nutrition_plan = gemini.calculate_nutrition(user_data)
        await send_long_message(update, nutrition_plan)
        
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
        supplements = gemini.recommend_supplements(user_data)
        await send_long_message(update, supplements)
        
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
    
    def calculate_changes(old_measurements, new_measurements):
        """Расчет изменений между замерами"""
        if not old_measurements or not new_measurements:
            return ""
        
        changes = []
        labels = {
            'chest': 'Грудь',
            'waist': 'Талия', 
            'hips': 'Бедра',
            'bicep': 'Бицепс'
        }
        
        for key in new_measurements:
            if key in old_measurements:
                old_val = float(old_measurements[key])
                new_val = float(new_measurements[key])
                change = new_val - old_val
                
                if change != 0:
                    label = labels.get(key, key.capitalize())
                    sign = "+" if change > 0 else ""
                    changes.append(f"{label}: {sign}{change:.1f} см")
        
        return "\n".join(changes) if changes else "Нет изменений"
    
    if not progress_history:
        current_measurements = format_measurements(user_data.get('measurements', {}))
        
        progress_text = (
            "📊 Твой профиль:\n\n"
            f"⚖️ Текущий вес: {user_data['weight']} кг\n\n"
            f"📏 Замеры тела:\n{current_measurements}\n\n"
            "📈 История изменений пуста.\n"
            "Обновляй замеры регулярно, чтобы отслеживать прогресс!"
        )
    else:
        progress_text = "📊 Твой прогресс:\n\n"
        
        for i, record in enumerate(progress_history[:5]):  # Показываем последние 5 записей
            date_str = record['date'][:10] if record['date'] else "Неизвестная дата"
            progress_text += f"📅 {date_str}\n"
            progress_text += f"⚖️ Вес: {record['weight']} кг\n"
            
            if record['measurements']:
                measurements_str = format_measurements(record['measurements'])
                progress_text += f"📏 Замеры:\n{measurements_str}\n"
                
                # Показываем изменения относительно предыдущей записи
                if i < len(progress_history) - 1:
                    prev_record = progress_history[i + 1]
                    if prev_record['measurements']:
                        changes = calculate_changes(prev_record['measurements'], record['measurements'])
                        if changes and changes != "Нет изменений":
                            progress_text += f"📈 Изменения:\n{changes}\n"
            
            progress_text += "\n"
        
        # Добавляем текущие данные
        current_measurements = format_measurements(user_data.get('measurements', {}))
        progress_text += "📋 Текущие данные:\n"
        progress_text += f"⚖️ Вес: {user_data['weight']} кг\n"
        progress_text += f"📏 Замеры:\n{current_measurements}"
    
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
        # Проверяем, подтверждает ли пользователь сброс данных
        if context.user_data.get('confirming_reset'):
            if text == 'ДА УДАЛИТЬ':
                user_id = update.effective_user.id
                
                # Удаляем пользователя из базы данных
                try:
                    with sqlite3.connect(DATABASE_PATH) as conn:
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
                        cursor.execute('DELETE FROM progress WHERE user_id = ?', (user_id,))
                        cursor.execute('DELETE FROM workout_plans WHERE user_id = ?', (user_id,))
                        conn.commit()
                    
                    await update.message.reply_text(
                        "🗑️ Все данные удалены!\n\n"
                        "🆕 Теперь ты можешь начать с чистого листа.\n"
                        "Отправь /start для новой регистрации!",
                        reply_markup=ReplyKeyboardMarkup([
                            [KeyboardButton("/start")]
                        ], resize_keyboard=True)
                    )
                    
                except Exception as e:
                    logger.error(f"Ошибка удаления данных пользователя {user_id}: {e}")
                    await update.message.reply_text(
                        "❌ Произошла ошибка при удалении данных.\n"
                        "Попробуй позже или обратись к администратору."
                    )
            elif "❌ Отмена" in text or text.lower() in ['отмена', 'нет', 'cancel']:
                await update.message.reply_text(
                    "✅ Сброс отменен!\n"
                    "Твои данные в безопасности.",
                    reply_markup=get_main_keyboard()
                )
            else:
                await update.message.reply_text(
                    "🤔 Не понял твой ответ.\n\n"
                    "Напиши 'ДА УДАЛИТЬ' для подтверждения удаления всех данных\n"
                    "или нажми '❌ Отмена' чтобы оставить все как есть.",
                    reply_markup=ReplyKeyboardMarkup([
                        [KeyboardButton("ДА УДАЛИТЬ"), KeyboardButton("❌ Отмена")]
                    ], resize_keyboard=True)
                )
                return
            
            # Убираем флаг подтверждения
            context.user_data.pop('confirming_reset', None)
            return
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
                    
                    # Красивое отображение обновленных замеров
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
                    
                    await update.message.reply_text(success_message)
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
                    response = gemini.generate_response(user_data, text)
                    # Отправляем ответ частями если он длинный
                    await send_long_message(update, response)
                except Exception as e:
                    logger.error(f"Ошибка генерации ответа: {e}")
                    await update.message.reply_text("Произошла ошибка. Попробуй переформулировать вопрос.")
            else:
                await update.message.reply_text("Сначала пройди регистрацию с помощью команды /start")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс данных пользователя"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text(
            "🤔 У тебя еще нет данных для сброса.\n"
            "Отправь /start чтобы начать регистрацию!"
        )
        return
    
    await update.message.reply_text(
        "⚠️ ВНИМАНИЕ! Это удалит ВСЕ твои данные:\n\n"
        "🗑️ Профиль и настройки\n"
        "📊 Историю прогресса\n"
        "🏋️ Сохраненные планы тренировок\n\n"
        "❓ Ты уверен, что хочешь начать с чистого листа?\n\n"
        "Напиши 'ДА УДАЛИТЬ' для подтверждения или любое другое сообщение для отмены.",
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("ДА УДАЛИТЬ"), KeyboardButton("❌ Отмена")]
        ], resize_keyboard=True)
    )
    context.user_data['confirming_reset'] = True

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Остановка работы с ботом"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if user_data:
        coach_name = "Ронни Коулман" if user_data['gender'] == 'male' else "Дженет Лайог"
        goodbye_message = (
            f"👋 До свидания от {coach_name}!\n\n"
            "🏆 Помни: чемпионы никогда не сдаются!\n"
            "💪 Твои данные сохранены и ждут твоего возвращения.\n\n"
            "🔄 Когда будешь готов продолжить - просто напиши /start\n"
            "🗑️ Если захочешь начать заново - используй /reset\n\n"
            "✨ Удачи в достижении твоих целей!"
        )
        
        if user_data['gender'] == 'male':
            goodbye_message += "\n\n💥 Yeah buddy! Light weight! Увидимся на тренировке!"
        else:
            goodbye_message += "\n\n✨ Оставайся сильной и красивой! До встречи!"
    else:
        goodbye_message = (
            "👋 До свидания!\n\n"
            "Спасибо, что попробовал IFBB Pro Dual-Coach AI!\n"
            "Возвращайся когда захочешь начать тренироваться! 💪"
        )
    
    # Убираем клавиатуру
    from telegram import ReplyKeyboardRemove
    await update.message.reply_text(goodbye_message, reply_markup=ReplyKeyboardRemove())
    
    # Помечаем пользователя как неактивного (можно добавить поле в БД)
    context.user_data.clear()

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
• Учет количества тренировок в неделю (2-5+)

👨‍🏫 Тренеры:
• Ронни Коулман (для мужчин) - 8x Mr. Olympia
• Дженет Лайог (для женщин) - Bikini Olympia Champion

📱 Команды:
/start - Начать работу с ботом
/help - Показать эту справку
/reset - Полный сброс данных и перезапуск
/stop - Остановить работу с ботом

🎯 Готов стать лучшей версией себя? 
Если еще не зарегистрирован - жми /start!
Если хочешь изменить данные - используй /reset!
    """
    
    await update.message.reply_text(help_text)