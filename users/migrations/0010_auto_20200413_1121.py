# Generated by Django 3.0.4 on 2020-04-13 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20200413_1059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='attempt_number',
        ),
        migrations.AddField(
            model_name='patient',
            name='current_attempt_number',
            field=models.BooleanField(default=1),
        ),
    ]
