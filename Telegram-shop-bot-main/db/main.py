from create_bot import dp
from aiogram import executor

from admin import admin_panel  # noqa: F401  — реєструє хендлери
import bot  # noqa: F401  — реєструє хендлери

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
