# Generated by Django 5.1.3 on 2024-11-27 14:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0017_user_is_blocked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='users_avatars/'),
        ),
    ]
