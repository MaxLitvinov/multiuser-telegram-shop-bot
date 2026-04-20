from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from create_bot import bot, dp
from db import (
    sql_start, add_value, add_user, add_order,
    print_products, get_info, checker, receive_method,
    add_suggestion, pay_method_db, add_check, get_check, delete_check
)
from markups import (
    order_markup, main_markup, basket_markup, pick_method_markup,
    buy_markup, pay_method, cash_markup, menu_markup, basket_main_markup, pay_menu
)
from admin import send_order, send_question
from pyqiwip2p import QiwiP2P
import random

QIWI_KEY = ""  # Вставте сюди ключ QIWI P2P
p2p = QiwiP2P(auth_key=QIWI_KEY)

# Стан кошика (в майбутньому краще перенести в БД для масштабованості)
user_sessions: dict = {}  # {username: {"choices": [], "rent_price": 0, ...}}

def get_session(username: str) -> dict:
    if username not in user_sessions:
        user_sessions[username] = {
            "choices": [],
            "rent_price": 0,
            "deposit_price": 0,
            "final_price": 0,
            "remove_check": [],
            "offset": 0,
            "showed": 5,
        }
    return user_sessions[username]

LIMIT = 5


class Address(StatesGroup):
    address = State()

class Suggestion(StatesGroup):
    suggestion = State()

class Ask(StatesGroup):
    question = State()


def get_username(message: types.Message) -> str:
    return message.from_user.username or str(message.from_user.id)


# ── /start ──────────────────────────────────────────────────────────────────
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    username = get_username(message)
    sql_start()
    add_user(username)
    await bot.send_photo(
        message.chat.id,
        photo=open("ui/img/greeting_photo.png", "rb"),
        reply_markup=main_markup,
    )


# ── /basket ──────────────────────────────────────────────────────────────────
@dp.message_handler(commands=["basket"])
async def cmd_basket(message: types.Message):
    username = get_username(message)
    await show_basket(message.chat.id, username)


# ── /home ────────────────────────────────────────────────────────────────────
@dp.message_handler(commands=["home"])
async def cmd_home(message: types.Message):
    username = get_username(message)
    await go_home(message.chat.id, username)


# ── /choose ──────────────────────────────────────────────────────────────────
@dp.message_handler(commands=["choose"])
async def cmd_choose(message: types.Message):
    username = get_username(message)
    await show_games(message, username)


# ── Допоміжні функції ────────────────────────────────────────────────────────
async def show_basket(chat_id: int, username: str):
    s = get_session(username)
    if s["choices"]:
        games_text = "\n\n🎲 ".join(s["choices"])
        await bot.send_message(
            chat_id,
            f"<b>🗑 Кошик:</b>\n\n🎲 {games_text}\n\n"
            f"<b>Сума оренди:</b> {s['rent_price']}\n\n"
            f"<b>Сума застави:</b> {s['deposit_price']}\n\n"
            f"<b>Загальна сума:</b> {s['final_price']}",
            parse_mode="html",
            reply_markup=basket_markup,
        )
    else:
        await bot.send_message(chat_id, "🕸 Кошик порожній")


async def go_home(chat_id: int, username: str):
    s = get_session(username)
    markup = main_markup if not s["choices"] else basket_main_markup
    await bot.send_message(chat_id, "<b>Ви у головному меню</b>", parse_mode="html", reply_markup=markup)


async def show_games(message: types.Message, username: str):
    s = get_session(username)
    s["offset"] = 0
    s["showed"] = LIMIT
    sql_start()
    if checker():
        await bot.send_message(message.chat.id, "🎮 Ігри в наявності:", reply_markup=order_markup)
        await print_products(message, s["offset"], LIMIT, s["showed"])
        s["offset"] += LIMIT
        s["showed"] += LIMIT
    else:
        await bot.send_message(message.chat.id, "📭 Ігор в наявності немає")


# ── Текстові кнопки ──────────────────────────────────────────────────────────
@dp.message_handler(content_types=["text"])
async def handle_text(message: types.Message):
    username = get_username(message)
    s = get_session(username)
    text = message.text

🤗 Раді вітати кожного!",
            parse_mode="html",
        )

    elif text == "⭐️ FAQ":
        await bot.send_message(
            message.chat.id,
            "🏮 <b>Часті запитання</b>\n\n"
            "🔷 <b>Як отримати замовлення?</b>\n"
            "🔹 Можна замовити доставку або забрати самовивозом (безкоштовно).\n\n"
            "🔷 <b>Як відбувається оплата?</b>\n"
            "🔹 Банківська карта (онлайн) або готівка (тільки при самовивозі).\n\n"
            "🔷 <b>Як повернути гру?</b>\n"
            "🔹 Повернення за адресою самовивозу.\n\n"
            "🔷 <b>Продавець не відповідає?</b>\n"
            "🔹 Зв'яжіться напряму через чат у Telegram.",
            parse_mode="html",
        )

    elif text == "🖌 Запитати":
        await Ask.question.set()
        await bot.send_message(message.chat.id, "📋 Введіть ваше запитання")

    elif text == "✂️ Прибрати з кошика":
        if not s["choices"]:
            await bot.send_message(message.chat.id, "🕸 Кошик порожній")
            return
        s["remove_check"] = []
        remove_markup = InlineKeyboardMarkup(resize_keyboard=True)
        for idx, item in enumerate(s["choices"]):
            game_name = item.split(" -")[0]
            period = "day" if item.endswith("1 день") else "week"
            btn = InlineKeyboardButton(
                f"Прибрати '{game_name}'",
                callback_data=f"rem_{period}_{game_name}i{idx}",
            )
            remove_markup.add(btn)
            s["remove_check"].append(game_name)
        await bot.send_message(message.chat.id, "Що прибрати?", reply_markup=remove_markup)

    elif text == "🟢 Оформити":
        if not s["choices"]:
            await bot.send_message(message.chat.id, "🕸 Кошик порожній")
            return
        order_games = ", ".join(s["choices"])
        sql_start()
        add_order(1, order_games, 0, s["rent_price"], s["final_price"], username)
        await bot.send_message(message.chat.id, "🎯 Виберіть спосіб отримання замовлення", reply_markup=pick_method_markup)

    elif text == "🚶🏻 Самовивіз":
        await receive_method("Самовивіз", 0, username)
        await bot.send_message(message.chat.id, "🗺 Самовивіз за адресою:\n<b></b>", parse_mode="html", reply_markup=buy_markup)

    elif text == "🚗 Доставка":
        await Address.address.set()
        await bot.send_message(message.chat.id, "🔥 Доставка від <b>200</b> грн\n(оплачується окремо)\n\nВведіть адресу доставки:", parse_mode="html")

    elif text == "💰 Оплатити":
        await bot.send_message(message.chat.id, "Виберіть спосіб оплати:", reply_markup=pay_method)

    elif text == "💳 Банківська карта":
        sql_start()
        await pay_method_db("Банківська карта", username)
        comment = f"{username}_{random.randint(1000, 9999)}"
        bill = p2p.bill(amount=int(s["final_price"]), lifetime=15, comment=comment)
        add_check(username, bill.bill_id)
        await bot.send_message(
            message.chat.id,
            f"Ваш рахунок сформовано на суму <b>{s['final_price']}</b> грн",
            parse_mode="html",
            reply_markup=pay_menu(url=bill.pay_url, bill=bill.bill_id),
        )

    elif text == "💵 Готівкою":
        await bot.send_message(message.chat.id, "❗️ Оплата готівкою тільки при самовивозі", reply_markup=cash_markup)
        sql_start()
        await pay_method_db("Готівкою", username)

    elif text == "✅ Підтвердити":
        await bot.send_message(message.chat.id, "❇️ Замовлення прийнято! Продавець зв'яжеться з вами найближчим часом.", reply_markup=menu_markup)
        await send_order(username)
        s["choices"] = []
        s["rent_price"] = s["deposit_price"] = s["final_price"] = 0

    elif text == "🖌 Змінити спосіб оплати":
        await bot.send_message(message.chat.id, "Виберіть спосіб оплати:", reply_markup=pay_method)

    elif text == "✉️ Запропонувати гру":
        await Suggestion.suggestion.set()
        await bot.send_message(message.chat.id, "⌨️ Введіть назви ігор, які хотіли б побачити в сервісі")


# ── Стани ────────────────────────────────────────────────────────────────────
@dp.message_handler(state=Address.address)
async def load_address(message: types.Message, state: FSMContext):
    username = get_username(message)
    await receive_method(message.text, 1, username)
    await bot.send_message(message.chat.id, "✅ Адресу збережено", reply_markup=buy_markup)
    await state.finish()


@dp.message_handler(state=Suggestion.suggestion)
async def load_suggestion(message: types.Message, state: FSMContext):
    username = get_username(message)
    sql_start()
    await add_suggestion(message.text, username)
    await bot.send_message(message.chat.id, "📤 Дякуємо! Пропозицію збережено.", reply_markup=main_markup)
    await state.finish()


@dp.message_handler(state=Ask.question)
async def load_question(message: types.Message, state: FSMContext):
    username = get_username(message)
    await send_question(username, message.text)
    await bot.send_message(message.chat.id, "✳️ Запитання надіслано продавцю.", reply_markup=main_markup)
    await state.finish()


# ── Callback: перевірка оплати ────────────────────────────────────────────────
@dp.callback_query_handler(lambda c: c.data.startswith("check_"))
async def check_payment(callback: types.CallbackQuery):
    username = callback.from_user.username or str(callback.from_user.id)
    s = get_session(username)
    bill_id = callback.data[6:]
    record = get_check(bill_id)
    if not record:
        await bot.send_message(callback.from_user.id, "❔ Рахунок не знайдено")
        return
    if str(p2p.check(bill_id=bill_id).status) == "PAID":
        await bot.send_message(callback.from_user.id, "❇️ Замовлення прийнято! Продавець зв'яжеться найближчим часом.", reply_markup=menu_markup)
        await send_order(username)
        s["choices"] = []
        s["rent_price"] = s["deposit_price"] = s["final_price"] = 0
        delete_check(username)
    else:
        await bot.send_message(callback.from_user.id, "🔒 Оплату ще не здійснено", reply_markup=pay_menu(False, bill=bill_id))


# ── Callback: додати до кошика ────────────────────────────────────────────────
@dp.callback_query_handler(lambda c: c.data.startswith("add_"))
async def add_to_basket(callback: types.CallbackQuery):
    username = callback.from_user.username or str(callback.from_user.id)
    s = get_session(username)
    data = callback.data

    if data.startswith("add_day_"):
        game_key = data.replace("add_day_", "")
        day_rent = True
    elif data.startswith("add_week_"):
        game_key = data.replace("add_week_", "")
        day_rent = False
    else:
        return

    if game_key in s["choices"]:
        await callback.answer("Гра вже у кошику")
        return

    sql_start()
    product = await get_info(game_key)
    if not product:
        await callback.answer("Гру не знайдено")
        return

    name, price_day, price_week, deposit = product[0]
    if day_rent:
        label = f"{name} - 📅 1 день"
        price = int(price_day)
    else:
        label = f"{name} - 📅 7 днів"
        price = int(price_week)

    s["choices"].append(label)
    s["rent_price"] += price
    s["deposit_price"] += int(deposit)
    s["final_price"] += price + int(deposit)
    add_value(name, 0)
    await callback.answer(text=f"Гру '{name}' додано до кошика")


# ── Callback: прибрати з кошика ───────────────────────────────────────────────
@dp.callback_query_handler(lambda c: c.data.startswith("rem_"))
async def remove_from_basket(callback: types.CallbackQuery):
    username = callback.from_user.username or str(callback.from_user.id)
    s = get_session(username)
    data = callback.data

    if data.startswith("rem_day_"):
        raw = data.replace("rem_day_", "")
        day_rent = True
    elif data.startswith("rem_week_"):
        raw = data.replace("rem_week_", "")
        day_rent = False
    else:
        return

    parts = raw.rsplit("i", 1)
    game_name = parts[0]
    try:
        idx = int(parts[1])
    except (IndexError, ValueError):
        return

    if game_name not in s["remove_check"]:
        return

    sql_start()
    product = await get_info(game_name)
    if not product:
        return

    _, price_day, price_week, deposit = product[0]
    price = int(price_day) if day_rent else int(price_week)

    s["remove_check"].remove(game_name)
    if 0 <= idx < len(s["choices"]):
        s["choices"].pop(idx)
    s["rent_price"] -= price
    s["deposit_price"] -= int(deposit)
    s["final_price"] -= price + int(deposit)
    add_value(game_name, 1)
    await callback.answer(text=f"Гру '{game_name}' прибрано з кошика")


# ── Callback: завантажити ще ──────────────────────────────────────────────────
@dp.callback_query_handler(lambda c: c.data == "load_more")
async def load_more(callback: types.CallbackQuery):
    username = callback.from_user.username or str(callback.from_user.id)
    s = get_session(username)
    # Потрібен збережений об'єкт message — передаємо через callback.message
    await print_products(callback.message, s["offset"], LIMIT, s["showed"])
    s["offset"] += LIMIT
    s["showed"] += LIMIT
