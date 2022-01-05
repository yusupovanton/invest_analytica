from aiogram import types
from aiogram.dispatcher.webhook import SendDocument

from dispatcher import dp
import config
from main import *
from aiogram.types import InputFile


@dp.message_handler(text='список')
async def text_in_handler(message: types.Message):
    file_name = get_available_stocks('ME')
    await message.answer("Успешно. Вот список компаний на Москвоской Бирже:")

    with open(file_name, 'rb') as file:
        await message.answer_document(file)


@dp.message_handler(found=True)
async def handle_found_on_stocks(message: types.Message, count: int):
    await message.answer(F"The ticker is not found! There are {count} records found on this ticker!")


@dp.message_handler()
async def basic_metrics_search(message: types.Message):

    file_name = get_basic_financials(message.text)
    if file_name:
        await message.answer(f"Хорошо. Сейчас предоставим данные по компании ({message.text}...)")
        with open(file_name, 'rb') as file:
            await message.answer_document(file)
    else:
        file_name = get_basic_financials(f'{message.text}.ME')
        if file_name:
            await message.answer(f"Хорошо. Сейчас предоставим данные по компании ({message.text}...)")
            with open(file_name, 'rb') as file:
                await message.answer_document(file)
        else:
            await message.answer(f"Мы не нашли данных по компании ({message.text}). Приносим извинения.")
            df = symbol_lookup(message.text)
            await message.answer(f"Вот результаты поиска по названию:")
            await message.answer(f"{df}")


