from typing import Optional, List

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from tortoise.query_utils import Prefetch
from tortoise.expressions import Q

from bot_elements.callback import MenuCallBack, SliderCallBack, KeywordCallBack, \
                                ContinueCallBack, SubscribeCallBack,  \
                                HandOverCallBack, OrderCallBack, BackCallBack, PointCallBack
from bot_elements.states import MenuState
from programming_elements.enums import MenuWays, SliderType, HandOverBack, HandOverStep, ReviewStep
from init_unit import shortdefault, shortnuberic

from models import *


async def generic_callback_button(object, callback_class, from_get_text: str,
                                  callback_parameters: list, callback_data: list) -> InlineKeyboardButton:
    text = str(object.__dict__[from_get_text])
    kwargs = {}
    for parameter, data_from in zip(callback_parameters, callback_data):
        kwargs[parameter] = str(object.__dict__[data_from])
    local_button = InlineKeyboardButton(text=text, callback_data=callback_class(**kwargs).pack())
    return local_button


async def back_menu_button_build() -> InlineKeyboardButton:
    bot_button_options = await BotButtons.get(button_name="menu")
    return InlineKeyboardButton(text=bot_button_options.text, callback_data=MenuCallBack(to=MenuWays.menu.value).pack())
    

async def back_button_build(menu_way: MenuWays = MenuWays.back) -> InlineKeyboardButton:
    bot_button_options = await BotButtons.get(button_name="back")
    return InlineKeyboardButton(text=bot_button_options.text, callback_data=MenuCallBack(to=menu_way.value).pack())


async def back_menu_keyboard_build() -> InlineKeyboardMarkup:
    local_keyboard = InlineKeyboardBuilder()
    local_keyboard.add(await back_menu_button_build())
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def back_keyboard_build(menu_way: MenuWays = MenuWays.back) -> InlineKeyboardMarkup:
    local_keyboard = InlineKeyboardBuilder()
    local_keyboard.add(await back_button_build(menu_way=menu_way))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def union_keyboard_build(buttons, menu_ways, settings_model, back_to_menu: bool = False, back_to_way: Optional[MenuWays] = None) -> InlineKeyboardMarkup:
    local_keyboard = InlineKeyboardBuilder()
    bot_button_options = await settings_model.first().only(*buttons)
    for field, way in zip(buttons, menu_ways):
        callback_data = "null"
        if way:
            callback_data = MenuCallBack(to=way.value).pack()
        local_keyboard.add(InlineKeyboardButton(text=bot_button_options.__dict__[field], callback_data=callback_data))
    if back_to_menu:
        local_keyboard.add(await back_menu_button_build())
    if back_to_way:
        local_keyboard.add(await back_button_build(menu_way=back_to_way))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def slider_keyboard_build(model, slider_type: SliderType, last_index: int = 0, action: int = 0, back_to_way = MenuWays.start) -> InlineKeyboardMarkup:
    local_keyboard = InlineKeyboardBuilder()
    usefull = await model.all()
    local_keyboard.add(InlineKeyboardButton(text="<-", callback_data=SliderCallBack(action=-1, last_index=last_index, stype = slider_type.value).pack()))
    local_keyboard.add(InlineKeyboardButton(text=f"{last_index+1}/{len(usefull)}", callback_data=SliderCallBack(action=0, last_index=last_index, stype = slider_type.value).pack()))
    local_keyboard.add(InlineKeyboardButton(text="->", callback_data=SliderCallBack(action=1, last_index=last_index, stype = slider_type.value).pack()))
    local_keyboard.add(await back_button_build(menu_way=back_to_way))
    local_keyboard.adjust(3,1,1)
    return local_keyboard.as_markup()


async def continue_keyboard_build(step, period, max_steps, count_message, back_to_way = MenuWays.start, infinite = False) -> InlineKeyboardMarkup:
    local_keyboard = InlineKeyboardBuilder()
    add_continue_button = True
    if step == max_steps or max_steps == 0:
        step = 0
        if not infinite:
            add_continue_button = False
    if add_continue_button:
        local_keyboard.add(InlineKeyboardButton(text="Продолжить", 
                                                callback_data=ContinueCallBack(s=step, 
                                                                                p=period, 
                                                                                mxs=max_steps,
                                                                                cw=count_message).pack()))
    local_keyboard.add(await back_button_build(menu_way=back_to_way))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def subscription_keyboard_build() -> InlineKeyboardMarkup:
    local_keyboard = InlineKeyboardBuilder()
    local_keyboard.add(InlineKeyboardButton(text="Да", callback_data=SubscribeCallBack(data=True).pack()))
    local_keyboard.add(InlineKeyboardButton(text="Нет", callback_data=SubscribeCallBack(data=False).pack()))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def choices_keyboard_build(type_=HandOverStep) -> InlineKeyboardMarkup:
    local_keyboard = InlineKeyboardBuilder()
    if type_ == HandOverStep.choice_service.value:
        services = await Services.all()
        for service in services:
            local_keyboard.add(InlineKeyboardButton(text=service.name, 
                                                    callback_data=HandOverCallBack(type_=HandOverStep.choice_service.value, data=service.id).pack()))
        local_keyboard.add(InlineKeyboardButton(text="Пропустить", 
                                                    callback_data=HandOverCallBack(type_=HandOverStep.choice_service.value, data=-1).pack()))
        local_keyboard.add(InlineKeyboardButton(text="Назад", callback_data=PointCallBack(
                    type_=ReviewStep.send_point.value,
                    data=-1
                ).pack()
            )
        )
    
    elif type_ == HandOverStep.choice_type_item.value:
        item_types = await ItemTypes.all()
        for item_type in item_types:
            local_keyboard.add(InlineKeyboardButton(text=item_type.name, 
                                                    callback_data=HandOverCallBack(type_=HandOverStep.choice_type_item.value, data=item_type.id).pack()))
        #local_keyboard.add(InlineKeyboardButton(text="Назад", callback_data=BackCallBack(to=HandOverBack.choice_service.value).pack()))
        local_keyboard.add(InlineKeyboardButton(text="Назад", callback_data=MenuCallBack(to=MenuWays.hand_over.value).pack()))
    
    elif type_ == HandOverStep.choice_wear_treat.value:
        wear_treats = await WearTreatments.all()
        for wear_treat in wear_treats:
            local_keyboard.add(InlineKeyboardButton(text=wear_treat.name, 
                                                    callback_data=HandOverCallBack(type_=HandOverStep.choice_wear_treat.value, data=wear_treat.id).pack()))
        #local_keyboard.add(InlineKeyboardButton(text="Назад", callback_data=BackCallBack(to=HandOverBack.choice_type_item.value).pack()))
        local_keyboard.add(InlineKeyboardButton(text="Назад", callback_data=MenuCallBack(to=MenuWays.hand_over.value).pack()))
    
    elif type_ == HandOverStep.agree.value or type_ == HandOverStep.agree_del.value:
        data = 1 if type_ == HandOverStep.agree.value else -1
        local_keyboard.add(InlineKeyboardButton(text="Да", callback_data=HandOverCallBack(type_=HandOverStep.agree.value, data=data).pack()))
        if data == 1:
            local_keyboard.add(InlineKeyboardButton(text="Нет", callback_data=MenuCallBack(to=MenuWays.hand_over.value).pack()))
        elif data == -1:
            local_keyboard.add(InlineKeyboardButton(text="Нет", callback_data=HandOverCallBack(type_=HandOverStep.agree.value, data=0).pack()))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def choice_delete(user_items):
    local_keyboard = InlineKeyboardBuilder()
    use_types = set()
    for user_item in user_items:
        item_type = await ItemTypes.get(id=user_item.item_type_id)
        point: ReceptionPoints = await ReceptionPoints.get(id=user_item.point_id)
        short_uuid = shortnuberic.encode(user_item.uuid)
        if short_uuid in use_types:
            continue
        use_types.add(short_uuid)
        text = ""
        service = None
        if user_item.service_id:
            service = await Services.get_or_none(id=user_item.service_id)
        if service:
            text = f"{item_type.name}|{service.name}"
        else:
            text = item_type.name
        text += f"|{point.name}"
        local_keyboard.add(InlineKeyboardButton(text=text, 
                                                    callback_data=HandOverCallBack(type_=HandOverStep.choice_del_item.value, data=int(short_uuid)).pack()))
    local_keyboard.add(InlineKeyboardButton(text="Назад", callback_data=HandOverCallBack(type_=HandOverStep.agree.value, data=0).pack()))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def hand_over_menu_keyboard_build(item_count) -> InlineKeyboardMarkup:
    local_keyboard = InlineKeyboardBuilder()
    make_order: BotButtons = await BotButtons.get_or_none(button_name="make_order")
    add_item: BotButtons = await BotButtons.get_or_none(button_name="add_item")
    del_item: BotButtons = await BotButtons.get_or_none(button_name="del_item")
    if item_count != 0:
        local_keyboard.add(InlineKeyboardButton(text=make_order.text, callback_data=HandOverCallBack(type_=HandOverStep.make_order.value, data=-1).pack()))
    local_keyboard.add(InlineKeyboardButton(text=add_item.text, callback_data=MenuCallBack(to=MenuWays.hand_over.value).pack()))
    local_keyboard.add(InlineKeyboardButton(text=del_item.text, callback_data=HandOverCallBack(type_=HandOverStep.del_type_item.value, data=-1).pack()))
    local_keyboard.add(InlineKeyboardButton(text="Назад", callback_data=MenuCallBack(to=MenuWays.menu.value).pack()))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def make_order_keyboard_build(order_uuid) -> InlineKeyboardMarkup:
    short_uuid = shortnuberic.encode(order_uuid)
    local_keyboard = InlineKeyboardBuilder()
    make_order: BotButtons = await BotButtons.get_or_none(button_name="order_hand_over")
    local_keyboard.add(InlineKeyboardButton(text=make_order.text, callback_data=HandOverCallBack(type_=HandOverStep.hand_over.value, data=int(short_uuid)).pack()))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def areas_group_add_buttons(groups_data, local_keyboard):
    for group_id, count in groups_data.items():
        if count > 1:
            area: AreaGroups = await AreaGroups.get(id=group_id)
            callback_data = PointCallBack(type_=ReviewStep.send_area_group.value, data=area.id).pack()
            local_keyboard.add(InlineKeyboardButton(text=area.name, callback_data=callback_data))
        elif count == 1:
            area_sub_group: AreaSubgroups = await AreaSubgroups.get(group_id=group_id)
            callback_data = PointCallBack(type_=ReviewStep.send_area_subgroup.value, data=area_sub_group.id).pack()
            local_keyboard.add(InlineKeyboardButton(text=area_sub_group.name, callback_data=callback_data))
        elif count == 0:
            continue
    
    return local_keyboard


async def areas_keyboard_build(last_id = None, ):
    local_keyboard = InlineKeyboardBuilder()
    if last_id:
        point = await ReceptionPoints.get(id=last_id)
        link = None
        callback_data = None
        callback_data = PointCallBack(type_=ReviewStep.send_point.value, data=point.pk).pack()
        local_keyboard.add(InlineKeyboardButton(text=f"Текущая точка: {point.name}", url=link, callback_data=callback_data))
    
    groups_data = {}
    areas: List[AreaGroups] = await AreaGroups.all().only("id")
    for area_group in areas:
        group_id = area_group.id
        areas_subgroup_count = await AreaSubgroups.filter(group_id=group_id).count()
        groups_data[group_id] = areas_subgroup_count

    local_keyboard = await areas_group_add_buttons(groups_data, local_keyboard)
    
    local_keyboard.add(InlineKeyboardButton(text="Назад", callback_data=MenuCallBack(to=MenuWays.menu.value).pack()))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def areas_sub_group_keyboard_build(group_id, state: Optional[str]):
    local_keyboard = InlineKeyboardBuilder()
    areas_subgroups: List[AreaSubgroups] = await AreaSubgroups.filter(group_id=group_id)
    for area_sub_group in areas_subgroups:
        name = area_sub_group.name
        area_sub_group_id = area_sub_group.id
        callback_data = PointCallBack(type_=ReviewStep.send_area_subgroup.value, data=area_sub_group_id).pack()
        local_keyboard.add(InlineKeyboardButton(text=name, callback_data=callback_data))
    
    if state == MenuState.show_points:
        local_keyboard.add(InlineKeyboardButton(text="Назад", 
                                                callback_data=MenuCallBack(to=MenuWays.points.value).pack()))
    elif state == MenuState.hand_over:
        local_keyboard.add(InlineKeyboardButton(text="Назад", 
                                                callback_data=MenuCallBack(to=MenuWays.hand_over.value).pack()))
    elif state == MenuState.feedback:
        local_keyboard.add(InlineKeyboardButton(text="Назад", 
                                                callback_data=MenuCallBack(to=MenuWays.feedback.value).pack()))
    elif state == MenuState.union:
        local_keyboard.add(InlineKeyboardButton(text="Назад", 
                                                callback_data=MenuCallBack(to=MenuWays.menu.value).pack()))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()    


async def points_keyboard_build(subgroup_id, with_link = True, search=False, state = None) -> InlineKeyboardMarkup:
    local_keyboard = InlineKeyboardBuilder()
    areas_subgroup: AreaSubgroups = await AreaSubgroups.get(id=subgroup_id)
    areas_subgroup_count = await AreaSubgroups.filter(group_id=areas_subgroup.group_id).count()
    if not search:
        points = await ReceptionPoints.filter(area_id=subgroup_id)
        for point in points:
            link = None
            callback_data = None
            if with_link:
                link = point.link
            else:
                callback_data = PointCallBack(type_=ReviewStep.send_point.value, data=point.pk).pack()
            local_keyboard.add(InlineKeyboardButton(text=point.name, url=link, callback_data=callback_data))
    else: 
        local_keyboard.add(InlineKeyboardButton(text=f"Поиск", switch_inline_query_current_chat=""))
    if areas_subgroup_count > 1:
        local_keyboard.add(InlineKeyboardButton(text="Назад", 
                                                callback_data=PointCallBack(type_=ReviewStep.send_area_group.value, 
                                                                            data=-1).pack()))
    else:
        if not state:
            local_keyboard.add(InlineKeyboardButton(text="Назад", 
                                                    callback_data=MenuCallBack(to=MenuWays.menu.value).pack()))
        elif state == MenuState.hand_over:
            local_keyboard.add(InlineKeyboardButton(text="Назад", 
                                                    callback_data=MenuCallBack(to=MenuWays.hand_over.value).pack()))
        elif state == MenuState.feedback:
            local_keyboard.add(InlineKeyboardButton(text="Назад", 
                                                    callback_data=MenuCallBack(to=MenuWays.feedback.value).pack()))
        elif state == MenuState.union:
            local_keyboard.add(InlineKeyboardButton(text="Назад", 
                                                    callback_data=MenuCallBack(to=MenuWays.menu.value).pack()))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def orders_keyboard_build(data, user: TelegramUsers) -> InlineKeyboardMarkup:
    local_keyboard = InlineKeyboardBuilder()
    orders = []
    if data == MenuWays.in_work.value:
        orders = await Orders.filter(Q(paid_for=False, ready_issued=False, join_type="OR") & Q(complete=False) & Q(user_id=user.id)).order_by("-created_at").limit(20)
    elif data == MenuWays.ready.value:
        orders = await Orders.filter(paid_for=True, ready_issued=True, complete=False, user_id=user.id).order_by("-created_at").limit(20)
    elif data == MenuWays.complete.value:
        orders = await Orders.filter(complete=True, user_id=user.id).order_by("-created_at").limit(20)

    for order in orders:
        short_uuid_callback = shortdefault.encode(order.uuid)
        local_keyboard.add(InlineKeyboardButton(text=order.short_uuid, callback_data=OrderCallBack(to=short_uuid_callback).pack()))
    
    local_keyboard.add(InlineKeyboardButton(text="Назад", callback_data=MenuCallBack(to=MenuWays.orders.value).pack()))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def review_back_button(step: ReviewStep):
    if step != ReviewStep.menu:
        return InlineKeyboardButton(text="Назад", callback_data=PointCallBack(type_=step.value, data=-1).pack())
    else:
        return await back_button_build(menu_way=MenuWays.menu)


async def review_back_keyboard(step: ReviewStep):
    local_keyboard = InlineKeyboardBuilder()
    local_keyboard.add(await review_back_button(step))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def rate_review_keyboard():
    local_keyboard = InlineKeyboardBuilder()
    for rate in range(1, 6):
        local_keyboard.add(InlineKeyboardButton(text=str(rate), callback_data=PointCallBack(type_=ReviewStep.send_rate.value, data=rate).pack()))
    local_keyboard.add(await back_button_build(MenuWays.feedback))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def order_get_last(with_search, back_way = MenuWays.menu):
    local_keyboard = InlineKeyboardBuilder()
    if with_search:
        local_keyboard.add(InlineKeyboardButton(text="Выбор пункта", callback_data=MenuCallBack(to=MenuWays.issued_order.value).pack()))
    local_keyboard.add(InlineKeyboardButton(text="Назад", callback_data=MenuCallBack(to=back_way.value).pack()))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()


async def order_get_point(getting, points: Optional[list[ReceptionPoints]]):
    local_keyboard = InlineKeyboardBuilder()
    # if getting:
    #     local_keyboard.add(InlineKeyboardButton(text="Выбор пункта", callback_data=MenuCallBack(to=MenuWays.issued_order.value).pack()))

    # elif not getting and point:
    #     local_keyboard.add(InlineKeyboardButton(text=f"Пункт: {point.name}", 
    #                                             url=point.link))
    if points:
        for point in points:
            local_keyboard.add(InlineKeyboardButton(text=f"Пункт: {point.name}", 
                                                    url=point.link))
    local_keyboard.add(InlineKeyboardButton(text="Назад", callback_data=MenuCallBack(to=MenuWays.orders.value).pack()))
    local_keyboard.adjust(1)
    return local_keyboard.as_markup()