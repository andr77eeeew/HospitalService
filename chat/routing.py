from django.urls import path

from chat import chat_consumers, notification_consumers

websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', chat_consumers.ChatConsumer.as_asgi()),
    path('ws/notification/', notification_consumers.NotificationConsumer.as_asgi()),
]
