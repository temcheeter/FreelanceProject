from aiogram.fsm.context import FSMContext
import config
import db
import random
import datetime
import asyncio
import time
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers import (get_card, admin)

bot = Bot(token=config.token)
dp = Dispatcher()

dp.include_routers(get_card.router, admin.router)


async def main() -> None:
    await dp.start_polling(bot)


loop = asyncio.get_event_loop()
admin_id = [878988386, 1854611737, 1147050798, 6094444931,
            701959983, 5950125811, 5601713157, 6839360948]

used_promo_dict = {}


def start():
    btn1 = '💨️ Получить дрифт-карту'
    btn2 = '🚬️ Мои дрифт-карты'
    btn3 = '🎪️ Drift Studio'
    kb = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text=btn1),
            KeyboardButton(text=btn2),
            KeyboardButton(text=btn3)
        ]
    ],
        resize_keyboard=True
    )
    return kb


def admin():
    items = [
        ('Получить таблицу', "get_table"), ('Получить ноухап', "get_nohup"),
        ('Добавить карту в кард шоп', "add_kart"),
        ('Всего игроков', "vsego"), ('Инфо о игроке', "info_o_igroke"),
        ('Добавить карту игроку', "nakrutka_kart"),
        ('Изменить карту в базе данных', "change_kart"),
        ('Выдать попытки игроку', "nakrutka_popitok"),
        ('Создать промокод', "add_promo")
    ]
    kb = InlineKeyboardBuilder()
    for item in items:
        kb.button(text=item[0], callback_data=f"{item[1]}")
    kb.adjust(2, 1, 2, 1, 1, 2)
    return kb.as_markup()


@dp.callback_query(F.text == "add_shop")
async def add_kart(call: types.CallbackQuery):
    await call.message.answer("Привет чепух")


def start_message():
    return f"""<b>🙆‍♂️️ Welcome to PhonkCard</b>

🌍️ Это простая игра по мотивам музыкального жанра(фонк)...

🥪️ Собирай карточки с фонком, копи очки, обходи друзей в рейтинге и учавствуй в конкурсах!

<i>По-моему все очень просто и понятно, давай начинать</i>
"""


def give_mod(_ref):
    _user_id = _ref
    rare = "MOD"
    loop = asyncio.get_event_loop()
    gr = loop.run_until_complete(db.get_rare(rare))
    rand = random.randint(0, len(gr) - 1)
    _rare = loop = loop.run_until_complete(db.get_rare(rare))[0]
    photo = _rare[1]
    caption = _rare[5] + '\n\nВот твоя карта за 10 приглашенных пользователей'
    fame = _rare[4]
    _fame, fame_all, fame_season = db.get_fame(_user_id)
    card = loop.run_until_complete(db.get_cards(_user_id))[0]
    _fame, fame_all, fame_season = db.get_fame(_user_id)
    db.update_cards(_user_id, card + ", " + str(_rare[0]))
    am = loop.run_until_complete(db.get_botnet(_user_id))[3]
    db.update_botnet(_user_id, "botnet_amount", am + 1)
    return _rare


@dp.message(F.text == '/start')
async def menu(message: types.Message, state: FSMContext):
    _user_id = message.chat.id
    _username = message.chat.username
    # print(await db.get_users_exist(message.chat.id))
    if await db.get_users_exist(message.chat.id):
        if message.text != "Назад" and message.text.startswith("/start "):
            _ref = message.text.replace("/start ", "")
            if int(message.chat.id) != int(_ref):
                await db.add_user(message.chat.id, message.chat.username, _ref, 0, '2020-11-11')
                await db.add_user_to_state(message.from_user.id, '2020-03-03', '2023-08-10 00:59:37')
                if int(await db.get_refs(_ref)) % 10 == 0 and int(await db.get_refs(_ref)) != 1:
                    _rare = give_mod(_ref)
                    photo = _rare[1]
                    caption = _rare[5] + \
                              '\n\nВот твоя карта за 10 приглашенных пользователей'
                    await bot.send_photo(_ref, photo, caption)
                await bot.send_message(chat_id=_ref,
                                       text=f"😎️ *Кто-то перешел по твоей ссылке!*\n\nВсего рефералов: {db.get_refs(_ref)}",
                                       parse_mode="Markdown")
            else:
                await db.add_user(message.chat.id, message.chat.username, 0, 0, '2020-11-11')
                await db.add_user_to_state(message.from_user.id, '2020-03-03', '2023-08-10 00:59:37')
        else:
            await db.add_user(message.chat.id, message.chat.username, 0, 0, '2020-11-11')
            await db.add_user_to_state(message.from_user.id, '2020-03-03', '2023-08-10 00:59:37')
    else:
        await db.add_user(message.chat.id, message.chat.username, 0, 0, '2020-11-11')
        await db.update_nickname(message.chat.id, message.chat.username)
    await message.answer(start_message(), reply_markup=start(), parse_mode="HTML")


@dp.message(F.text == '/admin')
async def _admin(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        await message.answer("Режим админа включен😎️", reply_markup=admin())
    else:
        await message.answer("Введите пароль:")


@dp.message(F.text == '/promo')
async def promo(message: types.Message, state: FSMContext):
    _user_id = message.chat.id
    print(await db.get_fame(_user_id))
    _data = message.text.split(" ")
    text = _data[1]
    all_promo = db.get_promo_all()
    if text in all_promo:
        if db.get_promo(text, "time") != str(0):
            time_promo = await db.get_promo(text, "time")
            time_promo = datetime.datetime.strptime(
                time_promo, '%Y-%m-%d %H:%M:%S')
            current_datetime = datetime.datetime.now()
            if current_datetime <= time_promo:
                if _user_id in used_promo_dict and text in used_promo_dict[_user_id]:
                    await message.answer('Вы уже использовали этот промокод.')
                else:
                    file_ = await db.get_promo(text, "card")
                    get_file = get_file = await db.get_file(file_)
                    photo = get_file[1]
                    caption = get_file[5]
                    fame, fame_all, fame_season = await db.get_fame(_user_id)
                    cards = await db.get_cards(_user_id)
                    card = cards[0]
                    await db.set_fame(_user_id, int(fame) + int(fame_all), int(fame_season))
                    if card == "0":
                        await db.update_cards(_user_id, str(get_file[0]))
                    else:
                        await db.update_cards(_user_id, card + ", " + str(get_file[0]))
                    await message.answer_photo(photo, caption)
                    if _user_id not in used_promo_dict:
                        used_promo_dict[_user_id] = set()
                    used_promo_dict[_user_id].add(text)
            else:
                await message.answer('Время на активацию закончилось 😔️')
        else:
            if await db.get_promo(text, "activation") <= 0:
                await message.answer('Активации закончились 😔️')
            else:
                if _user_id in used_promo_dict and text in used_promo_dict[_user_id]:
                    await message.answer('Вы уже использовали этот промокод.')
                else:
                    file_ = await db.get_promo(text, "card")
                    get_file = await db.get_file(file_)
                    photo = get_file[1]
                    caption = get_file[5]
                    fame = await get_file[4]
                    _fame, fame_all, fame_season = await db.get_fame(_user_id)
                    cards = await db.get_cards(_user_id)
                    card = cards[0]
                    await db.set_fame(_user_id, int(fame) + int(_fame), int(fame) + int(fame_all),
                                      int(fame) + int(fame_season))
                    if card == "0":
                        await db.update_cards(_user_id, str(get_file[0]))
                    else:
                        await db.update_cards(_user_id, card + ", " + str(get_file[0]))
                    await message.answer_photo(photo, caption)
                    activation = await db.get_promo(text, "activation")
                    await db.set_promo(text, "activation", activation - 1)
                    if _user_id not in used_promo_dict:
                        used_promo_dict[_user_id] = set()
                    used_promo_dict[_user_id].add(text)
    else:
        await message.answer("Такого промокода не существует")


def _random():
    # сюда все редкости, ниже вероятность
    values = ["LEGENDARY", "Epic", "Rare", "Normal"]
    data = random.choices(values, weights=[0.05, 0.15, 0.30, 0.5], k=10000)
    return random.choice(data)


if __name__ == '__main__':
    for i in range(10):
        rare = _random()
        print(rare, '-', end=' ')
        print(len(loop.run_until_complete(db.get_rare(rare))) - 1)
    while True:
        try:
            loop.run_until_complete(db.check_db())
            asyncio.run(main())
        except Exception as e:
            time.sleep(3)
            print(e)
