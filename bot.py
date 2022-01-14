from aiogram import executor
from dispatcher import dp
import asyncio
import aioschedule as schedule
from handlers.personal_actions import *


async def news_send(user_id):

    with open(f"userOptions/user_options{user_id.rstrip()}.txt", 'r') as file:
        file.seek(0)
        ticker_set = ast.literal_eval(file.read())

    for item in ticker_set:
        total_list_to_send = []
        today = datetime.today().strftime('%Y-%m-%d')
        news = get_company_news(ticker=item, fromdate=today, todate=today)

        if news:
            if len(news) > 5:
                news = news[0:5]
            for i in news:
                headline = str(i['headline'])
                url = str(i['url'])
                text = f'<a href="{url}">{headline.split(" ", 1)[0]}</a> {headline.split(" ", 1)[1]}'
                total_list_to_send.append(text)
            for j in total_list_to_send:
                await bot.send_message(chat_id=user_id, text=j, parse_mode='HTML', disable_web_page_preview=True)
        else:
            print('No news!')


async def scheduler():

    with open('user_list.txt', 'r') as file:
        user_set = ast.literal_eval(file.read())

    for user_id in user_set:
        with open(f'userOptions/{user_id.strip()}/user_time.txt') as time_file:
            time = time_file.read()

        schedule.every().day.at(time).do(news_send, user_id)

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):

    await asyncio.create_task(scheduler())


if __name__ == '__main__':

    executor.start_polling(dp, skip_updates=True)
