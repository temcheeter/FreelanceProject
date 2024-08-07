from os import system
import datetime
import aiosqlite


# Новая бд (если отсутствует)
async def check_db():
    _ = system("cls")
    _datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    databaseFile = ("database.db")
    async with aiosqlite.connect(databaseFile, check_same_thread=False) as db:
        cursor = await db.cursor()
        try:
            await db.execute("SELECT * FROM users")
            print("----   Database was found   ----")
        except aiosqlite.OperationalError:
            await db.execute(
                "CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INT, nickname TEXT, fame INT, ref_id INT, cards TEXT, pod_pass TEXT, fame_all INT, fame_season INT)")
            await db.commit()
            print("----   Database was create   ---")
        try:
            await db.execute("SELECT * FROM botnet")
        except aiosqlite.OperationalError:
            await db.execute(
                "CREATE TABLE botnet(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INT, nickname TEXT, botnet_amount INT, comp_points INT, comp_id TEXT)")
            await db.commit()
        try:
            await db.execute("SELECT * FROM files")
        except aiosqlite.OperationalError:
            await db.execute(
                "CREATE TABLE files(id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id TEXT, name TEXT, rare TEXT, fame INT, caption TEXT)")
            await db.commit()
        try:
            await db.execute("SELECT * FROM shop")
        except aiosqlite.OperationalError:
            await db.execute(
                "CREATE TABLE shop(id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id TEXT, name TEXT, rare TEXT, fame INT, caption TEXT)")
            await db.commit()
        try:
            await db.execute("SELECT * FROM states")
        except aiosqlite.OperationalError:
            await db.execute(
                "CREATE TABLE states(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INT, state_dice TEXT, state_free TEXT, state_card INT, state_casino TEXT, state_basketball TEXT)")
            await db.commit()
        try:
            await db.execute("SELECT * FROM promo")
        except aiosqlite.OperationalError:
            await db.execute(
                "CREATE TABLE promo(id INTEGER PRIMARY KEY AUTOINCREMENT, promo TEXT, card INT, activation INT, time TEXT, active INT)")
            await db.commit()
        try:
            await db.execute("SELECT * FROM squads")
        except aiosqlite.OperationalError:
            await db.execute(
                "CREATE TABLE squads(id INTEGER PRIMARY KEY AUTOINCREMENT, squad_name TEXT, description TEXT, squad_photo TEXT, members TEXT, owner TEXT, fame INT)")
            await db.commit()
        print(f"-----   {_datetime}   -----")
        print(f"---------   Users: {len(tuple(await get_all_users()))}   --------\n")


# ------------------------------
# Дата
async def get_now_date():
    date = datetime.date.today()
    return date


# Новый юзер
async def add_user(user_id, nickname, ref_id, cards, pod_pass):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f'SELECT user_id FROM users WHERE user_id = "{user_id}"')
        if not await cursor.fetchall():
            await db.execute(
                f'INSERT INTO users(user_id, nickname, fame, ref_id, cards, pod_pass, fame_all, fame_season) VALUES ("{user_id}", "{nickname}", "{0}", "{ref_id}", "{cards}", "{pod_pass}", "{0}", "{0}")')
        await cursor.execute(f"SELECT user_id FROM botnet WHERE user_id = '{user_id}'")
        if not await cursor.fetchall():
            await db.execute(
                f"INSERT INTO botnet(user_id, nickname, botnet_amount, comp_points) VALUES ({user_id}, '{nickname}', '{0}', '{0}')")
        await db.commit()


async def add_squad(squad_name, squad_photo, description, user_id):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            f"INSERT INTO squads(squad_name, squad_photo, description, members, owner) VALUES ('{squad_name}', '{squad_photo}', '{description}', '{user_id}', '{user_id}')")
        await db.execute(f"UPDATE botnet SET comp_id = '{squad_name}' WHERE user_id = '{user_id}'")
        await db.commit()


async def get_squad(squad_name):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM squads WHERE squad_name = '{squad_name}'")
        row = cursor.fetchone()
        return row


async def set_squad(squad_name, command, value):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await db.execute(f"UPDATE squads SET {command} = '{value}' WHERE squad_name = '{squad_name}'")
        await db.commit()


async def delete_squad(squad_name):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(f"DELETE FROM squads WHERE squad_name = '{squad_name}'")
        await db.commit()


async def update_nickname(user_id, nickname):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(f"UPDATE users SET nickname = '{nickname}' WHERE user_id = {user_id}")
        await db.execute(f"UPDATE botnet SET nickname = '{nickname}' WHERE user_id = {user_id}")
        await db.commit()


async def get_botnet(user_id):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM botnet WHERE user_id = {user_id}")
        row = await cursor.fetchone()
        return row


async def get_cards(user_id):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT cards FROM users WHERE user_id = {user_id}")
        row = await cursor.fetchone()
        return tuple(row)


async def update_cards(user_id, value):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(f"UPDATE users SET cards = '{value}' WHERE user_id = {user_id}")
        await db.commit()


async def update_pass(user_id, value):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(f"UPDATE users SET pod_pass = '{value}' WHERE user_id = {user_id}")
        await db.commit()


async def get_all_cards():
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT id FROM files")
        row = cursor.fetchall()
        return row


async def get_states(user_id, command):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT {command} FROM states WHERE user_id = {user_id}")
        row = await cursor.fetchone()
        return row[0]


async def update_states(user_id, command, value):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(f"UPDATE states SET {command} = '{value}' WHERE user_id = '{user_id}'")
        await db.commit()


async def get_botnet_nick(nickname):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM botnet WHERE nickname = '{nickname}'")
        row = cursor.fetchone()
        return row


async def update_botnet(user_id, command, value):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(f"UPDATE botnet SET {command} = '{value}' WHERE user_id = '{user_id}'")
        await db.commit()


async def delete_botnet(user_id, command):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(f"UPDATE botnet SET {command} = NULL WHERE user_id = '{user_id}'")
        await db.commit()


async def get_users_exist(user_id):
    async with aiosqlite.connect("database.db", check_same_thread=False) as db:
        cursor = await db.cursor()
        file = await cursor.execute(f"SELECT user_id FROM users WHERE user_id = '{user_id}'")
        if await cursor.fetchone() is None:
            return False
        else:
            return True


async def get_users_exist_state(user_id):
    async with aiosqlite.connect("database.db", check_same_thread=False) as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT user_id FROM states WHERE user_id = '{user_id}'")
        if cursor.fetchone() is None:
            return False
        else:
            return True


async def add_user_to_state(user_id, _id, _id2):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT user_id FROM states WHERE user_id = '{user_id}'")
        if not await cursor.fetchone():
            await cursor.execute(
                f"INSERT INTO states(user_id, state_dice, state_free, state_card, state_casino, state_basketball) VALUES ({user_id}, '{_id}', '{_id}', '{_id2}', '{_id}', '{_id}')")
        await db.commit()


async def get_info(user_id):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}")
        row = await cursor.fetchone()
        return row


async def add_promo_act(text, act, card):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            f"INSERT INTO promo(promo, card, time, activation, active) VALUES ('{text}', {card}, {0}, {act}, {0})")
        await db.commit()


async def add_promo_time(text, time, card):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            f"INSERT INTO promo(promo, card, time, activation, active) VALUES ('{text}', {card}, '{time}', {0}, {0})")
        await db.commit()


async def get_promo_all():
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT promo FROM promo")
        rows = await cursor.fetchall()
        promo_codes_list = [row[0] for row in rows]
        return promo_codes_list


async def set_promo(promo, command, value):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(f"UPDATE promo SET {command} = '{value}' WHERE promo = '{promo}'")
        await db.commit()


async def get_promo(promo, command):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT {command} FROM promo WHERE promo = '{promo}'")
        row = await cursor.fetchone()
        return row[0]


async def get_rare(rare):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM files WHERE rare = '{rare}'")
        row = await cursor.fetchall()
        print(row)
        return row


async def get_nickname(nickname):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM users WHERE nickname = '{nickname}'")
        row = cursor.fetchone()
        return row


async def get_fame(user_id):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT fame FROM users WHERE user_id = {user_id}")
        fame = await cursor.fetchone()
        await cursor.execute(f"SELECT fame_all FROM users WHERE user_id = {user_id}")
        fame_all = await cursor.fetchone()
        await cursor.execute(f"SELECT fame_season FROM users WHERE user_id = {user_id}")
        fame_season = await cursor.fetchone()
        return fame[0], fame_all[0], fame_season[0]


async def set_fame(user_id, fame, fame_all, fame_season):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(f"UPDATE users SET fame = {fame} WHERE user_id = {user_id}")
        await db.execute(f"UPDATE users SET fame_all = {fame_all} WHERE user_id = {user_id}")
        await db.execute(f"UPDATE users SET fame_season = {fame_season} WHERE user_id = {user_id}")
        await db.commit()


async def get_refs(user_id):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT user_id FROM users WHERE ref_id = {user_id}")
        row = await cursor.fetchall()
        return len(tuple(row))


async def get_pre_ref(user_id):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT ref_id FROM users WHERE user_id = {user_id}")
        row = await cursor.fetchone()
        return row[0]


async def get_top_ref(limit):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(
            f"SELECT COUNT(ref_id) AS ref_count, * FROM USERS WHERE ref_id != 0 GROUP BY ref_id ORDER BY COUNT(ref_id) DESC LIMIT {limit}")
        row = cursor.fetchall()
        return row


async def get_top_fame(limit):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM users ORDER BY fame_season DESC LIMIT 10;")
        row = cursor.fetchall()
        return row


async def get_top_fame_all(limit):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM users ORDER BY fame_all DESC LIMIT 10;")
        row = cursor.fetchall()
        return row


async def get_all_users():
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT user_id FROM users")
        row = await cursor.fetchall()
        return row


async def get_all_users_nickname():
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT nickname FROM users")
        row = cursor.fetchall()
        return row


async def add_file(_id, name, rare, fame, caption):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            f"INSERT INTO files(tg_id, name, rare, fame, caption) VALUES ('{_id}', '{name}', '{rare}', '{fame}', '{caption}')")
        await db.commit()


async def change_file(_id, photo, name, rare, fame, caption):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(f"UPDATE files SET tg_id = '{photo}' WHERE id = '{_id}'")
        await db.execute(f"UPDATE files SET name = '{name}' WHERE id = '{_id}'")
        await db.execute(f"UPDATE files SET rare = '{rare}' WHERE id = '{_id}'")
        await db.execute(f"UPDATE files SET fame = '{fame}' WHERE id = '{_id}'")
        await db.execute(f"UPDATE files SET caption = '{caption}' WHERE id = '{_id}'")
        await db.commit()


async def get_file(_id):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM files WHERE id = '{_id}'")
        file = await cursor.fetchone()
        return file


async def get_file_name(name):
    async with (aiosqlite.connect('database.db') as db):
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM files WHERE name = '{name}'")
        file = await cursor.fetchone()
        return file


async def add_shop(_id, name, rare, fame, caption):
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            f"INSERT INTO shop(tg_id, name, rare, fame, caption) VALUES ('{_id}', '{name}', '{rare}', '{fame}', '{caption}')")
        await db.commit()
        # file_id = cursor.execute(f"SELECT id FROM shop WHERE tg_id = '{_id}'").fetchone()[0]


async def get_shop(_id):
    async with (aiosqlite.connect('database.db') as db):
        cursor = await db.cursor()
        await db.commit()
        await cursor.execute(f"SELECT * FROM shop WHERE id = '{_id}'")
        file = await cursor.fetchone()
        return file


async def get_all_shop():
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM shop")
        row = cursor.fetchall()
        return row


async def find_card_by_name(card_name):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.cursor()
        card_name = card_name.lower()
        await cursor.execute(f"SELECT * FROM files WHERE LOWER(name) LIKE ? OR LOWER(caption) LIKE ?",
                             ('%' + card_name + '%', '%' + card_name + '%'))
        rows = cursor.fetchall()
        return rows
