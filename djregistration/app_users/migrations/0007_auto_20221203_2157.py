# Generated by Django 2.2 on 2022-12-03 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_users', '0006_auto_20221203_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='news_tag',
            field=models.ManyToManyField(blank=True, to='app_users.Tag', verbose_name='Новостной тег'),
        ),
    ]