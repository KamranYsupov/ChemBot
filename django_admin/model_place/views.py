from decimal import Decimal
import logging
import json
import uuid
from enum import Enum

from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from urllib.parse import urlparse, parse_qs

from bitrix24 import Bitrix24
from tbank_kassa_api.tbank_client import TClient
from tbank_kassa_api.tbank_models import NotificationPayment
from tbank_kassa_api.enums import PaymentStatus
from tbank_kassa_api.send_models import Init
from tbank_kassa_api.tbank_models import *
from telebot import TeleBot, types
import shortuuid

from model_place.models import *

logger = logging.getLogger(__name__)

"""
{b'event': [b'ONCRMDEALUPDATE'], b'data[FIELDS][ID]': [b'39'], 
b'ts': [b'1707749333'], b'auth[domain]': [b'b24-3tmral.bitrix24.ru'], 
b'auth[client_endpoint]': [b'https://b24-3tmral.bitrix24.ru/rest/'], 
b'auth[server_endpoint]': [b'https://oauth.bitrix.info/rest/'], 
b'auth[member_id]': [b'51e2c566fe259c926c60bc06c7158cda'], 
b'auth[application_token]': [b'e57xiy964jb6slr0gfa0j6lpigf7gnij']}
"""

class OrderStatus(str, Enum):
    created = "created"
    confirmed = "confirmed"
    cancelled = "cancelled"
    paid = "paid"
    complete = "complete"



@csrf_exempt
def bitrix_webhook(request):
    if request.method == 'POST':
        try:
            local_bitrix = settings.BITRIX
            if not local_bitrix:
                return HttpResponse(status=200)

            data_row = parse_qs(request.body.decode("utf-8"))
            data = {}
            for key, value in data_row.items():
                data[key] = value[0]
            
            if data["auth[application_token]"] != settings.BITRIX_IN:
                logger.info(f"Wrong token: {data['auth[application_token]']}")
                return HttpResponse(status=401)

            bitrix_order_id = int(data["data[FIELDS][ID]"])
            result = local_bitrix.callMethod('crm.deal.get', id = bitrix_order_id)
            opportunity = result.get("OPPORTUNITY")
            paid_for = bool(int(result.get("UF_CRM_PAID_FOR", 0)))
            ready_issued = bool(int(result.get("UF_CRM_READY_ISSUED", 0)))
            issued = bool(int(result.get("UF_CRM_ISSUED", 0)))
            order_data = result.get("UF_CRM_ORDER_DATA", "")
            
            if opportunity is None or opportunity == "0.00":
                opportunity = None
            else:
                opportunity = Decimal(opportunity)
            
            bot: TeleBot = settings.TELEGRAM_BOT
            order: Orders = Orders.objects.get(request_number=bitrix_order_id)
            user_tg_id = order.user.telegram_id
            client = settings.REDIS_CLIENT
            if order.amount != opportunity:
                sending_message = False
                if not order.amount:
                    sending_message = True
                order.amount = opportunity
                logger.info(f"Change order amount for - user:{user_tg_id}: order:{order.short_uuid}")
                
                
            if any([all([not order.ready_issued, ready_issued, order.paid_for]), all([paid_for, not order.paid_for, order.ready_issued])]):
                local_keyboard = types.InlineKeyboardMarkup()
                order_shortuuid = shortuuid.encode(order.uuid)

                local_keyboard.add(
                    types.InlineKeyboardButton(text="Данные о заказе", callback_data=f"ord:{order_shortuuid}"),
                )
                
                client.rpush(f"user_orders:{user_tg_id}", order.short_uuid)
                count_order_messages = client.llen(f"user_orders_mess:{user_tg_id}")
                while count_order_messages > 0:
                    row_data = client.rpop(f"user_orders_mess:{user_tg_id}")
                    message_order_id = int(row_data.decode("utf-8"))
                    try:
                        bot.delete_message(user_tg_id, message_order_id)
                    except:
                        ...
                        
                    count_order_messages = client.llen(f"user_orders_mess:{user_tg_id}")

                message = bot.send_message(user_tg_id, f"Заказ: {order.short_uuid} будет готов к выдаче на пункте после 18:00", reply_markup=local_keyboard)
                client.lpush(f"user_orders_mess:{user_tg_id}", str(message.message_id))
                client.set(f"user_last_message:{user_tg_id}", str(message.message_id))
                logger.info(f"Заказ: {order.short_uuid} будет готов к выдаче на пункте после 18:00")

            if order.paid_for != paid_for:
                order.paid_for = paid_for
                logger.info(f"Change paid_for for order: {order.short_uuid} to {paid_for}")
            if order.ready_issued != ready_issued:
                order.ready_issued = ready_issued
                logger.info(f"Change ready_issued for order: {order.short_uuid} to {ready_issued}")
            if all([issued, order.ready_issued, order.paid_for]) and not order.complete:
                order.complete = True
                order.order_status = OrderStatus.complete.value
                logger.info(f"Complete order: {order.short_uuid}")
            

            order.order_data = order_data
            order.save()

        except Exception as ex:
            logger.error(ex)

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)



@csrf_exempt
def tbank_notify(request: HttpRequest):
    if request.method == 'POST':
        data = request.body.decode("utf-8")
        local_tbank_clinet: TClient = settings.TBANK_CLIENT
        
        if not local_tbank_clinet:
            return HttpResponse("OK")

        result = local_tbank_clinet.pars_notification(data)
        client = settings.REDIS_CLIENT
        bot: TeleBot = settings.TELEGRAM_BOT
        if isinstance(result, NotificationPayment):
            if result.Status == PaymentStatus.CONFIRMED:
                order_id = uuid.UUID(result.OrderId)
                order = Orders.objects.get(uuid=order_id)
                short_ver_uuid = shortuuid.encode(order.uuid)
                order.paid_for = True
                user_tg_id = order.user.telegram_id
                local_bitrix: Bitrix24 = settings.BITRIX
                if local_bitrix and not settings.DEBUG:
                    local_bitrix.callMethod("crm.deal.update", id=order.request_number, fields={
                            "UF_CRM_PAID_FOR":"Y"
                        }
                    )
                
                local_keyboard = types.InlineKeyboardMarkup()
                # local_keyboard.add(
                #     types.InlineKeyboardButton(text="Выбор пункта выдачи", callback_data="menu:issued"),
                # )
                local_keyboard.add(
                    types.InlineKeyboardButton(text="Данные о заказе", callback_data=f"ord:{short_ver_uuid}"),
                )
                client.rpush(f"user_orders:{user_tg_id}", order.short_uuid)
                count_order_messages = client.llen(f"user_orders_mess:{user_tg_id}")
                while count_order_messages > 0:
                    row_data = client.rpop(f"user_orders_mess:{user_tg_id}")
                    message_order_id = int(row_data.decode("utf-8"))
                    try:
                        bot.delete_message(user_tg_id, message_order_id)
                    except:
                        ...
                        
                    count_order_messages = client.llen(f"user_orders_mess:{user_tg_id}")

                message = bot.send_message(user_tg_id, f"Заказ: {order.short_uuid} успешно оплачен!", reply_markup=local_keyboard)
                client.lpush(f"user_orders_mess:{user_tg_id}", str(message.message_id))
                client.set(f"user_last_message:{user_tg_id}", str(message.message_id))
                order.save()
                

        return HttpResponse("OK")


def tbank_payment(request: HttpRequest):
    pass