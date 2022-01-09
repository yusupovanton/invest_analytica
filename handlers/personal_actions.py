import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
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


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    """
 Conversation's entry point
 """
    # Set state

    keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
    btns_text = ('Получить базовые финансовые показатели компании', 'Получить список компаний')
    keyboard_markup.row(*(types.KeyboardButton(text) for text in btns_text))

    await Form.choice_command.set()

    await message.reply("Привет! Какую информацию ты хотел бы получить?",
                        reply_markup=keyboard_markup,
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
    # And remove keyboard (just in case)
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
    # Cancel state and inform user about it

    keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
    btns_text = ('Получить базовые финансовые показатели компании', 'Получить список компаний')
    keyboard_markup.row(*(types.KeyboardButton(text) for text in btns_text))

    await Form.choice_command.set()

    await message.reply("Привет! Какую информацию ты хотел бы получить?",
                        reply_markup=keyboard_markup,
                        reply=False)


@dp.message_handler(Text(equals='Получить список компаний', ignore_case=True), state=Form.choice_command)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process chosen command
    """
    await Form.all_companies.set()

    keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
    btns_text = ('Вернуться в меню', 'Стоп', 'Я не знаю названия биржи')
    keyboard_markup.row(*(types.KeyboardButton(text) for text in btns_text))

    await message.reply("Введите название биржи, например, МЕ",
                        reply_markup=keyboard_markup,
                        reply=False)


@dp.message_handler(Text(equals='Я не знаю названия биржи', ignore_case=True), state=Form.all_companies)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process chosen command
    """

    keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
    btns_text = ('Вернуться в меню', 'Стоп')
    keyboard_markup.row(*(types.KeyboardButton(text) for text in btns_text))
    await message.reply("Вот список доступных бирж и соотвествующих кодов \n<a href='https://docs.google.com/"
                        "spreadsheets/d/1I3pBxjfXB056-g_JYf_6o3Rns3BV2kMGG1nCatb91ls/"
                        "edit#gid=0'>A list of supported exchange codes</a>",
                        reply_markup=keyboard_markup,
                        parse_mode='html',
                        reply=False)
    await message.reply("Введите название биржи, например, МЕ",
                        reply_markup=keyboard_markup,
                        reply=False)
    print(get_basic_financials(message.text)[0])


@dp.message_handler(state=Form.all_companies)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process chosen command
    """

    keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
    btns_text = ('Вернуться в меню', 'Стоп')
    keyboard_markup.row(*(types.KeyboardButton(text) for text in btns_text))
    file_name = get_available_stocks(message.text)
    if file_name:
        with open(file_name, 'rb') as document:
            await message.reply_document(document,
                                         reply_markup=keyboard_markup,
                                         reply=False)
    else:
        await message.reply("Такой биржи не найдено",
                            reply_markup=keyboard_markup,
                            reply=False)


@dp.message_handler(Text(equals='Получить базовые финансовые показатели компании', ignore_case=True),
                    state=Form.choice_command)
async def process_name(message: types.Message, state: FSMContext):

    await Form.get_financials.set()

    keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
    btns_text = ('Вернуться в меню', 'Стоп')
    keyboard_markup.row(*(types.KeyboardButton(text) for text in btns_text))

    await message.reply("Введите тикер",
                        reply_markup=keyboard_markup,
                        reply=False)
    print(get_basic_financials(message.text)[0])


# Check age. Age gotta be digit
@dp.message_handler(lambda message: not get_basic_financials(message.text), state=Form.get_financials)
async def process_ticker_invalid(message: types.Message):
    """
    If age is invalid
    """
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
    btns_text = ('Вернуться в меню', 'Стоп')
    keyboard_markup.row(*(types.KeyboardButton(text) for text in btns_text))

    return await message.reply("Тикер или компания не в нашем списке (пока что) :(\nНе забывайте указывать биржу (.ME)"
                               "?..",
                               reply_markup=keyboard_markup,
                               reply=False)


@dp.message_handler(lambda message: get_basic_financials(message.text)[0], state=Form.get_financials)
async def process_ticker(message: types.Message, state: FSMContext):
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
    btns_text = ('Вернуться в меню', 'Стоп')
    keyboard_markup.row(*(types.KeyboardButton(text) for text in btns_text))

    file_name = get_basic_financials(message.text)[1]

    with open(file_name, 'rb') as document:
        await message.reply_document(document)
        await message.reply("Вот ваш файл! Введите еще один тикер?..",
                            reply_markup=keyboard_markup,
                            reply=False)

