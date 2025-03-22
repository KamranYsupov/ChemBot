from typing import Optional
from aiogram import types
import pathlib
from services.logger import log_debug, log_error

from init_unit import MEDIA_DIR, DEBUG
try:
    from models import BotMessages
except Exception as ex:
    log_error("Error message_builder import BotMessages")
    if DEBUG:
        pass
    else:
        raise ImportError()
from programming_elements.enums import MessagesBuildType


async def message_builder(message_field: str, image_field: str, video_field: Optional[str], model, 
                         first = True, by_field = None, media_by_id=False):
    bot_message = None
    if first and not by_field:
        bot_message = await model.first()
    elif by_field and not first:
       bot_message = await model.get(**by_field)
    else:
        raise ValueError("Either by_id or first should be True")

    if bot_message.__dict__[image_field] and (video_field and bot_message.__dict__.get(video_field, None)) and not media_by_id:
        list_media_group = [types.InputMediaPhoto(media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / bot_message.__dict__[image_field], caption=bot_message.__dict__[message_field]),),
                            types.InputMediaVideo(media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / bot_message.__dict__[video_field]))]
        return list_media_group
    elif bot_message.__dict__[image_field] and not media_by_id:
        return types.InputMediaPhoto(media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / bot_message.__dict__[image_field]), 
                            caption=bot_message.__dict__[message_field])
                            
    elif video_field and bot_message.__dict__.get(video_field, None) and not media_by_id:
        return types.InputMediaVideo(media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / bot_message.__dict__[video_field]), 
                                    caption=bot_message.__dict__[message_field])

    elif bot_message.__dict__[image_field] and media_by_id:
        return types.InputMediaPhoto(media=bot_message.__dict__[image_field], 
                                    caption=bot_message.__dict__[message_field])

    elif video_field and bot_message.__dict__.get(video_field, None) and media_by_id:
        return types.InputMediaVideo(media=bot_message.__dict__[video_field], 
                                    caption=bot_message.__dict__[message_field])
    else:
        return bot_message.__dict__[message_field]


async def union_message_builder(message_type: MessagesBuildType, model, first=True, by_field=None):
    data = message_type.value
    bot_message = await message_builder(data[0], data[1], data[2], model=model, first=first, by_field=by_field)
    return bot_message 