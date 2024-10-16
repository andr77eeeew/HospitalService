import json
import logging
from urllib.parse import urljoin

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q

from HospitalSystem import settings
from chat.models import ChatHistory, ChatRoom

logger = logging.getLogger('notification')


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        try:
            self.user = self.scope['user']
            self.user_id = self.user.id
            self.notification_room_name = f'notification_{self.user_id}'

            logger.info(f"Попытка подключения пользователя {self.user_id}")

            if self.scope['user'].is_anonymous:
                logger.warning("Анонимный пользователь попытался подключиться")
                await self.close()
            else:
                await self.channel_layer.group_add(
                    self.notification_room_name,
                    self.channel_name
                )
                logger.info(f"Пользователь {self.user_id} добавлен в группу {self.notification_room_name}")
                await self.accept()

                await self.send_notifications()  # This line was changed

        except Exception as e:
            logger.error(f"Ошибка при подключении пользователя {self.user_id}: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.notification_room_name,
                self.channel_name
            )
            logger.info(f"Пользователь {self.user_id} отключен от группы {self.notification_room_name}")
        except Exception as e:
            logger.error(f"Ошибка при отключении пользователя {self.user_id}: {e}")

    def format_notification(self, message):
        sender = message.sender
        room = message.room
        return {
            'room_name': room.name,
            'sender_id': sender.id,
            'sender_name': f"{sender.first_name} {sender.last_name}",
            'sender_avatar': self.build_media_absolute_uri(sender.avatar.url) if sender.avatar else None,
            'content': message.message if message.message else None,
            'media': self.build_media_absolute_uri(message.media.url) if message.media else None,
            'timestamp': message.timestamp.isoformat(),
        }

    @database_sync_to_async
    def get_unread_messages(self):
        user_rooms = ChatRoom.objects.filter(
            Q(doctor=self.user) | Q(patient=self.user)
        )
        unread_messages = ChatHistory.objects.filter(
            room__in=user_rooms,
            read_status=False
        ).exclude(
            sender=self.user
        )
        return unread_messages if unread_messages else []

    async def send_notifications(self, event=None):
        try:
            unread_messages = await self.get_unread_messages()
            if unread_messages:
                for message in unread_messages:
                    await self.send(text_data=json.dumps({
                        'type': 'notification',
                        'notification': await sync_to_async(self.format_notification)(message)
                    }))
            else:
                logger.info(f"Нет непрочитанных сообщений для пользователя {self.user_id}")

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления для пользователя {self.user_id}: {e}")

    async def send_notification(self, event):
        try:
            notification = event['notification']
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': notification
            }))
            logger.info(f"Отправлено уведомление для пользователя: {notification}")

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления пользователю: {e}")

    def build_media_absolute_uri(self, media_url):
        base_url = f"http://{settings.ALLOWED_HOSTS[0]}:8000" if settings.ALLOWED_HOSTS else "http://localhost:8000"
        return urljoin(base_url, media_url)
