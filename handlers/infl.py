from aiogram import types, F
from main import dp
import db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@dp.callback_query(F.text == "infl")
async def infl(call: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="👑️ Топ 10 за все время", callback_data="infl_all"))
    keyboard.add(InlineKeyboardButton(text="🏆️ Топ 10 в этом сезоне", callback_data="infl_season"))
    await call.message.answer("🏅️ Выберите категорию:", reply_markup = keyboard)

@dp.callback_query(F.text == "infl_all")
async def infl(call: types.CallbackQuery):
    top_fame = db.get_top_fame_all(10)
    _text = "👑️ Топ по зависимости за все время\n"
    
    top_users_text = [f"\n{_num}. {user[2]} - <b>{user[7]} Зависимости</b>" for _num, user in enumerate(top_fame, start=1)]
    _text += "".join(top_users_text)

    await call.message.answer(_text, parse_mode="HTML")

@dp.callback_query(F.text == "infl_season")
async def infl(call: types.CallbackQuery):
    top_fame = db.get_top_fame(10)
    _text = "👑️ Топ по зависимости в этом сезоне\n"
    
    top_users_text = [f"\n{_num}. {user[2]} - <b>{user[8]} Зависимости</b>" for _num, user in enumerate(top_fame, start=1)]
    _text += "".join(top_users_text)

    await call.message.answer(_text, parse_mode="HTML")

