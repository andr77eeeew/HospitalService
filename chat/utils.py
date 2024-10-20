from urllib.parse import urljoin

from asgiref.sync import sync_to_async

from HospitalSystem import settings

import logging

logger = logging.getLogger('chat')


def build_media_absolute_uri(media_url):
    base_url = f"http://{settings.ALLOWED_HOSTS[0]}:8000" if settings.ALLOWED_HOSTS else "http://localhost:8000"
    return urljoin(base_url, media_url)


@sync_to_async
def format_notification(message):
    sender = message.sender
    room = message.room
    logger.info(f"Форматируем уведомление: {message}")
    return {
        'room_name': room.name,
        'sender_id': sender.id,
        'sender_name': f"{sender.first_name} {sender.last_name}",
        **{'sender_avatar': build_media_absolute_uri(sender.avatar.url) if sender.avatar else None},
        **{'content': message.message if message.message else None},
        **{'media': build_media_absolute_uri(message.media.url) if message.media else None},
        'timestamp': message.timestamp.isoformat(),
    }


@sync_to_async
def format_message(message):
    logger.info(f"Форматируем сообщение: {message}")
    return {
        'id': message.id,
        'sender': message.sender.id,
        **{'content': message.message if message.message else None},
        **{'media': build_media_absolute_uri(message.media.url) if message.media else None},
        **{'file_type': message.file_type if message.file_type else None},
        'timestamp': message.timestamp.isoformat(),
        **{'replied_to': message.replied_to.message if message.replied_to else None},
        'is_edited': message.is_edited,
        'is_deleted': message.is_deleted,
        'is_read': message.read_status,
    }
