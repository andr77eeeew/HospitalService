import base64
import binascii
import json
import logging
from urllib.parse import urljoin
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from django.db.models import F

from HospitalSystem import settings
from chat.models import ChatRoom, ChatHistory

logger = logging.getLogger('chat')


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']

        self.room = await sync_to_async(ChatRoom.objects.get)(name=self.room_name)

        if self.user.is_anonymous:
            await self.close()
        else:
            active_users = await self.update_active_users(increment=True)

            self.room_group_name = f'chat_{self.room_name}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            await self.mark_unread_messages_as_read()

            await self.send_history()
            logger.info(f'Active users in room "{self.room_name}": {active_users}')

    async def disconnect(self, close_code):
        active_users = await self.update_active_users(increment=False)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        logger.info(f'Active users in room "{self.room_name}": {active_users}')

    async def update_active_users(self, increment=True):
        if increment:
            self.room.active_users = F('active_users') + 1
        else:
            self.room.active_users = F('active_users') - 1

        await sync_to_async(self.room.save)()

        updated_room = await sync_to_async(ChatRoom.objects.get)(name=self.room_name)
        logger.info(f'Active users in room "{self.room_name}": {updated_room.active_users}')

    async def mark_unread_messages_as_read(self):

        async for message in ChatHistory.objects.filter(
                room=self.room,
                read_status=False,
        ).select_related('sender'):

            if message.sender != self.user:
                message.read_status = True
                await sync_to_async(message.save)()

    async def send_history(self):
        try:
            history = []
            async for messages in (ChatHistory.objects.filter(room=self.room)
                    .order_by('timestamp')
                    .select_related('sender', 'room')):
                formatted_message = await sync_to_async(self.format_message)(messages)
                history.append(formatted_message)
            await self.send(text_data=json.dumps({'type': 'chat_history', 'messages': history}))
        except Exception as e:
            logger.error(f"Error while sending history: {str(e)}")

    def format_message(self, message):
        return {
            'id': message.id,
            'sender': message.sender.id,
            'content': message.message if message.message else None,
            'media': self.build_media_absolute_uri(message.media.url) if message.media else None,
            'timestamp': message.timestamp.isoformat(),
            'replied_to': message.replied_to.message if message.replied_to else None,
            'is_edited': message.is_edited,
            'is_deleted': message.is_deleted,
            'is_read': message.read_status,
        }

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

    async def create_notification(self, new_message):
        try:
            active_users = await sync_to_async(ChatRoom.objects.get)(name=self.room_name)
            logger.info(f"Количество активных пользователей в комнате {self.room_name}: {active_users.active_users}")

            if active_users.active_users == 1:
                logger.info("В комнате один пользователь.")
                other_user = await sync_to_async(
                    lambda: self.room.patient if self.scope['user'] == self.room.doctor else self.room.doctor)()
                logger.info(f"Отправляем уведомление пользователю {other_user.id}")

                notification_data = await sync_to_async(self.format_notification)(new_message)
                logger.info(f"Данные для уведомления: {notification_data}")

                await self.channel_layer.group_send(
                    f'notification_{other_user.id}',
                    {
                        'type': 'send_notification',
                        'notification': notification_data
                    }
                )
                logger.info(f"Уведомление отправлено в комнату уведомлений пользователя: notification_{other_user.id}")
            else:
                logger.info("В комнате больше одного пользователя, уведомление не требуется.")

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления пользователю: {e}")

    async def create_message(self, new_message):
        active_users = await sync_to_async(ChatRoom.objects.get)(name=self.room_name)

        if active_users.active_users == 2:
            new_message.read_status = True
            await sync_to_async(new_message.save)()

        formatted_message = await sync_to_async(self.format_message)(new_message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'messages': formatted_message
            }
        )
        logger.info(f"Message sent to WebSocket group of room: {self.room_group_name}")

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
        try:
            message = data['message']
            sender = self.scope['user']
            replied_to_id = data.get('replied_to', None)

            logger.info(f"User {sender.id} sent a text message to room {self.room_name}: {message}")

            replied_to_message = None
            if replied_to_id:
                try:
                    replied_to_message = await sync_to_async(ChatHistory.objects.get)(id=replied_to_id)
                    logger.info(f"Message {replied_to_id} found and attached as a reply.")
                except ChatHistory.DoesNotExist:
                    logger.error(f"Reply message with ID {replied_to_id} not found.")

            new_message = await sync_to_async(ChatHistory.objects.create)(
                room=self.room,
                sender=sender,
                message=message,
                replied_to=replied_to_message
            )
            logger.info(f"New message saved to database: {new_message.id}")

            await self.create_message(new_message)

        except Exception as e:
            logger.error(f"Error processing text message: {str(e)}")

    @staticmethod
    def validate_and_add_padding(base64_string):
        if len(base64_string) % 4 == 1:
            raise ValueError("Invalid base64 string length.")
        missing_padding = len(base64_string) % 4
        if missing_padding:
            base64_string += '=' * (4 - missing_padding)
        return base64_string

    async def handle_media_message(self, data):
        try:
            media_data = data['media']
            sender = self.scope['user']
            replied_to_id = data.get('replied_to', None)

            logger.info(f"Пользователь {sender.id} отправил медиа-сообщение в комнату {self.room_name}")

            media_data = await sync_to_async(self.validate_and_add_padding)(media_data)
            replied_to_message = None
            if replied_to_id:
                replied_to_message = await sync_to_async(ChatHistory.objects.get)(id=replied_to_id)
                logger.info(f"Сообщение {replied_to_id} было найдено и привязано как ответ для медиа-сообщения")

            try:
                media_file = ContentFile(base64.b64decode(media_data), name=f"media_{sender.id}.jpg")
                logger.info(f"Медиа-файл успешно создан для пользователя {sender.id}")
            except binascii.Error as e:
                error_message = f"Ошибка декодирования Base64 данных: {str(e)}"
                logger.error(error_message)
                raise ValueError(error_message)

            new_message = await sync_to_async(ChatHistory.objects.create)(
                room=self.room,
                sender=sender,
                media=media_file,
                message='',
                replied_to=replied_to_message
            )

            await self.create_message(new_message)

        except Exception as e:
            logger.error(f"Ошибка при обработке медиа-сообщения: {str(e)}")

    async def handle_edit_message(self, data):
        message_id = data['message_id']
        new_message = data['new_message']

        message = await sync_to_async(ChatHistory.objects.get)(id=message_id)
        message.message = new_message
        message.is_edited = True
        await sync_to_async(message.save)()

        formatted_message = await sync_to_async(self.format_message)(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'edit_message',
                'messages': formatted_message
            }
        )

    async def handle_delete_message(self, data):
        message_id = data['message_id']

        message = await sync_to_async(ChatHistory.objects.get)(id=message_id)
        message.is_deleted = True
        await sync_to_async(message.save)()

        formatted_message = await sync_to_async(self.format_message)(message)

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