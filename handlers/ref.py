from aiogram import types, F
from main import dp
import db

@dp.callback_query(F.text == "ref")
async def ref(call: types.CallbackQuery):
    await call.message.answer(f"""👩‍💻 Ваша реферальная программа

•Получено карт редкости MOD: {db.get_botnet(call.from_user.id)[3]}

•По твоей ссылке играют: {db.get_refs(call.from_user.id)} друзей.

🦋 Ссылочка, бро: https://t.me/PodsCardBot?start={call.from_user.id}

👨‍💻 За 10 приглашённых друзей, которые начнут играть в PodCards по твоей ссылке, ты можешь получить карточку редкостью MOD (15k Зависимости)
""")               #вместо https://t.me/PodsCardBot просто ссылку на бота
