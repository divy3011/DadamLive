# Generated by Django 3.2.8 on 2021-11-17 19:36

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0063_auto_20211118_0117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 17, 19, 36, 10, 546076, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='course',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 17, 19, 36, 10, 530408, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='enrolled_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 17, 19, 36, 10, 530408, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='imagesforactivity',
            name='timeStamp',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 17, 19, 36, 10, 546076, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 17, 19, 36, 10, 546076, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 17, 19, 36, 10, 546076, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 17, 19, 36, 10, 546076, tzinfo=utc)),
        ),
    ]
