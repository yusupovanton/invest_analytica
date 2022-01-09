from aiogram import executor
from dispatcher import dp

from handlers.personal_actions import *

if __name__ == '__main__':

    executor.start_polling(dp, skip_updates=True)
