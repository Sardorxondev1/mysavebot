from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove



async def main_panel():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton('🎧 Моя музика'), KeyboardButton('🎞 Мої відео'))
    markup.row(KeyboardButton('➕ Додати музику'), KeyboardButton('➕ Додати відео'))
    
    return markup

