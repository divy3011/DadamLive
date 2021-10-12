# Generated by Django 3.2.8 on 2021-10-12 15:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0024_auto_20211012_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='webDetectionDone',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 21, 13, 20538)),
        ),
        migrations.AlterField(
            model_name='course',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 21, 13, 12011)),
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='enrolled_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 21, 13, 12011)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 21, 13, 12011)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 21, 13, 12011)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 21, 13, 12011)),
        ),
    ]
