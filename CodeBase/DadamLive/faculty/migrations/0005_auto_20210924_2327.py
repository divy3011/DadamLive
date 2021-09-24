# Generated by Django 3.2.7 on 2021-09-24 17:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0004_auto_20210924_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='quiz_name',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 24, 23, 27, 56, 903148)),
        ),
        migrations.AlterField(
            model_name='course',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 24, 23, 27, 56, 894784)),
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='enrolled_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 24, 23, 27, 56, 895836)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 24, 23, 27, 56, 898512)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 24, 23, 27, 56, 898512)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 24, 23, 27, 56, 898512)),
        ),
    ]
