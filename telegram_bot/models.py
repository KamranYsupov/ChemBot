from tortoise import Model, fields


class DjangoMigrations(Model):
    id = fields.IntField(pk=True, )
    app = fields.CharField(max_length=255, )
    name = fields.CharField(max_length=255, )
    applied = fields.DatetimeField()


    class Meta:
        table='django_migrations'


class DjangoContentType(Model):
    id = fields.IntField(pk=True, )
    app_label = fields.CharField(max_length=100, )
    model = fields.CharField(max_length=100, )


    class Meta:
        table='django_content_type'


class AuthPermission(Model):
    id = fields.IntField(pk=True, )
    name = fields.CharField(max_length=255, )
    content_type_id = fields.IntField()
    codename = fields.CharField(max_length=100, )


    class Meta:
        table='auth_permission'


class AuthGroup(Model):
    id = fields.IntField(pk=True, )
    name = fields.CharField(max_length=150, )


    class Meta:
        table='auth_group'


class AuthGroupPermissions(Model):
    id = fields.IntField(pk=True, )
    group_id = fields.IntField()
    permission_id = fields.IntField()


    class Meta:
        table='auth_group_permissions'


class AuthUser(Model):
    id = fields.IntField(pk=True, )
    password = fields.CharField(max_length=128, )
    last_login = fields.DatetimeField(null=True, )
    is_superuser = fields.BooleanField()
    username = fields.CharField(max_length=150, )
    first_name = fields.CharField(max_length=150, )
    last_name = fields.CharField(max_length=150, )
    email = fields.CharField(max_length=254, )
    is_staff = fields.BooleanField()
    is_active = fields.BooleanField()
    date_joined = fields.DatetimeField()


    class Meta:
        table='auth_user'


class AuthUserGroups(Model):
    id = fields.IntField(pk=True, )
    user_id = fields.IntField()
    group_id = fields.IntField()


    class Meta:
        table='auth_user_groups'


class AuthUserUserPermissions(Model):
    id = fields.IntField(pk=True, )
    user_id = fields.IntField()
    permission_id = fields.IntField()


    class Meta:
        table='auth_user_user_permissions'


class DjangoAdminLog(Model):
    id = fields.IntField(pk=True, )
    action_time = fields.DatetimeField()
    object_id = fields.TextField(null=True, )
    object_repr = fields.CharField(max_length=200, )
    action_flag = fields.SmallIntField()
    change_message = fields.TextField()
    content_type_id = fields.IntField(null=True, )
    user_id = fields.IntField()


    class Meta:
        table='django_admin_log'


class AdminGroup(Model):
    id = fields.IntField(pk=True, )
    group_id = fields.IntField()
    thread_id = fields.IntField(null=True, )


    class Meta:
        table='admin_group'


class BotButtons(Model):
    id = fields.IntField(pk=True, )
    button_name = fields.CharField(max_length=255, )
    display_name = fields.CharField(max_length=255, null=True, )
    text = fields.CharField(max_length=55, )


    class Meta:
        table='bot_buttons'


class BotManagers(Model):
    id = fields.IntField(pk=True, )
    manager_link = fields.CharField(max_length=255, )
    manager_phone = fields.CharField(max_length=255, )


    class Meta:
        table='bot_managers'


class BotMessages(Model):
    id = fields.IntField(pk=True, )
    message_name = fields.CharField(max_length=255, )
    display_name = fields.CharField(max_length=255, )
    text = fields.TextField()
    image = fields.CharField(max_length=100, null=True, )
    video = fields.CharField(max_length=100, null=True, )


    class Meta:
        table='bot_messages'


class BotStandartButtons(Model):
    id = fields.IntField(pk=True, )
    contact = fields.CharField(max_length=55, )
    location = fields.CharField(max_length=55, )


    class Meta:
        table='bot_standart_buttons'


class Mailings(Model):
    id = fields.IntField(pk=True, )
    content = fields.TextField()
    image = fields.CharField(max_length=100, null=True, )
    video = fields.CharField(max_length=100, null=True, )
    mail_date = fields.DateField()
    mail_time = fields.TimeField()
    it_send = fields.BooleanField()


    class Meta:
        table='mailings'


class TelegramUsers(Model):
    id = fields.IntField(pk=True, )
    telegram_id = fields.IntField()
    fio = fields.CharField(max_length=550, )
    phone = fields.CharField(max_length=555, )
    email = fields.CharField(max_length=555, null=True, )
    subscription = fields.BooleanField()
    bitrix_contact_id = fields.IntField(null=True, )


    class Meta:
        table='telegram_users'


class Basket(Model):
    uuid = fields.UUIDField(pk=True, )
    created_at = fields.DatetimeField()
    old = fields.BooleanField()
    user_id = fields.IntField()


    class Meta:
        table='basket'


class AreaGroups(Model):
    id = fields.IntField(pk=True, )
    name = fields.CharField(max_length=55, )


    class Meta:
        table='area_groups'


class AreaSubgroups(Model):
    id = fields.IntField(pk=True, )
    name = fields.CharField(max_length=55, )
    group_id = fields.IntField()


    class Meta:
        table='area_subgroups'


class ItemTypes(Model):
    id = fields.IntField(pk=True, )
    name = fields.CharField(max_length=55, )


    class Meta:
        table='item_types'


class ItemsServices(Model):
    id = fields.IntField(pk=True, )
    item_id = fields.IntField()
    service_id = fields.IntField()


    class Meta:
        table='items_services'


class Services(Model):
    id = fields.IntField(pk=True, )
    name = fields.CharField(max_length=120, )
    price = fields.DecimalField(max_digits=10, decimal_places=2, )


    class Meta:
        table='services'


class UserItems(Model):
    uuid = fields.UUIDField(pk=True, )
    count = fields.IntField()
    old = fields.BooleanField()
    basket_id = fields.UUIDField()
    item_type_id = fields.IntField()
    point_id = fields.IntField(null=True, )
    service_id = fields.IntField(null=True, )
    user_id = fields.IntField()


    class Meta:
        table='user_items'


class DjangoSession(Model):
    session_key = fields.CharField(pk=True, max_length=40, )
    session_data = fields.TextField()
    expire_date = fields.DatetimeField()


    class Meta:
        table='django_session'


class ReceptionPoints(Model):
    id = fields.IntField(pk=True, )
    name = fields.CharField(max_length=55, )
    link = fields.CharField(max_length=2055, )
    area_id = fields.IntField()
    icon = fields.CharField(max_length=100, null=True, )


    class Meta:
        table='reception_points'


class Orders(Model):
    uuid = fields.UUIDField(pk=True, )
    short_uuid = fields.CharField(max_length=40, null=True, )
    request_number = fields.CharField(max_length=255, null=True, )
    amount = fields.DecimalField(max_digits=10, decimal_places=2, null=True, )
    additional_amount = fields.DecimalField(max_digits=10, decimal_places=2, null=True, )
    order_status = fields.CharField(max_length=255, )
    paid_for = fields.BooleanField()
    ready_issued = fields.BooleanField()
    complete = fields.BooleanField()
    plomb_photo = fields.CharField(max_length=100, null=True, )
    plomb_data = fields.TextField(null=True, )
    order_data = fields.TextField(null=True, )
    created_at = fields.DatetimeField()
    basket_id = fields.UUIDField()
    issued_point_id = fields.IntField(null=True, )
    user_id = fields.IntField()
    external_order_information = fields.TextField(null=True, )
    order_link = fields.TextField(null=True, )


    class Meta:
        table='orders'