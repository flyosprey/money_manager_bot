from django.urls import path

from .views import GithubWebhookView, MonobankWebhookView, TelegramWebhookView

urlpatterns = [
    path("get_tel_hook/", TelegramWebhookView.as_view(), name="get_tel_hook"),
    path(
        "handle_mono_webhook/<str:encrypted_user_id>",
        MonobankWebhookView.as_view(),
        name="handle_mono_webhook",
    ),
    path("deploy/", GithubWebhookView.as_view(), name="deploy"),
]
