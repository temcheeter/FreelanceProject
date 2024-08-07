from aiogram import types, F
from main import dp, bot
import db
import asyncio
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import random
import time
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import datetime

def kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🎲️ Кубик", callback_data="dice"))
    keyboard.add(InlineKeyboardButton(text="🎰 Casino", callback_data="casino"))
    keyboard.add(InlineKeyboardButton(text="🧩️ Free", callback_data="free"))
    return keyboard

def give_puff(_ref):
    _user_id = _ref
    rare = "RARE Pod"
    rand = random.randint(0, len(db.get_rare(rare))-1)
    _rare = db.get_rare(rare)[rand]
    photo = _rare[1]
    caption = _rare[5]+'\n\nПолучай бесплатную карту'
    fame = _rare[4]
    _fame, fame_all, fame_season = db.get_fame(_user_id)
    card = db.get_cards(_user_id)[0]
    db.set_fame(_user_id, int(fame)+int(_fame), fame_all, fame_season)
    db.update_cards(_user_id, card +", "+str(_rare[0]))
    return _rare

def get_next_monday():
    today = datetime.datetime.today()
    days_until_next_monday = (7 - today.weekday()) % 7
    next_monday = today + datetime.timedelta(days=days_until_next_monday)
    return next_monday.date()

@dp.callback_query(F.text == "jumanji")
async def jumanji(call: types.CallbackQuery):
    if not db.get_users_exist_state(call.from_user.id):
        db.add_user_to_state(call.from_user.id, '2020-03-03', '2023-08-10 00:59:37')
    await call.message.answer("💬️Выбери игру из списка", reply_markup = kb())
    

@dp.callback_query(F.text == "dice")
async def Dice(call: types.CallbackQuery):
    user_id = call.from_user.id
    stat_time = datetime.datetime.strptime(db.get_states(user_id, 'state_dice'), '%Y-%m-%d').date()
    current_date = datetime.datetime.now().date()
    next_monday = get_next_monday()
    pp_time = datetime.datetime.strptime(db.get_info(user_id)[6], '%Y-%m-%d').date()
    if (stat_time < current_date):
        if pp_time > current_date:
                future_date = next_monday
                db.update_states(call.from_user.id, 'state_dice', future_date)
                msg = await bot.send_dice(user_id)
                _num1 = msg.dice.value
                msg = await bot.send_dice(user_id)
                _num2 = msg.dice.value
                await asyncio.sleep(3)
                await call.message.answer(f"""На 🎲️ кубиках выпали числа <b>{_num1}</b> и <b>{_num2}</b>\n\nВы получаете <b>{_num1 + _num2}</b> бесплатных попыток на открытие карт""", parse_mode="HTML")
                prev_bt = db.get_botnet(user_id)[4]
                db.update_botnet(user_id, 'comp_points', _num1 + _num2 + prev_bt)
        else:
            future_date = next_monday
            db.update_states(call.from_user.id, 'state_dice', future_date)
            msg = await bot.send_dice(user_id)
            _num = msg.dice.value
            await asyncio.sleep(3)
            await call.message.answer(f"""На 🎲️ кубике выпало число <b>{_num}</b>\n\nВы получаете <b>{_num}</b> бесплатных попыток на открытие карт""", parse_mode="HTML")
            prev_bt = db.get_botnet(user_id)[4]
            db.update_botnet(user_id, 'comp_points', _num + prev_bt)
    else:
        await call.message.answer(f"⚠️ На этой неделе броски кубика закончились...")


@dp.callback_query(F.text == "casino")  # Изменили текст на "casino"
async def Casino(call: types.CallbackQuery):  # Изменили имя функции на Casino
    user_id = call.from_user.id
    stat_time = datetime.datetime.strptime(db.get_states(user_id, 'state_casino'), '%Y-%m-%d').date()
    current_date = datetime.datetime.now().date()
    next_monday = get_next_monday()
    pp_time = datetime.datetime.strptime(db.get_info(user_id)[6], '%Y-%m-%d').date()
    if pp_time > current_date:
        if (stat_time < current_date):
            future_date = next_monday
            db.update_states(call.from_user.id, 'state_casino', future_date)  # Изменили состояние на 'state_casino'
            # Здесь можно добавить логику для "казино-рулетки". Например, генерация случайного числа, рандомизация выигрыша и т.д.
            # Пример:
            random_value = random.randint(1, 10)  # Здесь генерируйте случайное значение для определения выигрыша или проигрыша
            winnings = random_value  # Пример количества выигранных попыток на открытие карт
            await call.message.answer(f"🎉 Поздравляем! Вы выиграли {winnings} бесплатных попыток на открытие карт!")
            prev_bt = db.get_botnet(user_id)[4]
            db.update_botnet(user_id, 'comp_points', winnings + prev_bt)
        else:
            await call.message.answer("⚠️ На этой неделе игры в казино закончились...")
    else:
        await call.message.answer("⚠️ Казино доступно только обладателям Pod Pass")

@dp.callback_query(F.text == "free")
async def free(call: types.CallbackQuery):
    user_id = call.from_user.id
    stat_time = datetime.datetime.strptime(db.get_states(user_id, 'state_free'), '%Y-%m-%d').date()
    current_date = datetime.datetime.now().date()
    next_monday = get_next_monday()
    if (stat_time < current_date):
        # Разрешено использовать команду
        future_date = next_monday
        db.update_states(call.from_user.id, 'state_free', future_date)
        _rare = give_puff(user_id)
        photo = _rare[1]
        caption = _rare[5]+'\n\n🆓️ Получай бесплатную карту'
        await bot.send_photo(user_id, photo, caption)
    else:
        await call.message.answer(f"⚠️ Ты уже получил бесплатную карту на этой неделе...")
