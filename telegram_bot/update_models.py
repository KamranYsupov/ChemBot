import asyncio

from init_unit import (
    BASE_DIR,
    dispatcher, bot, tortoise, config, 
    SETTINGS_FROM, database_link, 
    client_redis, aerich_client,
    DEBUG
    )
from programming_elements.classes import return_ways_models
from routes.menu import menu_router


async def database_init():
    await tortoise.init(
        db_url=database_link,
        modules={"models": ["models"]}
    )
    result = await aerich_client.inspectdb()
    with open(BASE_DIR/"models.py", "w") as f:
        f.write(result)


async def main():
    await database_init()

if __name__ == "__main__":
    asyncio.run(main())