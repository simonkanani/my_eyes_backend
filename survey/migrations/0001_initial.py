# Generated by Django 3.0.4 on 2020-03-25 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0006_auto_20200321_1233'),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_number', models.IntegerField()),
                ('question', models.CharField(max_length=150)),
                ('survey', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='survey.Survey')),
            ],
            options={
                'unique_together': {('question_number', 'survey')},
            },
        ),
        migrations.CreateModel(
            name='ResponseKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)])),
                ('response_key', models.CharField(choices=[('NT', 'NOT AT ALL TRUE'), ('LT', 'A LITTLE BIT TRUE'), ('MT', 'MOSTLY TRUE'), ('CT', 'COMPLETELY TRUE'), ('VD', 'VERY DIFFICULT'), ('D', 'DIFFICULT'), ('E', 'EASY'), ('VE', 'VERY EASY')], max_length=2)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Survey')),
            ],
            options={
                'unique_together': {('survey', 'response')},
            },
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)])),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='users.Patient')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Question')),
            ],
            options={
                'unique_together': {('question', 'patient')},
            },
        ),
    ]
