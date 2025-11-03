import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from langchain_gigachat.chat_models import GigaChat
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Словарь для хранения ID последних сообщений пользователей
user_last_messages = {}

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токенов из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GIGACHAT_CREDENTIALS = os.getenv('GIGACHAT_API_KEY')

# Проверка наличия токенов
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не найден!")
    exit(1)

if not GIGACHAT_CREDENTIALS:
    logger.error("GIGACHAT_API_KEY не найден!")
    exit(1)

# Инициализация GigaChat
llm = GigaChat(
    credentials=GIGACHAT_CREDENTIALS,
    verify_ssl_certs=False,
    scope="GIGACHAT_API_PERS"
)

# Создание промпта
prompt_template = """Ты - AI Проводник в поезде дальнего следования.
Ты помогаешь пассажирам с информацией о поезде, маршруте, услугах и отвечаешь на вопросы.
Отвечай дружелюбно, кратко и по делу. Используй эмодзи для наглядности.

Вопрос пассажира: {question}

Твой ответ:"""

prompt = PromptTemplate(template=prompt_template, input_variables=["question"])
chat_chain = LLMChain(llm=llm, prompt=prompt)


# ============================================
# КОМАНДА /START - ГЛАВНОЕ МЕНЮ
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню с кнопками"""
    keyboard = [
        [InlineKeyboardButton("🚂 Мой поезд", callback_data='my_train')],
        [InlineKeyboardButton("🍜 Меню проводника", callback_data='menu')],
        [InlineKeyboardButton("🎯 Услуги в поезде", callback_data='services')],
        [InlineKeyboardButton("📍 Где мы сейчас?", callback_data='location')],
        [InlineKeyboardButton("ℹ️ Полезная информация", callback_data='info')],
        [InlineKeyboardButton("❓ Частые вопросы", callback_data='faq')],
        [InlineKeyboardButton("📞 Связаться с проводником", callback_data='conductor')],
        [InlineKeyboardButton("🎮 Развлечения", callback_data='entertainment')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        "🚂 *Здравствуйте! Я AI Проводник*\n\n"
        "Ваш цифровой помощник в пути!\n\n"
        "🎯 *Я помогу вам с:*\n"
        "✅ Информацией о поезде и маршруте\n"
        "✅ Заказом еды и напитков\n"
        "✅ Услугами в вагоне\n"
        "✅ Ответами на любые вопросы\n\n"
        "📱 *Выберите раздел или задайте вопрос текстом:*"
    )
    
    if update.message:
        await update.message.reply_text(
            welcome_message, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.message.reply_text(
            welcome_message, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )


# ============================================
# КОМАНДА /HELP
# ============================================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь по использованию бота"""
    help_text = (
        "ℹ️ *ПОМОЩЬ ПО БОТУ*\n\n"
        "🚂 /start - Главное меню\n"
        "❓ /help - Эта справка\n"
        "📋 /menu - Меню проводника\n\n"
        "💬 *Вы можете:*\n"
        "• Выбрать раздел из меню\n"
        "• Задать вопрос текстом\n"
        "• Попросить помощь в любое время\n\n"
        "🤖 Я работаю на базе GigaChat 24/7!"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


# ============================================
# ОБРАБОТЧИК КНОПОК
# ============================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки меню"""
    query = update.callback_query
    await query.answer()
    
    back_button = [[InlineKeyboardButton("◀️ Назад в меню", callback_data='back_to_menu')]]
    
    # Возврат в главное меню
    if query.data == 'back_to_menu':
        await start(update, context)
        return
    
    # ========== МОЙ ПОЕЗД ==========
    if query.data == 'my_train':
        train_text = (
            "🚂 *ИНФОРМАЦИЯ О ПОЕЗДЕ*\n\n"
            "🎫 Поезд: *№042А «Россия»*\n"
            "📍 Маршрут: Москва → Владивосток\n"
            "🚉 Отправление: Москва - 13:20\n"
            "🏁 Прибытие: Владивосток - через 6 дней\n\n"
            "📊 *ТЕКУЩИЙ СТАТУС:*\n"
            "⏱️ В пути: 2 дня 14 часов\n"
            "📍 Последняя станция: Новосибирск\n"
            "➡️ Следующая: Красноярск (через 8 ч)\n\n"
            "🚃 Ваш вагон: *№7 (купе)*\n"
            "🔢 Место: *24 (верхнее)*"
        )
        await query.message.reply_text(
            train_text,
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode='Markdown'
        )
    
    # ========== МЕНЮ ПРОВОДНИКА ==========
    elif query.data == 'menu':
        menu_text = (
            "🍜 *МЕНЮ У ПРОВОДНИКА*\n\n"
            "☕ *ГОРЯЧИЕ НАПИТКИ:*\n"
            "• Чай чёрный/зелёный - 50₽\n"
            "• Кофе 3 в 1 - 60₽\n"
            "• Какао - 70₽\n\n"
            "🍜 *БЫСТРОЕ ПИТАНИЕ:*\n"
            "• Лапша Доширак - 120₽\n"
            "• Пюре быстрого приготовления - 80₽\n"
            "• Каша овсяная - 70₽\n\n"
            "🍪 *СНЕКИ:*\n"
            "• Печенье - 80₽\n"
            "• Шоколад - 90₽\n"
            "• Чипсы - 120₽\n\n"
            "🥤 *НАПИТКИ:*\n"
            "• Вода 0.5л - 60₽\n"
            "• Сок 0.2л - 80₽\n"
            "• Coca-Cola - 100₽\n\n"
            "💰 Оплата: наличные или карта\n"
            "♨️ Кипяток - *БЕСПЛАТНО*"
        )
        await query.message.reply_text(
            menu_text,
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode='Markdown'
        )
    
    # ========== УСЛУГИ ==========
    elif query.data == 'services':
        services_text = (
            "🎯 *УСЛУГИ В ПОЕЗДЕ*\n\n"
            "☕ *ПИТАНИЕ:*\n"
            "• Напитки и снеки у проводника\n"
            "• Доставка еды в купе\n"
            "• Горячая вода (бесплатно)\n\n"
            "🛏️ *ПОСТЕЛЬНОЕ БЕЛЬЁ:*\n"
            "• Включено в стоимость\n"
            "• Смена по запросу\n\n"
            "🚿 *ГИГИЕНА:*\n"
            "• Туалеты в начале и конце вагона\n"
            "• Умывальники с горячей водой\n\n"
            "📱 *СВЯЗЬ:*\n"
            "• Wi-Fi (бесплатно)\n"
            "• Розетки 220В в купе\n\n"
            "🎮 *РАЗВЛЕЧЕНИЯ:*\n"
            "• Библиотека книг\n"
            "• Настольные игры\n"
            "• Фильмы онлайн"
        )
        await query.message.reply_text(
            services_text,
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode='Markdown'
        )
    
    # ========== ГЕОЛОКАЦИЯ ==========
    elif query.data == 'location':
        current_time = datetime.now().strftime("%H:%M")
        location_text = (
            f"📍 *ГДЕ МЫ СЕЙЧАС*\n\n"
            f"🕐 Текущее время: *{current_time}* (МСК+4)\n"
            f"🚂 Поезд в движении\n\n"
            "📊 *ПОСЛЕДНЯЯ СТАНЦИЯ:*\n"
            "🚉 Новосибирск-Главный\n"
            "⏰ Отправление: 45 минут назад\n\n"
            "➡️ *СЛЕДУЮЩАЯ ОСТАНОВКА:*\n"
            "🚉 Красноярск\n"
            "⏱️ Прибытие: через ~8 часов\n"
            "⏳ Стоянка: 15 минут\n\n"
            "🗺️ Пройдено: 40% пути\n"
            "🌡️ Погода: -12°C, малооблачно"
        )
        await query.message.reply_text(
            location_text,
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode='Markdown'
        )
    
    # ========== ПОЛЕЗНАЯ ИНФО ==========
    elif query.data == 'info':
        info_text = (
            "ℹ️ *ПОЛЕЗНАЯ ИНФОРМАЦИЯ*\n\n"
            "🕐 *РЕЖИМ:*\n"
            "• Проводники: 24/7\n"
            "• Туалеты закрываются за 15 мин до станций\n\n"
            "💰 *ОПЛАТА:*\n"
            "• Наличные, карты, СБП\n\n"
            "📱 *WI-FI:*\n"
            "• Сеть: RZD_Free_WiFi\n"
            "• Пароль: на стикере в купе\n\n"
            "🔌 *РОЗЕТКИ:*\n"
            "• 2 розетки в каждом купе\n"
            "• Дополнительные в коридоре\n\n"
            "🚭 *КУРЕНИЕ ЗАПРЕЩЕНО!*\n"
            "• Курить можно на станциях\n"
            "• Штраф: от 1000₽\n\n"
            "📞 *ЭКСТРЕННЫЕ ТЕЛЕФОНЫ:*\n"
            "• РЖД: 8-800-775-00-00\n"
            "• Полиция: 102"
        )
        await query.message.reply_text(
            info_text,
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode='Markdown'
        )
    
    # ========== FAQ ==========
    elif query.data == 'faq':
        faq_text = (
            "❓ *ЧАСТЫЕ ВОПРОСЫ*\n\n"
            "*❔ Где взять кипяток?*\n"
            "✅ В конце вагона (бесплатно)\n\n"
            "*❔ Можно ли алкоголь?*\n"
            "✅ Да, но в меру в купе\n\n"
            "*❔ Что при краже?*\n"
            "✅ Сообщить проводнику\n\n"
            "*❔ Можно выйти на станции?*\n"
            "✅ Да, но следите за временем!\n\n"
            "*❔ Плохо себя чувствую?*\n"
            "✅ Есть аптечка у проводника\n\n"
            "*❔ Мобильная связь?*\n"
            "✅ Да, но местами пропадает\n\n"
            "💬 Не нашли ответ? Задайте вопрос!"
        )
        await query.message.reply_text(
            faq_text,
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode='Markdown'
        )
    
    # ========== СВЯЗЬ С ПРОВОДНИКОМ ==========
    elif query.data == 'conductor':
        conductor_keyboard = [
            [InlineKeyboardButton("📞 Позвать проводника", callback_data='call_conductor')],
            [InlineKeyboardButton("🍽️ Заказать еду", callback_data='order_food')],
            [InlineKeyboardButton("🛏️ Попросить бельё", callback_data='request_linen')],
            [InlineKeyboardButton("🔧 Сообщить о проблеме", callback_data='report_issue')],
            [InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]
        ]
        conductor_text = (
            "📞 *СВЯЗЬ С ПРОВОДНИКОМ*\n\n"
            "Выберите действие:\n\n"
            "• Позвать к купе\n"
            "• Заказать доставку еды\n"
            "• Попросить бельё\n"
            "• Сообщить о проблеме\n\n"
            "⏰ Время отклика: 5-10 минут"
        )
        await query.message.reply_text(
            conductor_text,
            reply_markup=InlineKeyboardMarkup(conductor_keyboard),
            parse_mode='Markdown'
        )
    
    elif query.data == 'call_conductor':
        await query.message.reply_text(
            "✅ *Проводник вызван!*\n\n"
            "📍 Ваше купе: №24, вагон №7\n"
            "⏰ Подойдёт в течение 5-10 минут",
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode='Markdown'
        )
    
    elif query.data == 'order_food':
        await query.message.reply_text(
            "🍜 *ЗАКАЗ ЕДЫ*\n\n"
            "📝 Напишите в чат что хотите заказать\n"
            "Например: _'Хочу Доширак и кофе'_\n\n"
            "💰 Оплата при получении\n"
            "⏰ Доставка: 5-10 минут",
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode='Markdown'
        )
    
    elif query.data == 'request_linen':
        await query.message.reply_text(
            "✅ *Запрос принят!*\n\n"
            "🛏️ Проводник принесёт бельё\n"
            "⏰ В течение 10 минут",
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode='Markdown'
        )
    
    elif query.data == 'report_issue':
        await query.message.reply_text(
            "🔧 *СООБЩИТЬ О ПРОБЛЕМЕ*\n\n"
            "Опишите проблему в чат:\n"
            "• Не работает розетка\n"
            "• Холодно в купе\n"
            "• Шумные соседи\n\n"
            "Проводник решит проблему!",
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode='Markdown'
        )
    
    # ========== РАЗВЛЕЧЕНИЯ ==========
    elif query.data == 'entertainment':
        entertainment_text = (
            "🎮 *РАЗВЛЕЧЕНИЯ В ПУТИ*\n\n"
            "📚 *БИБЛИОТЕКА:*\n"
            "• Книги, журналы, газеты\n"
            "• У проводника в начале вагона\n\n"
            "🎬 *КИНО:*\n"
            "• Wi-Fi + онлайн-кинотеатры\n"
            "• Не забудьте наушники!\n\n"
            "🎲 *НАСТОЛЬНЫЕ ИГРЫ:*\n"
            "• Шахматы, шашки, карты\n"
            "• Монополия\n"
            "• Взять у проводника\n\n"
            "🎵 *МУЗЫКА:*\n"
            "• Spotify, Яндекс.Музыка\n"
            "• Через Wi-Fi\n\n"
            "💡 Хорошего путешествия!"
        )
        await query.message.reply_text(
            entertainment_text,
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode='Markdown'
        )


# ============================================
# ОБРАБОТЧИК AI СООБЩЕНИЙ
# ============================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений через AI"""
    user_id = update.effective_user.id
    user_message = update.message.text
    user_name = update.effective_user.first_name
    current_question_id = update.message.message_id
    
    logger.info(f"📨 Сообщение от {user_name} (ID: {user_id}): {user_message}")
    
    # Удаление предыдущих сообщений
    if user_id in user_last_messages:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=user_last_messages[user_id]['question']
            )
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=user_last_messages[user_id]['answer']
            )
            logger.info(f"🗑️ Удалены старые сообщения для {user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось удалить: {e}")
    
    # Показываем что бот печатает
    await update.message.chat.send_action(action="typing")

    try:
        # Получаем ответ от AI
        response = chat_chain.invoke({"question": user_message})
        
        # Извлекаем только текст
        ai_response = response['text']
        
        # Отправляем ответ
        bot_message = await update.message.reply_text(ai_response)
        
        # Сохраняем ID для следующего удаления
        user_last_messages[user_id] = {
            'question': current_question_id,
            'answer': bot_message.message_id
        }
        
        logger.info(f"✅ Ответ отправлен {user_id}")

    except Exception as e:
        logger.error(f"❌ Ошибка AI: {e}")
        await update.message.reply_text(
            "😔 Извините, AI временно недоступен.\n"
            "Попробуйте выбрать раздел из меню /start"
        )


# ============================================
# ОБРАБОТЧИК ОШИБОК
# ============================================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error(f"❌ Ошибка: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "😔 Произошла ошибка. Попробуйте позже или нажмите /start"
        )


# ============================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================
def main():
    """Запуск бота"""
    logger.info("🚂 AI Проводник запускается...")
    
    # Создание приложения
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    logger.info("✅ Бот запущен успешно!")
    logger.info("🚂 AI Проводник готов помогать!")
    print("=" * 50)
    print("✅ БОТ УСПЕШНО ЗАПУЩЕН!")
    print("🚂 AI Проводник для пассажиров")
    print("⏸️  Для остановки: Ctrl+C")
    print("=" * 50)

    # Запуск polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
