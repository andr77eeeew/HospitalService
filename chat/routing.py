from django.urls import path

from chat import chat_consumers, notification_consumers, conference_consumers

websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', chat_consumers.ChatConsumer.as_asgi()),
    path('ws/conference/<str:room_name>/', conference_consumers.ConferenceConsumer.as_asgi()),
    path('ws/notification/', notification_consumers.NotificationConsumer.as_asgi()),
]
