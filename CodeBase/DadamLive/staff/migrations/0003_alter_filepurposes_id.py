# Generated by Django 3.2.8 on 2021-10-11 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_auto_20211010_0218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filepurposes',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
