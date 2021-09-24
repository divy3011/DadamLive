# Generated by Django 3.2.7 on 2021-09-20 13:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userType', models.CharField(max_length=20, null=True)),
                ('userTypeCode', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('userType', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.usertype')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='us_ma.png', upload_to='post_images/')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('userInformation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.userinformation')),
            ],
        ),
    ]
