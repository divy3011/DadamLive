# Generated by Django 3.2.8 on 2021-11-18 05:35

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0066_auto_20211118_0118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 18, 5, 35, 13, 568219, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='course',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 18, 5, 35, 13, 555579, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='enrolled_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 18, 5, 35, 13, 556624, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='imagesforactivity',
            name='timeStamp',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 18, 5, 35, 13, 565122, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='mcq',
            name='options',
            field=django_mysql.models.ListTextField(models.CharField(default='', max_length=100000), size=10),
        ),
        migrations.AlterField(
            model_name='mcq',
            name='question',
            field=models.CharField(max_length=50000, null=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 18, 5, 35, 13, 559254, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 18, 5, 35, 13, 559254, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 18, 5, 35, 13, 559254, tzinfo=utc)),
        ),
    ]
