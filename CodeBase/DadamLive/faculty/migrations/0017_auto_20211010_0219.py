# Generated by Django 2.2.22 on 2021-10-10 02:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0016_auto_20211010_0218'),
    ]

    operations = [
        migrations.AddField(
            model_name='illegalattempt',
            name='noPersonDetected',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 10, 2, 19, 50, 927979)),
        ),
        migrations.AlterField(
            model_name='course',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 10, 2, 19, 50, 914340)),
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='enrolled_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 10, 2, 19, 50, 915278)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 10, 2, 19, 50, 916396)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 10, 2, 19, 50, 916371)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 10, 2, 19, 50, 916338)),
        ),
    ]
