from enum import Enum


class MenuWays(Enum):
    back = "back"
    menu = "menu"
    start = "start"
    info = "info"
    reg_begin = "reg_begin"
    get_fio = "get_fio"
    get_phone = "get_phone"
    get_email = "get_email"
    user_agreement = "user_agreement"
    subscribe = "subscribe"
    hand_over = "hand_over"
    orders = "orders"
    in_work = "in_work"
    ready = "ready"
    complete = "complete"
    points = "points"
    feedback = "feedback"
    feedbacks = "feedbacks"
    faq = "faq"
    contacts = "contacts"
    support = "support"
    issued_order = "issued"


class OrderStatus(str, Enum):
    created = "Создан"
    confirmed = "Подтвержден"
    cancelled = "Отменен"
    paid = "Оплачен"
    complete = "Завершен"


class BasicMenuKeyboards(Enum):
    main_menu = {"fields":[], 
                "menu_ways":[],}


class MessagesBuildType(Enum):
    data_not_found_message = ["data_not_found_message_text", "data_not_found_message_image", None]
    get_word_message = ["get_word_message_text", "get_word_message_image", None]
    search404_message = ["search404_message_text", "search404_message_image", None]
    error_spec_sumbols_message = ["error_spec_sumbols_message_text", "error_spec_sumbols_message_image", None]
    error_two_word_message = ["error_two_word_message_text", "error_two_word_message_image", None]


class SliderAction(Enum):
    next_ = 1
    back = -1
    start = 0

class SliderType(Enum):
    news = "news"
    about = "about"
    reviews = "rewiews"


class HandOverStep(Enum):
    choice_service = "cs"
    choice_type_item = "cti"
    choice_wear_treat = "cwt"
    choice_point = "cp"
    agree = "ag"
    del_type_item = "dti"
    choice_del_item = "cdi"
    agree_del = "adel"
    make_order = "mo"
    hand_over = "ho"



class HandOverBack(Enum):
    begin = "b"
    choice_service = "cs"
    choice_type_item = "cti"
    choice_wear_treat = "cwt"


class ReviewStep(Enum):
    menu = "m"
    send_area_group = "sag"
    send_area_subgroup = "sas"
    send_point = "sp"
    send_rate = "sr"
