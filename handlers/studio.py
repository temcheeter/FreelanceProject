from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
async def pod_studio(message: types.Message):
    # keyboard = InlineKeyboardMarkup(1)
    # keyboard.add(InlineKeyboardButton(text="🏜 Pod Jumanji", callback_data="jumanji"))
    # keyboard.add(InlineKeyboardButton(text="👩‍💻️ Реферальная программа", callback_data="ref"))
    # keyboard.add(InlineKeyboardButton(text="🏆️ Influence", callback_data="infl"))
    # keyboard.add(InlineKeyboardButton(text="🧑‍💻️ Trade", callback_data="trade"))
    # keyboard.add(InlineKeyboardButton(text="🎒️ Pod Shop", callback_data="pod_shop"))
    # keyboard.add(InlineKeyboardButton(text="💼 Pod Pass", callback_data="pod_pass"))
    # keyboard.add(InlineKeyboardButton(text="🧸️ Squads", callback_data="squads"))
    # await message.answer("💬️ Выберите действие по кнопкам ниже", reply_markup = keyboard)
    kb = InlineKeyboardBuilder()
    items = [
        "🏜 Pod Jumanji",
        "👩‍💻️ Реферальная программа",
        "🏆️ Influence",
        "🧑‍💻️ Trade",
        "🎒️ Pod Shop",
        "💼 Pod Pass",
        "🧸️ Squads"
    ]
    [kb.button(text=item) for item in items]
    kb.adjust(1, 2, 1, 2, 1)
    await message.answer("💬️ Выберите действие по кнопкам ниже", reply_markup=kb.as_markup())