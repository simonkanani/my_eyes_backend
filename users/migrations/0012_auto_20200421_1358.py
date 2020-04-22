# Generated by Django 3.0.4 on 2020-04-21 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20200413_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preferences',
            name='theme',
            field=models.CharField(choices=[('DEFAULT', 'DEFAULT'), ('AUTUMN', 'AUTUMN'), ('DARK', 'DARK'), ('NEON', 'NEON')], default='DEFAULT', max_length=7),
        ),
    ]
