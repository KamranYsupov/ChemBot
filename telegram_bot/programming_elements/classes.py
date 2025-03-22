import asyncio
import pathlib
import decimal

from aiogram import types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from init_unit import MEDIA_DIR, SETTINGS_FROM, config
from bot_elements.callback import MenuCallBack
from programming_elements.enums import MenuWays
from services.get_config import get_config, get_ways



class MessageBuilder():
    def __init__(self, text, image = False, video = False):
        self.text = text
        self.image = image if image else None
        self.video = video if video else None
        self.message_data = None


    def return_telegram_message(self):
        self.message_data
        if self.message_data is None:
            if self.image and self.video:
                list_media_group = [types.InputMediaPhoto(media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / self.image, 
                                    caption=bot_message.__dict__[message_field]),), 
                                    types.InputMediaVideo(media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / self.video))]
                self.message_data = list_media_group
            elif self.image:
                return types.InputMediaPhoto(media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / self.image), 
                                    caption=self.text)
            elif self.video:
                self.message_data = types.InputMediaVideo(media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / self.video), caption=self.text)
            else:
                self.message_data = self.text
        
        return self.message_data

class KeyboardBuilder():
    def __init__(self, buttons, keyboard_type, ways: list | None = None, db_model = None):
        self.buttons = buttons
        self.keyboard_type = keyboard_type
        self.ways = ways
        self.keyboard = None
        self.db_model = db_model


    async def return_telegram_keyboard(self):

        local_keyboard = self.keyboard
        buttons_config = None
        bot_settings = config.get("bot_settings")
        if SETTINGS_FROM == "CONFIG":
            buttons_config = config["buttons"]
            
        if local_keyboard is None:

            if self.keyboard_type == "inline":
                local_keyboard = InlineKeyboardBuilder()
            elif self.keyboard_type == "reply":
                local_keyboard = ReplyKeyboardBuilder()
            
            for i, button in enumerate(self.buttons, 0):
                button_key = button
                for validate in ["__contact", "__location"]:
                    if validate in button and self.keyboard_type == "inline":
                        raise ValueError("Inline keyboard can't have contact or location buttons")

                    if validate in button and self.keyboard_type == "reply":
                        button_key = button.split("__")[-1]
                    
                if self.ways and self.keyboard_type == "reply":
                    raise ValueError("Reply keyboard can't have ways")
                button_text = ""

                if SETTINGS_FROM == "CONFIG":
                    if bot_settings.get("config_type") == "BIG":
                        button_text = buttons_config[button].get("text")
                    elif bot_settings.get("config_type") == "SMALL":
                        button_text = buttons_config[button]
                elif SETTINGS_FROM == "DB":
                    button_config = await self.db_model.get_or_none(button_name=button_key)
                    if not button_config:
                        assert KeyError(f"{button} not found in config file")
                    
                    button_text = button_config.text

                if self.keyboard_type == "inline":
                    local_keyboard.add(InlineKeyboardButton(text=button_text, callback_data=MenuCallBack(to=self.ways[i]).pack()))
                elif self.keyboard_type == "reply":
                    request_contact = True if "__contact" in button else False
                    local_keyboard.add(KeyboardButton(text=button_text, request_contact=request_contact))
                    
            local_keyboard.adjust(1)
            self.keyboard = local_keyboard.as_markup()

        return self.keyboard


class Way():
    def __init__(self, message, set_state, work_state, keyboard: bool | dict = False, way_callback: str | None = None, 
                 callback_only: bool = False, custom_keyboard: bool = False, *args, **kvargs):
        self.message = MessageBuilder(**message) if message else ""
        if not custom_keyboard:
            self.keyboard = KeyboardBuilder(**keyboard) if keyboard else None
        else:
            self.keyboard = None
        self.set_state = set_state
        self.work_state = work_state if work_state else None
        self.way_callback = way_callback if way_callback else None
        self.callback_only = callback_only


async def return_ways_models(message_model, button_model, config=get_config()):
    ways_models = []
    bot_messages = []
    
    for way in get_ways(config):
        message_row = way.get("message")
        if SETTINGS_FROM == "DB" and not isinstance(message_row, dict):
            if way['keyboard']:
                way["keyboard"]["db_model"] = button_model
            message = await message_model.get_or_none(message_name=message_row)
            
            message_data = {
                            "text": message.text, 
                            "image": message.image, 
                            "video": message.video
                            }
            way["message"] = message_data

        ways_models.append(Way(**way))
    return ways_models 