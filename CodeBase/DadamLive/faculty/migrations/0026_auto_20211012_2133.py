# Generated by Django 3.2.8 on 2021-10-12 16:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0025_auto_20211012_2121'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='writtenquestion',
            name='plagPercent',
        ),
        migrations.RemoveField(
            model_name='writtenquestion',
            name='sources',
        ),
        migrations.AddField(
            model_name='partofsubmission',
            name='plagPercent',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='partofsubmission',
            name='sources',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 33, 9, 344715)),
        ),
        migrations.AlterField(
            model_name='course',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 33, 9, 339684)),
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='enrolled_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 33, 9, 340700)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 33, 9, 340700)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 33, 9, 340700)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 21, 33, 9, 340700)),
        ),
    ]
