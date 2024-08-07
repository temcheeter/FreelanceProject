import asyncio
from aiogram import types, F, Router
import db
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
import datetime

admin_id = (878988386, 1854611737, 1147050798, 701959983, 5601713157, 6094444931)
router = Router()


class States(StatesGroup):
    info_o_igroke = State()
    nakrutka_balansa = State()
    nakrutka_botneta = State()
    nakrutka_pc = State()
    rasilka = State()
    nakrutka_kart = State()
    nakrutka_popitok = State()
    add_kart = State()
    add_kart_1 = State()
    add_kart_2 = State()
    add_kart_3 = State()
    change_kart = State()
    change_kart_1 = State()
    change_kart_2 = State()
    change_kart_3 = State()
    change_kart_4 = State()
    add_promo_act = State()
    add_promo_act_card = State()
    add_promo_act_ = State()
    add_promo_time = State()
    add_promo_time_card = State()
    add_promo_time_ = State()


def cancel():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ]
    )
    return kb


@router.callback_query()
async def cb(call: types.CallbackQuery, state: FSMContext):
    print(call.data)
    txt = call.data
    if txt == 'info_o_igroke':
        await cb_info_o_igroke(call, state)
    elif txt == 'vsego':
        await cb_vsego(call)
    elif txt == 'get_nohup':
        await cb_get_nohup(call)
    elif txt == 'get_table':
        await cb_get_table(call)
    elif txt == 'change_kart':
        await cb_change_kart(call, state)
    elif txt == 'rasilka':
        await cb_rasilka(call, state)
    elif txt == 'add_kart':
        await cb_add_kart(call, state)
    elif txt == 'promo_act':
        await cb_promo_act(call, state)
    elif txt == 'nakrutka_kart':
        await cb_nakrutka_kart(call, state)
    elif txt == 'nakrutka_popitok':
        await cb_nakrutka_popitok(call, state)


async def cb_info_o_igroke(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Айди игрока:", reply_markup=cancel())
    await state.set_state(States.info_o_igroke)


async def cb_vsego(call: types.CallbackQuery):
    await call.message.answer("Всего игроков:" + str(len(await db.get_all_users())))


@router.message(States.info_o_igroke)
async def change(message: types.Message, state: FSMContext):
    user_id = message.text
    try:
        nick = await db.get_info(user_id)
        nickb = await db.get_botnet(user_id)
        cards = await db.get_cards(nick[1])
        card = cards[0]
        __data = card.split(", ")
        _all = len(__data)
        await message.answer("ID: " + str(nick[1]) + "\nНик: " + str(nick[2]) + "\nДрифт очков: " + str(
            nick[3]) + "\nВсего карт: " + str(_all) + "\nБесплатных открытий: " + str(nickb[4]) + "\nРефов: " + str(
            await db.get_refs(nick[1])))
    except KeyError:
        await message.answer("Не найдено")
    finally:
        await state.clear()


async def cb_get_table(call: types.CallbackQuery):
    await call.message.answer_document(
        document=types.FSInputFile(
            path='C:\\Users\\akrav\\Desktop\\машынки\\database.db',
            filename='xyez.db'
        )
    )


async def cb_get_nohup(call: types.CallbackQuery):
    await call.message.reply_document(
        document=types.FSInputFile(
            path='C:\\Users\\akrav\\Desktop\\машынки\\nohup.out',
            filename='nohup.out')
    )


async def cb_rasilka(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Текст рассылки:", reply_markup=cancel())
    await state.set_state(States.rasilka)


async def cb_nakrutka_kart(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Айди игрока и карта", reply_markup=cancel())
    await state.set_state(States.nakrutka_kart)


@router.message(States.nakrutka_kart)
async def nakrutka(message: types.Message, state: FSMContext):
    try:
        _data = message.text.split(" ")
        user_id = _data[0]
        nick = await db.get_info(user_id)
        nick = nick[2]
        cards = await db.get_cards(user_id)
        cards = cards[0]
        _fame, fame_all, fame_season = await db.get_fame(user_id)
        fames = await db.get_file(_data[1])
        fame = fames[4]
        await db.set_fame(user_id, int(fame) + int(_fame), int(fame) + int(fame_all), int(fame) + int(fame_season))
        await db.update_cards(user_id, cards + ", " + str(_data[1]))
        await message.answer(f"Игроку {nick} добавлена карта с номером " + str(_data[1]))
        await message.answer_photo(fames[1],
                                   f"{fames[2]}\n\n✅️Вам добавлена карта")
    except:
        await message.answer("Не найдено")
    finally:
        await state.clear()


@router.message(States.rasilka)
async def change(message: types.Message, state: FSMContext):
    _text = message.text
    users = await db.get_all_users()
    a = 0
    for user in users:
        user_id = user[0]
        try:
            await message.answer(_text, parse_mode="HTML")
            a += 1
            await asyncio.sleep(0.1)
        except Exception:
            pass
    await message.answer(f"✅ Рассылка успешно завершена\nПолучили {a} пользователей")
    await state.clear()


async def cb_add_kart(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Отправьте фото:", reply_markup=cancel())
    await state.set_state(States.add_kart)


@router.message(States.add_kart, F.content_types == 'PHOTO')
async def admin_add_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    if message.from_user.id in admin_id:
        photo = file_id
        await state.update_data(photo=photo)
        await message.answer("Фото добавлено, теперь введите название: ", reply_markup=cancel())


@router.message(States.add_kart)
async def name(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        name = message.text
        await state.update_data(name=name)
        await message.answer("Имя добавлено, теперь введите редкость: ", reply_markup=cancel())
        await state.set_state(States.add_kart_1)


@router.message(States.add_kart_1)
async def rare(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        rare = message.text
        await state.update_data(rare=rare)
        await message.answer("Редкость добавлена, теперь введите количество очков: ", reply_markup=cancel())
        await state.set_state(States.add_kart_2)


@router.message(States.add_kart_2)
async def caption(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        fame = message.text
        await state.update_data(fame=fame)
        await message.answer(
            "Количество очков добавлено, теперь введите полный текст, который будет выдаваться при получении карты: ",
            reply_markup=cancel())
        await state.set_state(States.add_kart_3)


@router.message(States.add_kart_3)
async def final(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        caption = message.text
        _data = await state.get_data()
        photo = _data["photo"]
        name = _data["name"]
        rare = _data["rare"]
        fame = _data["fame"]
        await db.add_file(photo, name, rare, fame, caption)
        await message.answer("Карта полностью добавлена в базу данных")
        await state.clear()


async def cb_change_kart(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Id карты:", reply_markup=cancel())
    await state.set_state(States.change_kart)


@router.message(States.change_kart)
async def change_kart(message: types.Message, state: FSMContext):
    _id = message.text
    await state.update_data(_id=_id)
    await message.answer("Отправь фото:", reply_markup=cancel())
    await state.set_state(States.change_kart_1)


@router.message(States.change_kart_1, F.photo)
async def admin_add_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    if message.from_user.id in admin_id:
        photo = file_id
        await state.update_data(photo=photo)
        await message.answer("Фото изменено, теперь введи название: ", reply_markup=cancel())


@router.message(States.change_kart_1)
async def name(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        name = message.text
        await state.update_data(name=name)
        await message.answer("Имя изменено, теперь введи редкость: ", reply_markup=cancel())
        await state.set_state(States.change_kart_2)


@router.message(States.change_kart_2)
async def rare(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        rare = message.text
        await state.update_data(rare=rare)
        await message.answer("Редкость изменена, теперь введи количество очков: ", reply_markup=cancel())
        await state.set_state(States.change_kart_3)


@router.message(States.change_kart_3)
async def rare(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        fame = message.text
        await state.update_data(fame=fame)
        await message.answer(
            "Количество очков изменено, теперь введи полный текст, который будет выдаваться при получении карты: ",
            reply_markup=cancel())
        await state.set_state(States.change_kart_4)


@router.message(States.change_kart_4)
async def rare(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        caption = message.text
        _data = await state.get_data()
        _id = _data["_id"]
        photo = _data["photo"]
        name = _data["name"]
        rare = _data["rare"]
        fame = _data["fame"]
        await db.change_file(_id, photo, name, rare, fame, caption)
        await message.answer("Карта полностью изменена в базе данных")
        await state.clear()


async def kb():
    items = [("По количесту активаций", "promo_act"),
             ("По времени", "promo_time"),
             ("🚫️ Отменить", "cancel")]
    kb = InlineKeyboardBuilder()
    for item in items:
        kb.button(text=item[0], callback_data=f"{item[1]}")
    kb.adjust(2, 1)
    return kb.as_markup()


async def add_promo(call: types.CallbackQuery):
    keyboard = await kb()
    await call.message.answer("Какой промо создать", reply_markup=keyboard)


async def cb_promo_act(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Количество активаций:", reply_markup=cancel())
    await state.set_state(States.add_promo_act)


@router.message(States.add_promo_act)
async def add_promo_act(message: types.Message, state: FSMContext):
    act = message.text
    await state.update_data(act=act)
    await message.answer("Карта по id:", reply_markup=cancel())
    await state.set_state(States.add_promo_act_card)


@router.message(States.add_promo_act_card)
async def add_promo_act(message: types.Message, state: FSMContext):
    card = message.text
    await state.update_data(card=card)
    await message.answer("Сам промокод:", reply_markup=cancel())
    await state.set_state(States.add_promo_act_)


@router.message(States.add_promo_act_)
async def add_promo_act(message: types.Message, state: FSMContext):
    _data = await state.get_data()
    promo = message.text
    act = _data["act"]
    card = _data["card"]
    await db.add_promo_act(promo, act, card)
    await message.answer(f"Создан промокод {promo} на {act} активаций с картой под id {card}")
    await state.clear()


async def cb_promo_time(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Сколько промокод будет работать(в минутах)", reply_markup=cancel())
    await state.set_state(States.add_promo_time)


@router.message(States.add_promo_time)
async def add_promo_act(message: types.Message, state: FSMContext):
    _time = int(message.text)  # Парсим введенное пользователем значение времени в целое число
    current_datetime = datetime.datetime.now()
    time = (current_datetime + datetime.timedelta(minutes=_time)).strftime(
        '%Y-%m-%d %H:%M:%S')  # Добавляем введенное время к текущему времени
    await state.update_data(time=time)
    await message.answer("Карта по id:", reply_markup=cancel())
    await state.set_state(States.add_promo_time_card)


@router.message(States.add_promo_time_card)
async def add_promo_act(message: types.Message, state: FSMContext):
    card = message.text
    await state.update_data(card=card)
    await message.answer("Сам промокод:", reply_markup=cancel())
    await state.set_state(States.add_promo_time_)


@router.message(States.add_promo_time_)
async def add_promo_act(message: types.Message, state: FSMContext):
    _data = await state.get_data()
    promo = message.text
    time = _data["time"]
    card = _data["card"]
    await db.add_promo_time(promo, time, card)
    await message.answer(f"Создан промокод {promo} на который будет работать до *{time}* с картой под id {card}")
    await state.clear()


@router.message(F.text == "/pod_pass")
async def pod_pass(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        _data = message.text.split(" ")
        user_id = _data[1]
        current_date = datetime.datetime.now().date()
        pp_time = current_date + datetime.timedelta(days=30)
        _info = await db.get_info(user_id)
        await db.update_pass(user_id, pp_time)
        await message.answer(f"Пользователю {_info[2]} выдан пасс до {pp_time}")
        await message.answer("🎉️ Вы приобрели Pod Pass на 1 месяц")


async def cb_nakrutka_popitok(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Айди игрока и количество попыток", reply_markup=cancel())
    await state.set_state(States.nakrutka_popitok)


@router.message(States.nakrutka_popitok)
async def nakrutka(message: types.Message, state: FSMContext):
    try:
        _data = message.text.split(" ")
        user_id = _data[0]
        _info = await db.get_info(user_id)
        nick = _info[2]
        await db.update_botnet(user_id, 'comp_points', _data[1])
        await message.answer(f"Игроку {nick} выдано {str(_data[1])} попыток")
        await message.answer(f"Вам было начислено {str(_data[1])} попыток🎁")
        await state.clear()
    except:
        await message.answer("Не найдено")
        await state.clear()


@router.message(F.text == "/sbros_sezona")
async def pod_pass(message: types.Message, state: FSMContext):
    if message.from_user.id == 878988386:
        users = await db.get_all_users()
        a = 0
        b = 0
        for user in users:
            user_id = user[0]
            try:
                _info = await db.get_info(user_id)
                _text = f"⚡️ Начало нового сезона⚡️\n\n💨️ Никотина за все время: {_info[7]}"
                await message.answer(_text, parse_mode="HTML")
                a += 1
                await asyncio.sleep(0.1)
            except Exception:
                pass
        await message.answer(
            f"✅ Рассылка успешно завершена\nПолучили {a} пользователей\n\nНе получили {b} пользователей")
        await state.clear()
