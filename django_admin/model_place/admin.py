from django.contrib import admin
from model_place.models import *
from model_place.forms import MailingsForm

# Register your models here

class MailingsAdmin(admin.ModelAdmin):
    form = MailingsForm
    list_display = ('content', 'mail_date', 'mail_time', "it_send")

class OrdersAdmin(admin.ModelAdmin):
    list_display = ("uuid", "short_uuid", "request_number")

admin.site.register(TelegramUsers)
admin.site.register(UserItems)
admin.site.register(Basket)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(Mailings, MailingsAdmin)
admin.site.register(AreaGroups)
admin.site.register(AreaSubgroups)
admin.site.register(ReceptionPoints)
admin.site.register(ItemTypes)
admin.site.register(Services)