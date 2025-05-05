import os
import re
import pathlib
import typing
import datetime
from uuid import uuid4
import loguru

from typing import Optional

from tortoise.exceptions import DoesNotExist
import shortuuid

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram import filters, types
from aiogram_media_group import media_group_handler
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command

from tbank_kassa_api.tbank_client import TClient
from tbank_kassa_api.tbank_models import *
from tbank_kassa_api.enums import PaymentStatus
from tbank_kassa_api.send_models import Init


from bot_elements.callback import MenuCallBack, SliderCallBack, \
                                KeywordCallBack, ContinueCallBack, \
                                SubscribeCallBack, HandOverCallBack, \
                                BackCallBack, OrderCallBack, PointCallBack
from bot_elements.states import MenuState
from bot_elements.keyboard_build import *
from bot_elements.keyboards import *
from bot_elements.messages_builder import *
from programming_elements.enums import MenuWays, BasicMenuKeyboards, \
                                        MessagesBuildType, SliderType, \
                                        HandOverStep, HandOverBack, ReviewStep, OrderStatus
from programming_elements.classes import Way, KeyboardBuilder, MessageBuilder, return_ways_models
from init_unit import bot, config, MEDIA_DIR, shortnuberic, \
                        shortdefault, PAY_TOKEN, BITRIX_OUT, \
                        client_redis, SITE_HOST, DEBUG, TBANK_CLIENT
from models import *
from services import logger
from services.mini_services import delete_smiles_emoji, dict_user_fields




menu_router = Router(name="menu")


async def change_message(input_message: types.Message | types.CallbackQuery, last_message_id: Optional[int],
                         message_data, keyboard: InlineKeyboardMarkup, state = None):
    message = None

    if not last_message_id:
        row_data: Optional[str] = await client_redis.get(f"user_last_message:{input_message.from_user.id}")
        if not row_data is None:
            last_message_id = int(row_data.decode(encoding="utf-8"))
    
    else:
        second_last = None
        row_data: Optional[str] = await client_redis.get(f"user_last_message:{input_message.from_user.id}")
        if not row_data is None:
            second_last = int(row_data.decode(encoding="utf-8"))
        if last_message_id != second_last and not second_last is None:
            last_message_id = second_last
    
    if isinstance(input_message, types.Message):
        try:
            await bot.delete_message(chat_id=input_message.from_user.id, message_id=last_message_id)
        except Exception as ex:
            pass

    if isinstance(message_data, str):
        try:
            message = await bot.edit_message_text(text=message_data, reply_markup=keyboard, 
                                    chat_id=input_message.from_user.id, message_id=last_message_id)

            if isinstance(message, bool):
                raise Exception(f"Error editable text message:{last_message_id}")

        except Exception as ex:
            try:
                await bot.delete_message(chat_id=input_message.from_user.id, message_id=last_message_id)
            except Exception as ex:
                pass
            try:
                message = await bot.send_message(chat_id=input_message.from_user.id, 
                                                    text=message_data, reply_markup=keyboard)
            except Exception as ex:
                logger.log_error(ex)

    elif isinstance(message_data, list):
        try:
            await bot.delete_message(chat_id=input_message.from_user.id, message_id=last_message_id)
        except Exception as ex:
            pass
        try:
            text = message_data[0].caption if message_data[0].caption else "Выберите действие"
            message_list = []
            chat_id = input_message.from_user.id
            thread_id = None
            for media_data in message_data:
                if isinstance(media_data, types.InputMediaPhoto):
                    message_list.append(
                        types.InputMediaPhoto(
                            media=media_data.media
                        )
                    )

                elif isinstance(media_data, types.InputMediaVideo):
                    message_list.append(
                        types.InputMediaVideo(
                            media=media_data.media
                        )
                    )

                elif isinstance(media_data, types.InputMediaDocument):
                    message_list.append(
                        types.InputMediaDocument(
                            media=media_data.media
                        )
                    )

            message = await bot.send_media_group(chat_id=chat_id, message_thread_id=thread_id, 
                                        media=message_list)

            message = await bot.send_message(chat_id=input_message.from_user.id, 
                                                text=text, reply_markup=keyboard)
        except Exception as ex:
            logger.log_error(ex)


    elif any([isinstance(message_data, types.InputMediaPhoto), 
            isinstance(message_data, types.InputMediaVideo),
            isinstance(message_data, types.InputMediaDocument)]):
        try:
            message = await bot.edit_message_media(media=message_data, reply_markup=keyboard,
                                                            chat_id=input_message.from_user.id, 
                                                            message_id=last_message_id)
            if isinstance(message, bool):
                raise Exception(f"Error editable media message:{last_message_id}")
        except Exception as ex:
            try:
                await bot.delete_message(chat_id=input_message.from_user.id, message_id=last_message_id)
            except Exception as ex:
                pass
            try:
                if isinstance(message_data, types.InputMediaPhoto):
                    message = await bot.send_photo(chat_id=input_message.from_user.id, 
                                                    photo=message_data.media, 
                                                    reply_markup=keyboard, 
                                                    caption=message_data.caption)

                elif isinstance(message_data, types.InputMediaVideo):
                    message = await bot.send_video(chat_id=input_message.from_user.id, 
                                                    video=message_data.media,
                                                    reply_markup=keyboard, 
                                                    caption=message_data.caption)

                elif isinstance(message_data, types.InputMediaDocument):
                    message = await bot.send_document(chat_id=input_message.from_user.id,
                                                        document=message_data.media,
                                                        reply_markup=keyboard, 
                                                        caption=message_data.caption)
            except Exception as ex:
                logger.log_error(ex)

    try:
        await client_redis.set(f"user_last_message:{input_message.from_user.id}", str(message.message_id))
    except Exception as ex:
        logger.log_error(ex)

    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception as ex:
        logger.log_error(ex)

    return message


async def slider_data(slider_data, model_list, field="id"):
    slider_id = None
    last_index = 0
    action = 0
    if isinstance(slider_data, SliderCallBack):
            last_index = slider_data.last_index
            action = slider_data.action
            last_index += action
            if last_index > len(model_list) - 1:
                last_index = 0

            if last_index < 0:
                last_index = len(model_list) - 1

    if not slider_id:
        slider_id = model_list[last_index].__dict__[field]
        
    return slider_id, last_index, action


async def text_before(message, addition_text):
    local_message = message
    print(local_message)
    if isinstance(local_message, str):
        local_message = f"{message}{addition_text}"
    elif isinstance(local_message, types.InputMediaPhoto):
        local_message = types.InputMediaPhoto(media=local_message.media, caption=f"{local_message.caption}{addition_text}")
    
    return local_message


async def create_messages(message: types.Message | types.CallbackQuery, state: FSMContext, callback_data: MenuCallBack = None):
    state_data = await state.get_data()
    way_message = None
    way_keyboard = None
    local_state = await state.get_state()
    ways = await return_ways_models(BotMessages, BotButtons)
    for way in ways:
        state_geter = MenuState.__dict__.get(way.work_state)
        if state_geter == local_state:
            if callback_data or isinstance(message, types.CallbackQuery):

                if way.way_callback == callback_data.to:
                    way_message = way.message.return_telegram_message()
                    try:
                        way_keyboard = await way.keyboard.return_telegram_keyboard()
                    except:
                        pass
                    state_seter = MenuState.__dict__.get(way.set_state)
                    await state.set_state(state=state_seter)
                    break

            elif (isinstance(message, types.Message) or isinstance(message, list)) and not way.callback_only:
                way_message = way.message.return_telegram_message()
                way_keyboard = await way.keyboard.return_telegram_keyboard()
                await state.set_state(state=MenuState.__dict__[way.set_state])
                break
    
    return way_message, way_keyboard, state_data



@menu_router.callback_query(MenuCallBack.filter(F.to == MenuWays.start.value))
@menu_router.callback_query(MenuCallBack.filter(F.to == MenuWays.menu.value))
@menu_router.message(filters.CommandStart())
async def start(input_message: types.Message | list[types.Message] | types.CallbackQuery, state: FSMContext,
                     callback_data: MenuCallBack = None):
    state_data = await state.get_data()
    way_message = None
    way_keyboard = None
    local_state = await state.get_state()
    ways = await return_ways_models(BotMessages, BotButtons)
    user = await TelegramUsers.get_or_none(telegram_id=input_message.from_user.id)
    if user:
        await state.set_state(state=MenuState.union)
        callback_data = MenuCallBack(to=MenuWays.menu.value)
        way_message, way_keyboard, state_data = await create_messages(input_message, state, callback_data)
    else:
        for way in ways:

            if MenuState.__dict__.get(way.work_state) == local_state or not way.work_state:
                if callback_data or isinstance(input_message, types.CallbackQuery):

                    if way.way_callback == callback_data.to:
                        way_message = way.message.return_telegram_message()
                        way_keyboard = await way.keyboard.return_telegram_keyboard()
                        await state.set_state(state=MenuState.__dict__[way.set_state])
                        break

                elif isinstance(input_message, types.Message) :
                    way_message = way.message.return_telegram_message()
                    way_keyboard = await way.keyboard.return_telegram_keyboard()
                    await state.set_state(state=MenuState.__dict__[way.set_state])
                    break

    if not way_message:
        return

    message = await change_message(input_message, state_data.get("last_message_id"), way_message, way_keyboard, state)

    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...
        


@menu_router.message(MenuState.fio)
@menu_router.message(MenuState.email)
@menu_router.message(MenuState.phone, F.text.isdigit() | F.contact)
@menu_router.message(MenuState.end_reg)
async def reg(message: types.Message, state: FSMContext,
                     callback_data: MenuCallBack = None):
    way_message = None
    way_keyboard = None
    
    local_state = await state.get_state()
    if local_state == MenuState.phone:
        phone = ""
        if message.contact:
            phone = message.contact.phone_number
        else:
            phone_reg = re.match(r"^([\+7]{2}|7{1}|8{1})([\(\-]*[0-9]{3}[\)\-]*)([0-9\-]{7,9})$", 
                                    message.text)
            if phone_reg:
                phone = message.text
            else:
                return
        
        await state.update_data({"phone": phone})
        
    elif local_state == MenuState.fio:
        try:
            message.text.split()[2]
        except:
            state_data = await state.get_data()
            await change_message(message, state_data.get("last_message_id"), "Отправьте пожалуйства Фамилию Имя Отчество", await back_keyboard_build(MenuWays.reg_begin), state)
            try:
                await state.update_data(last_message_id=message.message_id)
            except Exception:
                ...
            return
        await state.update_data({"fio": message.text})
    
    elif local_state == MenuState.email:
        await state.update_data({"email": message.text})
    
    way_message, way_keyboard, state_data = await create_messages(message, state, callback_data)

    if local_state == MenuState.phone:
        if isinstance(way_message, str):
            way_message = types.InputMediaDocument(
                    media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / "user_agree.pdf"), 
                    caption=way_message
                )
        elif any([isinstance(message_data, types.InputMediaPhoto), 
            isinstance(message_data, types.InputMediaVideo)]):
                way_message = types.InputMediaDocument(
                    media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / "user_agree.pdf"), 
                    caption=way_message.caption
                )

    message = await change_message(message, state_data.get("last_message_id"), way_message, way_keyboard, state)
    
    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...


@menu_router.callback_query(SubscribeCallBack.filter())
async def subscribe_callback(input_message: types.CallbackQuery, state: FSMContext,
                     callback_data: SubscribeCallBack = None):

    user = await TelegramUsers.get_or_none(telegram_id=input_message.from_user.id)
    if not user:
        return
    user.subscription = callback_data.data
    await user.save()
    await start(input_message, state, None)


@menu_router.callback_query(MenuState.union, MenuCallBack.filter(F.to != MenuWays.start.value))
@menu_router.callback_query(MenuState.union, MenuCallBack.filter(F.to != MenuWays.hand_over.value))
@menu_router.callback_query(MenuState.fio, MenuCallBack.filter())
@menu_router.callback_query(MenuState.email, MenuCallBack.filter())
@menu_router.callback_query(MenuState.get_comment, MenuCallBack.filter())
@menu_router.callback_query(MenuState.hand_over, MenuCallBack.filter())
@menu_router.callback_query(MenuState.show_points, MenuCallBack.filter())
@menu_router.callback_query(MenuState.issued_order, MenuCallBack.filter())
@menu_router.callback_query(MenuState.get_point, MenuCallBack.filter())
@menu_router.callback_query(MenuCallBack.filter())
async def union(input_message: types.Message | types.CallbackQuery, state: FSMContext,
                     callback_data: MenuCallBack = None):
    await state.set_state(state=MenuState.union)
    way_message, way_keyboard, state_data = await create_messages(input_message, state, callback_data)

    if callback_data.to == MenuWays.subscribe.value:
        fio = state_data.get("fio")
        split_fio = fio.split()
        email = state_data.get("email", None)
        phone = state_data.get("phone")
        b24_contact_id = int(shortnuberic.random()[:10])
        if not DEBUG:
            b24_contact_id = BITRIX_OUT.callMethod("crm.contact.add", fields={
                    "ASSIGNED_BY_ID": 1,
                    "NAME": split_fio[1], 
                    "SECOND_NAME": split_fio[2], 
                    "LAST_NAME": split_fio[0],
                    "PHONE" : [ { "VALUE": phone, "VALUE_TYPE": "WORK" } ],
                    "TYPE_ID": "CLIENT",
                    "OPENED": "Y", 
                }
            )
        user, created = await TelegramUsers.get_or_create(telegram_id=input_message.from_user.id, 
                                                            fio=fio, 
                                                            email=email, 
                                                            phone=phone,
                                                            bitrix_contact_id=b24_contact_id,
                                                            subscription=False)
        way_keyboard = await subscription_keyboard_build()

    elif callback_data.to == MenuWays.hand_over.value:
        await state.set_state(state=MenuState.hand_over)
        last_point = state_data.get("last_point", None)
        way_keyboard = await areas_keyboard_build(last_id=last_point)
    
    elif any([callback_data.to == MenuWays.points.value, callback_data.to == MenuWays.issued_order.value]):
        if callback_data.to == MenuWays.issued_order.value:
            await state.set_state(state=MenuState.issued_order)
            way_message = await message_builder("text", "image", "video", BotMessages, False, {"message_name":"select_area_group"})
            telegram_id = input_message.from_user.id
            len_orders = state_data.get("len_orders")
            order_ready_id = state_data.get("order_ready_id", None)
            if not order_ready_id:
                order_ready_id_row = await client_redis.rpop(f"user_orders:{telegram_id}")
                if order_ready_id_row:
                    order_ready_id = order_ready_id_row.decode('utf-8')
                    order = None
                    while not order:
                        order: Orders = await Orders.get_or_none(short_uuid=str(order_ready_id))
                        if not order:
                            logger.log_info(f"Oreder {order_ready_id} not exist")
                            order_ready_id_row = await client_redis.rpop(f"user_orders:{telegram_id}")
                            order_ready_id = order_ready_id_row.decode('utf-8')
                            logger.log_info(f"Order ready id: {order_ready_id}")
                            continue
                        await state.update_data({"order_ready_id": order_ready_id})
                else:
                    logger.log_error(f"How {input_message.from_user.id} here?!")
                    return

            len_orders = await client_redis.llen(f"user_orders:{telegram_id}")
            await state.update_data({"len_orders": len_orders})
            
        way_keyboard = await areas_keyboard_build()

    elif callback_data.to in [MenuWays.in_work.value, MenuWays.ready.value, MenuWays.complete.value]:
        user = await TelegramUsers.get(telegram_id=input_message.from_user.id)
        await state.update_data({"order_ready_id": None})
        way_keyboard = await orders_keyboard_build(callback_data.to, user)
    
    elif callback_data.to == MenuWays.feedback.value:
        way_keyboard = await areas_keyboard_build()

    elif callback_data.to == MenuWays.contacts.value:
        text = ""
        if isinstance(way_message, str):
            text = way_message
        elif isinstance(way_message, list):
            text = way_message[0].caption
        elif isinstance(way_message, types.InputMedia):
            text = way_message.caption
        price_a = types.InputMediaDocument(
            media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / "price_a.png"), 
            caption=text
        )
        price_b = types.InputMediaDocument(
            media=types.FSInputFile(pathlib.Path(MEDIA_DIR) / "price_b.png"), 
        )

        way_message = [price_a, price_b]


    if not way_message:
        return

    message = await change_message(input_message, state_data.get("last_message_id"), way_message, way_keyboard, state)
    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...


@menu_router.callback_query(PointCallBack.filter(F.type_ == ReviewStep.send_area_group.value))
async def get_area_group(input_message: types.CallbackQuery, state: FSMContext, callback_data: PointCallBack):
    # Here i get area_group_id and return keyboard sub_groups
    state_data = await state.get_data()
    state_name = await state.get_state()
    if not state_name:
        await state.set_state(MenuState.union)
    group_id = callback_data.data
    if group_id != -1:
        await state.update_data(group_id=group_id)
    else:
        group_id = state_data.get("group_id")
    way_message = await message_builder("text", "image", "video", BotMessages, False, {"message_name":"select_area_subgroup"})
    way_keyboard = await areas_sub_group_keyboard_build(group_id, state_name)

    message = await change_message(input_message, state_data.get("last_message_id"), way_message, way_keyboard, state)
    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...

@menu_router.callback_query(PointCallBack.filter(F.type_ == ReviewStep.send_area_subgroup.value))
async def get_area_subgroup(input_message: types.CallbackQuery, state: FSMContext, callback_data: PointCallBack):
    # Here i get area subgroup_id and return keyboard points
    state_data = await state.get_data()
    subgroup_id = callback_data.data
    if subgroup_id != -1:
        await state.update_data(subgroup_id = subgroup_id)
    else:
        subgroup_id = state_data.get("subgroup_id")
    state_name = await state.get_state()
    with_link = False
    search = False
    order_ready_id = state_data.get("order_ready_id", None)
    if state_name == MenuState.union:
        with_link = True

    else:
        search = True
    
    way_message = await message_builder("text", "image", "video", BotMessages, False, {"message_name":"select_point"})
    way_keyboard = await points_keyboard_build(subgroup_id, with_link, search, state_name)
    
    message = await change_message(input_message, state_data.get("last_message_id"), way_message, way_keyboard, state)
    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...


@menu_router.inline_query(MenuState.hand_over)
@menu_router.inline_query(MenuState.feedback)
async def search_inline(inline_query: types.InlineQuery, state: FSMContext):

    state_data = await state.get_data()

    subgroup_id = state_data.get("subgroup_id")
    
    points = await ReceptionPoints.filter(area_id=subgroup_id)

    media = []
    for point in points:
        if not inline_query.query.lower() in point.name.lower() and inline_query.query != "":
            continue
        thumbnail_url = ""
        if point.icon:
            thumbnail_url = SITE_HOST.strip("/").replace(".", "-") + ".sslip.io" + "/media"+ f"/{point.icon}" 
        if not thumbnail_url and DEBUG:
            thumbnail_url = "http://old-dos.ru/screens/3/9/f/a1f7cf628e9b1089e39590f32bef8.png"
        media.append(types.InlineQueryResultArticle(
            id=str(point.id),
            title=point.name,
            description=None,
            input_message_content=types.InputTextMessageContent(
                    message_text=point.name,
                ),
            thumbnail_url = thumbnail_url,
            thumbnail_width = 256,
            thumbnail_height = 256
            )
        )
    await inline_query.answer(results=media, cache_time=1)


@menu_router.inline_query(MenuState.issued_order)
async def search_inline_order(inline_query: types.InlineQuery, state: FSMContext):
    telegram_id = inline_query.from_user.id
    state_data = await state.get_data()
    subgroup_id = state_data.get("subgroup_id")
    order_ready_id = state_data.get("order_ready_id", None)
    if not order_ready_id:
        order_ready_id = await client_redis.rpop(f"user_orders:{telegram_id}")
        logger.log_info(f"Order ready id: {order_ready_id.decode('utf-8')}")
        len_orders = await client_redis.llen(f"user_orders:{telegram_id}")
        await state.update_data({"order_ready_id": order_ready_id.decode("utf-8")})
        await state.update_data({"len_orders": len_orders})
    if order_ready_id:
        await state.set_state(state=MenuState.get_point)
        points = await ReceptionPoints.filter(area_id=subgroup_id)
        
        media = []
        for point in points:
            if not inline_query.query.lower() in point.name.lower() and inline_query.query != "":
                continue
            thumbnail_url = ""
            if point.icon:
                thumbnail_url = SITE_HOST.strip("/").replace(".", "-") + ".sslip.io" + "/media"+ f"/{point.icon}" 
            print(thumbnail_url)
            if not thumbnail_url and DEBUG:
                thumbnail_url = "https://deti-online.com/i/4/94/57480/main/cyplenok.webp"
            media.append(types.InlineQueryResultArticle(
                id=str(point.id),
                title=point.name,
                description=None,
                input_message_content=types.InputTextMessageContent(
                        message_text=point.name,
                    ),
                thumbnail_url=thumbnail_url,
                thumbnail_width = 256,
                thumbnail_height = 256
                )
            )
        await inline_query.answer(results=media, cache_time=1)


@menu_router.message(MenuState.get_point)
async def take_point_done(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    len_orders = state_data.get("len_orders")
    order_ready_id = state_data.get("order_ready_id")
    point_name = message.text
    point = await ReceptionPoints.get_or_none(name=point_name)
    if not point:
        log_error(f"point with name '{point_name}' not found!")
        return
    order: Orders = await Orders.get_or_none(short_uuid=str(order_ready_id))
    order.issued_point_id = point.id
    await order.save()
    if not order:
        logger.log_info(f"Order not found: {order_ready_id}")
        return
    fields = {}
    deal_data: dict = {}
    if not DEBUG:
        deal_data = BITRIX_OUT.callMethod("crm.deal.get", id=order.request_number)
    deal_order_data = deal_data.get("UF_CRM_ORDER_DATA")
    user_fields: dict = await dict_user_fields(ISSUED_POINT=point_name)
    for key, value in user_fields.items():
        fields[key] = value
    if not DEBUG:
        BITRIX_OUT.callMethod("crm.deal.update", id=order.request_number, fields=fields)
    text = "Ожидайте, в ближайшее время мы с вами свяжемся."
    with_search = False
    telegram_id = message.from_user.id
    if len_orders > 0:
        with_search = True
        order_ready_id_row = await client_redis.rpop(f"user_orders:{telegram_id}")
        if order_ready_id_row:
            order_ready_id = order_ready_id_row.decode("utf-8")
            while order_ready_id == order.short_uuid:
                logger.log_info(f"Order {order_ready_id} be used get next one")
                order_ready_id_row = await client_redis.rpop(f"user_orders:{telegram_id}")
                order_ready_id = order_ready_id_row.decode("utf-8")
            
            order = None
            while not order:
                order: Orders = await Orders.get_or_none(short_uuid=str(order_ready_id))
                if not order:
                    logger.log_info(f"Order {order_ready_id} not exist")
                    order_ready_id_row = await client_redis.rpop(f"user_orders:{telegram_id}")
                    order_ready_id = order_ready_id_row.decode('utf-8')
                    logger.log_info(f"Order ready id: {order_ready_id}")
                    len_orders = await client_redis.llen(f"user_orders:{telegram_id}")
                    continue
                await state.update_data({"order_ready_id": order_ready_id})
                len_orders = await client_redis.llen(f"user_orders:{telegram_id}")
                await state.update_data({"len_orders": len_orders})
        else:
            logger.log_error(f"WTF!?!?! How it happen!? {telegram_id}")
        text += "\n\nУ вас еще есть заказ готовый к выдаче: " + order_ready_id + "\nПожалуйста выберите пункт приема."
    local_keyboard = await order_get_last(with_search)
    await change_message(message, state_data.get("last_message_id", None), text, local_keyboard, state)
    if not with_search:
        await state.update_data({"order_ready_id": None})
        await state.update_data({"len_orders": 0})


@menu_router.callback_query(MenuState.feedback, PointCallBack.filter(F.type_ == ReviewStep.send_point.value))
@menu_router.callback_query(MenuState.get_comment, PointCallBack.filter(F.type_ == ReviewStep.send_point.value))
@menu_router.message(MenuState.feedback)
async def get_point(input_message: types.CallbackQuery | types.Message, state: FSMContext,
                    callback_data: Optional[PointCallBack] = None):
    state_data = await state.get_data()
    if isinstance(input_message, types.CallbackQuery):
        if callback_data.data != -1:
            await state.set_data({"point_id": callback_data.data})
    elif isinstance(input_message, types.Message):
            point = await ReceptionPoints.get_or_none(name=input_message.text)
            if point:
                await state.update_data({"point_id": point.id})
            else: 
                log_error(f"point with name '{input_message.text}' not found!")
                return
        
    way_message = await message_builder("text", "image", "video", BotMessages, False, {"message_name":"feedback_rate"})
    way_keyboard = await rate_review_keyboard()
    message = await change_message(input_message, state_data.get("last_message_id"), way_message, way_keyboard, state)
    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...


@menu_router.callback_query(PointCallBack.filter(F.type_ == ReviewStep.send_rate.value))
async def get_rate_review(input_message: types.CallbackQuery, state: FSMContext, callback_data: PointCallBack):
    state_data = await state.get_data()
    if callback_data.data != -1:
        await state.update_data({"rate": callback_data.data})

    way_message = await message_builder("text", "image", "video", BotMessages, False, {"message_name":"feedback_request"})
    way_keyboard = await review_back_keyboard(ReviewStep.send_point)
    await state.set_state(MenuState.get_comment)
    message = await change_message(input_message, state_data.get("last_message_id"), way_message, way_keyboard, state)
    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...


async def error_comment(input_message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    way_message = await message_builder("text", "image", "video", BotMessages, False, {"message_name":"feedback_content_error"})
    way_keyboard = await review_back_keyboard(ReviewStep.send_rate)
    message = await change_message(input_message, state_data.get("last_message_id"), way_message, way_keyboard, state)
    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...


@menu_router.message(MenuState.get_comment)
async def get_comment_review(input_message: types.Message, state: FSMContext):
    if not input_message.text and not input_message.caption:
        await error_comment(input_message, state)
        return
    
    text = None
    photo_id = None
    video_id = None
    document_id = None
    audio_id = None
    if input_message.content_type == types.ContentType.PHOTO or input_message.content_type == types.ContentType.VIDEO or input_message.content_type == types.ContentType.DOCUMENT:
        if input_message.video:
            video_id = input_message.video.file_id
        if input_message.photo:
            photo_id = input_message.photo[-1].file_id
        if input_message.document:
            document_id = input_message.document.file_id
        if input_message.audio:
            audio_id = input_message.audio.file_id 

    if input_message.caption:
        text = input_message.caption
    elif input_message.text and not input_message.caption:
        text = input_message.text
    
    if len(text) > 800:
        await error_comment(input_message, state)
        return

    user = await TelegramUsers.get(telegram_id=input_message.from_user.id)
    state_data = await state.get_data()
    rate = state_data.get("rate")
    point_id = state_data.get("point_id")
    point = await ReceptionPoints.get(id=point_id)
    review_text = f"Автор:{user.fio}\nПункт:{point.name}\nОценка: {rate}/5\n\n{text}"
    group = await AdminGroup.first()
    if group:
        if input_message.video:
            await bot.send_video(group.group_id, video_id, caption=review_text, message_thread_id=group.thread_id)
        elif input_message.photo:
            await bot.send_photo(group.group_id, photo_id, caption=review_text, message_thread_id=group.thread_id)
        elif input_message.document:
            await bot.send_document(group.group_id, document_id, caption=review_text, message_thread_id=group.thread_id)
        elif input_message.audio:
            await bot.send_audio(group.group_id, audio_id, caption=review_text, message_thread_id=group.thread_id)
        else:
            await bot.send_message(group.group_id, review_text, message_thread_id=group.thread_id)

    await state.set_state(MenuState.union)
    way_message = await message_builder("text", "image", "video", BotMessages, False, {"message_name":"feedback_send"})
    way_keyboard = await review_back_keyboard(ReviewStep.menu)
    message = await change_message(input_message, state_data.get("last_message_id"), way_message, way_keyboard, state)
    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...


@menu_router.callback_query(OrderCallBack.filter())
async def order_data(input_message: types.CallbackQuery, state: FSMContext, callback_data: OrderCallBack = None):
    short_uuid = callback_data.to
    oreder_uuid = shortdefault.decode(short_uuid)
    order: Orders = await Orders.get_or_none(uuid=oreder_uuid)
    state_data = await state.get_data()
    bot_user = await bot.get_me()
    if order:
        points = set()
        way_keyboard = await back_keyboard_build(MenuWays.orders)
        text = f"Статус: {OrderStatus[order.order_status].value}"
        items: UserItems =  await UserItems.filter(basket_id=order.basket_id)
        
        service_text: str = order.order_data

        if not service_text:
            text += "\n\nДанные заказа:\n"
            for item in items:
                item_type = await ItemTypes.get(id=item.item_type_id)
                service = None
                if item.service_id:
                    service = await Services.get_or_none(id=item.service_id)
                point = await ReceptionPoints.get(id=item.point_id)
                points.add(point)
                second_part = ""
                if service:
                    second_part = f"| {service.name} |"
                else:
                    second_part = "|"
                second_part += f" {point.name} x{item.count}"
                text += f"\n{item_type.name} {second_part}"
                service_text_row = f"\n{item_type.name} {second_part}"
                service_text = service_text_row.replace("\n", ' ')
        
        elif service_text:
            local_text = "Общая информация по заказу:"
            local_text += "\nКоличество вещей в заказе:\n"
            service_text.replace(
                local_text, ""
            )
            text += "\n\nДанные заказа:\n"+service_text
            
        text += "\n\nДата создания: " + order.created_at.strftime("%d.%m.%Y %H:%M")
        if not order.amount:
            text += "\nСтоимость заказа еще не известна"
        elif order.amount and not order.paid_for:
            order_link = order.order_link
            if not order_link:
                local_tbank_client: TClient = TBANK_CLIENT
                user = await TelegramUsers.get(id=order.user_id)
                phone = user.phone
                phone = phone.strip("+")
                if phone.startswith("8") or phone.startswith("7"):
                    phone = "+7"+phone[1:]
                
                amount_sell = int(order.amount) * 100
                item = ItemFFD105(
                    Name = "Услуга химчистки",
                    Price = amount_sell,
                    Quantity = 1,
                    PaymentObject = PaymentObject.SERVICE,
                    Tax = Tax.NONE
                )
                receipt = ReceiptFFD105(
                    Email = user.email,
                    Phone = phone,
                    Items = [item],
                    Taxation = Taxation.PATENT
                )
                exp = datetime.datetime.now() + datetime.timedelta(days=20)
                model = Init(
                    OrderId = str(order.uuid),
                    Amount = amount_sell,
                    Description = service_text,
                    CustomerKey = str(user.pk),
                    NotificationURL = SITE_HOST + "/tbank_notify/",
                    Receipt = receipt,
                    RedirectDueDate=exp.isoformat(timespec='seconds')
                )
                response = await local_tbank_client.async_send_model(model)
                payment_url = ""
                if response.get("Success"):
                    payment_url = response.get("PaymentURL")
                else:
                    return
                order_link = payment_url

            text += f"\nСтоимость заказа: {order.amount}"
            
            try:
                await bot.delete_message(chat_id=input_message.from_user.id, message_id=state_data.get("last_message_id"))
            except Exception:
                ...
            local_keyboard = InlineKeyboardBuilder()
            local_keyboard.add(
                InlineKeyboardButton(text="Перейти к оплате", url=order_link)# web_app=types.WebAppInfo(url=payment_url))
            )
            message = await bot.send_message(chat_id=input_message.from_user.id, text=text, reply_markup=local_keyboard.as_markup())
            
            #await bot.send_invoice(chat_id=input_message.from_user.id, title="Оплата заказа", 
            #                        description=f"Вещи: {service_text}", payload=short_uuid, provider_token=PAY_TOKEN, currency='RUB',
            #                        prices=[types.LabeledPrice(label="Услуги химчистки", amount=amount_sell)])
            try:
                await state.update_data(last_message_id=message.message_id)
            except Exception:
                ...
            return
        elif order.amount and order.paid_for and not order.ready_issued:
            text += f"\nСтоимость заказа: {order.amount}"
            text += "\nОжидайте готовности к выдаче"
        elif order.paid_for and order.ready_issued and not order.complete:
            text += f"\nСтоимость заказа: {order.amount}"
            # point = None
            getting = False
            # if not order.issued_point_id:
            #     getting = True
            #     text += "\nВыберете пункт для получения заказа"
            #     await state.update_data({"order_ready_id": order.short_uuid})
            # else:
            #     point = await ReceptionPoints.get(id = order.issued_point_id)
            #     text += "\nОжидайте когда заказ будет в пункте выдачи"
            point_text = "пункте" if len(points) <= 1 else "пунктах"
            text += f"\nЗаказ ожидает вас в {point_text} выдачи"
            
            way_keyboard = await order_get_point(getting, points)
        elif order.complete:
            text += f"\nСтоимость заказа: {order.amount}"
            text += "\nЗаказ был завершен"
        
        message = await change_message(input_message, state_data.get("last_message_id"), 
                                        text, way_keyboard, state)

        try:
            await state.update_data(last_message_id=input_message.message_id)
        except Exception:
            ...


@menu_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@menu_router.message(F.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
async def success_payment(message: types.Message, state: FSMContext):
    short_uuid = message.successful_payment.invoice_payload
    order_uuid = shortdefault.decode(short_uuid)
    state_data = await state.get_data()
    text = ""
    order = await Orders.get_or_none(uuid=order_uuid)
    if order:
        order.paid_for = True
        fields = {}
        user_fields = await dict_user_fields(PAID_FOR="Y")
        for key, value in user_fields.items():
            fields[key] = value
        if not DEBUG:
            BITRIX_OUT.callMethod("crm.deal.update", id=order.request_number, fields=fields)
        await order.save()
        text = "Оплата прошла успешно! Ждите когда заказ будет готов к выдаче"
    else:
        text = "Ошибка при поиске заказа, обратитесь к поддержку"

    await state.set_state(MenuState.union)
    message = await change_message(message, state_data.get("last_message_id"), text, await back_keyboard_build(MenuWays.orders), state)

    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...


@menu_router.callback_query(MenuState.hand_over, PointCallBack.filter(F.type_ == ReviewStep.send_point.value))
@menu_router.message(MenuState.hand_over)
async def take_point_answer_type(input_message: types.CallbackQuery | types.Message, state: FSMContext,
                     callback_data = None):
    
    state_data = await state.get_data()
    way_keyboard = await choices_keyboard_build(HandOverStep.choice_type_item.value)
    way_message = await message_builder("text", "image", "video", BotMessages, 
                                        first=False, by_field={"message_name": "choice_type_item"})
    last_point = state_data.get("last_point", None)
    if isinstance(callback_data, PointCallBack) and isinstance(input_message, types.CallbackQuery):
        second_last_point = callback_data.data
        if second_last_point != -1:
            await state.update_data({"point": second_last_point})
            await state.update_data({"last_point": second_last_point})
    elif isinstance(input_message, types.Message):
        point = await ReceptionPoints.get_or_none(name=input_message.text)
        if point:
            await state.update_data({"point": point.id})
            await state.update_data({"last_point": point.id})
        else: 
            log_error(f"point with name '{input_message.text}' not found!")
            return

    message = await change_message(input_message, state_data.get("last_message_id"), way_message, way_keyboard, state)
    
    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...


@menu_router.callback_query(HandOverCallBack.filter())
async def hand_over(input_message: types.CallbackQuery, state: FSMContext,
                     callback_data = None):
    way_message = None
    way_keyboard = None
    state_data = await state.get_data()

    if isinstance(callback_data, HandOverCallBack) or isinstance(callback_data, BackCallBack):
        
        hand_over_step = ""
        choise_data = ""
        back_data = ""
        if isinstance(callback_data, HandOverCallBack):
            hand_over_step = callback_data.type_
            choise_data = callback_data.data
        elif isinstance(callback_data, BackCallBack):
            back_data = callback_data.to

        message = None
        text = ""

        way_data = {
            HandOverStep.choice_type_item.value: {
                        "update_key": "type_item", 
                        "choice_keyboard": HandOverStep.agree.value,
                        # "message": "choice_service",
                        # "alt_message": "Выберите доп. сервис"
                        "message": "accept_add",
                        "alt_message": "Хотите добавить "
                    },
            HandOverStep.choice_service.value : {
                        "update_key": "choise_service", 
                        "choice_keyboard": HandOverStep.agree.value,
                        "message": "accept_add",
                        "alt_message": "Хотите добавить"
                    },
            HandOverStep.choice_del_item.value: {
                        "update_key": "choise_del_item",
                        "choice_keyboard": HandOverStep.agree_del.value,
                        "message": "choice_del_item",
                        "alt_message": "Какую вещь убрать?",
                    },
            HandOverStep.agree.value: {
                        "update_key": "",
                        "choice_keyboard": "",
                        "message": "hand_over_menu",
                        "alt_message": "Меню",
                    },
            HandOverStep.hand_over.value: {
                        "update_key": "choise_del_item",
                        "choice_keyboard": "",
                        "message": "order_get_photo",
                        "alt_message": "Приложите фото пломбы",
                    },
        }

        update_key = ""
        choice_keyboard = ""
        message_name = ""
        alt_message_text = "Если вы видете этот текст, значит произошла ошибка, передайте ее программисту"

        if way_data.get(hand_over_step, False):
            update_key = way_data[hand_over_step].get("update_key")
            choice_keyboard = way_data[hand_over_step].get("choice_keyboard")
            message_name = way_data[hand_over_step].get("message")
            alt_message = way_data[hand_over_step].get("alt_message")
        
        message_text = alt_message_text

        message = await BotMessages.get_or_none(message_name=message_name)
        if message:
            message_text = message.text

        if choice_keyboard != "":
            way_keyboard = await choices_keyboard_build(choice_keyboard)

        if isinstance(callback_data, HandOverCallBack) and update_key != "":
                if choise_data != -1:
                    await state.update_data({update_key: choise_data})
                else:
                    await state.update_data({update_key: None})
        
        state_data = await state.get_data()

        if hand_over_step == HandOverStep.choice_service.value:
            pass

        elif hand_over_step == HandOverStep.choice_type_item.value:
            text = message_text
            item_type = await ItemTypes.get(id=state_data.get("type_item"))
            service = None
            selected_service = state_data.get("choise_service", None)
            point = await ReceptionPoints.get(id=state_data.get("point"))
            if selected_service:
                service = await Services.get(id=selected_service)
            second_part = f"\nВещь: {item_type.name}\nПункт: {point.name}"
            if service:
                second_part += f"\nСервис: {service.name}"
                await state.update_data({"choise_service": service.id})
            else:
                await state.update_data({"choise_service": service})
            text = f"{text}? {second_part}"
            state_data = await state.get_data()
            
        elif hand_over_step == HandOverStep.choice_del_item.value:
            short_number = str(choise_data)
            item_uuid = shortnuberic.decode(short_number)
            user_item = await UserItems.get(uuid=item_uuid)
            item_type = await ItemTypes.get(id=user_item.item_type_id)
            await state.update_data({"type_item": item_type.id})
            service = None
            if user_item.service_id:
                service = await Services.get_or_none(id=user_item.service_id)
            point = await ReceptionPoints.get(id=user_item.point_id)
            await state.update_data({"point": point.id})
            text = message_text
            second_part = f"\nВещь: {item_type.name}\n"
            if service:
                second_part += f"Сервис: {service.name}"
                await state.update_data({"choise_service": service.id})
            else:
                await state.update_data({"choise_service": service})
            text = f"{text}? {second_part}"
            
        elif hand_over_step == HandOverStep.choice_point.value:
            text = message_text
            state_data = await state.get_data()
            choice_type_item = await ItemTypes.get(id=state_data.get("type_item"))
            text = f"{text}\n\n{choice_service.name}\n{choice_type_item.name}\n{choice_wear_treat.name}"
            way_keyboard = await choices_keyboard_build(HandOverStep.agree.value)

        elif hand_over_step == HandOverStep.del_type_item.value:
            user = await TelegramUsers.get(telegram_id=input_message.from_user.id)
            basket: Basket = await Basket.get_or_none(user_id=user.id, old=False)
            if not basket:
                basket_uuid = str(uuid4())
                basket = await Basket.create(uuid=basket_uuid, user_id=user.id, old=False, 
                                            created_at=datetime.datetime.now())
            items = await UserItems.filter(basket_id=basket.uuid)
            text = message_text
            way_keyboard = await choice_delete(items)

        elif hand_over_step == HandOverStep.agree.value:
            selected_service = state_data.get("choise_service", None)
            choice_type_item = state_data.get("type_item")
            point = state_data.get("point")
            #choice_wear_treat = await WearTreatments.get(id=state_data.get("choise_wear_treat"))
            user: TelegramUsers = await TelegramUsers.get(telegram_id=input_message.from_user.id)
            basket: Basket = await Basket.get_or_none(user_id=user.id, old=False)
            if not basket:
                basket_uuid = str(uuid4())
                basket = await Basket.create(uuid=basket_uuid, user_id=user.id, old=False, 
                                          created_at=datetime.datetime.now())
            #await UserItems.create(uuid=item_uuid, user_id=user.id, basket_id=basket.uuid, service=choice_service, item_type=choice_type_item, wear_treatment=choice_wear_treat)
            item: UserItems = await UserItems.get_or_none(user_id=user.id, basket_id=basket.uuid, item_type_id=choice_type_item, 
                                                service_id=selected_service, point_id=point, old=False)
            if not item:
                if choise_data == -1:
                    item: UserItems = await UserItems.get_or_none(user_id=user.id, basket_id=basket.uuid, item_type_id=choice_type_item, point_id=point, old=False)
                    if not item:
                        return
                    elif choise_data == -1 and item.count > 1:
                        item.count += choise_data
                        await item.save()
                    elif choise_data == -1 and item.count == 1 or item.count <= 0:
                        await item.delete()
                elif choise_data == 1:
                    item_uuid = str(uuid4())
                    item: UserItems = await UserItems.create(uuid=item_uuid, user_id=user.id, 
                                                    basket_id=basket.uuid, item_type_id=choice_type_item, 
                                                    service_id=selected_service, point_id=point, old=False, count=1)
            else:
                if choise_data == -1 and item.count > 1:
                    item.count += choise_data
                    await item.save()
                elif choise_data == -1 and item.count == 1 or item.count <= 0:
                    await item.delete()
                elif choise_data == 1:
                    item.count += choise_data
                    await item.save()

            items_count = await UserItems.filter(basket_id=basket.uuid).count()
            items = await UserItems.filter(basket_id=basket.uuid)
            text = message_text
            text += "\nКоличество вещей в заказе:\n"
            for item in items:
                item_type = await ItemTypes.get(id=item.item_type_id)
                service = None
                if item.service_id:
                    service = await Services.get_or_none(id=item.service_id)
                point = await ReceptionPoints.get(id=item.point_id)
                second_part = ""
                if service:
                    second_part = f"| {service.name} |"
                else:
                    second_part = "|"
                second_part += f" {point.name} x{item.count}"
                text += f"\n{item_type.name} {second_part}"
            way_keyboard = await hand_over_menu_keyboard_build(items_count)
        
        elif hand_over_step == HandOverStep.make_order.value:
            user: TelegramUsers = await TelegramUsers.get(telegram_id=input_message.from_user.id)
            basket: Basket = await Basket.get_or_none(user_id=user.id, old=False)
            if not basket:
                basket_uuid = str(uuid4())
                basket = await Basket.create(uuid=basket_uuid, user_id=user.id, old=False, 
                                            created_at=datetime.datetime.now())
            items_count = await UserItems.filter(basket_id=basket.uuid).count()
            items = await UserItems.filter(basket_id=basket.uuid)
            text = "Общая информация по заказу:"
            text += "\nКоличество вещей в заказе:\n"
            service_text = ""
            items_list = []
            for item in items:
                item_type = await ItemTypes.get(id=item.item_type_id)
                service = None
                if item.service_id:
                    service = await Services.get_or_none(id=item.service_id)
                point = await ReceptionPoints.get(id=item.point_id)
                second_part = ""
                if service:
                    second_part = f"| {service.name} |"
                else:
                    second_part = "|"
                second_part += f" {point.name} x{item.count}"
                service_text += f"\n{item_type.name} {second_part}"

            text += service_text
            order_uuid = uuid4()
            short_uuid_order = shortnuberic.encode(order_uuid)[:15]
            order: Orders = await Orders.create(uuid=order_uuid, short_uuid=short_uuid_order, user_id=user.id, basket_id=basket.uuid,
                                            created_at=datetime.datetime.now(), complete=False, 
                                            ready_issued=False, paid_for=False, order_status="created", order_data=service_text.strip())
            way_keyboard = await make_order_keyboard_build(order_uuid=order_uuid)
        
        elif hand_over_step == HandOverStep.hand_over.value:
            order_uuid = shortnuberic.decode(str(choise_data))
            order = await Orders.get_or_none(uuid=order_uuid)
            message_text = message_text
            text = f"Номер заявки: {order.short_uuid}\n{message.text}"
            await state.set_state(state=MenuState.get_plombo)
            await state.update_data(order_uuid=order_uuid)

        way_message = text

    message = await change_message(input_message, state_data.get("last_message_id"), way_message, way_keyboard, state)
    
    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception as e:
        loguru.logger.info(str(e))


@menu_router.message(MenuState.get_plombo)
async def hand_over(input_message: types.Message, state: FSMContext):
    loguru.logger.info('get_plombo')
    await state.set_state(MenuState.union)
    user = await TelegramUsers.get(telegram_id=input_message.from_user.id)
    state_data = await state.get_data()
    order_uuid = state_data.get("order_uuid")
    order: Orders = await Orders.get_or_none(uuid=order_uuid)
    text = "Произошла ошибка при обработке заявки"
    if order:
        db_path = None
        if input_message.photo:
            photo_id = input_message.photo[-1].file_id
            file = await bot.get_file(file_id=photo_id)
            file_path = file.file_path
            short_path = shortdefault.uuid()[:15] + photo_id[:15] + shortdefault.uuid()[:15]
            db_directory = os.path.join(MEDIA_DIR, "orders")
            db_path =  f"orders/{short_path}.{file_path.split('.')[-1]}"
            path_to_save = os.path.join(MEDIA_DIR, db_path)
            try:
                await bot.download_file(file_path, path_to_save)
            except FileNotFoundError:
                os.makedirs(db_directory)
                await bot.download_file(file_path, path_to_save)

        items_count = await UserItems.filter(basket_id=order.basket_id).count()
        items = await UserItems.filter(basket_id=order.basket_id)
        basket: Basket = await Basket.get_or_none(uuid=order.basket_id)
        order.plomb_photo = db_path
        order.plomb_data = input_message.text
        text = order.order_data
        items_list = []
        for item in items:
            item.old = True
            await item.save()

        FIO = user.fio.split()
        fields = {
            "TITLE": f"Заказ №{order.short_uuid} | {order.plomb_data if order.plomb_data else 'Проверьте фото'}",
            "STAGE_ID": "NEW",
            "CURRENCY_ID": 'RUB',
            "OPPORTUNITY": "0.00",
            "CONTACT_IDS": [user.bitrix_contact_id],
        }

        user_fields: dict = await dict_user_fields(PAID_FOR=False, READY_ISSUED=False, ISSUED=False, 
                                            ORDER_DATA=text, ORDER_PHOTO="", CLIENT_COMMENT="", ISSUED_POINT="")
        for key, value in user_fields.items():
            fields[key] = value
        result = int(shortnuberic.random()[:10])
        if not DEBUG:
            result = BITRIX_OUT.callMethod("crm.deal.add", fields=fields)
        order.request_number = result
        await order.save()
        basket.old = True
        await basket.save()
        url = ""
        if order.plomb_photo:
            url = SITE_HOST + "/media" + "/" + order.plomb_photo
        user_fields: dict = await dict_user_fields(CLIENT_COMMENT=order.plomb_data, ORDER_PHOTO=url)
        for key, value in user_fields.items():
            fields[key] = value
        if not DEBUG:
            BITRIX_OUT.callMethod("crm.deal.update", id=result, fields=fields)
        order.order_status = "confirmed"
        await  order.save()
        text = (await BotMessages.get(message_name='successful_request')).text

    message = await change_message(input_message, None, text, await back_menu_keyboard_build(), state)
    loguru.logger.info(text)

    try:
        await state.update_data(last_message_id=message.message_id)
    except Exception:
        ...

    
