from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher

from create_bot import bot, dp
from db import sql_start, add_game, add_value, del_game
from markups import admin_markup, sub_res_markup

_admin_id: int | None = None
_pending_game: dict = {}


class AddGame(StatesGroup):
    name = State()
    price_day = State()
    price_week = State()
    deposit = State()
    photo = State()


class SetAvailable(StatesGroup):
    game_name = State()


class DeleteGame(StatesGroup):
    game_name_del = State()


# ── Відкрити адмін-панель ────────────────────────────────────────────────────
@dp.message_handler(lambda m: "Адмін панель" in m.text, is_chat_admin=True)
async def admin_panel(message: types.Message):
    global _admin_id
    _admin_id = message.from_user.id
    await message.delete()
    await bot.send_message(message.from_user.id, "📟 Адмін панель — оберіть дію:", reply_markup=admin_markup)


def _is_admin(message: types.Message) -> bool:
    return message.from_user.id == _admin_id


# ── Додати гру ───────────────────────────────────────────────────────────────
@dp.message_handler(lambda m: "🎲 Додати нову гру" in m.text, state=None)
async def adm_add_start(message: types.Message):
    if not _is_admin(message):
        return
    await AddGame.name.set()
    await bot.send_message(message.chat.id, "📖 Введіть назву гри")


@dp.message_handler(state=AddGame.name)
async def adm_load_name(message: types.Message, state: FSMContext):
    if not _is_admin(message):
        return
    async with state.proxy() as data:
        data["name"] = message.text
    await AddGame.next()
    await bot.send_message(message.chat.id, "💸 Введіть ціну оренди за добу")


@dp.message_handler(state=AddGame.price_day)
async def adm_load_price_day(message: types.Message, state: FSMContext):
    if not _is_admin(message):
        return
    async with state.proxy() as data:
        data["day_price"] = message.text
    await AddGame.next()
    await bot.send_message(message.chat.id, "💵 Введіть ціну оренди за тиждень")


@dp.message_handler(state=AddGame.price_week)
async def adm_load_price_week(message: types.Message, state: FSMContext):
    if not _is_admin(message):
        return
    async with state.proxy() as data:
        data["week_price"] = message.text
    await AddGame.next()
    await bot.send_message(message.chat.id, "💰 Введіть суму застави")


@dp.message_handler(state=AddGame.deposit)
async def adm_load_deposit(message: types.Message, state: FSMContext):
    if not _is_admin(message):
        return
    async with state.proxy() as data:
        data["deposit"] = message.text
    await AddGame.next()
    await bot.send_message(message.chat.id, "🏞 Завантажте фото гри")


@dp.message_handler(content_types=["photo"], state=AddGame.photo)
async def adm_load_photo(message: types.Message, state: FSMContext):
    if not _is_admin(message):
        return
    global _pending_game
    async with state.proxy() as data:
        data["photo"] = message.photo[-1].file_id  # беремо найбільшу версію
        _pending_game = dict(data)
        await bot.send_message(
            message.chat.id,
            f"📋 Введена інформація:\n\n"
            f"Назва: {data['name']}\n"
            f"Ціна за день: {data['day_price']}\n"
            f"Ціна за тиждень: {data['week_price']}\n"
            f"Застава: {data['deposit']}",
            reply_markup=sub_res_markup,
        )
    await state.finish()


@dp.message_handler(lambda m: "✅ Додати" in m.text)
async def adm_confirm_add(message: types.Message):
    if not _is_admin(message):
        return
    global _pending_game
    if not _pending_game:
        await bot.send_message(message.chat.id, "🔴 Спочатку введіть дані нової гри")
        return
    sql_start()
    await add_game(
        _pending_game["name"],
        _pending_game["day_price"],
        _pending_game["week_price"],
        _pending_game["deposit"],
        _pending_game["photo"],
    )
    _pending_game = {}
    await bot.send_message(message.chat.id, "🟢 Гру додано до бази даних", reply_markup=admin_markup)


@dp.message_handler(lambda m: "🗯 Скинути" in m.text)
async def adm_reset(message: types.Message):
    if not _is_admin(message):
        return
    global _pending_game
    _pending_game = {}
    await bot.send_message(message.chat.id, "📂 Зміни скинуто", reply_markup=admin_markup)


# ── Видалити гру ─────────────────────────────────────────────────────────────
@dp.message_handler(lambda m: "💥 Видалити гру" in m.text)
async def adm_delete_start(message: types.Message):
    if not _is_admin(message):
        return
    await DeleteGame.game_name_del.set()
    await bot.send_message(message.chat.id, "⌨️ Введіть назву гри, яку потрібно видалити")


@dp.message_handler(state=DeleteGame.game_name_del)
async def adm_delete_confirm(message: types.Message, state: FSMContext):
    if not _is_admin(message):
        return
    game_name = message.text
    sql_start()
    await del_game(game_name)
    await bot.send_message(message.chat.id, f"☄️ Гру '{game_name}' видалено з бази даних", reply_markup=admin_markup)
    await state.finish()


# ── Повернути гру в наявність ─────────────────────────────────────────────────
@dp.message_handler(lambda m: "📪 Повернути в наявність" in m.text)
async def adm_set_available_start(message: types.Message):
    if not _is_admin(message):
        return
    await SetAvailable.game_name.set()
    await bot.send_message(message.chat.id, "🏷 Введіть назву гри для повернення в наявність")


@dp.message_handler(state=SetAvailable.game_name)
async def adm_set_available(message: types.Message, state: FSMContext):
    if not _is_admin(message):
        return
    game_name = message.text
    sql_start()
    add_value(game_name, 1)
    await bot.send_message(message.chat.id, f"🎉 Гру '{game_name}' повернено в наявність!", reply_markup=admin_markup)
    await state.finish()
