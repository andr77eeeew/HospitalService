import base64
import binascii
import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from django.db.models import F

from chat.models import ChatRoom, ChatHistory
from chat.utils import format_message, format_notification


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']

        self.room = await ChatRoom.objects.aget(name=self.room_name)

        if self.user.is_anonymous:
            await self.close()
        else:
            await self.update_active_users(increment=True)

            self.room_group_name = f'chat_{self.room_name}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            await self.mark_unread_messages_as_read()

            await self.send_history()

    async def disconnect(self, close_code):
        await self.update_active_users(increment=False)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def update_active_users(self, increment=True):
        if increment:
            self.room.active_users = F('active_users') + 1
        else:
            self.room.active_users = F('active_users') - 1

        await self.room.asave()

        updated_room = await ChatRoom.objects.aget(name=self.room_name)

        return updated_room.active_users

    async def mark_unread_messages_as_read(self):
        active_users = await ChatRoom.objects.aget(name=self.room_name)
        async for message in ChatHistory.objects.filter(
                room=self.room,
                read_status=False,
        ).select_related('sender', 'room', 'replied_to'):

            if message.sender != self.user:
                message.read_status = True
                await message.asave()
                if active_users.active_users == 2:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'update_status',
                            'id': message.id,
                            "read_status:": True,
                        }
                    )

    async def send_history(self):
        history = []
        async for messages in (ChatHistory.objects.filter(room=self.room)
                .order_by('timestamp')
                .select_related('sender', 'room', 'replied_to')):
            formatted_message = await format_message(messages)
            history.append(formatted_message)
        await self.send(text_data=json.dumps({'type': 'chat_history', 'messages': history}))

    async def create_notification(self, new_message):
        active_users = await ChatRoom.objects.aget(name=self.room_name)

        if active_users.active_users == 1:
            other_user = await sync_to_async(
                lambda: self.room.patient if self.scope['user'] == self.room.doctor else self.room.doctor)()

            notification_data = await format_notification(new_message)

            await self.channel_layer.group_send(
                f'notification_{other_user.id}',
                {
                    'type': 'send_notification',
                    'notification': notification_data
                }
            )

    async def create_message(self, new_message):
        active_users = await ChatRoom.objects.aget(name=self.room_name)

        if active_users.active_users == 2:
            new_message.read_status = True
            await new_message.asave()

        formatted_message = await format_message(new_message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'messages': formatted_message
            }
        )

        await self.create_notification(new_message)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'text')

        if message_type == 'text':
            await self.handle_text_message(data)
        elif message_type == 'media':
            await self.handle_media_message(data)
        elif message_type == 'edit':
            await self.handle_edit_message(data)
        elif message_type == 'delete':
            await self.handle_delete_message(data)

    async def handle_text_message(self, data):
        message = data['message']
        sender = self.scope['user']
        replied_to_id = data.get('replied_to', None)

        replied_to_message = None
        if replied_to_id:
            replied_to_message = await ChatHistory.objects.aget(id=replied_to_id)

        new_message = await ChatHistory.objects.acreate(
            room=self.room,
            sender=sender,
            message=message,
            replied_to=replied_to_message
        )

        await self.create_message(new_message)

    @staticmethod
    def validate_and_add_padding(base64_string):
        if len(base64_string) % 4 == 1:
            raise ValueError("Invalid base64 string length.")
        missing_padding = len(base64_string) % 4
        if missing_padding:
            base64_string += '=' * (4 - missing_padding)
        return base64_string

    async def handle_media_message(self, data):
        media_data = data['media']
        file_name = data.get('file_name', None)
        file_type = data.get('file_type', None)
        sender = self.scope['user']
        replied_to_id = data.get('replied_to', None)

        media_data = await sync_to_async(self.validate_and_add_padding)(media_data)

        replied_to_message = None
        if replied_to_id:
            replied_to_message = await ChatHistory.objects.aget(id=replied_to_id)

        media_file = ContentFile(base64.b64decode(media_data), name=f"{file_name}")

        new_message = await ChatHistory.objects.acreate(
            room=self.room,
            sender=sender,
            media=media_file,
            file_type=file_type,
            message='',
            replied_to=replied_to_message
        )

        await self.create_message(new_message)

    async def handle_edit_message(self, data):
        message_id = data['message_id']
        new_message = data['new_message']

        message = await ChatHistory.objects.aget(id=message_id)
        message.message = new_message
        message.is_edited = True
        await message.asave()

        formatted_message = await format_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'edit_message',
                'messages': formatted_message
            }
        )

    async def handle_delete_message(self, data):
        message_id = data['message_id']

        message = await ChatHistory.objects.aget(id=message_id)
        message.is_deleted = True
        await message.asave()

        formatted_message = await format_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'delete_message',
                'messages': formatted_message
            }
        )

    async def chat_message(self, event):
        message = event['messages']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'messages': message
        }))

    async def delete_message(self, event):
        message = event['messages']

        await self.send(text_data=json.dumps({
            'type': 'delete_message',
            'messages': message
        }))

    async def edit_message(self, event):
        message = event['messages']

        await self.send(text_data=json.dumps({
            'type': 'edit_message',
            'messages': message
        }))

    async def update_status(self, event):
        id = event['id']
        read_status = event['read_status:']

        await self.send(text_data=json.dumps({
            'type': 'update_status',
            'id': id,
            "read_status:": read_status
        }))

    async def send_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification
        }))
