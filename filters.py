from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
import config
from typing import List, Union
from main import *

class IsOwnerFilter(BoundFilter):
    """
    Custom filter "is_owner".
    """
    key = "is_owner"

    def __init__(self, is_owner):
        self.is_owner = is_owner

    async def check(self, message: types.Message):
        return message.from_user.id == config.BOT_OWNER


class IsIncluded(BoundFilter):
    """
    Custom filter "is_owner".
    """
    key = "is_included"

    def __init__(self, is_included: bool):
        self.is_included = is_included

    async def check(self, message: types.Message):
        return message.from_user.id in config.INCLUDED


class IsAdminFilter(BoundFilter):
    """
    Filter that checks for admin rights existence
    """
    key = "is_admin"

    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin() == self.is_admin


class MemberCanRestrictFilter(BoundFilter):
    """
    Filter that checks member ability for restricting
    """
    key = 'member_can_restrict'

    def __init__(self, member_can_restrict: bool):
        self.member_can_restrict = member_can_restrict

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)

        # I don't know why, but telegram thinks, if member is chat creator, he cant restrict member
        return (member.is_chat_creator() or member.can_restrict_members) == self.member_can_restrict


class FoundOnStockFilter(BoundFilter):
    """
    Checking for the number of characters in a message/callback_data
    """

    key = "found"

    def __init__(self, found):
        if isinstance(found, bool):
            self.bool_ = found
        else:
            raise ValueError(
                f"filter letters must be a boolean, not {type(found).__name__}"
            )

    async def check(self, message: types.Message):
        data = message.text
        if data:
            output = symbol_lookup(data)
            records_found = output['count']
            if records_found < 1:
                return {'count': records_found}
            return False
        return False
