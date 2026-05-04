import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import google.generativeai as genai  # Gemini kutubxonasi

# Fayllarni yuklash
from keyboards import main_menu, back_menu
from states import LessonStates, AdminStates

load_dotenv()

# --- GEMINI SOZLAMALARI ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash') # Tezkor va tekin model

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}!\n"
        "Geminiga ulangan ta'lim botiga xush kelibsiz.",
        reply_markup=main_menu()
    )

# --- O'QITUVCHI: DARS QO'SHISH (GEMINI BILAN) ---
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
    await message.answer("Dars matnini yuboring (Gemini tahlil qilishi uchun):")
    await state.set_state(LessonStates.waiting_for_content)

@dp.message(LessonStates.waiting_for_content)
async def lesson_content(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await cmd_start(message)

    user_data = await state.get_data()
    text = message.text
    await message.answer("🤖 Gemini darsni tahlil qilmoqda...")

    try:
        # Gemini-ga so'rov yuborish
        prompt = f"""
        Siz professional o'qituvchisiz. Quyidagi dars matni asosida:
        1. Darsning qisqacha xulosasini yozing.
        2. Matn bo'yicha talabalar uchun 3 ta qiziqarli test savolini tuzing.
        Hammasi o'zbek tilida bo'lsin.
        
        Matn: {text}
        """
        
        response = model.generate_content(prompt)
        ai_res = response.text
        
        await message.answer(
            f"✅ **Dars tayyorlandi!**\n\n**Mavzu:** {user_data['title']}\n\n{ai_res}", 
            parse_mode="Markdown", 
            reply_markup=main_menu()
        )
    except Exception as e:
        print(f"Xato: {e}")
        await message.answer("❌ Gemini bilan bog'lanishda xato yuz berdi. Kalitni tekshiring.", reply_markup=main_menu())
    
    await state.clear()

# --- ADMIN LOGIN ---
@dp.message(F.text == "🔑 Admin")
async def admin_login(message: types.Message, state: FSMContext):
    await message.answer("Admin parolini kiriting:", reply_markup=back_menu())
    await state.set_state(AdminStates.waiting_for_password)

@dp.message(AdminStates.waiting_for_password)
async def check_admin(message: types.Message, state: FSMContext):
    if message.text == os.getenv("ADMIN_PASSWORD"):
        await message.answer("Xush kelibsiz Admin!", reply_markup=main_menu())
    else:
        await message.answer("Xato parol!", reply_markup=main_menu())
    await state.clear()

async def main():
    print("Bot Gemini bilan ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
