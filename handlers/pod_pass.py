import hashlib
from aiogram.enums import ParseMode
from aiogram import types, F
import time
from main import dp, bot

PAYOK_SECRET_KEY = 'b9eabe4fe269069f2466ac4f9cb862e8'
PAYOK_SHOP_ID = '10415'

def pp_text1():
    text = """💭 Бро, давай расскажу тебе о <b>Pod Pass</b>, это рюкзачок, с полезным содержимым, а именно:

• Уведомление о следующей попытке. 
• 3 часа ожидания следующей карты, вместо 4
• Возможность бросать 🎲 кубик два раза в неделю.
• Иногда засылаем редчашйие карты.

💼 <b>Pod Pass - 100 рублей</b>"""
    return text

def pp_text2(link):
    text = f"""🔑 Для приобретения <b>Pod Pass</b> оплатите покупку
воспользовавшись <a href="{link}">этой ссылкой</a>

❗ <b>Так как автоматичекое принятие платежей еще не настроено, администраторы будут выдавать Pod Pass вручную в течении 2 часов</b>

ℹ️ Если у вас не прогрузились способы оплаты, скорее всего, вы перешли по ссылке из telegram desktop, и этот способ иногда багается 
Попробуйте открыть ссылку в браузере в режиме инкогнито или через телефон."""
    return text

def generate_payment_number(user_id):
    # Создаем уникальный номер заказа на основе user_id и текущего времени
    timestamp = str(int(time.time()))
    payment_number = f"{user_id}_{timestamp}"
    return payment_number

def generate_payment_link(user_id, amount, currency, desc, email, method, lang):
    payment_number = generate_payment_number(user_id)
    sign_data = "|".join([str(amount), payment_number, str(PAYOK_SHOP_ID), currency, desc, PAYOK_SECRET_KEY])
    sign = hashlib.md5(sign_data.encode()).hexdigest()

    payment_url = "https://payok.io/pay"
    
    payment_params = {
        'amount': amount,
        'payment': payment_number,
        'shop': PAYOK_SHOP_ID,
        'currency': currency,
        'desc': desc,
        'email': email,
        'method': method,
        'lang': lang,
        'sign': sign
    }

    payment_link = payment_url + '?' + '&'.join([f'{key}={value}' for key, value in payment_params.items()])

    return payment_link


@dp.callback_query(F.text == ['pod_pass'])
async def generate_payment(call: types.CallbackQuery):
    user_id = call.from_user.id  # Получаем user_id из сообщения
    amount = 100.0
    currency = "RUB"
    desc = "Pod_Pass"
    email = "podscardbot@rambler.ru"
    method = "cd"
    lang = "RU" 

    payment_link = generate_payment_link(user_id, amount, currency, desc, email, method, lang)

    await bot.send_message(call.from_user.id, pp_text1(), parse_mode=ParseMode.HTML)
    await bot.send_message(call.from_user.id, pp_text2(payment_link), parse_mode=ParseMode.HTML)

#недоделаная обработка платежей
"""@app.route('/payment_notification', methods=['POST'])
def payment_notification():
    data = request.form

    sign_data = "|".join([
        PAYOK_SECRET_KEY,
        data.get('desc', ''),
        data.get('currency', ''),
        str(data.get('shop', '')),
        str(data.get('payment_id', '')),
        str(data.get('amount', ''))
    ])
    calculated_sign = hashlib.md5(sign_data.encode()).hexdigest()

    if calculated_sign != data.get('sign', ''):
        return 'Invalid signature', 400

    payment_id = data.get('payment_id')
    shop = data.get('shop')
    amount = data.get('amount')
    profit = data.get('profit')
    desc = data.get('desc')
    currency = data.get('currency')
    email = data.get('email')
    date = data.get('date')
    method = data.get('method')
    custom1 = data.get('custom[param1]')
    custom2 = data.get('custom[param2]')

    # Ваш код для обработки уведомления

    return 'Notification received', 200

async def process_payment_notification(data):
    # Извлекаем необходимую информацию из data
    payment_id = data.get('payment_id')
    shop = data.get('shop')
    amount = data.get('amount')
    profit = data.get('profit')
    desc = data.get('desc')
    currency = data.get('currency')
    email = data.get('email')
    date = data.get('date')
    method = data.get('method')
    custom1 = data.get('custom[param1]')
    custom2 = data.get('custom[param2]')

    # Отправляем сообщение в телеграм (в данном случае просто выводим информацию)
    message = f"Поступил платеж:\n" \
              f"Номер заказа: {payment_id}\n" \
              f"Магазин: {shop}\n" \
              f"Сумма: {amount} {currency}\n" \
              f"Описание: {desc}\n" \
              f"Email: {email}\n" \
              f"Дата: {date}\n" \
              f"Способ оплаты: {method}\n" \
              f"Дополнительный параметр 1: {custom1}\n" \
              f"Дополнительный параметр 2: {custom2}"
    
    user_id = payment_id.text.split("_")[0]
    # Замените этот код на вашу логику отправки сообщения в телеграм
    await bot.send_message(chat_id=user_id, text="Вы приобрели Pod Pass на 1 месяц")"""
