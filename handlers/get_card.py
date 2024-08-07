from aiogram import types, Router, F
import db
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random
import time
import datetime
import asyncio

last_request_times = {}
router = Router()


def _random():
    # сюда все редкости, ниже вероятность
    values = ["LEGENDARY", "Epic", "Rare", "Normal"]
    data = random.choices(values, weights=[0.05, 0.15, 0.30, 0.5], k=10000)
    return random.choice(data)


def kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Подписаться', url='https://t.me/phonkcard')
    return keyboard


@router.message(F.text == '💨️ Получить дрифт-карту')
async def get_cards(message: types.Message):
    _user_id = message.chat.id
    # print(_user_id, '-', type(_user_id))
    # is_subscribed = await bot.get_chat_member(-1001903219993, _user_id)
    # print(is_subscribed)
    # if is_subscribed.status == "left":
    #     await bot.send_message(_user_id, "*Для дальнейшей игры вам необходимо подписаться на канал⬇️*", reply_markup=kb().as_markup(), parse_mode="Markdown")
    current_time_ms = int(time.time() * 1000)
    last_request_time_ms = last_request_times.get(_user_id, 0)
    last_request_times[_user_id] = current_time_ms
    if current_time_ms - last_request_time_ms < 500:
        await message.answer("⏳️ Не спамь!!!")
        return
    else:
        frees = await db.get_botnet(message.from_user.id)
        free = frees[4]
        if free == 0:
            user_id = message.from_user.id
            # Получаем строку с датой и временем
            stat_time_str = await db.get_states(user_id, 'state_card')
            stat_time = datetime.datetime.strptime(
                stat_time_str, '%Y-%m-%d %H:%M:%S')  # Преобразовываем дату и время
            current_datetime = datetime.datetime.now()  # Используем текущую дату и время
            current_date = datetime.datetime.now().date()
            info = await db.get_info(user_id)
            pp_time = datetime.datetime.strptime(
                info[6], '%Y-%m-%d').date()
            pphours = 4
            if (pp_time > current_date):
                pphours = 3
            if current_datetime <= stat_time:
                await db.update_states(user_id, 'state_card',
                                       (current_datetime + datetime.timedelta(hours=pphours)).strftime(
                                           '%Y-%m-%d %H:%M:%S'))
                _user_id = message.chat.id
                rare = _random()
                # print(rare)

                rand = random.randint(0, b=(len(await db.get_rare(rare)) - 1))
                _rares = await db.get_rare(rare)
                _rare = _rares[rand]
                photo = _rare[1]
                caption = _rare[5] + \
                          f'\n\n🍜 Следущая попытка будет доступна через {pphours} часа, заходи к нам позже…'
                fame = _rare[4]
                _fame, fame_all, fame_season = await db.get_fame(_user_id)
                cards = await db.get_cards(_user_id)
                card = cards[0]
                await db.set_fame(_user_id, int(fame) + int(_fame), int(fame) + int(fame_all),
                                  int(fame) + int(fame_season))
                if card == "0":
                    await db.update_cards(_user_id, str(_rare[0]))
                else:
                    await db.update_cards(_user_id, card + ", " + str(_rare[0]))
                await message.answer(caption)
                # await bot.send_photo(photo, caption)
                if pp_time >= current_date:
                    await asyncio.sleep(3 * 60 * 60)
                    await message.answer("💨️ Вы снова можете открыть карту")
            else:
                remaining_time = stat_time - current_datetime
                hours = remaining_time.seconds // 3600
                minutes = (remaining_time.seconds % 3600) // 60
                await message.answer(f"Следующая попытка будет доступна через {hours}ч {minutes}м")
        else:
            _user_id = message.from_user.id
            rare = _random()
            rand = random.randint(0, len(await db.get_rare(rare)) - 1)
            _rares = await db.get_rare(rare)
            _rare = _rares[rand]
            photo = _rare[1]
            caption = _rare[5]
            fame = _rare[4]
            _fame, fame_all, fame_season = await db.get_fame(_user_id)
            cards = await db.get_cards(_user_id)
            card = cards[0]
            await db.set_fame(_user_id, int(fame) + int(_fame), int(fame) + int(fame_all), int(fame) + int(fame_season))
            if card == "0":
                await db.update_cards(_user_id, str(_rare[0]))
            else:
                await db.update_cards(_user_id, card + ", " + str(_rare[0]))
            # await bot.send_photo(photo, caption)
            await db.update_botnet(message.from_user.id, 'comp_points', free - 1)
