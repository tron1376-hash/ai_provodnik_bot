import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_gigachat.chat_models import GigaChat
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

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
    logger.error("TELEGRAM_BOT_TOKEN не найден в .env файле!")
    exit(1)

if not GIGACHAT_CREDENTIALS:
    logger.error("GIGACHAT_API_KEY не найден в .env файле!")
    exit(1)

# Инициализация GigaChat
llm = GigaChat(
    credentials=GIGACHAT_CREDENTIALS,
    verify_ssl_certs=False,
    scope="GIGACHAT_API_PERS"
)

# Создание промпта для AI проводника
prompt_template = """Ты - AI Проводник, умный помощник для путешественников.
Твоя задача - помогать людям с вопросами о путешествиях, маршрутах, билетах и туризме.
Отвечай дружелюбно, информативно и по существу.

Вопрос пользователя: {question}

Твой ответ:"""

prompt = PromptTemplate(template=prompt_template, input_variables=["question"])

# Создание цепочки LangChain
chat_chain = LLMChain(llm=llm, prompt=prompt)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_message = """
🚂 Добро пожаловать в AI Проводник!

Я - ваш умный помощник для путешествий, работающий на базе GigaChat.

Что я умею:
✅ Помогать планировать маршруты
✅ Консультировать по вопросам путешествий
✅ Давать советы туристам
✅ Отвечать на вопросы о транспорте

Просто задайте мне вопрос! Например:
• "Как доехать из Москвы в Санкт-Петербург?"
• "Что посмотреть в Казани?"
• "Сколько стоит билет до Сочи?"

Команды:
/start - Начать работу
/help - Помощь
/menu - Главное меню
    """
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
❓ СПРАВКА ПО ИСПОЛЬЗОВАНИЮ

📌 Команды:
/start - Запустить бота
/help - Показать эту справку
/menu - Открыть главное меню

💬 Как пользоваться:
1. Просто напишите ваш вопрос в чат
2. AI-помощник ответит на вопросы о путешествиях
3. Используйте кнопки меню для быстрого доступа

📝 Примеры вопросов:
• "Как доехать из Москвы в Санкт-Петербург?"
• "Сколько стоит билет до Казани?"
• "Какие документы нужны для поездки?"
• "Что посмотреть в Сочи?"

🤖 Бот работает на базе GigaChat от Сбера
    """
    await update.message.reply_text(help_text)


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /menu"""
    menu_text = """
📋 ГЛАВНОЕ МЕНЮ

Выберите действие или просто напишите свой вопрос:

🔍 Поиск маршрутов
💬 Задать вопрос AI
ℹ️ О боте
❓ Помощь

Для выбора просто напишите, что вас интересует!
    """
    await update.message.reply_text(menu_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений с удалением предыдущих"""
    user_id = update.effective_user.id
    user_message = update.message.text
    current_question_id = update.message.message_id
    
    logger.info(f"Получено сообщение от {user_id}: {user_message}")
    
    # Удаляем предыдущие сообщения пользователя
    if user_id in user_last_messages:
        try:
            # Удаляем старый вопрос пользователя
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=user_last_messages[user_id]['question']
            )
            logger.info(f"Удалён старый вопрос пользователя {user_id}")
            
            # Удаляем старый ответ бота
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=user_last_messages[user_id]['answer']
            )
            logger.info(f"Удалён старый ответ бота для {user_id}")
        except Exception as e:
            logger.warning(f"Не удалось удалить старые сообщения: {e}")
    
    # Показываем что бот печатает
    await update.message.chat.send_action(action="typing")
    
    try:
        # Получаем ответ от AI
        response = chat_chain.invoke({"question": user_message})
        
        # Отправляем ответ
        bot_message = await update.message.reply_text(response)
        
        # Сохраняем ID сообщений для следующего удаления
        user_last_messages[user_id] = {
            'question': current_question_id,
            'answer': bot_message.message_id
        }
        
        logger.info(f"Ответ отправлен пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text(
            "😔 Извините, произошла ошибка. Попробуйте ещё раз."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Произошла ошибка: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "😔 Произошла ошибка при обработке запроса. Попробуйте позже."
        )


def main():
    """Главная функция запуска бота"""
    logger.info("🚂 AI Provodnik запущен и готов помогать пассажирам!")
    
    # Создание приложения
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    
    # Регистрация обработчика текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Регистрация обработчика ошибок
    application.add_error_handler(error_handler)
    
    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
