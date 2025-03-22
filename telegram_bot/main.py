import asyncio

from aiogram.types import BotCommand
import loguru
from init_unit import (
    BASE_DIR,
    dispatcher, bot, tortoise, config, 
    SETTINGS_FROM, database_link, 
    client_redis, aerich_client,
    DEBUG
    )
from programming_elements.classes import return_ways_models
from routes.menu import menu_router
from services import notification, logger
try:
    from models import BotMessages, BotButtons
except ImportError:
    logger.log_info("Error import models for main.py")
    if DEBUG:
        pass
    else:
        raise ImportError()

async def database_init():
    await tortoise.init(
        db_url=database_link,
        modules={"models": ["models"]}
    )
    result = await aerich_client.inspectdb()
    with open(BASE_DIR/"models.py", "w") as f:
        f.write(result)


async def close_database():
    await tortoise.close_connections()
    await client_redis.aclose()

async def main():

    bot_settings = config.get("bot_settings")
    if SETTINGS_FROM == "DB":

        await database_init()
        #add rows on database if they don't exist

        messages_config = config.get("messages")
        for message in messages_config.get("messages_list"):
            try:
                bot_message = await BotMessages.get_or_none(message_name = message)
            except Exception as ex:
                logger.log_error(ex)
                if DEBUG:
                    logger.log_info("MENU.PY: RESTART PROGRAMM")
                    raise Exception("MENU.PY: RESTART PROGRAMM")
                else:
                    raise ex
            if bot_message:
                continue
            message_data = messages_config.get(message)
            video = None
            image = None
            if message_data.get("video"):
                video = message_data.get("video")
            if message_data.get("image"):
                image = message_data.get("image")
            config_message = {
                        "message_name": message,
                        "display_name": message_data.get("display_name"),
                        "text": message_data.get("text"), 
                        "video": video, "image": image
                    }
            if bot_message is None:
                await BotMessages.create(**config_message)
            
        
        buttons_config = config.get("buttons")
        for button in buttons_config.get("button_list"):
            button_key = button
            

            button_config = None
            for validate in ["__contact", "__location"]:
                if validate in button:
                    button_key = button.split("__")[-1]
            bot_button = await BotButtons.get_or_none(button_name = button_key)
            if bot_button:
                continue
            button_config = buttons_config[button]
            
            if bot_button is None:
                await BotButtons.create(button_name = button_key, **button_config)

        await return_ways_models(BotMessages, BotButtons)

        await bot.set_my_commands(
            commands=[
                BotCommand(command="start", description="Перейти в начало"),
            ]
        )

    dispatcher.include_router(menu_router)
    notify_task = asyncio.create_task(notification.send_notification())
    dispatcher_task = asyncio.create_task(dispatcher.start_polling(bot))
    loguru.logger.info("Телеграмм бот запущен")
    await asyncio.gather(dispatcher_task, notify_task)
    await close_database()

if __name__ == "__main__":
    asyncio.run(main())


