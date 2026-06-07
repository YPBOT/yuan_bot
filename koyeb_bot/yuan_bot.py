import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8928977352:AAGziHxAzmLUVGcSm1niDWf5HxDCpzDQXSo"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def yuan_to_byn(yuan: float) -> float:
    return 0.56383 * yuan - 0.00002553 * yuan * yuan

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    message_text = (
        f"Привет, {user_name}!\n"
        "Я бот, который поможет рассчитать сумму твоего заказа 😉💰\n\n"
        "Рабочий диапазон: 150–2500 юаней.\n\n"
        "Желаем вам приятных покупок 😊🛍️"
    )
    keyboard = [
        [InlineKeyboardButton("Рассчитать заказ", callback_data="calculate")],
        [InlineKeyboardButton("Отзывы", url="https://t.me/YPComs")],
        [InlineKeyboardButton("Оформить заказ", url="https://t.me/YourAgnt")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message_text, reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_main_menu(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "calculate":
        # Отправляем новое сообщение без reply-клавиатуры, только текст
        await query.message.reply_text("Пожалуйста, введите цену в юанях:")
        context.user_data['awaiting_amount'] = True

async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_amount'):
        return
    try:
        yuan_text = update.message.text.strip().replace(',', '.')
        yuan = float(yuan_text)
        if yuan < 150:
            await update.message.reply_text("❌ Сумма должна быть не менее 150 юаней.\nПожалуйста, введите число от 150 до 2500.")
            return
        if yuan > 2500:
            await update.message.reply_text("❌ Сумма должна быть не выше 2500 юаней.\nПожалуйста, введите число от 150 до 2500.")
            return
        
        byn = yuan_to_byn(yuan)
        byn_display = str(round(byn))
        
        if yuan.is_integer():
            yuan_display = f"{int(yuan)}"
        else:
            yuan_display = f"{yuan:.2f}"
        
        result_text = (
            f"✅ Итоговая стоимость: {byn_display} BYN (без учёта доставки)\n\n"
            "Доставка оплачивается по приезду ваших товаров в РБ. Стоимость доставки 7$ кг.\n\n"
            "❗️Для оформления заказа необходимо отправить ссылку на товар, скриншот и размер выбранной позиции: @YourAgnt"
        )
        
        keyboard = [
            [InlineKeyboardButton("Рассчитать заказ", callback_data="calculate")],
            [InlineKeyboardButton("Отзывы", url="https://t.me/YPComs")],
            [InlineKeyboardButton("Оформить заказ", url="https://t.me/YourAgnt")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(result_text, reply_markup=reply_markup)
        context.user_data['awaiting_amount'] = False
        
    except ValueError:
        await update.message.reply_text("❌ Ошибка: введите число, например 500 или 150.75")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount))
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
