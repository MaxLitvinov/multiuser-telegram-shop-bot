import sqlite3
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from create_bot import bot
from markups import load_markup

base: sqlite3.Connection | None = None
cursor: sqlite3.Cursor | None = None


def sql_start():
    global base, cursor
    base = sqlite3.connect("db/database.db")
    cursor = base.cursor()


def add_value(name: str, available: int):
    cursor.execute(
        "UPDATE game_checker SET available = ? WHERE game_name = ?",
        (available, name),
    )
    base.commit()


def add_user(username: str):
    cursor.execute(
        "INSERT OR IGNORE INTO users(username_tg) VALUES(?)",
        (username,),
    )
    base.commit()


def add_order(ordered, order_text, order_paid, rent_price, order_price, username):
    cursor.execute(
        "UPDATE users SET ordered = ?, order_text = ?, order_paid = ?, "
        "rent_price = ?, order_price = ? WHERE username_tg = ?",
        (ordered, order_text, order_paid, rent_price, order_price, username),
    )
    base.commit()


def checker():
    result = cursor.execute(
        "SELECT 1 FROM game_checker WHERE available = 1 LIMIT 1"
    ).fetchone()
    base.commit()
    return result


async def print_products(message, offset: int, limit: int, showed: int):
    rows = cursor.execute(
        "SELECT * FROM game_checker WHERE available = 1 LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()

    for obj in rows:
        markup = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(
            InlineKeyboardButton(f"Орендувати '{obj[0]}' на день", callback_data=f"add_day_{obj[0]}"),
            InlineKeyboardButton(f"Орендувати '{obj[0]}' на тиждень", callback_data=f"add_week_{obj[0]}"),
        )
        await bot.send_photo(
            message.chat.id,
            obj[5],
            caption=(
                f"‎\n🥏 <b>{obj[0]}</b>\n\n"
                f"🔹 Ціна за день: {obj[2]}\n\n"
                f"🔹 Ціна за тиждень: {obj[3]}\n\n"
                f"🔹 Застава: {obj[4]}"
            ),
            parse_mode="html",
            reply_markup=markup,
        )

    total = cursor.execute(
        "SELECT COUNT(*) FROM game_checker WHERE available = 1"
    ).fetchone()[0]

    if total > showed:
        await bot.send_message(
            message.chat.id,
            f"Показано <b>{showed}</b> ігор з <b>{total}</b>",
            parse_mode="html",
            reply_markup=load_markup,
        )
    else:
        await bot.send_message(
            message.chat.id,
            f"Показано <b>{min(showed, total)}</b> ігор з <b>{total}</b>",
            parse_mode="html",
        )


async def get_info(name: str):
    result = cursor.execute(
        "SELECT game_name, price_day, price_week, deposit FROM game_checker WHERE game_name = ?",
        (name,),
    ).fetchmany()
    base.commit()
    return result


async def receive_method(address: str, is_delivery: int, username: str):
    cursor.execute(
        "UPDATE users SET user_adress = ?, delivery = ? WHERE username_tg = ?",
        (address, is_delivery, username),
    )
    base.commit()


async def pay_method_db(method: str, username: str):
    cursor.execute(
        "UPDATE users SET pay_method = ? WHERE username_tg = ?",
        (method, username),
    )
    base.commit()


async def add_suggestion(text: str, username: str):
    cursor.execute(
        "UPDATE users SET suggestion = ? WHERE username_tg = ?",
        (text, username),
    )
    base.commit()


async def get_order(username: str):
    result = cursor.execute(
        "SELECT username_tg, order_text, rent_price, order_price, "
        "user_adress, delivery, pay_method FROM users WHERE username_tg = ?",
        (username,),
    ).fetchmany()
    base.commit()
    return result


async def add_game(name, day_price, week_price, deposit, photo):
    cursor.execute(
        "INSERT INTO game_checker(game_name, price_day, price_week, deposit, photo) "
        "VALUES(?, ?, ?, ?, ?)",
        (name, day_price, week_price, deposit, photo),
    )
    base.commit()


async def del_game(game_name: str):
    cursor.execute(
        "DELETE FROM game_checker WHERE game_name = ?",
        (game_name,),
    )
    base.commit()


def add_check(username: str, bill_id: str):
    cursor.execute(
        "UPDATE users SET bill_id = ? WHERE username_tg = ?",
        (bill_id, username),
    )
    base.commit()


def get_check(bill_id: str):
    result = cursor.execute(
        "SELECT * FROM users WHERE bill_id = ?",
        (bill_id,),
    ).fetchone()
    base.commit()
    if not result:
        return False
    return result[0]


def delete_check(username: str):
    cursor.execute(
        "UPDATE users SET bill_id = ? WHERE username_tg = ?",
        ("", username),
    )
    base.commit()
