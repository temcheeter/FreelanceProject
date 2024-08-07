import aiogram
from aiogram import types, F
from main import dp, bot
import db
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InputMediaPhoto

class States(StatesGroup):
    _prev_next = State()
    _prev_next_ = State()
    _nickname_trade = State()

def keyboard(_all, __num):
    keyboard = InlineKeyboardMarkup(1)
    button = types.InlineKeyboardButton(text="⬅️", callback_data="prev")
    button2 = types.InlineKeyboardButton(text=str(__num)+"/"+str(_all), callback_data="-")
    button3 = types.InlineKeyboardButton(text="➡️", callback_data="next")
    button4 = types.InlineKeyboardButton(text="🔄️ Обмен", callback_data="_trade")
    button5 = types.InlineKeyboardButton(text="🚫️ Отменить", callback_data="cancel")
    keyboard.row(button, button2, button3)
    keyboard.add(button4)
    keyboard.add(button5)
    return keyboard

def _keyboard(_all, __num):
    keyboard = InlineKeyboardMarkup(1)
    button = types.InlineKeyboardButton(text="⬅️", callback_data="_prev")
    button2 = types.InlineKeyboardButton(text=str(__num)+"/"+str(_all), callback_data="-")
    button3 = types.InlineKeyboardButton(text="➡️", callback_data="_next")
    button4 = types.InlineKeyboardButton(text="🌵️ Выбрать карту", callback_data="_trade_")
    button5 = types.InlineKeyboardButton(text="🧨️ Отклонить", callback_data="decline")
    keyboard.row(button, button2, button3)
    keyboard.add(button4)
    keyboard.add(button5)
    return keyboard

def keyboard_accept():
    keyboard = InlineKeyboardMarkup(1)
    button = types.InlineKeyboardButton(text="🌵️ Выбрать карту для трейда", callback_data="select_card")
    button2 = types.InlineKeyboardButton(text="🧨️ Отклонить", callback_data="decline")
    keyboard.add(button)
    keyboard.add(button2)
    return keyboard

def keyboard_accept_all():
    keyboard = InlineKeyboardMarkup(1)
    button = types.InlineKeyboardButton(text="🌵️ Подтвердить трейд", callback_data="trade_ok")
    button2 = types.InlineKeyboardButton(text="🧨️ Отклонить", callback_data="decline")
    keyboard.add(button)
    keyboard.add(button2)
    return keyboard

@dp.callback_query(F.text == "trade")
async def trade(call: types.CallbackQuery, state: FSMContext):
    if await state.get_state() in (States._prev_next.state, States._prev_next_.state, States._nickname_trade.state):
        await call.message.answer("🚫 Вы уже находитесь в процессе трейда. Завершите текущий трейд, прежде чем начинать новый.")
    else:
        if db.get_cards(call.from_user.id)[0] == "0":
            await call.message.answer("🚫️ У вас еще нет карт для трейда")
            await state.finish()
        else:
            await States._prev_next.set()
            await state.finish()
            card = db.get_cards(call.from_user.id)[0]
            __data = card.split(", ")
            _all = len(__data)
            caption = f'''{db.get_file(__data[0])[2]}\nРедкость: {db.get_file(__data[0])[3]}\n\n🌵 Бро, нужно выбрать карту из твоей коллекции, которую ты хочешь обменять.'''
            await States._prev_next.set()
            await state.update_data(_num=1)
            await state.update_data(_num1=1)
            await state.update_data(lla=_all)
            await state.update_data(_num_card=__data[0])
            await call.message.answer_photo(db.get_file(__data[0])[1], caption, reply_markup=keyboard(_all, 1))

@dp.callback_query(F.text == ["next", "prev"], state=States._prev_next)
async def next_or_prev(call: types.CallbackQuery, state: FSMContext):
    _data = await state.get_data()
    card = db.get_cards(call.from_user.id)[0]
    __data = card.split(", ")
    __num = _data['_num']
    _all = _data['lla']

    if call.data == "next":
        next_num = 1 if __num == _all else __num + 1
    else:
        next_num = _all if __num == 1 else __num - 1

    photo = db.get_file(__data[next_num - 1])[1]
    caption = f'''{db.get_file(__data[next_num - 1])[2]}\nРедкость: {db.get_file(__data[next_num - 1])[3]}\n\n🌵 Бро, нужно выбрать карту из твоей коллекции, которую ты хочешь обменять.'''
    media = InputMediaPhoto(photo, caption=caption)

    try:
        await call.message.edit_media(media, reply_markup=keyboard(_all, next_num))
        await state.update_data(_num=next_num)
        await state.update_data(_num1=next_num)
        await state.update_data(_num_card=__data[next_num - 1])
    except aiogram.utils.exceptions.MessageNotModified:
        pass


@dp.callback_query(F.text == "_trade", state=States._prev_next)
async def set_trade(call: types.CallbackQuery, state: FSMContext):
    _data = await state.get_data()
    card = db.get_cards(call.from_user.id)[0]
    __data = card.split(", ")
    __num = _data['_num']
    _all = _data['lla']
    traded_card = __data[__num - 1]
    _num_card = _data['_num_card']
    caption = f'''🧟 Введи @username, которому хочешь отправить предложение обмена\n\n🦝 Если @username игрока не находится, ему нужно прописать /start в боте!'''
    media = InputMediaPhoto(db.get_file(traded_card)[1], caption=caption)
    await call.message.edit_media(media)
    await States._nickname_trade.set()
    await state.update_data(_num_card=_num_card)
    await state.update_data(card=traded_card)

@dp.message(state=States._nickname_trade)
async def nick_trade(message: types.Message, state: FSMContext):
    _data = await state.get_data()
    card = _data['card']
    _num_card = _data['_num_card']
    _num1 = _data['_num1']
    photo = db.get_file(_num_card)[1]
    karta = db.get_file(_num_card)[2]
    _data = message.text.split("@")
    _user = db.get_nickname(_data[1])[1]
    if _user == message.chat.id:
        await message.answer(f"🚫️ Вы не можете отправить запрос на обмен себе")
    else:
        try:
            _data = message.text.split("@")
            _user = db.get_nickname(_data[1])[1]
            await bot.send_photo(_user, photo, f"{karta}\n\n@{message.chat.username} предлагает тебе обмен", reply_markup=keyboard_accept())
            await message.answer(f"✅️ Запрос на обмен отправлен @{_data[1]}")
            _state = dp.current_state(chat=_user, user=_user)
            await _state.set_state(States._nickname_trade)
            await _state.update_data(card=card)
            await _state.update_data(_num1=_num1)
            await _state.update_data(prev_id=message.chat.id)
            await _state.update_data(_num_card=_num_card)
        except:
            await message.answer('🚫️ Пользователь не найден')
            await state.finish()

@dp.callback_query(F.text == "decline", state="*")
async def decline(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await state.finish()

@dp.callback_query(F.text == "select_card", state=States._nickname_trade)
async def select_card(call: types.CallbackQuery, state: FSMContext):
    if await state.get_state() in (States._prev_next.state, States._prev_next_.state):
        await call.message.answer("🚫 Вы уже находитесь в процессе трейда. Завершите текущий трейд, прежде чем начинать новый.")
    else:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        _data = await state.get_data()
        card = _data['card']
        prev_id = _data['prev_id']
        _num_card = _data['_num_card']
        await States._prev_next_.set()
        await state.update_data(card=card)
        await state.update_data(prev_id=prev_id)
        if db.get_cards(call.from_user.id)[0] == "0":
            await call.message.answer("🚫️ У вас еще нет карт для трейда")
            await state.finish()
        else:
            card = db.get_cards(call.from_user.id)[0]
            __data = card.split(", ")
            _all = len(__data)
            caption = f'''{db.get_file(__data[0])[2]}\nРедкость: {db.get_file(__data[0])[3]}\n\n🌵 Бро, нужно выбрать карту из твоей коллекции, которую ты хочешь обменять.'''
            await States._prev_next_.set()
            await state.update_data(_num=1)
            await state.update_data(_card=card)
            await state.update_data(lla=_all)
            await state.update_data(_num2=1)
            await state.update_data(_num_card=_num_card)
            await state.update_data(_num_card_=__data[0])
            await call.message.answer_photo(db.get_file(__data[0])[1], caption, reply_markup=_keyboard(_all, 1))

@dp.callback_query(F.text == ["_next", "_prev"], state=States._prev_next_)
async def next_or_prev(call: types.CallbackQuery, state: FSMContext):
    _data = await state.get_data()
    card = db.get_cards(call.from_user.id)[0]
    __data = card.split(", ")
    __num = _data['_num']
    _all = _data['lla']

    if call.data == "_next":
        next_num = 1 if __num == _all else __num + 1
    else:
        next_num = _all if __num == 1 else __num - 1

    photo = db.get_file(__data[next_num - 1])[1]
    caption = f'''{db.get_file(__data[next_num - 1])[2]}\nРедкость: {db.get_file(__data[next_num - 1])[3]}\n\n🌵 Бро, нужно выбрать карту из твоей коллекции, которую ты хочешь отдать взамен.'''
    media = InputMediaPhoto(photo, caption=caption)

    try:
        await call.message.edit_media(media, reply_markup=_keyboard(_all, next_num))
        await state.update_data(_num=next_num)
        await state.update_data(_num2=next_num)
        await state.update_data(_num_card_=__data[next_num - 1])
    except aiogram.utils.exceptions.MessageNotModified:
        pass


@dp.callback_query(F.text == "_trade_", state=States._prev_next_)
async def _trade_(call: types.CallbackQuery, state: FSMContext):
    _data = await state.get_data()
    sel_card = _data['card']
    prev_id = _data['prev_id']
    _num_card = _data['_num_card']
    _num_card_ = _data['_num_card_']
    _num2 = _data['_num2']
    card = _data['card']
    _card = _data['_card']
    _num1 = _data['_num1']
    photo = db.get_file(_num_card_)[1]
    karta = db.get_file(_num_card_)[2]
    _state = dp.current_state(chat=prev_id, user=prev_id)
    await _state.set_state(States._nickname_trade)
    await _state.update_data(card=card)
    await _state.update_data(_card=_card)
    await _state.update_data(_num2=_num2)
    await _state.update_data(prev_id=prev_id)
    await _state.update_data(sel_card=sel_card)
    await _state.update_data(_num_card=_num_card)
    await _state.update_data(_num_card_=_num_card_)
    await _state.update_data(prev_id=call.from_user.id)
    await _state.update_data(_num1=_num1)
    await bot.send_photo(prev_id, photo, f"{karta}\n\n@{call.from_user.username} предлагает взамен эту карту💬️", reply_markup=keyboard_accept_all())
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await call.message.answer('💬️ Встречное предложение обмена отправлено')
    await state.finish()

@dp.callback_query(F.text == "trade_ok", state=States._nickname_trade)
async def trade_ok(call: types.CallbackQuery, state: FSMContext):
    _data = await state.get_data()
    _num1 = _data['_num1']
    _num2 = _data['_num2']
    _card = _data['_card']
    prev_id = _data['prev_id']
    num_card2 = _data['_num_card']
    num_card1 = _data['_num_card_']

    # Получаем текущие списки карт в виде списков
    card1 = db.get_cards(call.from_user.id)[0].split(", ")
    card2 = db.get_cards(prev_id)[0].split(", ")

    # Меняем местами обмениваемые карты между двумя пользователями
    temp_card = card1[_num1 - 1]
    card1[_num1 - 1] = card2[_num2 - 1]
    card2[_num2 - 1] = temp_card

    # Объединяем списки обратно в строки
    text1 = ', '.join(card1)
    text2 = ', '.join(card2)

    # Завершаем текущее состояние
    await state.finish()

    # Обновляем списки карт в базе данных для обоих пользователей
    db.update_cards(call.from_user.id, text1)
    db.update_cards(prev_id, text2)

    # Отправляем подтверждающие сообщения с обмениваемыми картами
    await bot.send_photo(prev_id, db.get_file(num_card2)[1], "Обмен завершен, вот твоя карта🃏️")
    await bot.send_photo(call.from_user.id, db.get_file(num_card1)[1], "Обмен завершен, вот твоя карта🃏️")

