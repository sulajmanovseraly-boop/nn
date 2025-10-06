import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_CHAT_ID = int(os.environ["ADMIN_CHAT_ID"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

messages = []
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💡 Предложение", callback_data="Предложение")],
        [InlineKeyboardButton("⚠️ Жалоба", callback_data="Жалоба")],
        [InlineKeyboardButton("🚀 Идея", callback_data="Идея")],
        [InlineKeyboardButton("📚 Вопрос", callback_data="Вопрос")]
    ]
    await update.message.reply_text(
        "🎓 Анонимный Школьный Бот\n\n🔒 ВСЁ АНОНИМНО\n\nВыбери категорию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_sessions[query.from_user.id] = query.data
    await query.edit_message_text(f"📝 {query.data}\n\nНапиши сообщение:")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_sessions:
        await update.message.reply_text("❌ Сначала выбери категорию через /start")
        return
    
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
    
    await update.message.reply_text(f"✅ Отправлено анонимно!\n\nID: #{msg_data['id']}\nКатегория: {msg_data['category']}")
    
    user_info = f"👤 {msg_data['name']} (@{msg_data['username']})" if msg_data['name'] else f"👤 @{msg_data['username']}"
    await context.bot.send_message(
        ADMIN_CHAT_ID,
        f"🆕 #{msg_data['id']} {msg_data['category']}\n"
        f"🕒 {msg_data['time']}\n"
        f"{user_info}\n🆔 {msg_data['user_id']}\n\n"
        f"📝 {msg_data['text']}\n\n💬 /view"
    )
    
    del user_sessions[user_id]

async def view_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ Нет доступа")
        return
    if not messages:
        await update.message.reply_text("📭 Сообщений нет")
        return
    
    recent = messages[-5:][::-1]
    response = "📋 Сообщения:\n\n"
    for msg in recent:
        response += f"#{msg['id']} {msg['category']}\n👤 {msg['name']} (@{msg['username']})\n📝 {msg['text'][:60]}...\n\n"
    await update.message.reply_text(response + f"📊 Всего: {len(messages)}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    if not messages:
        await update.message.reply_text("📊 Нет сообщений")
        return
    
    categories = {}
    users = set()
    for msg in messages:
        categories[msg['category']] = categories.get(msg['category'], 0) + 1
        users.add(msg['user_id'])
    
    stats_text = f"📊 Статистика\n\nВсего: {len(messages)}\nОтправителей: {len(users)}\n\n"
    for cat, count in categories.items():
        stats_text += f"• {cat}: {count}\n"
    await update.message.reply_text(stats_text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("view", view_messages))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("🚀 Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
