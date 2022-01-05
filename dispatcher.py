import logging
from aiogram import Bot, Dispatcher, types, executor
from config import API_TOKEN
from filters import IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter, FoundOnStockFilter, IsIncluded

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)

dp.filters_factory.bind(IsIncluded)
dp.filters_factory.bind(FoundOnStockFilter)
