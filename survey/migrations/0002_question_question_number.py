# Generated by Django 3.0.4 on 2020-03-20 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_number',
            field=models.IntegerField(default=0),
        ),
    ]
