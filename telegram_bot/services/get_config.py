import tomllib
from init_unit import CONFIG_TYPE, CONFIG_FILE_PATH, DEBUG, SETTINGS_FROM
from services import logger


def get_config():
    config = {}
    with open(CONFIG_FILE_PATH, 'r') as file:
        if CONFIG_TYPE.lower() == 'yaml':
            config = yaml.load(file, Loader=yaml.SafeLoader)
        if CONFIG_TYPE.lower() == "toml":
            config = tomllib.loads(file.read())
    return config


def get_ways(config):
    ways_list = []
    messages_config = config.get("messages")
    ways_config = config.get("ways")
    keyboards_config = config.get("keyboards")
    ways = ways_config.get("ways")
    for way in ways:
        local_way = ways_config.get(way)
        if not local_way:
            if DEBUG:
                logger.log_error(f"{way} not found in config file!")
                continue
            else:
                logger.log_error(f"{way} not found in config file!")
                assert KeyError(f"{way} not found in config file")
        if SETTINGS_FROM == "CONFIG":
            message = messages_config.get(local_way.get("message"))
        elif SETTINGS_FROM == "DB":
            message = local_way.get("message")
        
        keyboard = keyboards_config.get(local_way.get("keyboard"))
        ways_list.append({"message": message, "keyboard": keyboard, 
                        "set_state": local_way.get("set_state"), "work_state": local_way.get("work_state"), 
                        "way_callback": local_way.get("way_callback"), "callback_only": local_way.get("callback_only", False), 
                        "custom_keyboard": local_way.get("custom_keyboard", False)})
    return ways_list