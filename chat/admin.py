from django.contrib import admin

from chat.models import ChatRoom, ChatHistory


# Register your models here.

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'doctor', 'patient', 'created_at', 'active_users', 'active_voice_users')
    list_filter = ('doctor', 'patient')


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'room', 'sender', 'message', 'media', 'timestamp', 'is_edited', 'is_deleted', 'replied_to', 'read_status')
    list_filter = ('sender',)
