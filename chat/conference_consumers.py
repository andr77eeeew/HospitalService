import json

from channels.generic.websocket import AsyncWebsocketConsumer
import logging

from django.db.models import F

from chat.models import ChatRoom

logger = logging.getLogger('chat')


class ConferenceConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']

        self.room = await ChatRoom.objects.aget(name=self.room_name)
        logger.info(
            f"User {self.user.first_name} {self.user.last_name} is connected to conference room {self.room_name} active users {self.room.active_users}")

        if self.user.is_anonymous:
            logger.warning("Анонимный пользователь попытался подключиться")
            await self.close()
        else:
            self.room_group_name = f'conference_{self.room_name}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            active_users = await self.update_active_users(increment=True)

            logger.info(f'Active users in room conference "{self.room_name}": {active_users}')

    async def update_active_users(self, increment=True):
        try:
            if increment:
                self.room.active_voice_users = F('active_voice_users') + 1
            else:
                self.room.active_voice_users = F('active_voice_users') - 1

            await self.room.asave()

            updated_room = await ChatRoom.objects.aget(name=self.room_name)
            logger.info(f'Active users in room "{self.room_name}": {updated_room.active_voice_users}')

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'active_users',
                    'users': updated_room.active_voice_users,
                }
            )
            logger.info(f'Sending active users count')
            return updated_room.active_voice_users
        except Exception as e:
            logger.error(f"Error while updating active users: {str(e)}")

    async def disconnect(self, close_code):
        active_users = await self.update_active_users(increment=False)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        logger.info(f'Active users in conference room "{self.room_name}": {active_users}')

    async def receive(self, text_data):
        logger.info(f"Получен сообщение: {text_data}")
        try:
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
                logger.info(f"Получен оффер: {sdp_offer}")
                await self.send_offers(sdp_offer)
            elif type == 'answer':
                sdp_answer = text_data_json.get('sdp')
                logger.info(f"Получен ответ: {sdp_answer}")
                await self.send_answers(sdp_answer)
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")

    async def send_signals(self, signal):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'signal',
                'signal': signal if signal else None,
            }
        )

    async def send_signal(self, event):
        logger.info(f'Обработка сигнального сообщения: {event}')
        try:
            signal = event['signal']
            logger.info(f'Получен сигнал: signal={signal}')

            await self.send(json.dumps({
                'type': 'signal',
                'signal': signal,
            }))
        except Exception as e:
            logger.error(f'Ошибка при отправке сигнала: {e}')

    async def send_offers(self, sdp):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_offer',
                'offer': sdp if sdp else None,
            }
        )

    async def send_offer(self, event):
        logger.info(f"Обработка оффера: {event}")
        try:
            offer = event['offer']
            logger.info(f"Получен оффер: offer={offer}")

            await self.send(json.dumps({
                'type': 'offer',
                'sdp': offer,
            }))
        except Exception as e:
            logger.error(f"Ошибка при отправке оффера: {e}")

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
        logger.info(f"Обработка ответа: {event}")
        try:
            answer = event['answer']
            logger.info(f"Получен ответ: answer={answer}")

            await self.send(json.dumps({
                'type': 'answer',
                'sdp': answer,
            }))
        except Exception as e:
            logger.error(f"Ошибка при отправке ответа: {e}")

    async def ice_candidate(self, event):
        logger.info(f"Обработка ICE кандидата: {event}")
        try:
            candidate = event['candidate']
            logger.info(f"Получен ICE кандидат: candidate={candidate}")

            await self.send(json.dumps({
                'type': 'ice_candidate',
                'candidate': candidate,
            }))
        except Exception as e:
            logger.error(f"Ошибка при отправке ICE кандидата: {e}")

    async def active_users(self, event):
        try:
            active_voice_users = event['users']
            await self.send(json.dumps({
                'type': 'active_users',
                'users': active_voice_users
            }))
            logger.info('Active users count sended')
        except Exception as e:
            logger.error(f"Error while sending active users: {str(e)}")
