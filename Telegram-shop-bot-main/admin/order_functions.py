from create_bot import bot, ADMIN_CHAT_ID
from db import sql_start, get_order


async def send_order(username: str):
    sql_start()
    order_info = await get_order(username)
    if not order_info:
        return
    row = order_info[0]
    tg_user, order_text, rent_price, order_price, address, is_delivery, pay_method = row

    delivery_line = (
        f"🚗 Доставка\n\n🗺 <b>Адреса:</b>\n{address}"
        if is_delivery == 1
        else "🚶🏻 Самовивіз"
    )

    text = (
        f"🔥 <b>Нове замовлення!</b>\n\n"
        f"👱‍♂️ <b>Користувач:</b>\n{tg_user}\n\n"
        f"🏵 <b>Замовлення:</b>\n{order_text}\n\n"
        f"💵 <b>Ціна оренди:</b> {rent_price}\n\n"
        f"💰 <b>Загальна сума:</b> {order_price}\n\n"
        f"📦 <b>Спосіб отримання:</b>\n{delivery_line}\n\n"
        f"💸 <b>Спосіб оплати:</b>\n{pay_method}"
    )

    await bot.send_message(ADMIN_CHAT_ID, text, parse_mode="html")


async def send_question(username: str, question: str):
    await bot.send_message(
        ADMIN_CHAT_ID,
        f"❓ <b>Запитання від {username}:</b>\n{question}",
        parse_mode="html",
    )
