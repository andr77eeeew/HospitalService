# Generated by Django 5.1.3 on 2024-11-27 14:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0008_chatroom_active_voice_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chathistory',
            name='media',
            field=models.FileField(blank=True, null=True, upload_to='chat_media/'),
        ),
    ]
