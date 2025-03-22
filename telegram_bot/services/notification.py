import datetime
import asyncio

from aiogram import types
from tortoise.expressions import Q

from init_unit import bot, DEBUG
from bot_elements.messages_builder import message_builder
from services import logger
try:
    from models import TelegramUsers, Mailings
except ImportError as ex:
    logger.log_error("Error import models in notifications.py")
    if DEBUG:
        pass
    else:
        raise ImportError()



async def send_message(telegram_id, message_data):
    message = None
    if isinstance(message_data, str):
        try:
            message = await bot.send_message(chat_id=telegram_id, text=message_data)
        except Exception as ex:
            logger.log_error(ex)
    elif isinstance(message_data, list):
        try:
            await bot.send_media_group(chat_id=input.from_user.id, media=message_data)
        except Exception:
            logger.log_error(ex)
    elif isinstance(message_data, types.InputMediaPhoto):
        try:
            message = await bot.send_photo(chat_id=input.from_user.id, photo=message_data.media, 
                                            caption=message_data.caption)
        except Exception:
            logger.log_error(ex)
    elif isinstance(message_data, types.InputMediaVideo):
        try:
            await bot.send_video(chat_id=input.from_user.id, video=message_data.media, caption=message_data.caption)
        except Exception as ex:
            logger.log_error(ex)
                    
    return message


async def send_notification():
    while True:
        timezone = datetime.timezone(datetime.timedelta(hours=3))
        date_now = datetime.datetime.now(tz=timezone)
        date = date_now.date()
        time = date_now.time().replace(tzinfo=datetime.timezone.utc)
        mails = await Mailings.filter(Q(mail_date__lte=date) & Q(it_send=False))
        users = await TelegramUsers.filter(subscription=True)
        for mail in mails:
            try:
                if time < mail.mail_time and date == mail.mail_date:
                    continue
            except Exception as ex:
                logger.log_error(ex)
            mail.it_send = True
            try:
                await mail.save()
            except Exception as ex:
                logger.log_error(ex)
            message = await message_builder(message_field="content", image_field="image", video_field="video", model=Mailings, first=False, by_field={"id": mail.id})
            for i, user in enumerate(users, 1):
                try:
                    await send_message(telegram_id=user.telegram_id, message_data=message)
                except Exception:
                    logger.log_error(ex)
                if i % 25 == 0:
                    await asyncio.sleep(300)
        
        await asyncio.sleep(300)