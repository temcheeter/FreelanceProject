import aiogram
from aiogram import types, F
from main import dp
import db
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

class States(StatesGroup):
    prev_next = State()
    _search = State()

def keyboard(_all, __num):
    keyboard = InlineKeyboardMarkup(1)
    button = types.InlineKeyboardButton(text="⬅️", callback_data="prev")
    button2 = types.InlineKeyboardButton(text=str(__num)+"/"+str(_all), callback_data="-")
    button3 = types.InlineKeyboardButton(text="➡️", callback_data="next")
    button4 = types.InlineKeyboardButton(text="🍫️ Сортировать", callback_data="sort")
    button5 = types.InlineKeyboardButton(text="🥤️ Крафт", callback_data="craft")
    button6 = types.InlineKeyboardButton(text="🔍️ Поиск", callback_data="search")
    keyboard.row(button, button2, button3)
    keyboard.add(button4)
    keyboard.add(button5)
    return keyboard

def sort_kb():
    keyboard = InlineKeyboardMarkup(1)
    button = types.InlineKeyboardButton(text="🎭 One Puff", callback_data="sort_one_puff")
    button1 = types.InlineKeyboardButton(text="✨ MINI Pod", callback_data="sort_mini_pod")
    button2 = types.InlineKeyboardButton(text="⭐️ Pod", callback_data="sort_pod")
    button3 = types.InlineKeyboardButton(text="🌟 RARE Pod", callback_data="sort_rare_pod")
    button4 = types.InlineKeyboardButton(text="🏵 MOD", callback_data="sort_mod")
    button5 = types.InlineKeyboardButton(text="💧 Жидкость", callback_data="sort_liq")
    button6 = types.InlineKeyboardButton(text="🤖 Limited", callback_data="sort_limit")
    keyboard.add(button)
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    keyboard.add(button4)
    keyboard.add(button5)
    keyboard.add(button6)
    return keyboard

def craft_kb():
    keyboard = InlineKeyboardMarkup(1)
    button = types.InlineKeyboardButton(text="Скрафтить из 10 🎭 One Puff", callback_data="craft_one_puff")
    button2 = types.InlineKeyboardButton(text="Скрафтить из 10 ✨ MINI Pod", callback_data="craft_mini_pod")
    button3 = types.InlineKeyboardButton(text="Скрафтить из 5 ⭐️ Pod", callback_data="craft_pod")
    button4 = types.InlineKeyboardButton(text="Скрафтить из 5 🌟 RARE Pod", callback_data="craft_rare_pod")
    button5 = types.InlineKeyboardButton(text="Скрафтить из 1 🏵 MOD", callback_data="craft_mod")
    keyboard.add(button)
    keyboard.add(button2)
    keyboard.add(button3)
    keyboard.add(button4)
    keyboard.add(button5)
    return keyboard

def sortirovka(user_id, rare):
    all_c = db.get_cards(user_id)[0]
    ott_c = all_c.split(", ")
    text=[]
    for i in range(len(ott_c)):
        a = db.get_file(ott_c[i])[3]
        if a == rare:
            text.append(ott_c[i])
    return text

def povtorki(user_id, rare):
    all_c = db.get_cards(user_id)[0]
    ott_c = all_c.split(", ")
    card_counts = {}
    
    for card in ott_c:
        card_rarity = db.get_file(card)[3]
        if card_rarity == rare:
            if card in card_counts:
                card_counts[card] += 1
            else:
                card_counts[card] = 1
    
    repeated_cards_count = sum(count - 1 for card, count in card_counts.items() if count > 1)
    
    return repeated_cards_count

def delete_repeats(user_id, rarity, count_to_delete):
    cards = db.get_cards(user_id)[0].split(", ")
    new_cards = []
    card_counts = {}

    # Подсчет количества каждой карты
    for card in cards:
        card_rarity = db.get_file(card)[3]
        if card_rarity == rarity:
            if card in card_counts:
                card_counts[card] += 1
            else:
                card_counts[card] = 1

    # Удаление повторяющихся карт
    for card in cards:
        if card in card_counts and card_counts[card] > 1 and count_to_delete > 0:
            count_to_delete -= 1
            card_counts[card] -= 1
        else:
            new_cards.append(card)

    db.update_cards(user_id, ", ".join(new_cards))

def nicotine(user_id):
    card = db.get_cards(user_id)[0]
    __data = card.split(", ")
    _all = len(__data)
    col_vo = 0
    for i in range(0, _all):
        a = db.get_file(__data[i])[4]
        col_vo += a
    return col_vo

@dp.message(F.text == "🚬️ Мои подики")
async def my_cards(message: types.Message, state: FSMContext):
    if db.get_cards(message.chat.id)[0] == "0":
        await message.answer("У вас еще нет карт")
    else:
        await States.prev_next.set()
        await state.finish()
        card = db.get_cards(message.chat.id)[0]
        __data = card.split(", ")
        _all = len(__data)
        photo = db.get_file(__data[0])[1]
        caption = f'''{db.get_file(__data[0])[2]}\nРедкость: {db.get_file(__data[0])[3]}\n\n💨 Никотин в этом сезоне: {db.get_info(message.from_user.id)[8]}\n\n 😎️ Бро, это все твои подики'''
        await States.prev_next.set()
        await state.update_data(_num=1)
        await state.update_data(lla=_all)
        await state.update_data(cards=__data)
        await message.answer_photo(photo, caption, reply_markup=keyboard(_all, 1))

@dp.callback_query(F.text == ["next", "prev"])
async def next_or_prev(call: types.CallbackQuery, state: FSMContext):
    _data = await state.get_data()
    __data = _data['cards']
    __num = _data['_num']
    _all = _data['lla']

    if call.data == "next":
        next_num = 1 if __num == _all else __num + 1
    else:
        next_num = _all if __num == 1 else __num - 1

    photo = db.get_file(__data[next_num - 1])[1]
    caption = f'''{db.get_file(__data[next_num - 1])[2]}\nРедкость: {db.get_file(__data[next_num - 1])[3]}\n\n💨 Никотин в этом сезоне: {db.get_info(call.from_user.id)[8]}\n\n 😎️ Бро, это все твои подики'''

    try:
        media = InputMediaPhoto(photo, caption=caption)
        await call.message.edit_media(media, reply_markup=keyboard(_all, next_num))
        await state.update_data(_num=next_num)
    except aiogram.utils.exceptions.MessageNotModified:
        pass

    await state.update_data(lla=_all)

@dp.message(F.text == "/search")
async def menu(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('🚫️ Отменить', callback_data="cancel"))
    await message.answer("🔍️ Введите ключевое слово:")
    await States._search.set()

@dp.message()
async def _search(message: types.Message, state: FSMContext):
    search_term = message.text
    user_id = message.chat.id
    user_cards_str = db.get_cards(user_id)[0]


    if not user_cards_str or user_cards_str == "0":
        await message.answer("У вас еще нет карт")
        return

    user_cards = list(map(int, user_cards_str.split(", ")))

    result_list = []
    search_results = db.find_card_by_name(search_term)

    for card in search_results:
        card_id = card[0]
        if card_id in user_cards:
            result_list.append(card_id)

    if result_list:
        _all = len(result_list)
        photo = db.get_file(result_list[0])[1]
        caption = f'''{db.get_file(result_list[0])[2]}\nРедкость: {db.get_file(result_list[0])[3]}\n\n💨 Никотин в этом сезоне: {db.get_info(user_id)[8]}\n\n 😎️ Бро, это все твои подики'''
        media = InputMediaPhoto(photo, caption=caption)
        await state.update_data(cards=result_list)
        await state.update_data(_num=1)
        await state.update_data(lla=_all)
        await message.answer_photo(photo, caption, reply_markup=keyboard(_all, 1))
    else:
        await message.answer("Карты с таким названием не найдены.")


@dp.callback_query(F.text == "sort")
async def sort(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Выберите редкость для сортировки:", reply_markup=sort_kb())

@dp.callback_query(F.text == "sort_one_puff")
async def sort(call: types.CallbackQuery, state: FSMContext):
    cards = sortirovka(call.from_user.id, "One Puff")
    _all = len(cards)
    if _all != 0:
        photo = db.get_file(cards[0])[1]
        caption = f'''{db.get_file(cards[0])[2]}\nРедкость: {db.get_file(cards[0])[3]}\n\n💨 Никотин в этом сезоне: {db.get_info(call.from_user.id)[8]}\n\n 😎️ Бро, это все твои подики'''
        media = InputMediaPhoto(photo, caption=caption)
        await state.update_data(cards=cards)
        await state.update_data(_num=1)
        await state.update_data(lla=_all)
        await call.message.answer_photo(photo, caption, reply_markup=keyboard(_all, 1))
    else:
        await call.message.answer("У вас еще нет карт редкости:\n🎭 One Puff")

@dp.callback_query(F.text == "sort_mini_pod")
async def sort(call: types.CallbackQuery, state: FSMContext):
    cards = sortirovka(call.from_user.id, "MINI Pod")
    _all = len(cards)
    if _all != 0:
        photo = db.get_file(cards[0])[1]
        caption = f'''{db.get_file(cards[0])[2]}\nРедкость: {db.get_file(cards[0])[3]}\n\n💨 Никотин в этом сезоне: {db.get_info(call.from_user.id)[8]}\n\n 😎️ Бро, это все твои подики'''
        media = InputMediaPhoto(photo, caption=caption)
        await state.update_data(cards=cards)
        await state.update_data(_num=1)
        await state.update_data(lla=_all)
        await call.message.answer_photo(photo, caption, reply_markup=keyboard(_all, 1))
    else:
        await call.message.answer("У вас еще нет карт редкости:\n✨ MINI Pod")

@dp.callback_query(F.text == "sort_pod")
async def sort(call: types.CallbackQuery, state: FSMContext):
    cards = sortirovka(call.from_user.id, "Pod")
    _all = len(cards)
    if _all != 0:
        photo = db.get_file(cards[0])[1]
        caption = f'''{db.get_file(cards[0])[2]}\nРедкость: {db.get_file(cards[0])[3]}\n\n💨 Никотин в этом сезоне: {db.get_info(call.from_user.id)[8]}\n\n 😎️ Бро, это все твои подики'''
        media = InputMediaPhoto(photo, caption=caption)
        await state.update_data(cards=cards)
        await state.update_data(_num=1)
        await state.update_data(lla=_all)
        await call.message.answer_photo(photo, caption, reply_markup=keyboard(_all, 1))
    else:
        await call.message.answer("У вас еще нет карт редкости:\n⭐️ Pod")

@dp.callback_query(F.text == "sort_rare_pod")
async def sort(call: types.CallbackQuery, state: FSMContext):
    cards = sortirovka(call.from_user.id, "RARE Pod")
    _all = len(cards)
    if _all != 0:
        photo = db.get_file(cards[0])[1]
        caption = f'''{db.get_file(cards[0])[2]}\nРедкость: {db.get_file(cards[0])[3]}\n\n💨 Никотин в этом сезоне: {db.get_info(call.from_user.id)[8]}\n\n 😎️ Бро, это все твои подики'''
        media = InputMediaPhoto(photo, caption=caption)
        await state.update_data(cards=cards)
        await state.update_data(_num=1)
        await state.update_data(lla=_all)
        await call.message.answer_photo(photo, caption, reply_markup=keyboard(_all, 1))
    else:
        await call.message.answer("У вас еще нет карт редкости:\n🌟 RARE Pod")

@dp.callback_query(F.text == "sort_mod")
async def sort(call: types.CallbackQuery, state: FSMContext):
    cards = sortirovka(call.from_user.id, "MOD")
    _all = len(cards)
    if _all != 0:
        photo = db.get_file(cards[0])[1]
        caption = f'''{db.get_file(cards[0])[2]}\nРедкость: {db.get_file(cards[0])[3]}\n\n💨 Никотин в этом сезоне: {db.get_info(call.from_user.id)[8]}\n\n 😎️ Бро, это все твои подики'''
        media = InputMediaPhoto(photo, caption=caption)
        await state.update_data(cards=cards)
        await state.update_data(_num=1)
        await state.update_data(lla=_all)
        await call.message.answer_photo(photo, caption, reply_markup=keyboard(_all, 1))
    else:
        await call.message.answer("У вас еще нет карт редкости:\n🏵 MOD")

@dp.callback_query(F.text == "sort_liq")
async def sort(call: types.CallbackQuery, state: FSMContext):
    cards = sortirovka(call.from_user.id, "Жидкость")
    _all = len(cards)
    if _all != 0:
        photo = db.get_file(cards[0])[1]
        caption = f'''{db.get_file(cards[0])[2]}\nРедкость: {db.get_file(cards[0])[3]}\n\n💨 Никотин в этом сезоне: {db.get_info(call.from_user.id)[8]}\n\n 😎️ Бро, это все твои подики'''
        media = InputMediaPhoto(photo, caption=caption)
        await state.update_data(cards=cards)
        await state.update_data(_num=1)
        await state.update_data(lla=_all)
        await call.message.answer_photo(photo, caption, reply_markup=keyboard(_all, 1))
    else:
        await call.message.answer("У вас еще нет карт редкости:\n💧 Жидкость")

@dp.callback_query(F.text == "sort_limit")
async def sort(call: types.CallbackQuery, state: FSMContext):
    cards = sortirovka(call.from_user.id, "Limited")
    _all = len(cards)
    if _all != 0:
        photo = db.get_file(cards[0])[1]
        caption = f'''{db.get_file(cards[0])[2]}\nРедкость: {db.get_file(cards[0])[3]}\n\n💨 Никотин в этом сезоне: {db.get_info(call.from_user.id)[8]}\n\n 😎️ Бро, это все твои подики'''
        media = InputMediaPhoto(photo, caption=caption)
        await state.update_data(cards=cards)
        await state.update_data(_num=1)
        await state.update_data(lla=_all)
        await call.message.answer_photo(photo, caption, reply_markup=keyboard(_all, 1))
    else:
        await call.message.answer("У вас еще нет карт редкости:\n🤖 Limited")

@dp.callback_query(F.text == "craft")
async def craft(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(f"""🧃 Бро, это крафт, здесь ты можешь создать попытки из повторных карт, а может и не только попытки…

Количество повторок:

🎭 One Puff: {povtorki(call.from_user.id, 'One Puff')}
✨ MINI Pod: {povtorki(call.from_user.id, 'MINI Pod')}
⭐️ Pod: {povtorki(call.from_user.id, 'Pod')}
🌟 RARE Pod: {povtorki(call.from_user.id, 'RARE Pod')}
🏵 MOD: {povtorki(call.from_user.id, 'MOD')}


<b>10</b> One Puff = <b>3</b> попытки
<b>10</b> MINI Pod = <b>5</b> попыток
<b>5</b> Pod = <b>6</b> попыток
<b>5</b> RARE Pod = <b>9</b> попыток
<b>1</b> MOD = <b>5</b> попыток
""", reply_markup=craft_kb(), parse_mode="HTML")

@dp.callback_query(F.text == "craft_one_puff")
async def craft_one_puff(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    repeat_count = povtorki(user_id, 'One Puff')

    if repeat_count >= 10:
        delete_repeats(user_id, 'One Puff', 10)
        comp_points = db.get_botnet(user_id)[4]
        updated_points = comp_points + 3
        db.update_botnet(user_id, "comp_points", updated_points)

        await call.message.answer("Вы успешно скрафтили 3 попытки с помощью повторок!")
    else:
        await call.message.answer("У вас недостаточно повторок для крафта.")

@dp.callback_query(F.text == "craft_mini_pod")
async def craft_one_puff(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    repeat_count = povtorki(user_id, 'MINI Pod')

    if repeat_count >= 10:

        delete_repeats(user_id, 'MINI Pod', 10)
        comp_points = db.get_botnet(user_id)[4]
        updated_points = comp_points + 5
        db.update_botnet(user_id, "comp_points", updated_points)

        await call.message.answer("Вы успешно скрафтили 5 попыток с помощью повторок!")
    else:
        await call.message.answer("У вас недостаточно повторок для крафта.")

@dp.callback_query(F.text == "craft_pod")
async def craft_one_puff(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    repeat_count = povtorki(user_id, 'Pod')

    if repeat_count >= 5:
        delete_repeats(user_id, 'Pod', 5) 
        comp_points = db.get_botnet(user_id)[4]
        updated_points = comp_points + 6
        db.update_botnet(user_id, "comp_points", updated_points)

        await call.message.answer("Вы успешно скрафтили 6 попыток с помощью повторок!")
    else:
        await call.message.answer("У вас недостаточно повторок для крафта.")

@dp.callback_query(F.text == "craft_rare_pod")
async def craft_one_puff(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    repeat_count = povtorki(user_id, 'RARE Pod')

    if repeat_count >= 5:
        delete_repeats(user_id, 'RARE Pod', 5) 
        comp_points = db.get_botnet(user_id)[4]
        updated_points = comp_points + 9
        db.update_botnet(user_id, "comp_points", updated_points)

        await call.message.answer("Вы успешно скрафтили 9 попыток с помощью повторок!")
    else:
        await call.message.answer("У вас недостаточно повторок для крафта.")

@dp.callback_query(F.text == "craft_mod")
async def craft_one_puff(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    repeat_count = povtorki(user_id, 'MOD')

    if repeat_count >= 1:
        delete_repeats(user_id, 'MOD', 1) 
        comp_points = db.get_botnet(user_id)[4]
        updated_points = comp_points + 5
        db.update_botnet(user_id, "comp_points", updated_points)

        await call.message.answer("Вы успешно скрафтили 5 попыток с помощью повторок!")
    else:
        await call.message.answer("У вас недостаточно повторок для крафта.")
