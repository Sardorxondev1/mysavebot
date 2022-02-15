from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove



async def main_panel():
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('🎧 Моя музика')
    ).add(
        KeyboardButton('Мої відео')
    )
    return markup

