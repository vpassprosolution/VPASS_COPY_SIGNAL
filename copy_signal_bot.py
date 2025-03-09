import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from database import add_subscription, is_user_subscribed, remove_subscription
import magic

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
BOT_TOKEN = "7900613582:AAGCwv6HCow334iKB4xWcyzvWj_hQBtmN4A"  # Replace with your actual bot token

# Conversation states
GROUP_LINK, SIGNAL_FORMAT, CONFIRM_UNSUBSCRIBE = range(3)

# Start command - Shows welcome message
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome to VPASS COPY SIGNAL! 📡\n"
        "You can subscribe to signals from any Telegram group.\n"
        "Use /subscribe to start or /unsubscribe to stop receiving signals."
    )

# Subscribe command - Asks user for group link
def subscribe(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("🔗 Please send the Telegram group link where you want to copy signals.")
    return GROUP_LINK

# Handles user input (Telegram group link)
def group_link(update: Update, context: CallbackContext) -> int:
    group_link = update.message.text

    # Extract group ID (assuming the bot is already in the group)
    if "t.me/" in group_link:
        group_id = group_link.split("/")[-1]  # Extract ID from link
    else:
        try:
            group_id = int(group_link)  # Direct ID input
        except ValueError:
            update.message.reply_text("❌ Invalid group link or ID. Please try again.")
            return GROUP_LINK

    context.user_data["group_id"] = group_id
    update.message.reply_text("✅ Group detected! Now, what type of signals do you want to receive?\n"
                              "Example: 'Gold Buy/Sell', 'Crypto Breakout', 'Forex TP/SL'")
    return SIGNAL_FORMAT

# Handles user input (Signal Format)
def signal_format(update: Update, context: CallbackContext) -> int:
    signal_format = update.message.text
    user_id = update.message.chat_id
    group_id = context.user_data["group_id"]

    # Save subscription to database
    add_subscription(user_id, group_id, signal_format)

    update.message.reply_text(f"✅ Subscription successful!\n"
                              f"You will receive signals from **{group_id}** with format: {signal_format}.\n"
                              "Use /unsubscribe to stop anytime.")
    return ConversationHandler.END

# Unsubscribe command
def unsubscribe(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id

    # Check if user is subscribed
    subscription = is_user_subscribed(user_id)
    if subscription:
        update.message.reply_text(
            "⚠️ Are you sure you want to unsubscribe?\n"
            "You will no longer receive signals from this group.",
            reply_markup=ReplyKeyboardMarkup([["✅ Yes", "❌ No"]], one_time_keyboard=True)
        )
        return CONFIRM_UNSUBSCRIBE
    else:
        update.message.reply_text("❌ You are not subscribed to any group.")
        return ConversationHandler.END

# Handles Unsubscribe Confirmation
def confirm_unsubscribe(update: Update, context: CallbackContext) -> int:
    user_id = update.message.chat_id
    response = update.message.text

    if response == "✅ Yes":
        remove_subscription(user_id)
        update.message.reply_text("✅ You have been unsubscribed. You will no longer receive signals.")
    else:
        update.message.reply_text("❌ Unsubscribe canceled.")

    return ConversationHandler.END

# Cancel function (if user cancels)
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("🚫 Action canceled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Main function - Start the bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Conversation handler for subscribing
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("subscribe", subscribe)],
        states={
            GROUP_LINK: [MessageHandler(Filters.text & ~Filters.command, group_link)],
            SIGNAL_FORMAT: [MessageHandler(Filters.text & ~Filters.command, signal_format)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation handler for unsubscribing
    unsubscribe_handler = ConversationHandler(
        entry_points=[CommandHandler("unsubscribe", unsubscribe)],
        states={
            CONFIRM_UNSUBSCRIBE: [MessageHandler(Filters.text & ~Filters.command, confirm_unsubscribe)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv_handler)
    dp.add_handler(unsubscribe_handler)

    # Start bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
