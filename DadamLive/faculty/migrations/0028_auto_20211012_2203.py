# Generated by Django 3.2.8 on 2021-10-12 16:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0027_auto_20211012_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='marks_assigned',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 22, 3, 5, 303596)),
        ),
        migrations.AlterField(
            model_name='course',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 22, 3, 5, 298610)),
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='enrolled_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 22, 3, 5, 298610)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 22, 3, 5, 299607)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 22, 3, 5, 299607)),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 22, 3, 5, 299607)),
        ),
    ]