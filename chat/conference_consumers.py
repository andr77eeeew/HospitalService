import json

from channels.generic.websocket import AsyncWebsocketConsumer

from django.db.models import F

from chat.models import ChatRoom


class ConferenceConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']

        self.room = await ChatRoom.objects.aget(name=self.room_name)

        if self.user.is_anonymous:
            await self.close()
        else:
            self.room_group_name = f'conference_{self.room_name}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            active_users = await self.update_active_users(increment=True)

    async def update_active_users(self, increment=True):
        if increment:
            self.room.active_voice_users = F('active_voice_users') + 1
        else:
            self.room.active_voice_users = F('active_voice_users') - 1
        await self.room.asave()

        updated_room = await ChatRoom.objects.aget(name=self.room_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'active_users',
                'users': updated_room.active_voice_users,
            }
        )
        return updated_room.active_voice_users

    async def disconnect(self, close_code):
        active_users = await self.update_active_users(increment=False)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json.get('type')
        if type == 'signal':
            signal = text_data_json.get('signal')
            await self.send_signals(signal)
        elif type == 'ice_candidate':
            candidate = text_data_json.get('candidate')
            await self.send_ice_candidate(candidate)
        elif type == 'offer':
            sdp_offer = text_data_json.get('sdp')
            await self.send_offers(sdp_offer)
        elif type == 'answer':
            sdp_answer = text_data_json.get('sdp')
            await self.send_answers(sdp_answer)

    async def send_signals(self, signal):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'signal',
                'signal': signal if signal else None,
            }
        )

    async def send_signal(self, event):
        signal = event['signal']

        await self.send(json.dumps({
            'type': 'signal',
            'signal': signal,
        }))

    async def send_offers(self, sdp):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_offer',
                'offer': sdp if sdp else None,
            }
        )

    async def send_offer(self, event):
        offer = event['offer']

        await self.send(json.dumps({
            'type': 'offer',
            'sdp': offer,
        }))

    async def send_ice_candidate(self, candidate):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'ice_candidate',
                'candidate': candidate,
            }
        )

    async def send_answers(self, sdp):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_answer',
                'answer': sdp if sdp else None,
            }
        )

    async def send_answer(self, event):
        answer = event['answer']

        await self.send(json.dumps({
            'type': 'answer',
            'sdp': answer,
        }))

    async def ice_candidate(self, event):
        candidate = event['candidate']

        await self.send(json.dumps({
            'type': 'ice_candidate',
            'candidate': candidate,
        }))

    async def active_users(self, event):
        active_voice_users = event['users']

        await self.send(json.dumps({
            'type': 'active_users',
            'users': active_voice_users
        }))
