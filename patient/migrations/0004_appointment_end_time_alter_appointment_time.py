# Generated by Django 5.1.1 on 2024-09-19 19:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('patient', '0003_alter_appointment_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='time',
            field=models.TimeField(choices=[(datetime.time(0, 0), '12:00 AM'), (datetime.time(1, 0), '01:00 AM'),
                                            (datetime.time(2, 0), '02:00 AM'), (datetime.time(3, 0), '03:00 AM'),
                                            (datetime.time(4, 0), '04:00 AM'), (datetime.time(5, 0), '05:00 AM'),
                                            (datetime.time(6, 0), '06:00 AM'), (datetime.time(7, 0), '07:00 AM'),
                                            (datetime.time(8, 0), '08:00 AM'), (datetime.time(9, 0), '09:00 AM'),
                                            (datetime.time(10, 0), '10:00 AM'), (datetime.time(11, 0), '11:00 AM'),
                                            (datetime.time(12, 0), '12:00 PM'), (datetime.time(13, 0), '01:00 PM'),
                                            (datetime.time(14, 0), '02:00 PM'), (datetime.time(15, 0), '03:00 PM'),
                                            (datetime.time(16, 0), '04:00 PM'), (datetime.time(17, 0), '05:00 PM'),
                                            (datetime.time(18, 0), '06:00 PM'), (datetime.time(19, 0), '07:00 PM'),
                                            (datetime.time(20, 0), '08:00 PM'), (datetime.time(21, 0), '09:00 PM'),
                                            (datetime.time(22, 0), '10:00 PM'), (datetime.time(23, 0), '11:00 PM')]),
        ),
    ]
