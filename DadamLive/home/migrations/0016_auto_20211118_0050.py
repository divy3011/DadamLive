# Generated by Django 3.2.8 on 2021-11-18 00:50

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_auto_20211118_0049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forgotpassword',
            name='uni_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 17, 18, 50, 42, 385037, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='teachingassistant',
            name='uni_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 17, 18, 50, 42, 385037, tzinfo=utc)),
        ),
    ]
