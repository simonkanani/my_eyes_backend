# Generated by Django 3.0.4 on 2020-03-22 20:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20200321_1233'),
        ('survey', '0007_response_time_stamp'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='response',
            unique_together={('question', 'patient')},
        ),
    ]