# Generated by Django 3.0.4 on 2020-04-13 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20200401_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='part_1_attempt_number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='part_2_attempt_number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
