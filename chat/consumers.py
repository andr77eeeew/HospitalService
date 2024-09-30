import json
import logging
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import ChatRoom, ChatHistory

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']

        self.room = await sync_to_async(ChatRoom.objects.get)(name=self.room_name)
        if self.user.is_anonymous:
            await self.close()
        else:
            self.room_group_name = f'chat_{self.room_name}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            await self.send_history()
            logger.info(f"WebSocket connected for room '{self.room_name}'")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(
            f"WebSocket disconnected for room '{self.room_name}' with code {close_code}"
        )

    async def send_history(self):
        try:
            history = []
            async for messages in ChatHistory.objects.filter(room=self.room).order_by('timestamp').select_related(
                    'sender', 'room'):
                formatted_message = self.format_message(messages)
                history.append(formatted_message)
            await self.send(text_data=json.dumps({'type': 'chat_history', 'messages': history}))
        except Exception as e:
            logger.error(f"Error while sending history: {str(e)}")

    def format_message(self, message):
        return {
            'id': message.id,
            'sender': message.sender.id,
            'content': message.message,
            'media': message.media.url if message.media else None,
            'timestamp': message.timestamp.isoformat(),
            'replied_to': message.replied_to.message if message.replied_to else None,
            'is_edited': message.is_edited,
            'is_deleted': message.is_deleted,
        }

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'text')

        if message_type == 'text':
            await self.handle_text_message(data)
        else:
            pass

    async def handle_text_message(self, data):
        message = data['message']
        sender = self.scope['user']
        replied_to_id = data.get('replied_to', None)

        replied_to_message = None
        if replied_to_id:
            replied_to_message = await sync_to_async(ChatHistory.objects.get)(id=replied_to_id)

        new_message = await sync_to_async(ChatHistory.objects.create)(
            room=self.room,
            sender=sender,
            message=message,
            replied_to=replied_to_message
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'messages': self.format_message(new_message)
            }
        )

    async def chat_message(self, event):
        message = event['messages']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'messages': message
        }))
