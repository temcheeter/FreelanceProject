import aiogram
from aiogram import types, F
from main import dp
import db
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InputMediaPhoto

class States(StatesGroup):
    shop_prev_next = State()

def keyboard(_all, __num, cost):
    keyboard = InlineKeyboardMarkup(1)
    button = types.InlineKeyboardButton(text="⬅️", callback_data="shop_prev")
    button2 = types.InlineKeyboardButton(text=str(__num)+"/"+str(_all), callback_data="-")
    button3 = types.InlineKeyboardButton(text="➡️", callback_data="shop_next")
    button4 = types.InlineKeyboardButton(text=str(cost)+" никотина", callback_data="buy_shop")
    keyboard.add(button4)
    keyboard.row(button, button2, button3)
    return keyboard

@dp.callback_query(text="pod_shop")
async def pod_shop(call: types.CallbackQuery, state: FSMContext):
    await States.shop_prev_next.set()
    await state.finish()
    card = db.get_shop(1)[0]
    _all = len(db.get_all_shop())
    photo = db.get_shop(card)[1]
    caption = db.get_shop(card)[5]+f"\n\nУ тебя всего: {db.get_info(call.from_user.id)[3]}\n\nКупить за:"
    await States.shop_prev_next.set()
    await state.update_data(_num=1)
    await state.update_data(lla=_all)
    await call.message.answer_photo(photo, caption, reply_markup=keyboard(_all, 1, db.get_shop(1)[4]))

@dp.callback_query(text=["shop_next", "shop_prev"], state=States.shop_prev_next)
async def next_or_prev(call: types.CallbackQuery, state: FSMContext):
    _data = await state.get_data()
    card = db.get_all_shop()
    __num = _data['_num']
    _all = _data['lla']

    if call.data == "shop_next":
        next_num = 1 if __num == _all else __num + 1
    else:
        next_num = _all if __num == 1 else __num - 1

    photo = db.get_shop(card[next_num - 1][0])[1]
    caption = db.get_shop(card[next_num - 1][0])[5]+f"\n\nУ тебя всего: {db.get_info(call.from_user.id)[3]}\n\nКупить за:"

    try:
        media = InputMediaPhoto(photo, caption=caption)
        await call.message.edit_media(media, reply_markup=keyboard(_all, next_num, db.get_shop(next_num)[4]))
        await state.update_data(_num=next_num)
    except aiogram.utils.exceptions.MessageNotModified:
        pass

    await state.update_data(lla=_all)

@dp.callback_query(F.text == "buy_shop", state=States.shop_prev_next)
async def buy_shop(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    _data = await state.get_data()
    card = db.get_all_shop()
    __num = _data['_num']
    cost = db.get_shop(__num)[4]
    fame, fame_all, fame_season = db.get_fame(user_id)
    us_cards = db.get_cards(user_id)[0]
    if fame < cost:
        await call.message.answer("У вас не хватает никотина для покупки")
    else:
        db.set_fame(user_id, int(fame)-int(cost), fame_all, fame_season)
        ad_card = db.get_file_name(db.get_shop(__num)[2])[0]
        db.update_cards(user_id, us_cards +", "+str(ad_card))
        await call.message.answer(f"Вы приобрели {db.get_shop(__num)[2]}\nтеперь карта находится у вас в инветнаре")
