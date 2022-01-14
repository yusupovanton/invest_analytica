from aiogram import executor
from dispatcher import dp
import asyncio
import aioschedule as schedule
from handlers.personal_actions import *


async def scheduler():

    with open('user_list.txt', 'r') as file:
        user_list = file.readlines()

    for user_id in user_list:
        schedule.every().day.at('19:13').do(news_send, user_id)

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)
        print('ahahhahah')


async def on_startup(_):
    asyncio.create_task(scheduler())
    print("tratata")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
