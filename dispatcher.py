import logging
from aiogram import Bot, Dispatcher, types, executor
from config import API_TOKEN
from filters import IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter, FoundOnStockFilter, IsIncluded
from aiogram.contrib.fsm_storage.memory import MemoryStorage


'''Logging'''

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')

'''BOT'''

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

dp.filters_factory.bind(IsIncluded)
dp.filters_factory.bind(FoundOnStockFilter)
