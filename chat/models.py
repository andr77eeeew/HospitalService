from django.db import models

from users.models import User


# Create your models here.

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_doctor')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_patient')
    created_at = models.DateTimeField(auto_now_add=True)
    active_users = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Room between {self.doctor} and {self.patient}'


class ChatHistory(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField(null=True, blank=True)
    media = models.FileField(upload_to='chat_media', blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    replied_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    read_status = models.BooleanField(default=False)

    def __str__(self):
        if self.is_deleted:
            return "This message has been deleted."
        return f"Message from {self.sender} in {self.room}"
