from django.db import models


class AdminGroup(models.Model):
    group_id = models.BigIntegerField(null=False, unique=True, verbose_name="ID Группа")
    thread_id = models.BigIntegerField(null=True, unique=True, verbose_name="ID Обсуждения", blank=False)

    class Meta:
        db_table = "admin_group"
        verbose_name = "Группа админов бота"
        verbose_name_plural = "Группы админов бота"

    def __str__(self):
        return str(self.group_id)


class BotManagers(models.Model):
    manager_link = models.CharField(max_length=255, verbose_name="Ссылка на менеджера")
    manager_phone = models.CharField(max_length=255, verbose_name="Телефон менеджера")
    
    class Meta:
        db_table = "bot_managers"
        verbose_name = "Менеджер бота"
        verbose_name_plural = "Менеджеры бота"
        

class BotMessages(models.Model):
    message_name = models.CharField(max_length=255, unique=True, verbose_name="Название сообщения")
    display_name = models.CharField(max_length=255, unique=True, verbose_name="Отображаемое имя")
    text = models.TextField(max_length=1024, verbose_name="Текст сообщения")
    image = models.ImageField(null=True, blank=True, verbose_name="Изображение", upload_to="images/")
    video = models.FileField(null=True, blank=True, verbose_name="Видео", upload_to="videos/")

    class Meta:
        db_table = "bot_messages"
        verbose_name = "Сообщение бота"
        verbose_name_plural = "Сообщения бота"
    
    def __str__(self):
        return self.display_name


class BotStandartButtons(models.Model):
    contact = models.CharField(max_length=55, default="Поделиться контактом", 
                                verbose_name="Кнопка 'Поделиться контактом'")
    location = models.CharField(max_length=55, default="Поделиться местоположением", 
                                verbose_name="Кнопка 'Поделиться местоположением'")

    class Meta:
        db_table = "bot_standart_buttons"
        verbose_name = "Стандартные кнопки бота"
        verbose_name_plural = "Стандартные кнопки бота"
    
    def __str__(self):
        return "Стандартные кнопки бота"


# create model for bot buttons: materials_menu_button, ski_button, snowboard_button, materials_button, address_button,
# contact_button, get_phone_button, write_manager_button
# create model for bot buttons
class BotButtons(models.Model):
    button_name = models.CharField(max_length=255, unique=True, verbose_name="Название кнопки")
    display_name = models.CharField(max_length=255, unique=True, 
                                    null=True, blank=True, verbose_name="Отображаемое имя")
    text = models.CharField(max_length=55, default="Кнопка", verbose_name="Текст кнопки")

    class Meta:
        db_table = "bot_buttons"
        verbose_name = "Кнопка бота"
        verbose_name_plural = "Кнопки бота"
    
    def __str__(self):
        return self.display_name