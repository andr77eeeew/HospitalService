# Generated by Django 5.1.2 on 2024-11-14 18:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0015_resetpassword'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='role',
            new_name='roles',
        ),
    ]
