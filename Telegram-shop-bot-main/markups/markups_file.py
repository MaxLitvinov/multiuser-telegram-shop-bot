from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton,
)

# ── Кнопки ───────────────────────────────────────────────────────────────────
choose_game   = KeyboardButton("🎮 Вибрати гру")
menu_btn      = KeyboardButton("🏠 Головне меню")
about_btn     = KeyboardButton("🌀 Про нас")
faq_btn       = KeyboardButton("⭐️ FAQ")
ask_btn       = KeyboardButton("🖌 Запитати")
suggestion_btn = KeyboardButton("✉️ Запропонувати гру")
basket_btn    = KeyboardButton("🗑 Кошик")
basket_remove_btn = KeyboardButton("✂️ Прибрати з кошика")
buy_btn_kb    = KeyboardButton("🟢 Оформити")
pay_btn       = KeyboardButton("💰 Оплатити")
pickup_btn    = KeyboardButton("🚶🏻 Самовивіз")
delivery_btn  = KeyboardButton("🚗 Доставка")
card_btn      = KeyboardButton("💳 Банківська карта")
cash_btn      = KeyboardButton("💵 Готівкою")
submit_btn    = KeyboardButton("✅ Підтвердити")
change_pay_btn = KeyboardButton("🖌 Змінити спосіб оплати")
available_btn = KeyboardButton("📪 Повернути в наявність")
add_new_btn   = KeyboardButton("🎲 Додати нову гру")
del_game_btn  = KeyboardButton("💥 Видалити гру")
sub_add_btn   = KeyboardButton("✅ Додати")
reset_btn     = KeyboardButton("🗯 Скинути")

# ── Клавіатури ────────────────────────────────────────────────────────────────
menu_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(menu_btn)

main_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
    about_btn, faq_btn, ask_btn, choose_game, suggestion_btn
)

order_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(basket_btn, menu_btn)

basket_main_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(
    about_btn, faq_btn, ask_btn, basket_btn, suggestion_btn
)

basket_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    basket_remove_btn, basket_btn, menu_btn, choose_game, buy_btn_kb
)

choice_basket_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    choose_game, menu_btn, basket_btn
)

pick_method_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    pickup_btn, delivery_btn, menu_btn
)

buy_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    pay_btn, basket_btn, menu_btn
)

pay_method = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    card_btn, cash_btn, menu_btn
)

cash_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    submit_btn, change_pay_btn, menu_btn
)

admin_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    available_btn, add_new_btn, del_game_btn, menu_btn
)

sub_res_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    sub_add_btn, reset_btn, menu_btn
)

# ── Inline ────────────────────────────────────────────────────────────────────
load_markup = InlineKeyboardMarkup(resize_keyboard=True).add(
    InlineKeyboardButton("Показати ще", callback_data="load_more")
)


def pay_menu(is_url: bool = True, url: str = "", bill: str = "") -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    if is_url:
        markup.add(InlineKeyboardButton("Посилання на оплату", url=url))
    markup.add(InlineKeyboardButton("Перевірити оплату", callback_data=f"check_{bill}"))
    return markup
