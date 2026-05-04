from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📚 Fanlar"), KeyboardButton(text="➕ Dars qo'shish")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="🔑 Admin")]
    ], resize_keyboard=True)

def back_menu():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⬅️ Orqaga")]], resize_keyboard=True)