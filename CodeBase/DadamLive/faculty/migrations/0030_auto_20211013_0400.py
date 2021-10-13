# Generated by Django 3.2.8 on 2021-10-12 22:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0029_auto_20211013_0006'),
    ]

    operations = [
        migrations.AddField(
            model_name='illegalattempt',
            name='numberOfTimesAudioDetected',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 13, 4, 0, 53, 886387)),
        ),
        migrations.AlterField(
            model_name='course',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 13, 4, 0, 53, 879334)),
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='enrolled_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 13, 4, 0, 53, 880299)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 13, 4, 0, 53, 880299)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 13, 4, 0, 53, 880299)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 13, 4, 0, 53, 880299)),
        ),
    ]