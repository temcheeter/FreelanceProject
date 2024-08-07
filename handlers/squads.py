from aiogram import types, F
from main import dp, bot
import db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class States(StatesGroup):
    name_squad = State()
    photo_squad = State()
    descript_squad = State()
    invite_sq = State()
    sq_acordc = State()
    delete_sq = State()
    dissolve_sq = State()
    new_photo_sq = State()
    new_desc_sq = State()

def cancel():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🚫️ Отменить", callback_data="cancel"))
    return keyboard

@dp.callback_query(F.text == "cancel")
async def cancell(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer("🚫️ Отменено")

@dp.callback_query(F.text == "squads")
async def squads(call: types.CallbackQuery):
    if db.get_botnet(call.from_user.id)[5] == None: 
        keyboard = InlineKeyboardMarkup(1)
        keyboard.add(InlineKeyboardButton(text="🧸️ Создать свой сквад", callback_data="add_squad"))
        keyboard.add(InlineKeyboardButton(text="☂️ Вступить в сквад", callback_data="join_squad"))
        await call.message.answer("💬️ Выберите действие по кнопкам ниже", reply_markup = keyboard)
    else:
        name = db.get_botnet(call.from_user.id)[5]
        photo = db.get_squad(name)[3]
        desc = db.get_squad(name)[2]
        owner = db.get_squad(name)[5]
        all_members = db.get_squad(name)[4]
        members = ""
        mem_num = 0
        if int(call.from_user.id) == int(owner):
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text="🙆‍♂️️ Пригласить в Squad", callback_data="invite_sq"))
            keyboard.add(InlineKeyboardButton(text="🙅‍♂️️ Исключить из Squad", callback_data="delete_sq"))
            keyboard.add(InlineKeyboardButton(text="☠️ Распустить Squad", callback_data="dissolve_sq"))
            keyboard.add(InlineKeyboardButton(text="✍️ Настройки Squad", callback_data="settings_sq"))
        else:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text="⛱️ Покинуть Squad", callback_data="leave_sq"))
        for i in range(len(all_members.split(", "))):
            memb_text = f"\n@{db.get_info(all_members.split(', ')[i])[2]} ({db.get_info(all_members.split(', ')[i])[3]} Зависимости)"
            members += "".join(memb_text)
            mem_num += db.get_info(all_members.split(', ')[i])[3]
        db.set_squad(name, 'fame', mem_num)
        text = f"""<b>🧸 Squad - {name}</b>

🍿 Всего: {mem_num} Зависимости

<b>🦁 Президент:</b>
@{db.get_info(owner)[2]}

<b>Участники:</b>{members}

<b>🥷 Описание:</b>
{desc}"""
        await call.message.answer_photo(photo, text, reply_markup = keyboard, parse_mode="HTML")

@dp.callback_query(F.text == "join_squad")
async def join_squad(call: types.CallbackQuery):
    await call.message.answer(f"""🧟 Чтобы попасть в сквад, ты должен найти владельца, который примет тебя в свою банду, выслав тебе приглашение.

🪪 Либо же ты можешь создать свой Squad, приобретя <b>Pod Pass</b>.""", parse_mode="HTML")


@dp.callback_query(F.text == "add_squad")
async def add_squad(call: types.CallbackQuery):
    user_id = call.from_user.id
    current_date = datetime.datetime.now().date()
    pp_time = datetime.datetime.strptime(db.get_info(user_id)[6], '%Y-%m-%d').date()
    if (pp_time > current_date):
        await States.name_squad.set()
        await call.message.answer(f"❓️ Как назовешь свой сквад?\nДавай придумаем название (максимум 50 символов)", reply_markup = cancel())
    else:
        await call.message.answer(f"⚠️ Для создания своего Squad необходимо иметь <b>Pod Pass</b>", parse_mode="HTML")

@dp.message(state=States.name_squad)
async def name_squad(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer(f"""🧟 Отлично, название банды: {name}


🧑‍🎨 Теперь зашли мне фоточку своей банды, визуал сквада очень важен, верно?

🤦‍♂️ За непристойные фотографии будем банить)""", reply_markup = cancel())
    await States.photo_squad.set()

@dp.message(content_types=types.ContentTypes.PHOTO, state=States.photo_squad)
async def photo_squad(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    photo = file_id
    await state.update_data(photo=photo)
    await message.answer(f"""🧑‍🎨 Отлично, неплохой выбор.

🧛 Теперь нужно накидать небольшое описание твоего клана.
(максимум 400 символов)""", reply_markup = cancel())
    await States.descript_squad.set()

@dp.message(state=States.descript_squad)
async def descript_squad(message: types.Message, state: FSMContext):
    description = message.text
    _data = await state.get_data()
    squad_name = _data['name']
    squad_photo = _data['photo']
    user_id = message.from_user.id
    db.add_squad(squad_name, squad_photo, description, user_id)
    await message.answer_photo(squad_photo, f"<b>🧸 Squad - {squad_name}</b>\n\n🥷 <b>Описание:\n{description}</b>", parse_mode="HTML")
    await state.finish()

@dp.callback_query(F.text == "invite_sq")
async def invite_sq(call: types.CallbackQuery, state: FSMContext):
    await States.invite_sq.set()
    name = db.get_botnet(call.from_user.id)[5]
    photo = db.get_squad(name)[3]
    desc = db.get_squad(name)[2]
    await state.update_data(name=name)
    await state.update_data(photo=photo)
    await state.update_data(desc=desc)
    await call.message.answer("💬️ Введите @username пользователя", reply_markup = cancel())

@dp.message(state=States.invite_sq)
async def invite_sq(message: types.Message, state: FSMContext):
    sq_info = await state.get_data()
    sq_name = sq_info['name']
    sq_photo = sq_info['photo']
    sq_desc = sq_info['desc']
    username = message.text
    _data = username.split("@")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Принять", callback_data="accept_sq"))
    keyboard.add(InlineKeyboardButton(text="Отклонить", callback_data="cancel"))
    try:
        _user = db.get_nickname(_data[1])[1]
        if db.get_botnet(_user)[5] != None:
            await message.answer("🤷‍♂️️ Пользователь уже состоит в скваде")
        else:
            await bot.send_photo(_user, sq_photo, f"Вы были приглашены в Squad\n\n<b>🧸 Squad - {sq_name}</b>\n\n<b>🍿 Всего:</b> {db.get_squad(sq_name)[6]} Зависимости\n\n<b>🥷 Описание:</b>\n{sq_desc}", reply_markup = keyboard, parse_mode="HTML")
            await message.answer("🎫️ Приглашение отправлено")
            _state = dp.current_state(chat=_user, user=_user)
            await _state.set_state(States.sq_acordc)
            await _state.update_data(sq_name=sq_name)
    except:
        await message.answer("🤷‍♂️️ Пользователь не найден\n\nВозможно игроку нужно прописать /start в боте!")
    await state.finish()

@dp.callback_query(F.text == "accept_sq", state=States.sq_acordc)
async def sq_acordc(call: types.CallbackQuery, state: FSMContext):
    _user = call.from_user.id
    _data = await state.get_data()
    if db.get_botnet(_user)[5] == None:
        sq_name = _data['sq_name']
        db.update_botnet(_user, 'comp_id', sq_name)
        members = db.get_squad(sq_name)[4]
        db.set_squad(sq_name, 'members', str(members) + ", " + str(_user))
        await call.message.answer(f"Вы вступили в 🧸 Squad - {sq_name}")
    else:
        await call.message.answer("👨‍👨‍👧‍👦️ Вы уже состоите в скваде")
    await state.finish()

@dp.callback_query(F.text == "delete_sq")
async def delete_sq(call: types.CallbackQuery, state: FSMContext):
    await States.delete_sq.set()
    await call.message.answer("💬️ Введите @username пользователя", reply_markup = cancel())

@dp.message(state=States.delete_sq)
async def delete_sq(message: types.Message, state: FSMContext):
    username = message.text
    _data = username.split("@")
    _user = db.get_nickname(_data[1])[1]
    if message.chat.id == _user:
        await message.answer("🤦‍♀️️ Вы не можете исключить себя")
    else:
        sq_name = db.get_botnet(message.from_user.id)[5]
        members = db.get_squad(sq_name)[4]
        _members = members.split(", ")
        if str(_user) in _members:
            members = members.replace(f'{_user}, ', '').replace(f', {_user}', '')
            db.set_squad(sq_name, 'members', members)
            db.delete_botnet(_user, 'comp_id')
            await message.answer("⚠️ Пользователь исключен")
            await bot.send_message(_user, "⚠️ Владелец сквада исключил вас")
        else:
            await message.answer("🤷‍♂️️ Пользователь не найден")
    await state.finish()

@dp.callback_query(F.text == "dissolve_sq")
async def dissolve_sq(call: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🧸️ Распусить", callback_data="dis_sq"))
    keyboard.add(InlineKeyboardButton(text="🚫️ Отклонить", callback_data="cancel"))
    await States.dissolve_sq.set()
    await call.message.answer("⚠️ Вы уверены что хотите распустить Squad?", reply_markup = keyboard)

@dp.callback_query(F.text == "dis_sq", state=States.dissolve_sq)
async def dissolve_sq(call: types.CallbackQuery, state: FSMContext):
    name = db.get_botnet(call.from_user.id)[5]
    members = db.get_squad(name)[4]
    members = members.split(", ")
    for i in range (len(members)):
        db.delete_botnet(members[i], 'comp_id')
        try:
            if str(call.from_user.id) != members[i]:
                await bot.send_message(members[i], "⚠️ Ваш сквад был распущен владельцем")
        except:
            pass
    db.delete_squad(name)
    await call.message.answer("⚠️ Вы распустили свой Squad")
    await state.finish()

@dp.callback_query(F.text == "settings_sq")
async def settings_sq(call: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🌌️ Поменять фотокарточку", callback_data="change_photo"))
    keyboard.add(InlineKeyboardButton(text="🥷 Поменять описание", callback_data="change_desc"))
    keyboard.add(InlineKeyboardButton(text="🚫️ Отменить", callback_data="cancel"))
    await call.message.answer("💬️ Выберите действие по кнопкам ниже", reply_markup = keyboard)

@dp.callback_query(F.text == "change_photo")
async def change_photo(call: types.CallbackQuery, state: FSMContext):
    await States.new_photo_sq.set()
    await call.message.answer("🌌️ Отправь новое фото для своего Squad", reply_markup = cancel())

@dp.message(content_types=types.ContentTypes.PHOTO, state=States.new_photo_sq)
async def new_photo_sq(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    photo = file_id
    db.set_squad(db.get_botnet(message.from_user.id)[5], 'squad_photo', photo)
    await message.answer("🌌️ Фотокарточка обновлена")
    await state.finish()

@dp.callback_query(F.text == "change_desc")
async def change_desc(call: types.CallbackQuery, state: FSMContext):
    await States.new_desc_sq.set()
    await call.message.answer("📝️ Отправь новое описание для своего Squad", reply_markup = cancel())

@dp.message(state=States.new_desc_sq)
async def new_desc_sq(message: types.Message, state: FSMContext):
    desc = message.text
    db.set_squad(db.get_botnet(message.from_user.id)[5], 'description', desc)
    await message.answer("🥷 Описание обновлено")
    await state.finish()

@dp.callback_query(F.text == "leave_sq")
async def leave_sq(call: types.CallbackQuery, state: FSMContext):
    _user = call.from_user.id
    sq_name = db.get_botnet(call.from_user.id)[5]
    members = db.get_squad(sq_name)[4]
    members = members.replace(f'{_user}, ', '').replace(f', {_user}', '')
    db.set_squad(sq_name, 'members', members)
    db.delete_botnet(_user, 'comp_id')
    await call.message.answer("⚠️ Вы покинули сквад")
