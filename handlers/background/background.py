from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ChatJoinRequest, ChatMemberUpdated
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, MEMBER, KICKED

from database.db import Database
from filters.is_channel_auth import IsChannelAdded

from aiogram.filters.chat_member_updated import \
    ChatMemberUpdated, JOIN_TRANSITION

background = Router()


@background.chat_join_request(IsChannelAdded())
async def join_requests_processor(
        request: ChatJoinRequest
):
    db = Database()
    if not db.is_requested(request.chat.id, request.from_user.id):
        db.register_join_request(request)


@background.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated):
    db = Database()
    db.delete_user(event.from_user.id)


@background.chat_member(
    IsChannelAdded(),
    ChatMemberUpdatedFilter(JOIN_TRANSITION),
    F.chat.type == 'channel'
)
async def new_chat_member(event: ChatMemberUpdated):
    db = Database()
    db.delete_request(
        user_id=event.new_chat_member.user.id,
        channel_id=event.chat.id
    )
