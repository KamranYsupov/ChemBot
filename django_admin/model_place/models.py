from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from bitrix24 import Bitrix24
from tbank_kassa_api.tbank_client import TClient
from tbank_kassa_api.tbank_models import NotificationPayment
from tbank_kassa_api.enums import PaymentStatus
from tbank_kassa_api.send_models import Init
from tbank_kassa_api.tbank_models import *
from telebot import TeleBot, types

import uuid
import shortuuid


# model for request users
class TelegramUsers(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    fio = models.CharField(max_length=550, verbose_name="ФИО")
    phone = models.CharField(max_length=555, verbose_name="Телефон")
    email = models.CharField(max_length=555, verbose_name="Email", null=True, default=None)
    subscription = models.BooleanField(default=False, verbose_name="Подписка")
    bitrix_contact_id = models.BigIntegerField(unique=True, null=True, default=None)
    
    class Meta:
        db_table = "telegram_users"
        verbose_name = "Пользователь Telegram"
        verbose_name_plural = "Пользователи Telegram"

    def __str__(self):
        return self.fio


class Basket(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False)
    user = models.ForeignKey(TelegramUsers, on_delete=models.CASCADE, 
                                related_name="user_basket", verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    old = models.BooleanField(default=False, verbose_name="Старый")

    class Meta:
        db_table = "basket"
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
    
    def __str__(self):
        return f"{self.user} - {'Старая' if self.old else 'Новая'} корзина"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = uuid.uuid4()
        super().save(*args, **kwargs)


class ItemTypes(models.Model):
    name = models.CharField(max_length=55, verbose_name="Тип товара")
    
    class Meta:
        db_table = "item_types"
        verbose_name = "Тип товара"
        verbose_name_plural = "Типы товаров"
    
    def __str__(self):
        return self.name


class Services(models.Model):
    name = models.CharField(max_length=120, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, 
                                verbose_name="Цена", default=0, editable=False)

    class Meta:
        db_table = "services"
        verbose_name = "Доп Услуга"
        verbose_name_plural = "Доп Услуги"

    def __str__(self):
        return self.name


class ItemsServices(models.Model):
    item = models.ForeignKey(ItemTypes, on_delete=models.CASCADE, )
    service = models.ForeignKey(Services, on_delete=models.CASCADE, )

    class Meta:
        db_table = "items_services"
        verbose_name = "Предмет-Доп.услуга"
        verbose_name_plural = "Предметы-Доп.услуги"
    
    def __str__(self):
        return f"{self.item} - {self.service}"

class AreaGroups(models.Model):
    name = models.CharField(max_length=55, verbose_name="Название")

    class Meta:
        db_table = "area_groups"
        verbose_name = "Группа областей"
        verbose_name_plural = "Группы областей"
    
    def __str__(self):
        return self.name


class AreaSubgroups(models.Model):
    name = models.CharField(max_length=55, verbose_name="Название")
    group = models.ForeignKey(AreaGroups, on_delete=models.CASCADE, 
                                related_name="group_subgroups", verbose_name="Группа")

    class Meta:
        db_table = "area_subgroups"
        verbose_name = "Подгруппа областей"
        verbose_name_plural = "Подгруппы областей"
    
    def __str__(self):
        return self.name


class ReceptionPoints(models.Model):
    name = models.CharField(max_length=55, verbose_name="Название")
    link = models.URLField(max_length=2055, verbose_name="Ссылка")
    area = models.ForeignKey(AreaSubgroups, on_delete=models.CASCADE, 
                                related_name="reception_points_area", verbose_name="Область")
    icon = models.ImageField(null=True, blank=True, verbose_name="Иконка", upload_to="recept_icon/")

    class Meta:
        db_table = "reception_points"
        verbose_name = "Пункт приема"
        verbose_name_plural = "Пункты приема"
    
    def __str__(self):
        return self.name


class UserItems(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False)
    user = models.ForeignKey(TelegramUsers, on_delete=models.CASCADE, related_name="user_items", 
                                verbose_name="Пользователь")
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="basket_items", 
                                verbose_name="Корзина")
    item_type = models.ForeignKey(ItemTypes, on_delete=models.CASCADE, related_name="item_type_items", 
                                    verbose_name="Тип товара")
    service = models.ForeignKey(Services, on_delete=models.CASCADE, related_name="services_items", 
                                verbose_name="Сервис", null=True, blank=False)
    point = models.ForeignKey(ReceptionPoints, on_delete=models.CASCADE, related_name="points_items", 
                                verbose_name="Точка", null=True, blank=False)
    count = models.IntegerField(default=1, verbose_name="Количество")
    old = models.BooleanField(default=False, verbose_name="Старый")

    class Meta:
        db_table = "user_items"
        verbose_name = "Товар пользователя"
        verbose_name_plural = "Товары пользователей"
    
    def __str__(self):
        return str(self.uuid)
    
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)


class Orders(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False)
    short_uuid = models.CharField(max_length=40, editable=False, 
                                    verbose_name="Короткий идентификатор", null=True, blank=True)
    request_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Номер заявки")
    user = models.ForeignKey(TelegramUsers, on_delete=models.CASCADE, 
                                related_name="user_orders", verbose_name="Пользователь")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Сумма")
    additional_amount = models.DecimalField(max_digits=10, decimal_places=2, 
                                            null=True, blank=True, verbose_name="Доп.сумма", 
                                            default=0, editable=False)
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, 
                                related_name="basket_orders", verbose_name="Корзина")
    issued_point = models.ForeignKey(ReceptionPoints, on_delete=models.SET_NULL, 
                                    related_name="issued_point_orders", verbose_name="Точка выдачи", null=True, blank=True)
    order_status = models.CharField(max_length=255, verbose_name="Статус заказа")
    paid_for = models.BooleanField(default=False, verbose_name="Оплачен")
    ready_issued = models.BooleanField(default=False, verbose_name="Готов к выдаче")
    complete = models.BooleanField(default=False, verbose_name="Завершен")
    external_order_information = models.TextField(verbose_name="Внешняя информация заказа", editable=False, null=True, default="")
    order_link = models.TextField(verbose_name="Сслыка на оплату заказа", editable=False, null=True, default="")
    plomb_photo = models.ImageField(null=True, blank=True, 
                                    verbose_name="Изображение пломбы", upload_to="orders/")
    plomb_data = models.TextField(null=True, blank=True, verbose_name="Данные пломбы")
    order_data = models.TextField(null=True, blank=True, verbose_name="Данные заказа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        db_table = "orders"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
    
    def __str__(self):
        return str(self.uuid)
    
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        
        if not self.short_uuid:
            self.short_uuid = settings.SHOTRNUMBERS_UUID.encode(self.uuid)[:15]
        
        if not self.paid_for and self.amount:
            points = set()
            user = self.user
            user_tg_id = user.telegram_id
            order_shortuuid = shortuuid.encode(self.pk)
            client = settings.REDIS_CLIENT
            bot = settings.TELEGRAM_BOT
            local_tbank_client: TClient = settings.TBANK_CLIENT
            items: UserItems = UserItems.objects.filter(basket_id=self.basket_id)
            service_text: str = self.order_data


            if not service_text:
                service_text = "Данные заказа:\n"

                for item in items:
                    item_type = ItemTypes.objects.get(id=item.item_type_id)
                    service = None
                    if item.service_id:
                        service = Services.objects.get(id=item.service_id)
                    point = ReceptionPoints.objects.get(id=item.point_id)
                    points.add(point)
                    second_part = ""
                    if service:
                        second_part = f"| {service.name} |"
                    else:
                        second_part = "|"
                    second_part += f" {point.name} x{item.count}"
                    service_text_row = f"\n{item_type.name} {second_part}"
                    service_text = service_text_row.replace("\n", ' ')


            elif service_text:
                text = "Общая информация по заказу:"
                text += "\nКоличество вещей в заказе:\n"
                service_text.replace(
                    text, ""
                )
                service_text = "\nДанные заказа:\n" + service_text

            if not self.order_link:
                phone = user.phone
                phone = phone.strip("+")
                if phone.startswith("8") or phone.startswith("7"):
                    phone = "+7"+phone[1:]

                amount_sell = int(self.amount) * 100
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

                exp = timezone.now() + timedelta(days=20)
                model = Init(
                    OrderId = str(self.uuid),
                    Amount = amount_sell,
                    Description = service_text,
                    CustomerKey = str(user.pk),
                    NotificationURL = settings.SITE_HOST + "/tbank_notify/",
                    Receipt = receipt,
                    RedirectDueDate = exp.isoformat(timespec='seconds')
                )
                response = local_tbank_client.sync_send_model(model)
                payment_url = ""
                if response.get("Success"):
                    payment_url = response.get("PaymentURL")
                else:
                    super().save(*args, **kwargs)
                    return
                self.order_link = payment_url

            local_keyboard = types.InlineKeyboardMarkup()
            local_keyboard.add(
                types.InlineKeyboardButton(text="Перейти к оплате", url=self.order_link )#,web_app=types.WebAppInfo(url=payment_url)),
            )
            message = bot.send_message(user_tg_id, 
                                        f"Получены данные о сумме заказа: {self.short_uuid}, пожалуйста оплатите его.\n"+service_text, 
                                        reply_markup=local_keyboard)
            client.set(f"user_last_message:{user_tg_id}", str(message.message_id))
            
        super().save(*args, **kwargs)


class Mailings(models.Model):
    content = models.TextField(verbose_name="Содержание")
    image = models.ImageField(verbose_name="Изображение", null=True, blank=True, upload_to="mailings/")
    video = models.FileField(verbose_name="Видео", null=True, blank=True, upload_to="mailings/")
    mail_date = models.DateField(verbose_name="Дата рассылки")
    mail_time = models.TimeField(verbose_name="Время рассылки")
    it_send = models.BooleanField(verbose_name="Рассылка отправлена", default=False)

    class Meta:
        db_table = "mailings"
        verbose_name = "рассылки"
        verbose_name_plural = "Рассылки"
    def __str__(self):
        return self.content[0:50]