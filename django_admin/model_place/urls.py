from django.urls import path
from model_place.views import bitrix_webhook, tbank_notify

urlpatterns = [
    path('bitrix/', bitrix_webhook, name='bitrix_webhook'),
    path("tbank_notify/", tbank_notify, name="tbank_notify")
    # Другие пути
]