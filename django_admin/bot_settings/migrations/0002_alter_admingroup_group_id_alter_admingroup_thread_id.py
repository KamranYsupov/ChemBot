# Generated by Django 5.0 on 2024-03-07 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_settings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admingroup',
            name='group_id',
            field=models.BigIntegerField(unique=True, verbose_name='ID Группа'),
        ),
        migrations.AlterField(
            model_name='admingroup',
            name='thread_id',
            field=models.BigIntegerField(null=True, unique=True, verbose_name='ID Обсуждения'),
        ),
    ]
