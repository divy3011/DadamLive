# Generated by Django 3.2.8 on 2021-10-06 08:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0010_auto_20211006_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 6, 14, 11, 16, 548787)),
        ),
        migrations.AlterField(
            model_name='course',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 6, 14, 11, 16, 547278)),
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='enrolled_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 6, 14, 11, 16, 547278)),
        ),
        migrations.AlterField(
            model_name='partofsubmission',
            name='answer',
            field=models.CharField(max_length=1000000, null=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 6, 14, 11, 16, 548787)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 6, 14, 11, 16, 548787)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 6, 14, 11, 16, 548787)),
        ),
    ]
