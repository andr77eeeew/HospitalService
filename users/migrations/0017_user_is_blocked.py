# Generated by Django 5.1.2 on 2024-11-14 19:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0016_rename_role_user_roles'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]
