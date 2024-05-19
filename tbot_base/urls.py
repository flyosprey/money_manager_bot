from django.urls import path

from .views import MonobankWebhookView, TelegramWebhookView

urlpatterns = [
    path("get_tel_hook/", TelegramWebhookView.as_view(), name="get_tel_hook"),
    path("handle_mono_webhook/<int:chat_id>/", MonobankWebhookView.as_view(), name="handle_mono_webhook"),
]
