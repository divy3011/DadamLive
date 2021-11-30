# Generated by Django 3.2.8 on 2021-10-19 18:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0046_auto_20211019_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 19, 23, 38, 45, 529477)),
        ),
        migrations.AlterField(
            model_name='course',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 19, 23, 38, 45, 523496)),
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='enrolled_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 19, 23, 38, 45, 524526)),
        ),
        migrations.AlterField(
            model_name='imagesforactivity',
            name='image',
            field=models.ImageField(null=True, upload_to='images_for_activity/'),
        ),
        migrations.AlterField(
            model_name='imagesforactivity',
            name='timeStamp',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 19, 23, 38, 45, 529477)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 19, 23, 38, 45, 525488)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 19, 23, 38, 45, 525488)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 19, 23, 38, 45, 525488)),
        ),
    ]