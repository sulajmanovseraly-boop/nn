import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext
from datetime import datetime

# Настройки
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8372633951:AAGNZQfYEfVw2qwIE0F3EB1y8hcuOxurBlw")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "1159623437"))

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Хранилище
messages = []
user_sessions = {}

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💡 Предложение", callback_data="Предложение")],
        [InlineKeyboardButton("⚠️ Жалоба", callback_data="Жалоба")],
        [InlineKeyboardButton("🚀 Идея", callback_data="Идея")],
        [InlineKeyboardButton("📚 Вопрос", callback_data="Вопрос")]
    ]
    update.message.reply_text(
        "🎓 Анонимный Школьный Бот\n\n🔒 ВСЁ АНОНИМНО\n\nВыбери категорию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_sessions[query.from_user.id] = query.data
    query.edit_message_text(f"📝 {query.data}\n\nНапиши сообщение:")

def message_handler(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id not in user_sessions:
        update.message.reply_text("❌ Сначала выбери категорию через /start")
        return
    
    # Сохраняем сообщение
    msg_data = {
        'id': len(messages) + 1,
        'time': datetime.now().strftime('%H:%M %d.%m'),
        'category': user_sessions[user_id],
        'text': update.message.text,
        'user_id': user_id,
        'username': update.effective_user.username or 'без username',
        'name': f"{update.effective_user.first_name or ''} {update.effective_user.last_name or ''}".strip()
    }
    messages.append(msg_data)
    
    # Ответ пользователю
    update.message.reply_text(
        f"✅ Сообщение отправлено анонимно!\n\n"
        f"ID: #{msg_data['id']}\n"
        f"Категория: {msg_data['category']}"
    )
    
    # Уведомление админу
    user_info = f"👤 {msg_data['name']} (@{msg_data['username']})" if msg_data['name'] else f"👤 @{msg_data['username']}"
    context.bot.send_message(
        ADMIN_CHAT_ID,
        f"🆕 #{msg_data['id']} {msg_data['category']}\n"
        f"🕒 {msg_data['time']}\n"
        f"{user_info}\n"
        f"🆔 {msg_data['user_id']}\n\n"
        f"📝 {msg_data['text']}"
    )
    
    del user_sessions[user_id]

def view_messages(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_CHAT_ID:
        update.message.reply_text("❌ Нет доступа")
        return
    
    if not messages:
        update.message.reply_text("📭 Сообщений нет")
        return
    
    # Показываем последние 5 сообщений
    recent = messages[-5:][::-1]
    response = "📋 Сообщения:\n\n"
    
    for msg in recent:
        response += f"#{msg['id']} {msg['category']}\n👤 {msg['name']} (@{msg['username']})\n📝 {msg['text'][:50]}...\n\n"
    
    update.message.reply_text(response)

def main():
    # Создаем Updater
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Получаем dispatcher
    dp = updater.dispatcher
    
    # Добавляем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("view", view_messages))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    
    # Запускаем бота
    print("🚀 Бот запущен!")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
