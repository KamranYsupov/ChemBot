import asyncio
import os
import logging
import pathlib
from datetime import datetime
import time
import pathlib
import tomllib

from aerich import Command

import yaml
from redis.asyncio import Redis
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from tortoise import Tortoise
from shortuuid import ShortUUID
from bitrix24 import Bitrix24

from tbank_kassa_api.tbank_client import TClient


BASE_DIR = pathlib.Path(__file__).resolve(strict=True).parent

DEBUG = int(os.environ.get('DEBUG', 0))
CONFIGURE_FILES_DIR = 'files_configure'

MEDIA_DIR = os.environ.get('MEDIA_FILES')
SETTINGS_FROM = os.environ.get('SETTINGS_FROM')
PAY_TOKEN = os.environ.get('PAY_TOKEN')
BITRIX_OUT = Bitrix24(os.environ.get("BITRIX_OUT"))

shortnuberic = ShortUUID("0123456789")
shortdefault = ShortUUID()

try:
    logging.basicConfig(level=logging.INFO,
                        filename=BASE_DIR / f'loggs/devlog{datetime.now().strftime("%d-%m-%Y")}.log',filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")
except FileNotFoundError:
    os.makedirs("loggs/")
    logging.basicConfig(level=logging.INFO,
                        filename= BASE_DIR / f'loggs/devlog{datetime.now().strftime("%d-%m-%Y")}.log', filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")


DB_ENGINE = os.environ.get('DB_ENGINE')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')

database_link = ''

if DB_ENGINE == "sqlite":
    database_link = f"{DB_ENGINE}://{DB_NAME}"

else:
    database_link = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

CONFIG_TYPE = os.environ.get('CONFIG_TYPE')
config = {}
ways_list = []
CONFIG_FILE_PATH = os.path.join(CONFIGURE_FILES_DIR, f'config.{CONFIG_TYPE.lower()}')
with open(CONFIG_FILE_PATH, 'r') as file:
    if CONFIG_TYPE.lower() == 'yaml':
        config = yaml.load(file, Loader=yaml.SafeLoader)
    if CONFIG_TYPE.lower() == "toml":
        config = tomllib.loads(file.read())
    
    try:
        bitrix = config.get("bitrix")
        user_fields = bitrix.get("user_fields")
        bitrix_user_deal_fields = BITRIX_OUT.callMethod('crm.deal.userfield.list')
        exist_fields = []
        if bitrix_user_deal_fields:
            for field_deal in bitrix_user_deal_fields:
                row_field_name = field_deal.get("FIELD_NAME")
                field_name = row_field_name.replace(bitrix.get("user_fields_prefix"), "")
                if field_name in user_fields:
                    exist_fields.append(field_name)
                    continue
                else:
                    user_field_data = bitrix.get(field_name)
                    if not user_field_data:
                        continue      
        
        for field in user_fields:
            if field in exist_fields:
                continue

            user_field_data = bitrix.get(field)
            if not user_field_data:
                continue
            try:
                BITRIX_OUT.callMethod('crm.deal.userfield.add', fields=user_field_data)
            except Exception as ex:
                logging.error(ex)
    except Exception:
        pass



bot = Bot(token=os.environ.get('TELEGRAM_TOKEN'))
dispatcher = Dispatcher()

tortoise = Tortoise()

TORTOISE_CONFIG = {
    'connections': {
        'default': {
            "connections": {"default": f"{database_link}"},
        },
    },
    'apps': {
        'models': {
            'models': ['models'],
            'default_connection': 'default',
        },
    },
}

aerich_client = Command(
    tortoise_config=TORTOISE_CONFIG,
    app="models",
    location="migrations",
)

client_redis = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))

SITE_HOST = os.environ.get('SITE_HOST')

TBANK_TERMINAL_ID = os.environ.get("TBANK_TERMINAL_ID")
TBANK_TERMINAL_PASSWORD = os.environ.get("TBANK_TERMINAL_PASSWORD")
TBANK_CLIENT = None

try:
    TBANK_CLIENT = TClient(TBANK_TERMINAL_ID, TBANK_TERMINAL_PASSWORD)
except Exception as ex:
    print(ex)


