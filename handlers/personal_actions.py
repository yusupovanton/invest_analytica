import asyncio
import logging
from datetime import datetime

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from main import *

from config import API_TOKEN
logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    choice_command = State()  # Will be represented in storage as 'Form:choice_command'
    get_financials = State()
    ticker_lookup = State()
    all_companies = State()
    set_options = State()


buttons_text_menu_options = ('Получить базовые финансовые показатели компании', 'Получить список компаний',
                             'Найти тикер по названию компании', 'Задать опции')
keyboard_markup_menu_options = types.ReplyKeyboardMarkup(row_width=3)
keyboard_markup_menu_options.row(*(types.KeyboardButton(text) for text in buttons_text_menu_options))

buttons_text_go_back = ('Вернуться в меню', 'Стоп')
keyboard_markup_go_back = types.ReplyKeyboardMarkup(row_width=2)
keyboard_markup_go_back.row(*(types.KeyboardButton(text) for text in buttons_text_go_back))

buttons_text_go_back2 = ('Вернуться в меню', 'Стоп', 'Я не знаю названия биржи')
keyboard_markup_go_back2 = types.ReplyKeyboardMarkup(row_width=3)
keyboard_markup_go_back2.row(*(types.KeyboardButton(text) for text in buttons_text_go_back2))


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):

    await Form.choice_command.set()

    await message.reply("Привет! Какую информацию ты хотел бы получить?",
                        reply_markup=keyboard_markup_menu_options,
                        reply=False)


@dp.message_handler(state='*', commands='stop')
@dp.message_handler(Text(equals='Стоп', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
 Allow user to cancel any action
 """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()

    await message.reply('Пойду отдохну! Для повторного запуска бота отправьте команду \n/start',
                        reply_markup=types.ReplyKeyboardRemove(),
                        reply=False)


@dp.message_handler(state='*', commands='menu')
@dp.message_handler(Text(equals='Вернуться в меню', ignore_case=True), state='*')
async def back_to_menu_handler(message: types.Message, state: FSMContext):
    """
 Allow user to go back to menu
 """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Going back to menu %r', current_state)

    await Form.choice_command.set()
    await message.reply("Привет! Какую информацию ты хотел бы получить?",
                        reply_markup=keyboard_markup_menu_options,
                        reply=False)


@dp.message_handler(Text(equals='Получить список компаний', ignore_case=True), state=Form.choice_command)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process chosen command
    """
    await Form.all_companies.set()

    await message.reply("Введите название биржи, например, МЕ",
                        reply_markup=keyboard_markup_go_back2,
                        reply=False)


@dp.message_handler(Text(equals='Я не знаю названия биржи', ignore_case=True), state=Form.all_companies)
async def process_name(message: types.Message, state: FSMContext):

    await message.reply("Вот список доступных бирж и соотвествующих кодов \n<a href='https://docs.google.com/"
                        "spreadsheets/d/1I3pBxjfXB056-g_JYf_6o3Rns3BV2kMGG1nCatb91ls/"
                        "edit#gid=0'>A list of supported exchange codes</a>",
                        reply_markup=keyboard_markup_go_back,
                        parse_mode='html',
                        reply=False)
    await message.reply("Введите название биржи, например, МЕ",
                        reply_markup=keyboard_markup_go_back,
                        reply=False)
    print(get_basic_financials(message.text)[0])


@dp.message_handler(state=Form.all_companies)
async def process_name(message: types.Message, state: FSMContext):
    file_name = get_available_stocks(message.text)
    if file_name:
        with open(file_name, 'rb') as document:
            await message.reply_document(document,
                                         reply_markup=keyboard_markup_go_back,
                                         reply=False)
    else:
        await message.reply("Такой биржи не найдено",
                            reply_markup=keyboard_markup_go_back,
                            reply=False)


@dp.message_handler(Text(equals='Получить базовые финансовые показатели компании', ignore_case=True),
                    state=Form.choice_command)
async def process_name(message: types.Message):

    await Form.get_financials.set()

    await message.reply("Введите тикер",
                        reply_markup=keyboard_markup_go_back,
                        reply=False)
    print(get_basic_financials(message.text)[0])


# Check age. Age gotta be digit
@dp.message_handler(lambda message: not get_basic_financials(message.text), state=Form.get_financials)
async def process_ticker_invalid(message: types.Message):

    add_se_name = str(message.text) + '.ME'

    file_name = get_basic_financials(add_se_name)
    if file_name:
        with open(file_name, 'rb') as document:
            await message.reply_document(document)
            await message.reply("Вот ваш файл! Введите еще один тикер?..",
                                reply_markup=keyboard_markup_go_back,
                                reply=False)
    else:
        return await message.reply("Тикер или компания не в нашем списке (пока что) :(\nНе забыли указывать биржу "
                                   "(.ME)?..",
                                   reply_markup=keyboard_markup_go_back,
                                   reply=False)


@dp.message_handler(lambda message: get_basic_financials(message.text)[0], state=Form.get_financials)
async def process_ticker(message: types.Message, state: FSMContext):

    file_name = get_basic_financials(message.text)[1]

    with open(file_name, 'rb') as document:
        await message.reply_document(document)
        await message.reply("Вот ваш файл! Введите еще один тикер?..",
                            reply_markup=keyboard_markup_go_back,
                            reply=False)


@dp.message_handler(Text(equals='Найти тикер по названию компании', ignore_case=True),
                    state=Form.choice_command)
async def lookup_ticker(message: types.Message, state: FSMContext):

    await Form.ticker_lookup.set()

    await message.reply('Введите название компании, например, "apple"',
                        reply_markup=keyboard_markup_go_back,
                        reply=False)


@dp.message_handler(state=Form.ticker_lookup)
async def lookup_ticker_name(message: types.Message, state: FSMContext):

    df_file_name = symbol_lookup(message.text)
    if not df_file_name:
        await message.reply('Нет такой компании (по крайней мере мы так думаем)... Попробуйте еще раз '
                            'или посмотрите в общем реестре компаний',
                            reply_markup=keyboard_markup_go_back,
                            reply=False)
    else:
        with open(df_file_name[1], 'rb') as document:
            await message.reply_document(document)
            await message.reply("Вот список ! Введите еще один тикер?..",
                                reply_markup=keyboard_markup_go_back,
                                reply=False)


@dp.message_handler(Text(equals='Задать опции', ignore_case=True),
                    state=Form.choice_command)
async def lookup_ticker(message: types.Message, state: FSMContext):

    await Form.set_options.set()

    await message.reply('Введите список тикеров компаний на которые вы хотели бы подписаться. Ввод тикеров следует '
                        'осуществить через пробел. Пример:  AAPL GAZP.ME SBER.ME\nПравильный формат тикеров'
                        'можно узнать запросив список тикеров или выполнив поиск по названию компаний через бота.',
                        reply_markup=keyboard_markup_go_back,
                        reply=False)


@dp.message_handler(state=Form.set_options)
async def process_options(message: types.Message, state: FSMContext):
    options_set = set()
    user_id = message.chat.id
    tickers_set = message.text.split(' ')
    for item in tickers_set:
        try:
            options_set.add(item)
        except Exception as ex:
            print(ex)

    with open(f'user_list.txt', 'w+') as user_list_file:
        user_list_file.write(f'{user_id}\n')

    with open(f'userOptions/user_options{user_id}.txt', 'w') as options_file:
        options_file.write(f'{options_set}\n')
