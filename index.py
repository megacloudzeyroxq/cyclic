import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# In-memory storage for invited counts (resets if bot restarts)
user_invites = {}

# Your bot token and group ID
BOT_TOKEN = "7961842023:AAEXgSZXzfspEhJ8fwNaJgy-pjP7lBA7QkI"
GROUP_ID = -1002851710605  # Your group numeric ID

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Only act in your group
    if chat_id != GROUP_ID:
        return

    if user_id not in user_invites:
        user_invites[user_id] = 0

    if user_invites[user_id] < 3:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        except Exception as e:
            logging.warning(f"Failed to delete message: {e}")

        keyboard = [
            [InlineKeyboardButton("Invite Contacts", switch_inline_query="")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Hey [{update.effective_user.first_name}](tg://user?id={user_id}), you need to invite 3 members to send messages!\n\nClick below to invite.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != GROUP_ID:
        return

    inviter_id = update.message.from_user.id
    if inviter_id not in user_invites:
        user_invites[inviter_id] = 0
    user_invites[inviter_id] += len(update.message.new_chat_members)

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Thanks [{update.message.from_user.first_name}](tg://user?id={inviter_id})! You have invited {user_invites[inviter_id]}/3 members.",
        parse_mode="Markdown"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Invite 3 members to start chatting.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    print("Bot is running...")
    app.run_polling()
