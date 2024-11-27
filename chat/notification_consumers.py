import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q

from chat.models import ChatHistory, ChatRoom
from chat.utils import format_notification


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        try:
            self.user = self.scope['user']
            self.user_id = self.user.id
            self.notification_room_name = f'notification_{self.user_id}'

            if self.scope['user'].is_anonymous:
                await self.close()
            else:
                await self.channel_layer.group_add(
                    self.notification_room_name,
                    self.channel_name
                )
                await self.accept()

                await self.send_notifications()  # This line was changed

        except Exception as e:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.notification_room_name,
            self.channel_name
        )

    async def get_unread_messages(self):
        unread_messages = []
        async for messages in ChatHistory.objects.filter(
                room__in=ChatRoom.objects.filter(
                    Q(doctor=self.user) | Q(patient=self.user)
                ),
                read_status=False
        ).exclude(
            sender=self.user
        ).select_related('room').all():
            unread_messages.append(messages)
        return list(unread_messages) if unread_messages else None

    async def send_notifications(self):
        unread_messages = await self.get_unread_messages()
        if unread_messages:
            for message in unread_messages:
                await self.send(text_data=json.dumps({
                    'type': 'notification',
                    'notification': await format_notification(message)
                }))
        else:
            print("No unread messages")

    async def send_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification
        }))
