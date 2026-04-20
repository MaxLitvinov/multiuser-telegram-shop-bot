from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

TOKEN = ""  # Вставте сюди токен бота
ADMIN_CHAT_ID = ""  # ID чату адміна для отримання замовлень

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
