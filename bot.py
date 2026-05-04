import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from openai import OpenAI

# Fayllarni yuklash
from keyboards import main_menu, back_menu
from states import LessonStates, AdminStates

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# --- 1. START KOMANDASI ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}!\n"
        "O'quv botiga xush kelibsiz. Quyidagi menyudan foydalaning:",
        reply_markup=main_menu()
    )

# --- 2. O'QITUVCHI: DARS QO'SHISH (AI BILAN) ---
@dp.message(F.text == "➕ Dars qo'shish")
async def add_lesson(message: types.Message, state: FSMContext):
    await message.answer("Dars mavzusini kiriting:", reply_markup=back_menu())
    await state.set_state(LessonStates.waiting_for_title)

@dp.message(LessonStates.waiting_for_title)
async def lesson_title(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await cmd_start(message)
    
    await state.update_data(title=message.text)
    await message.answer("Dars matnini yuboring (AI tahlil qilishi uchun):")
    await state.set_state(LessonStates.waiting_for_content)

@dp.message(LessonStates.waiting_for_content)
async def lesson_content(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await cmd_start(message)

    user_data = await state.get_data()
    text = message.text
    await message.answer("🤖 AI darsni qayta ishlamoqda, kuting...")

    # AI Orqali xulosa chiqarish
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Quyidagi matndan qisqa xulosa va 3 ta test savoli tuzib ber: {text}"}]
        )
        ai_res = response.choices[0].message.content
        
        await message.answer(f"✅ Dars tayyor!\n\nMavzu: {user_data['title']}\n\n{ai_res}", reply_markup=main_menu())
    except Exception as e:
        await message.answer("❌ AI bilan bog'lanishda xato yuz berdi.", reply_markup=main_menu())
    
    await state.clear()

# --- 3. ADMIN: LOGIN ---
@dp.message(F.text == "🔑 Admin")
async def admin_login(message: types.Message, state: FSMContext):
    await message.answer("Admin parolini kiriting:", reply_markup=back_menu())
    await state.set_state(AdminStates.waiting_for_password)

@dp.message(AdminStates.waiting_for_password)
async def check_admin(message: types.Message, state: FSMContext):
    if message.text == os.getenv("ADMIN_PASSWORD"):
        await message.answer("Xush kelibsiz Admin! Sizda barcha huquqlar bor.", reply_markup=main_menu())
    else:
        await message.answer("Xato parol!", reply_markup=main_menu())
    await state.clear()

# --- 4. BOTNI ISHGA TUSHIRISH ---
async def main():
    print("Bot yoqildi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())